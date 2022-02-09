"""
gadgets_primitives.py | Author : Catherine Wong.

Graphics primitives for rendering gadgest in the Gadgets1K dataset. Based on simple stroke primitives and spatial relations.

Defines Python semantics for DreamCoder primitives: objects are numpy arrays containing an image; transformations are operations on arrays.

Also defines rendering utilities to convert programs and sets of strokes into single images.

This also contains utilities for generating parseable program strings for certain common higher order objects.

Credit: builds on primitives designed by Lucas Tian in: https://github.com/ellisk42/ec/blob/draw/dreamcoder/domains/draw/primitives.py
"""
import os
import math
import cairo
import imageio
import numpy as np
from dreamcoder.utilities import Curried
from dreamcoder.program import *
from dreamcoder.type import baseType, arrow, tmaybe, t0, t1, t2

from primitives.object_primitives import (
    tstroke,
    ttransmat,
    _makeAffine,
    _tform_once,
    some_none,
    _repeat,
    _connect,
    transform,
)

tfloat = baseType("tfloat")

## Mathematical operations.
SCALES = np.arange(0.5, 10, 0.25)  # Scaling constants
DISTS = np.arange(-3.0, 3.25, 0.25)  # Distances
INTEGERS = range(0, 13)  # General scaling constants
numeric_constants = set(list(SCALES) + list(DISTS) + list(INTEGERS))
constants = [
    Primitive(f"{n:g}", tfloat, n, override_globals=True) for n in numeric_constants
]
constants += [Primitive("pi", tfloat, math.pi, override_globals=True)]


def _addition(x):
    return lambda y: x + y


def _subtraction(x):
    return lambda y: x - y


def _multiplication(x):
    return lambda y: x * y


def _division(x):
    return lambda y: x / y


def _pow(x):
    return lambda y: x ** y


def _max(x):
    return lambda y: max(x, y)


def _min(x):
    return lambda y: min(x, y)


math_operations = [
    Primitive("-", arrow(tfloat, tfloat, tfloat), _subtraction, override_globals=True),
    Primitive("+", arrow(tfloat, tfloat, tfloat), _addition, override_globals=True),
    Primitive(
        "*", arrow(tfloat, tfloat, tfloat), _multiplication, override_globals=True
    ),
    Primitive("/", arrow(tfloat, tfloat, tfloat), _division),
    Primitive("pow", arrow(tfloat, tfloat, tfloat), _pow),
    Primitive("sin", arrow(tfloat, tfloat), math.sin),
    Primitive("cos", arrow(tfloat, tfloat), math.cos),
    Primitive("tan", arrow(tfloat, tfloat), math.tan),
    Primitive("max", arrow(tfloat, tfloat, tfloat), _max),
    Primitive("min", arrow(tfloat, tfloat, tfloat), _min),
]

### Basic transform.
# We use a weaker typing than the original in object_primitives.


def _makeAffineSimple(s=1.0, theta=0.0, x=0.0, y=0.0):
    return _makeAffine(s, theta, x, y)


transformations = [
    Primitive(
        "M",  # Makes a transformation matrix
        arrow(
            tfloat,  # Scale
            tfloat,  # Angle
            tfloat,  # Translation X
            tfloat,  # Translation Y
            ttransmat,
        ),
        Curried(_makeAffineSimple),
        alternate_names={
            DEFAULT_NAME: "M",
            VERBOSITY_0: "transform_matrix",
            VERBOSITY_1: "transform_matrix_scale_angle_x_y",
        },
    ),
    Primitive(
        "T",
        arrow(tstroke, ttransmat, tstroke),
        Curried(_tform_once),
        alternate_names={
            DEFAULT_NAME: "T",
            VERBOSITY_0: "transform",
            VERBOSITY_1: "apply_transform_matrix_to_stroke",
        },
    ),  # Transform: applies a transformation to a stroke array
    Primitive(
        "C",
        arrow(tstroke, tstroke, tstroke),
        Curried(_connect),
        alternate_names={
            DEFAULT_NAME: "C",
            VERBOSITY_0: "connect_strokes",
            VERBOSITY_1: "connect_strokes",
        },
    ),  # Connects two strokes into a single new primitive
    Primitive(
        "repeat",
        arrow(tstroke, tfloat, ttransmat, tstroke),
        Curried(_repeat),
        override_globals=True,
        alternate_names={
            DEFAULT_NAME: "repeat",
            VERBOSITY_0: "repeat_transform",
            VERBOSITY_1: "repeat_transform_n_times",
        },
    ),  # Repeats a transformation n times against a base primitive.
]


def connect_strokes(stroke_strings):
    # Utility function to connect several strings into a single stroke. This could be replaced later with a continuation.
    if len(stroke_strings) == 1:
        return stroke_strings[0]

    connected = f"(C {stroke_strings[0]} {stroke_strings[1]})"
    for i in range(2, len(stroke_strings)):
        connected = f"(C {connected} {stroke_strings[i]})"
    return connected


### Basic graphics objects
# Note that any basic graphics object is a list of pixel arrays.
_line = [np.array([(0.0, 0.0), (1.0, 0.0)])]
_circle = [
    np.array(
        [
            (0.5 * math.cos(theta), 0.5 * math.sin(theta))
            for theta in np.linspace(0.0, 2.0 * math.pi, num=30)
        ]
    )
]
_rectangle = [
    np.array([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5)])
]


def __scaled_rectangle(width, height):
    strokes = transform(_line, s=width, x=-(width * 0.5), y=height * 0.5) + transform(
        _line, s=width, x=-(width * 0.5), y=-(height * 0.5)
    )
    vertical_line = transform(_line, theta=math.pi / 2)
    strokes += transform(vertical_line, s=height, x=(width * 0.5), y=-(height * 0.5))
    strokes += transform(vertical_line, s=height, x=-(width * 0.5), y=-(height * 0.5))

    return strokes


def _scaled_rectangle(w):
    return lambda h: __scaled_rectangle(w, h)


_emptystroke = []
objects = [
    Primitive(
        "empt",
        tstroke,
        _emptystroke,
        alternate_names={
            DEFAULT_NAME: "empt",
            VERBOSITY_0: "empty_stroke",
            VERBOSITY_1: "empty_stroke",
        },
    ),
    Primitive(
        "l",
        tstroke,
        _line,
        alternate_names={
            DEFAULT_NAME: "l",
            VERBOSITY_0: "line",
            VERBOSITY_1: "base_line",
        },
    ),
    Primitive(
        "c",
        tstroke,
        _circle,
        alternate_names={
            DEFAULT_NAME: "c",
            VERBOSITY_0: "circle",
            VERBOSITY_1: "base_circle",
        },
    ),
    Primitive(
        "r",
        tstroke,
        _rectangle,
        alternate_names={
            DEFAULT_NAME: "r",
            VERBOSITY_0: "square",
            VERBOSITY_1: "base_square",
        },
    ),
    Primitive(
        "r_s",
        arrow(tfloat, tfloat, tstroke),
        _scaled_rectangle,
        alternate_names={
            DEFAULT_NAME: "r_s",
            VERBOSITY_0: "rectangle",
            VERBOSITY_1: "scaled_rectangle_w_h",
        },
    ),
]

## Higher order utility functions for generating program strings simultaneously with stroke primitives.


def peval(program_string):
    try:
        return float(program_string)
    except:
        p = Program.parse(program_string)
        output = p.evaluate([])
        return output


def get_simplified(program_string):
    try:
        return f"{float(program_string):g}"
    except:
        p = Program.parse(program_string)
        output = p.evaluate([])
        output = f"{output:g}"
        try:
            p = Program.parse(output)
            _ = p.evaluate([])
            return str(output)
        except:
            return program_string


def M_string(s="1", theta="0", x="0", y="0", simplify=True):
    affine_matrix = _makeAffineSimple(peval(s), peval(theta), peval(x), peval(y))
    if simplify:
        m_string = f"(M {get_simplified(s)} {get_simplified(theta)} {get_simplified(x)} {get_simplified(y)})"
    else:
        m_string = f"(M {s} {theta} {x} {y})"
    return affine_matrix, m_string


def T_string(p, p_string, s="1", theta="0", x="0", y="0", simplify=True):
    """Transform Python utility wrapper that applies an affine transformation matrix directly to a primitive, while also generating a string that can be applied to a downstream stroke. Python-usable API that mirrors the functional semantics"""
    tmat, m_string = M_string(s, theta, x, y, simplify=simplify)  # get affine matrix.
    p = _tform_once(p, tmat)
    t_string = f"(T {p_string} {m_string})"
    return p, t_string


def scaled_rectangle_string(w, h, simplify=True):
    if simplify:
        w, h = get_simplified(w), get_simplified(h)
    scaled_rectangle_string = f"(r_s {w} {h})"
    return peval(scaled_rectangle_string), scaled_rectangle_string


def polygon_string(n, simplify=True):
    if simplify:
        n = get_simplified(str(n))
    y = f"(/ 0.5 (tan (/ pi {n})))"
    theta = f"(/ (* 2 pi) {n})"

    # Base line that forms the side.
    _, base_line = T_string(_line, "l", x="-0.5", y=y)

    # Rotation
    _, rotation = M_string(theta=theta)

    polygon_string = f"(repeat {base_line} {n} {rotation})"
    return peval(polygon_string), polygon_string


def nested_scaling_string(shape_string, n, scale_factor):
    # Scale factor
    _, scale = M_string(s=scale_factor)
    nested_scaling_string = f"(repeat {shape_string} {n} {scale})"

    return peval(nested_scaling_string), nested_scaling_string


def rotation_string(
    p, p_string, n, displacement="0.5", decorator_start_angle="(/ pi 4)", simplify=True
):
    if simplify:
        n = get_simplified(n)
        displacement = get_simplified(displacement)
    y = f"(* {displacement} (sin {decorator_start_angle}))"
    x = f"(* {displacement} (cos {decorator_start_angle}))"
    theta = f"(/ (* 2 pi) {n})"

    # Base line that forms the side.
    _, base_object = T_string(p, p_string, x=x, y=y)

    # Rotation
    _, rotation = M_string(theta=theta)

    rotated_object_string = f"(repeat {base_object} {n} {rotation})"
    return peval(rotated_object_string), rotated_object_string


c_string = (
    _circle,
    "c",
)  # Circle
r_string = (_rectangle, "r")  # Rectangle
cc_string = T_string(c_string[0], c_string[-1], s="2")  # Double scaled circle
hexagon_string = polygon_string(6)
octagon_string = polygon_string(8)
l_string = (_line, "l")
short_l_string = T_string(
    l_string[0], l_string[-1], x="(- 0 0.5)"
)  # Short horizontal line

# Shape classes.
LANG_TINY, LANG_SMALL, LANG_MEDIUM, LANG_LARGE = "tiny", "small", "medium", "large"
LANG_CIRCLE, LANG_RECTANGLE, LANG_LINE, LANG_SQUARE = (
    "circle",
    "rectangle",
    "line",
    "square",
)
LANG_GON_NAMES = {
    "3": "triangle",
    "4": "square",
    "5": "pentagon",
    "6": "hexagon",
    "7": "septagon",
    "8": "octogon",
    "9": "nonagon",
}


class Shape:
    def __init__(
        self,
        strokes=None,
        base_program=None,
        synthetic_adjectives=None,
        synthetic_noun=None,
        synthetic_abstractions=None,
    ):
        self.strokes = strokes
        self.base_program = base_program
        self.synthetic_adjectives = synthetic_adjectives
        self.synthetic_noun = synthetic_noun
        self.synthetic_abstractions = synthetic_abstractions


c_shape = Shape(
    _circle, "c", synthetic_adjectives=[LANG_TINY], synthetic_noun=LANG_CIRCLE
)
r_shape = Shape(
    _rectangle, "r", synthetic_adjectives=[LANG_TINY], synthetic_noun=LANG_SQUARE
)
