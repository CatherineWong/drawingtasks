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
from dreamcoder.program import Program, Primitive, tint
from dreamcoder.type import baseType, arrow, tmaybe, t0, t1, t2

from primitives.object_primitives import (
    tstroke,
    ttransmat,
    _makeAffine,
    _tform_once,
    some_none,
    _repeat,
    _connect,
    transform
)

tfloat = baseType("tfloat")


## Mathematical operations.
SCALES = np.arange(0.5, 10, 0.25)  # Scaling constants
DISTS = np.arange(-3.0, 3.25, 0.25)  # Distances
INTEGERS = range(0, 13)  # General scaling constants
numeric_constants = set(list(SCALES) + list(DISTS) + list(INTEGERS))
constants = [Primitive(f"{n:g}", tfloat, n) for n in numeric_constants]
constants += [Primitive("pi", tfloat, math.pi)]


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


math_operations = [
    Primitive("-", arrow(tfloat, tfloat, tfloat), _subtraction),
    Primitive("+", arrow(tfloat, tfloat, tfloat), _addition),
    Primitive("*", arrow(tfloat, tfloat, tfloat), _multiplication),
    Primitive("/", arrow(tfloat, tfloat, tfloat), _division),
    Primitive("^", arrow(tfloat, tfloat, tfloat), _pow),
    Primitive("sin", arrow(tfloat, tfloat), math.sin),
    Primitive("cos", arrow(tfloat, tfloat), math.cos),
    Primitive("tan", arrow(tfloat, tfloat), math.tan),
    Primitive("max", arrow(tfloat, tfloat, tfloat), max),
    Primitive("min", arrow(tfloat, tfloat, tfloat), min),
]

### Basic transform.
# We use a weaker typing than the original in object_primitives.


def _makeAffineSimple(s=1.0, theta=0.0, x=0.0, y=0.0):
    return _makeAffine(s, theta, x, y)


transformations = [
    Primitive(
        "M",  # Makes a transformation matrix
        arrow(
            tmaybe(tfloat),  # Scale
            tmaybe(tfloat),  # Angle
            tmaybe(tfloat),  # Translation X
            tmaybe(tfloat),  # Translation Y
            ttransmat,
        ),
        Curried(_makeAffineSimple),
    ),
    Primitive(
        "T", arrow(tstroke, ttransmat, tstroke), Curried(_tform_once)
    ),  # Transform: applies a transformation to a stroke array
    Primitive(
        "C", arrow(tstroke, tstroke, tstroke), Curried(_connect)
    ),  # Connects two strokes into a single new primitive
    Primitive(
        "repeat", arrow(tstroke, tfloat, ttransmat, tstroke), Curried(_repeat)
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

def _scaled_rectangle(w) : return lambda h: __scaled_rectangle(w, h)

_emptystroke = []
objects = [
    Primitive("[]", tstroke, _emptystroke),
    Primitive("l", tstroke, _line),
    Primitive("c", tstroke, _circle),
    Primitive("r", tstroke, _rectangle),
    Primitive("r_s", arrow(tfloat, tfloat, tstroke), _scaled_rectangle)
]

## Higher order utility functions for generating program strings simultaneously with stroke primitives.


def peval(program_string):
    p = Program.parse(program_string)
    output = p.evaluate([])
    return output


def M_string(s="1", theta="0", x="0", y="0"):
    affine_matrix = _makeAffineSimple(peval(s), peval(theta), peval(x), peval(y))
    m_string = f"(M {s} {theta} {x} {y})"
    return affine_matrix, m_string


def T_string(p, p_string, s="1", theta="0", x="0", y="0"):
    """Transform Python utility wrapper that applies an affine transformation matrix directly to a primitive, while also generating a string that can be applied to a downstream stroke. Python-usable API that mirrors the functional semantics"""
    tmat, m_string = M_string(
        s,
        theta,
        x,
        y,
    )  # get affine matrix.
    p = _tform_once(p, tmat)
    t_string = f"(T {p_string} {m_string})"
    return p, t_string

def scaled_rectangle_string(w, h):
    scaled_rectangle_string = f"(r_s {w} {h})"
    return peval(scaled_rectangle_string), scaled_rectangle_string

def polygon_string(n):
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
    p, p_string, n, displacement="0.5", decorator_start_angle="(/ pi 4)"
):
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
short_l_string = T_string(l_string[0], l_string[-1], x="(- 0 0.5)")
