"""test_gadgets_primitives.py | Author : Catherine Wong"""

import os
import math
import numpy as np
from numpy.testing._private.utils import assert_almost_equal
from dreamcoder.program import DEFAULT_NAME, VERBOSITY_0, VERBOSITY_1, Program
import primitives.gadgets_primitives as to_test
from primitives.test_object_primitives import (
    _test_parse_render_save_programs,
    _test_render_save_programs,
    _test_parse_render_save_shape_programs,
)
from tasksgenerator.bases_parts_tasks_generator import *
from tasksgenerator.dial_tasks_generator import DIAL_SMALL

DESKTOP = "/Users/catwong/Desktop/test"  # Internal for testing purposes.


def assert_evaluation_same(program_string, ground_truth):
    EPSILON = 0.01
    p = Program.parse(program_string)
    e = p.evaluate([])
    if type(e) == float:
        assert np.abs(e - ground_truth) < EPSILON


def test_mathematical_constants():
    for p in to_test.constants:
        print(p)
        if str(p) != "pi":
            assert (
                type(float(str(p))) == float
            )  # Test that we can convert directly to float.
    assert_evaluation_same("(+ 1.0 1.25)", 2.25)
    assert_evaluation_same("(/ 2.0 0.5)", 4.0)
    assert_evaluation_same("(* 3.0 0.5)", 1.5)
    assert_evaluation_same("(sin (* 2 pi))", 0.0)
    assert_evaluation_same("(cos pi)", -1.0)
    assert_evaluation_same("(tan pi)", 0.0)


def test_T_string_only():
    p, p_string = to_test._line, "l"

    n = 1
    y = f"(/ 0.5 (tan (/ pi {n})))"
    p, base_line_string = to_test.T_string(p, p_string, x="-0.5", y=y)
    _test_parse_render_save_programs(program_strings=[base_line_string], tmpdir=DESKTOP)


def test_T_shape():
    shape = to_test.l_shape
    n = 1
    y = f"(/ 0.5 (tan (/ pi {n})))"
    shape = to_test.T_shape(shape, x="-0.5", y=y)
    _test_parse_render_save_shape_programs([shape], tmpdir=DESKTOP)


def test_T_string_human_readable():
    p, p_string = to_test._line, "l"

    n = 1
    y = f"(/ 0.5 (tan (/ pi {n})))"
    for simplify in True, False:
        p, base_line_string = to_test.T_string(
            p, p_string, x="-0.5", y=y, simplify=simplify
        )
        for verbosity_level in [DEFAULT_NAME, VERBOSITY_0, VERBOSITY_1]:
            program_string = Program.parse(base_line_string).show(
                isFunction=False, alternate_names=verbosity_level
            )
            print(program_string)


def test_T_string_to_polygon():
    n = 3
    y = f"(/ 0.5 (tan (/ pi {n})))"
    true_y = 0.5 / math.tan(math.pi / n)

    theta = f"(/ (* 2 pi) {n})"

    # Base line that forms the side.
    p, base_line = to_test.T_string(to_test._line, "l", x="-0.5", y=y)
    strokes = to_test._repeat(p, n, to_test._makeAffineSimple(theta=2 * math.pi / n))
    _test_render_save_programs(stroke_arrays=[strokes], export_dir=DESKTOP)


def test_generate_dsl_primitives():
    test_strings = [
        p_string
        for (p, p_string) in [to_test.c_string, to_test.l_string, to_test.r_string]
    ]
    _test_parse_render_save_programs(program_strings=test_strings, tmpdir=DESKTOP)


def test_shape_dsl_primitives():
    shapes = [to_test.c_shape, to_test.r_shape, to_test.l_shape]
    for shape in shapes:
        print(shape.base_program)
        shape._connect_language()
        shape._print_language()
    _test_parse_render_save_shape_programs(shapes, tmpdir=DESKTOP)


def test_polygon():
    test_programs = []

    for n_sides in range(3, 7):
        test_programs.append(to_test.polygon_string(n_sides)[-1])
    _test_parse_render_save_programs(program_strings=test_programs, tmpdir=DESKTOP)


def test_polygon_shape():
    shapes = [to_test.polygon_shape(n) for n in range(3, 7)]
    for shape in shapes:
        print(shape.base_program)
        shape._connect_language()
        shape._print_language()
        if shape.unsimplified_program is not None:
            print(shape.unsimplified_program)
    _test_parse_render_save_shape_programs(shapes, tmpdir=DESKTOP)


def test_scaled_rectangle_strings():
    test_programs = []
    for (w, h) in [(1, 1), (1, 2), (2, 1), (2, 3)]:
        test_programs.append(to_test.scaled_rectangle_string(w, h)[-1])
    _test_parse_render_save_programs(program_strings=test_programs, tmpdir=DESKTOP)


def test_scaled_rectangle_strokes():
    test_strokes = []
    for (w, h) in [(1, 1), (1, 2), (2, 1), (2, 3)]:
        test_strokes.append(to_test.scaled_rectangle_string(w, h)[0])
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)


def test_nested_scaling_string():
    test_programs = []
    for n in range(1, 3):
        _, shape_string = to_test.c_string
        scale_factor = f"(+ {SMALL} {SCALE_UNIT})"
        test_programs.append(
            to_test.nested_scaling_string(shape_string, n, scale_factor=scale_factor)[
                -1
            ]
        )
    _test_parse_render_save_programs(program_strings=test_programs, tmpdir=DESKTOP)


def test_object_constants():
    test_programs = []
    for strokes, stroke_string in [
        to_test.c_string,
        to_test.cc_string,
        to_test.hexagon_string,
        to_test.octagon_string,
    ]:
        test_programs += [stroke_string]
    _test_parse_render_save_programs(program_strings=test_programs, tmpdir=DESKTOP)


def test_rotate_axis():
    test_programs = []
    for strokes, stroke_string in [
        to_test.c_string,
        to_test.hexagon_string,
        to_test.octagon_string,
    ]:
        for n_sides in range(3, 7):
            rotated, rotation_string = to_test.rotation_string(
                strokes, stroke_string, n_sides, displacement="1"
            )
            test_programs += [rotation_string]
    _test_parse_render_save_programs(program_strings=test_programs, tmpdir=DESKTOP)
