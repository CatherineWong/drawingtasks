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
from num2words import num2words
from dreamcoder.utilities import Curried
from dreamcoder.program import *
from dreamcoder.type import baseType, arrow, tmaybe, t0, t1, t2
from tasksgenerator.tasks_generator import *

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


def M_string(s="1", theta="0", x="0", y="0", simplify=False):
    affine_matrix = _makeAffineSimple(peval(s), peval(theta), peval(x), peval(y))
    if simplify:
        m_string = f"(M {get_simplified(s)} {get_simplified(theta)} {get_simplified(x)} {get_simplified(y)})"
    else:
        m_string = f"(M {s} {theta} {x} {y})"
    return affine_matrix, m_string


def T_string(p, p_string, s="1", theta="0", x="0", y="0", simplify=False):
    """Transform Python utility wrapper that applies an affine transformation matrix directly to a primitive, while also generating a string that can be applied to a downstream stroke. Python-usable API that mirrors the functional semantics"""
    tmat, m_string = M_string(s, theta, x, y, simplify=simplify)  # get affine matrix.
    p = _tform_once(p, tmat)
    t_string = f"(T {p_string} {m_string})"
    return p, t_string


def scaled_rectangle_string(w, h, simplify=False):
    if simplify:
        w, h = get_simplified(w), get_simplified(h)
    scaled_rectangle_string = f"(r_s {w} {h})"
    return peval(scaled_rectangle_string), scaled_rectangle_string


def polygon_string(n, simplify=False):
    if simplify:
        n = get_simplified(str(n))
    y = f"(/ 0.5 (tan (/ pi {n})))"
    theta = f"(/ (* 2 pi) {n})"

    # Base line that forms the side.
    _, base_line = T_string(_line, "l", x="-0.5", y=y, simplify=simplify)

    # Rotation
    _, rotation = M_string(theta=theta, simplify=simplify)

    polygon_string = f"(repeat {base_line} {n} {rotation})"
    return peval(polygon_string), polygon_string


def nested_scaling_string(shape_string, n, scale_factor):
    # Scale factor
    _, scale = M_string(s=scale_factor)
    nested_scaling_string = f"(repeat {shape_string} {n} {scale})"

    return peval(nested_scaling_string), nested_scaling_string


def rotation_string(
    p, p_string, n, displacement="0.5", decorator_start_angle="(/ pi 4)", simplify=False
):

    if simplify:
        n = get_simplified(n)
        displacement = get_simplified(displacement)
    y = f"(* {displacement} (sin {decorator_start_angle}))"
    x = f"(* {displacement} (cos {decorator_start_angle}))"
    theta = f"(/ (* 2 pi) {n})"

    # Base line that forms the side.
    _, base_object = T_string(p, p_string, x=x, y=y, simplify=simplify)

    # Rotation
    _, rotation = M_string(theta=theta, simplify=simplify)

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


### Shape wrapper class. Contains sub-fields for the stroke array, base DSL program, synthetic language, and synthetic abstractions associated with the shape.
LANG_A = "a"
LANG_TINY, LANG_SMALL, LANG_MEDIUM, LANG_LARGE, LANG_VERY_LARGE = (
    "tiny",
    "small",
    "medium",
    "large",
    "very large",
)
LANG_SIZES = [LANG_TINY, LANG_SMALL, LANG_MEDIUM, LANG_LARGE, LANG_VERY_LARGE]
LANG_CIRCLE, LANG_RECTANGLE, LANG_LINE, LANG_SQUARE = (
    "circle",
    "rectangle",
    "line",
    "square",
)
LANG_CENTER_OF_THE_IMAGE = "center of the image"
LANG_GON_NAMES = {
    3: "triangle",
    4: "square",
    5: "pentagon",
    6: "hexagon",
    7: "septagon",
    8: "octagon",
    9: "nonagon",
}


class Shape:
    def __init__(
        self,
        strokes=[],
        base_program=None,
        unsimplified_program=None,
        synthetic_language=None,  # A list of language dicts for each stroke.
        synthetic_abstractions=None,
    ):
        self.strokes = strokes
        self.base_program = base_program
        self.unsimplified_program = unsimplified_program
        if self.base_program is not None and self.unsimplified_program is None:
            self.unsimplified_program = base_program
        self.synthetic_language = synthetic_language
        if synthetic_language is None:
            self.synthetic_language = [copy.deepcopy(SYNTHETIC_LANG_DICT)]
        self.synthetic_abstractions = synthetic_abstractions
        if synthetic_abstractions is None:
            self.synthetic_abstractions = copy.deepcopy(SYNTHETIC_DICT)

    def add_shapes(self, new_shapes):
        # Connect all of the programs.
        base_program = connect_strokes([s.base_program for s in new_shapes])
        unsimplified_program = connect_strokes(
            [s.unsimplified_program for s in new_shapes]
        )
        self.base_program = (
            base_program
            if self.base_program is None
            else connect_strokes([self.base_program, base_program])
        )
        self.unsimplified_program = (
            unsimplified_program
            if self.unsimplified_program is None
            else connect_strokes([self.unsimplified_program, unsimplified_program])
        )
        for s in new_shapes:
            self.strokes += copy.deepcopy(s.strokes)
            for k in s.synthetic_abstractions:
                self.synthetic_abstractions[k] += s.synthetic_abstractions[k]
            self.synthetic_language += s.synthetic_language

    @staticmethod
    def init_with_language(
        strokes,
        base_program,
        unsimplified_program=None,
        level=MID_LEVEL_LANG,
        nouns=[],
        adjectives=[],
        article=[],
        where=[LANG_CENTER_OF_THE_IMAGE],
    ):
        shape = Shape(
            strokes=strokes,
            base_program=base_program,
            unsimplified_program=unsimplified_program,
        )
        shape.synthetic_language[0][level][LANG_NOUNS] = nouns
        shape.synthetic_language[0][level][LANG_ADJECTIVES] = adjectives
        shape.synthetic_language[0][level][LANG_ARTICLE] = article
        shape.synthetic_language[0][level][LANG_WHERE] = where
        return shape

    def _connect_language(self):
        # Connects all of the what language into one.
        for stroke in range(len(self.synthetic_language)):
            for level in self.synthetic_language[stroke]:
                self.synthetic_language[stroke][level][LANG_WHAT] = " ".join(
                    self.synthetic_language[stroke][level][LANG_ARTICLE]
                    + self.synthetic_language[stroke][level][LANG_ADJECTIVES]
                    + self.synthetic_language[stroke][level][LANG_NOUNS]
                )

    def _replace_size_language(self, new_size, stroke=0, level=MID_LEVEL_LANG):
        new_adjectives = []
        for adjective in self.synthetic_language[stroke][level][LANG_ADJECTIVES]:
            new_adj = adjective if adjective not in LANG_SIZES else new_size
            new_adjectives.append(new_adj)
        self.synthetic_language[stroke][level][LANG_ADJECTIVES] = new_adjectives

    def _replace_article(self, prefix, n, stroke=0, level=MID_LEVEL_LANG):
        self.synthetic_language[stroke][level][LANG_ARTICLE] = [
            prefix + " " + num2words(n)
        ]
        self.synthetic_language[stroke][level][LANG_NOUNS] = [
            n + "s" for n in self.synthetic_language[stroke][level][LANG_NOUNS]
        ]

    def _print_language(
        self, level=MID_LEVEL_LANG, whats=True, wheres=False, silent=False
    ):
        if whats:
            what_lang = [stroke[level][LANG_WHAT] for stroke in self.synthetic_language]
            if not silent:
                print(what_lang)
            return what_lang
        if wheres:
            where_lang = [
                stroke[level][LANG_WHERE] for stroke in self.synthetic_language
            ]
            if not silent:
                print(where_lang)
            return where_lang


r_shape = Shape.init_with_language(
    _rectangle, "r", nouns=[LANG_SQUARE], adjectives=[LANG_TINY], article=[LANG_A]
)
l_shape = Shape.init_with_language(
    _line, "l", nouns=[LANG_LINE], adjectives=[LANG_TINY], article=[LANG_A]
)
c_shape = Shape.init_with_language(
    _circle, "c", nouns=[LANG_CIRCLE], adjectives=[LANG_TINY], article=[LANG_A]
)

cc_shape = Shape.init_with_language(
    cc_string[0],
    cc_string[1],
    nouns=[LANG_CIRCLE],
    adjectives=[LANG_SMALL],
    article=[LANG_A],
)


def T_shape(shape, s="1", theta="0", x="0", y="0", simplify=True):
    tmat, m_string = M_string(s, theta, x, y, simplify=simplify)  # get affine matrix.
    shape = copy.deepcopy(shape)
    shape.strokes = _tform_once(shape.strokes, tmat)
    shape.base_program = f"(T {shape.base_program} {m_string})"

    # Generate an unconstant folded one also.
    tmat, m_string = M_string(s, theta, x, y, simplify=False)
    shape.unsimplified_program = f"(T {shape.unsimplified_program} {m_string})"
    return shape


def rotation_shape(
    shape,
    prefix,
    n,
    displacement="0.5",
    decorator_start_angle="(/ pi 4)",
    simplify=True,
):

    rotated_strokes, base_program = rotation_string(
        p=shape.strokes,
        p_string=shape.base_program,
        n=n,
        displacement=displacement,
        decorator_start_angle=decorator_start_angle,
        simplify=simplify,
    )

    _, unsimplified_program = rotation_string(
        p=shape.strokes,
        p_string=shape.unsimplified_program,
        n=n,
        displacement=displacement,
        decorator_start_angle=decorator_start_angle,
        simplify=simplify,
    )
    shape = copy.deepcopy(shape)
    shape.strokes = rotated_strokes
    shape.base_program = base_program
    shape.unsimplified_program = unsimplified_program
    shape._replace_article(prefix, n)
    return shape


def polygon_shape(n, simplify=True):
    stroke, program = polygon_string(n, simplify)
    s, unsimplified_program = polygon_string(n, simplify=False)
    shape = Shape.init_with_language(
        stroke,
        program,
        unsimplified_program,
        nouns=[LANG_GON_NAMES[n]],
        adjectives=[LANG_TINY],
        article=[LANG_A],
    )
    return shape

