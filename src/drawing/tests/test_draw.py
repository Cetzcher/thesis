from drawing.kernels import circle
from drawing.color_palettes import seaborn_like_128
from util.paths import OUT_PATH
from drawing.image import Image

def test_draw_primitives():
    im = Image(
        size=128
    )

    im.line((0, 0), (128, 128), 0.5, thickness=3)
    im.line((128, 0), (128//2, 128//2), 0.3)

    im.circle((128//2, 20), 20, 0.8)
    im.as_byte_image().save(str(OUT_PATH / "primitve_test.png"))

def test_draw_pallettization():
    im = Image(
        size=128
    )

    im.line((0, 0), (128, 128), 0.5, thickness=3)
    im.line((128, 0), (128//2, 128//2), 0.3)

    im.circle((128//2, 20), 20, 0.8)
    im.as_byte_image().as_pallete(seaborn_like_128).save(str(OUT_PATH / "primitve_pallettization_test.png"))


def test_draw_directly():
    im = Image(
        size=128
    )

    circle(im.data, (64, 64), 32, 1, lambda x: x ** (1/2))
    im.as_byte_image().save(str(OUT_PATH / "draw_directly.png"))
