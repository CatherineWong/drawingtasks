"""object_primitives.py | Author : Catherine Wong.
Graphics primitives based on objects and spatial relations. Places predefined objects on a grid.

Defines Python semantics for DreamCoder primitives: objects are numpy arrays containing an image; transformations are operations on arrays.

Also defines rendering utilities to convert programs and sets of strokes into single images.

Credit: builds on primitives designed by Lucas Tian in: https://github.com/ellisk42/ec/blob/draw/dreamcoder/domains/draw/primitives.py
"""
import os
import math
import cairo
import imageio
import numpy as np
from dreamcoder.program import Program, Primitive
from dreamcoder.type import baseType, arrow, tmaybe, t0, t1, t2

### Base types
tstroke = baseType("tstroke")
tangle = baseType("tangle")
tscale = baseType("tscale")
tdist = baseType("tdist")
ttrorder = baseType("ttorder")
ttransmat = baseType("ttransmat")
trep = baseType("trep")

### Constant values
XYLIM = 3.0  # i.e., -3 to 3
SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT = 128

SCALES = [0.5, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0]
NPOLY = range(3, 7)  # range of regular polyogns allowed.
DISTS = (
    [-2.5, -2.0, -1.5, -1.0, -0.5, -0.25, 0, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    + [-1.75, -0.65, 0.45, 1.55, 1.1]
    + [0.5 / math.tan(math.pi / n) for n in range(3, 7)]
)
THETAS = (
    [j * (2 * math.pi / 8) for j in range(8)] + [-2 * math.pi / 6] + [-2 * math.pi / 12]
)
ORDERS = ["trs", "tsr", "rts", "rst", "srt", "str"]

scales = [Primitive("scale{}".format(i), tscale, j) for i, j in enumerate(SCALES)]
distances = [Primitive("dist{}".format(i), tdist, j) for i, j in enumerate(DISTS)]
angles = [Primitive("angle{}".format(i), tangle, j) for i, j in enumerate(THETAS)]
orders = [Primitive(j, ttrorder, j) for j in ORDERS]
repetitions = [
    Primitive("rep{}".format(i), trep, j + 1) for i, j in enumerate(range(7))
]

# Basic graphics objects
_line = [np.array([(0.0, 0.0), (1.0, 0.0)])]
_circle = [
    np.array(
        [
            (0.5 * math.cos(theta), 0.5 * math.sin(theta))
            for theta in np.linspace(0.0, 2.0 * math.pi, num=30)
        ]
    )
]

_emptystroke = []  # ---
objects = [
    Primitive("emptystroke", tstroke, _emptystroke),
    Primitive("line", tstroke, _line),
    Primitive("circle", tstroke, _circle),
]

# Utilities for importing grammars over object primitives.

# Utilities for rendering and derendering images.
def render_stroke_arrays_to_canvas(
    stroke_arrays,
    stroke_width_height=2 * XYLIM,
    canvas_width_height=SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT,
):
    """See original source: prog2pxl https://github.com/ellisk42/ec/blob/draw/dreamcoder/domains/draw/primitives.py"""
    scale = canvas_width_height / stroke_width_height

    canvas_array = np.zeros((canvas_width_height, canvas_width_height), dtype=np.uint8)
    surface = cairo.ImageSurface.create_for_data(
        canvas_array, cairo.Format.A8, canvas_width_height - 2, canvas_width_height - 2
    )
    context = cairo.Context(surface)
    context.set_source_rgb(256, 256, 256)

    for stroke_array in stroke_arrays:
        renderable_stroke = np.copy(stroke_array)
        renderable_stroke += stroke_width_height / 2  # Centering
        renderable_stroke *= scale
        for pixel in renderable_stroke:
            context.line_to(pixel[0], pixel[1])
        context.stroke()
    return np.flip(canvas_array, 0) / (canvas_width_height * 2)


def render_parsed_program(program):
    if not hasattr(program, "rendering"):
        program.rendering = render_stroke_arrays_to_canvas(program.evaluate([]))
    return program.rendering


def export_rendered_program(rendered_array, export_id, export_dir):
    filename = os.path.join(export_dir, f"{export_id}.png")
    inverted_array = 1 - rendered_array  # Invert B/W image for aesthetics.
    imageio.imwrite(filename, inverted_array)
    return filename
