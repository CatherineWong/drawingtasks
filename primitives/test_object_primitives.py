"""test_object_primitives.py | Author : Catherine Wong"""

import os
import math
import numpy as np
from dreamcoder.program import Program
import primitives.object_primitives as to_test

SIMPLE_OBJECT_PROGRAMS = ["(line)", "(circle)", "(rectangle)"]


def _test_parse_render_save_programs(program_strings, tmpdir):
    export_dir = tmpdir
    for program_id, program_string in enumerate(program_strings):
        try:
            # Can it parse the program?
            p = Program.parse(program_string)
            # Can it render the program?
            rendered = to_test.render_parsed_program(p)
            assert rendered.shape == (
                to_test.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT,
                to_test.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT,
            )
            assert np.sum(rendered) > 0
            # Can it save the program?
            saved_file = to_test.export_rendered_program(
                rendered, program_id, export_dir=export_dir
            )
            assert os.path.exists(saved_file)
        except:
            print(f"Failed to evaluate: {program_string}")
            assert False


def test_parse_render_save_simple_objects(tmpdir):
    _test_parse_render_save_programs(SIMPLE_OBJECT_PROGRAMS, tmpdir)


def assert_equal_program_array(program_string, ground_truth):
    p = Program.parse(program_string)
    output = p.evaluate([])
    if type(output) == type([]):
        all(np.array_equal(i, j) for i, j in zip(output, ground_truth))
    else:
        assert np.array_equal(ground_truth, output)


def _get_test_scale():
    test_scale_value = to_test.SCALES[2]
    ground_truth_scale = np.array(
        [[test_scale_value, 0.0, 0.0], [0.0, test_scale_value, 0.0], [0.0, 0.0, 1.0]]
    )
    program = "(transmat (Some scale2) None None None None)"
    return ground_truth_scale, test_scale_value, program


def _get_test_rotation():
    test_theta_value = to_test.THETAS[2]
    ground_truth_rotation = np.array(
        [
            [math.cos(test_theta_value), -math.sin(test_theta_value), 0.0],
            [math.sin(test_theta_value), math.cos(test_theta_value), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    program = "(transmat None (Some angle2) None None None)"
    return ground_truth_rotation, test_theta_value, program


def _get_test_translation():
    test_translation_value = to_test.DISTS[2]
    ground_truth_translation = np.array(
        [
            [1.0, 0.0, test_translation_value],
            [0.0, 1.0, test_translation_value],
            [0.0, 0.0, 1.0],
        ]
    )
    program = "(transmat None None (Some dist2) (Some dist2) None)"
    return ground_truth_translation, test_translation_value, program


def test_make_affine_and_transmat_primitive():
    # Test scaling.
    ground_truth_scale, test_scale_value, program = _get_test_scale()
    assert np.array_equal(
        ground_truth_scale,
        to_test._makeAffine(s=test_scale_value, theta=None, x=None, y=None),
    )
    assert_equal_program_array(program, ground_truth_scale)

    # Test rotation.
    ground_truth_rotation, test_theta_value, program = _get_test_rotation()
    assert np.array_equal(
        ground_truth_rotation,
        to_test._makeAffine(s=None, theta=test_theta_value, x=None, y=None),
    )
    assert_equal_program_array(program, ground_truth_rotation)

    # Test translation.
    ground_truth_translation, test_translation_value, program = _get_test_translation()

    assert np.array_equal(
        ground_truth_translation,
        to_test._makeAffine(
            s=None, theta=None, x=test_translation_value, y=test_translation_value
        ),
    )

    assert_equal_program_array(program, ground_truth_translation)

    # Test ordering.
    test_order = "srt"
    ground_truth = ground_truth_scale @ ground_truth_rotation @ ground_truth_translation
    assert np.array_equal(
        ground_truth,
        to_test._makeAffine(
            s=test_scale_value,
            theta=test_theta_value,
            x=test_translation_value,
            y=test_translation_value,
            order=test_order,
        ),
    )
    program = (
        "(transmat (Some scale2) (Some angle2) (Some dist2) (Some dist2) (Some srt))"
    )
    assert_equal_program_array(program, ground_truth)


def test_tform_once_and_transform():
    ground_truth_scale, test_scale_value, transformation = _get_test_scale()
    transformation_program = f"(transform circle {transformation})"
    p = to_test._circle
    assert_equal_program_array(
        transformation_program, to_test.transform(p, s=test_scale_value)
    )

    ground_truth_rotation, test_theta_value, transformation = _get_test_rotation()
    transformation_program = f"(transform circle {transformation})"
    assert_equal_program_array(
        transformation_program, to_test.transform(p, theta=test_theta_value)
    )

    (
        ground_truth_translation,
        test_translation_value,
        transformation,
    ) = _get_test_translation()
    transformation_program = f"(transform circle {transformation})"
    assert_equal_program_array(
        transformation_program,
        to_test.transform(p, x=test_translation_value, y=test_translation_value),
    )


def test_reflect():
    ground_truth_reflection = [np.array([(-1.0, 0.0), (0.0, 0.0)])]
    transformation_program = "(reflect line angle2)"
    assert_equal_program_array(transformation_program, ground_truth_reflection)


def test_repeat():
    (
        ground_truth_translation,
        test_translation_value,
        translation_program,
    ) = _get_test_translation()
    transformation_program = f"(repeat line rep2 {translation_program})"
    p = Program.parse(transformation_program)
    # Can it render the program?
    rendered = to_test.render_parsed_program(p)
    assert np.sum(rendered) > 0


def test_connect():
    p1 = to_test._circle
    p2 = to_test._line
    transformation_program = "(connect circle line)"

    assert_equal_program_array(transformation_program, p1 + p2)


def _test_render_save_programs(stroke_arrays, export_dir, no_blanks=True):
    for program_id, s in enumerate(stroke_arrays):
        # Can it render the program?

        canvas_size = to_test.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT
        rendered = to_test.render_stroke_arrays_to_canvas(
            s,
            stroke_width_height=4 * to_test.XYLIM,
            canvas_width_height=canvas_size,
        )
        assert not no_blanks or np.sum(rendered) > 0
        # Can it save the program?
        saved_file = to_test.export_rendered_program(
            rendered, program_id, export_dir=export_dir
        )
        print(f"Saving to id {program_id}")
        assert os.path.exists(saved_file)


DESKTOP = "/Users/catwong/Desktop/test"  # Internal for testing purposes.


def test_polygon():
    test_strokes = []

    for n_sides in range(3, 7):
        test_strokes.append(to_test.polygon(n_sides))
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)


def test_rectangle():
    test_strokes = []

    for width in to_test.SCALES:
        for height in to_test.SCALES:
            test_strokes.append(to_test.rectangle(width=width, height=height))
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
