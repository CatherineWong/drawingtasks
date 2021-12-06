"""test_gadgets_primitives.py | Author : Catherine Wong"""

import os
import math
import numpy as np
from numpy.testing._private.utils import assert_almost_equal
from dreamcoder.program import Program
import primitives.gadgets_primitives as to_test
from primitives.test_object_primitives import (
    _test_parse_render_save_programs,
    _test_render_save_programs,
)

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


def test_T_string():
    p, p_string = to_test._line, "l"

    n = 1
    y = f"(/ 0.5 (tan (/ pi {n})))"
    p, base_line_string = to_test.T_string(p, p_string, x="-0.5", y=y)
    _test_parse_render_save_programs(program_strings=[base_line_string], tmpdir=DESKTOP)


def test_T_string_to_polygon():
    n = 3
    y = f"(/ 0.5 (tan (/ pi {n})))"
    true_y = 0.5 / math.tan(math.pi / n)

    theta = f"(/ (* 2 pi) {n})"

    # Base line that forms the side.
    p, base_line = to_test.T_string(to_test._line, "l", x="-0.5", y=y)
    strokes = to_test._repeat(p, n, to_test._makeAffineSimple(theta=2 * math.pi / n))
    _test_render_save_programs(stroke_arrays=[strokes], export_dir=DESKTOP)


def test_polygon():
    test_programs = []

    for n_sides in range(3, 7):
        test_programs.append(to_test.polygon_string(n_sides))
    _test_parse_render_save_programs(program_strings=test_programs, tmpdir=DESKTOP)
