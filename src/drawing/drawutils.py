from drawing.color_palettes import seaborn_like_128
from . import util as ut
from . import map_operations as mapops
from PIL import ImageDraw
from PIL import Image
import numpy as np
from skimage.draw import line_aa


class Drawutils:

    def __init__(self, heightmap: HeightMap, graph, options=None, draw_widget_callback=None) -> None:
        self.__hm = heightmap
        self.__graph = graph
        self.__draw_callback = draw_widget_callback
        if not options:
            options = {
                "invert": False,
                "normalize": True,
                "edges": True,
                "palette": seaborn_like_128,
                "add_key": False,
                "border_width": 0,
                "nodes": True,
                "labels": True
            }
        self.__options = options

    def set_option(self, name, value):
        self.__options[name] = value

    @property
    def heightmap(self):
        return self.__hm

    def draw(self, node_positions=None):
        current_map_state = self.__hm.map_state
        size = self.__hm.size
        max_val = np.max(current_map_state)
        if not current_map_state.flags.writeable:
            print(current_map_state, "TYPE", type(current_map_state), "SIZE", current_map_state.size)
            tmp = np.zeros((size, size))
            for y in range(size):
                for x in range(size):
                    tmp[y][x] = current_map_state[y][x]
            current_map_state = tmp
            assert current_map_state.flags.writeable
        pad_width = self.__options["border_width"]
        if pad_width > 0:
            current_map_state = np.pad(current_map_state, pad_width)

        if self.__options.get("normalize", True):
            current_map_state = mapops.normalize(current_map_state)

        current_map_state = mapops.to_byte(current_map_state)
        # palletize
        palette = self.__options.get("palette", seaborn_like_128)
        current_map_state = mapops.to_palette(current_map_state, palette)
    
        if node_positions:
            if self.__options.get("edges"):
                current_map_state = self._draw_edges(
                    node_positions, 
                    current_map_state, 
                    use_color=self.__options.get("edge_color", (0, 128, 0))
                )
        

            if self.__options.get("nodes"):
                current_map_state = self._draw_nodes(
                    node_positions, 
                    current_map_state, 
                    use_color=self.__options.get("node_color", (255, 0, 0))
                )

            if self.__options.get("labels"):
                current_map_state = self._draw_labels(
                    node_positions, 
                    current_map_state,
                    use_color=self.__options.get("label_color", (0, 255, 255))
                )
            if not current_map_state.flags.writeable:
              current_map_state = current_map_state.copy()
              assert current_map_state.flags.writeable
            
            if self.__options.get("add_key"):
                #raise Exception("Not implemented currently")
                entries = len(palette)  # number of intervals
                key_item_w = self.__hm.size // entries
                key_item_height = pad_width // 2  if pad_width > 0 else 5
                key_item_height = max(key_item_height, 5)
                for i, item in enumerate(palette):                    
                    for j in range(key_item_w * i, key_item_w * (i+1)):
                        for h in range(key_item_height):
                            try:
                                current_map_state[h, pad_width + j] = palette[i][2]  # set color in this region 
                            except Exception as e:
                                raise Exception(f"Oops {type(current_map_state)}, flags:{current_map_state.flags}") from e
                        # add black line seperator
                        current_map_state[key_item_height + 1, pad_width + j] = (0, 0, 0)

                if self.__options.get("add_key_labels", True):
                    im = Image.fromarray(current_map_state)
                    idraw = ImageDraw.Draw(im)
                    for i, item in enumerate(palette):                    
                        start, end, val = item
                        start_p = start / 255
                        end_p = end / 255
                        if i > 0 and i < entries - 1:
                            idraw.text((pad_width + key_item_w * i, key_item_height), f"<{start_p * 100:.2f}", fill=(128, 128, 255))
                        elif i == entries - 1:
                            idraw.text((pad_width + key_item_w * i, key_item_height), f"{start_p * 100:.2f}-{end_p * 100:.2f}", fill=(128, 128, 255))
                        else:
                            idraw.text((pad_width + key_item_w * i, key_item_height), f"{start_p * 100:.2f}", fill=(128, 128, 255))
                    idraw.text((0, 0), f"1={max_val*100:.2f}", fill=(128, 128, 255))
                    current_map_state = np.array(im)
            
            if self.__draw_callback:
                current_map_state = self.__draw_callback(self, current_map_state)
            return current_map_state
        
    def save(self, pos, name="figure.png"):
        state = self.draw(pos)
        if not isinstance(name, str):
            name = str(name)
        mapops.write(state, name, mode="RGB")

    def _draw_nodes(self, positions, map_state, use_color=(255, 0, 0)):
        # use color can either be a tuple, then we will use if for every color or a dict 
        # with entry "default": (3-tupple) and id: (3-tuple) for coloring a specific node
        FALLBACK_COLOR = (255, 0, 0)
        default_color = FALLBACK_COLOR
        if isinstance(use_color, dict):
            default_color = use_color.get("default", FALLBACK_COLOR)
        
        offset = self.__options.get("border_width", 0)
        hm = self.__hm
        for node, pos in positions.items():
            x, y = pos
            for i in range(-4, 4):
                for j in range(-4, 4):
                    if hm.in_bounds(x + i, y + j):
                        color = use_color
                        if isinstance(use_color, dict):
                            color = use_color.get(node, default_color)
                        else:
                            color = use_color	
                        map_state[y + j + offset, x + i + offset] = color
        return map_state

    def _draw_edges(self, positions, map_state, use_color=(0, 128, 0)):
        offset = self.__options.get("border_width", 0)

        for u, v in self.__graph.G.edges:
            ux, uy = positions[u]
            vx, vy = positions[v]
            self.draw_line(map_state, positions[u], positions[v], use_color)
        return map_state
    
    def draw_line(self, map_state, xystart, xyend, color):
        offset = self.__options.get("border_width", 0)
        ux, uy = xystart
        vx, vy = xyend
        line_y, line_x, line_intensity = line_aa(uy, ux, vy, vx)
        for i in range(len(line_y)):
            cx, cy = line_x[i], line_y[i]
            ypos = cy + offset
            xpos = cx + offset
            map_state[cy + offset, cx + offset] = color
        return map_state

    def _draw_labels(self, positions, map_state, use_color=(0, 255, 255), do_show=False):
        offset = self.__options.get("border_width", 0)

        im = Image.fromarray(map_state)
        idraw = ImageDraw.Draw(im)
        for node, pos in positions.items():
            x, y = pos
            x, y = x + offset, y + offset
            idraw.text((x, y), str(node), fill=use_color)
        if do_show:
            im.show()
        return np.asarray(im)