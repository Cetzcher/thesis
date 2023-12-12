import drawing.map_operations as ops
import cv2 
import numpy as np

class Image:
    """An image here is basically a grey scale image i.e. each 
    pixel in the image is in the range of [0, 1]
    
    This data can later be transformed into RGB images by applying a pallette to it
    """

    def __init__(self, size=512, init_data=None, is_byte=False, is_rgb=False) -> None:
        self.__size = size
        self.__is_byte = is_byte
        self.__is_rgb = is_rgb
        if init_data is None:
            self.__data = np.zeros((size, size), np.double)
        else:
            self.__data = init_data 

    def save(self, path):
        #ops.write(self.data, path)
        dim = self.__data.shape[-1] 
        if dim == 4:
            c_red, c_green, c_blue, c_alpha = cv2.split(self.__data)
            mat = cv2.merge((c_blue, c_green, c_red, c_alpha))
        elif dim == 3:
            c_red, c_green, c_blue = cv2.split(self.__data)
            mat = cv2.merge((c_blue, c_green, c_red))

        else:
            mat = self.__data
        cv2.imwrite(path, mat)

    @property
    def data(self):
        return self.__data

    def copy(self):
        return Image(
            size=self.__size, 
            init_data=self.data,
            is_byte=self.__is_byte,
            is_rgb=self.__is_rgb
        )

    def as_byte_image(self):
        """Maps the image from [0, 1] to [0, 255]"""
        if self.__is_byte:
            return self.copy()
        return Image(
            size=self.__size,
            init_data=ops.to_byte(self.data),
            is_byte=True,
            is_rgb=self.__is_rgb
        )

    def as_pallete(self, palette):
        if self.__is_rgb:
            return self.copy()
        if not self.__is_byte:
            return self.as_byte_image().as_pallete(palette=palette)
        return Image(
            size=self.__size,
            init_data=ops.to_palette(self.data, palette),
            is_byte=True,
            is_rgb=True
        )
    
    def as_alpha(self):
        assert self.__is_rgb
        c_red, c_green, c_blue = cv2.split(self.__data)
        alpha = np.ones((self.__size, self.__size), np.uint8) * 255
        rgba = cv2.merge((c_red, c_green, c_blue, alpha))
        return Image(
            size=self.__size,
            init_data=rgba,
            is_byte=True,
            is_rgb=True
        )
    

    def __validate_value(self, value):
        if self.__is_rgb:
            assert len(value) == 3 or len(value) == 4
        elif self.__is_byte:
            assert value >= 0 and value <= 255
        else:
            assert value >= 0 and value <= 1

    def line(self, start, end, value, thickness=1):
        self.__validate_value(value)
        cv2.line(self.data, start, end, value, thickness=thickness)
    
    def circle(self, center, radius, value):
        self.__validate_value(value)
        try:
            cv2.circle(self.data, center, radius, value, thickness=-1)
        except cv2.error:
            print(f"Error upon call of circle with center = {center}, r={radius}, value={value}")
            raise


    def text(self, postion, text, value):
        pass
