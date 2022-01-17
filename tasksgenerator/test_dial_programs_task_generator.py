"""
test_dial_programs_tasks_generator.py | Author: Catherine Wong
"""
import os
import numpy as np
from tasksgenerator.bases_parts_tasks_generator import (
    LARGE,
    SMALL,
    STR_RIGHT,
    STR_VERTICAL,
    STR_ZERO,
)
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
from primitives.gadgets_primitives import *
from primitives.test_object_primitives import (
    _test_parse_render_save_programs,
    _test_render_save_programs,
)
import tasksgenerator.dial_programs_task_generator as to_test

DESKTOP = f"/Users/catherinewong/Desktop/zyzzyva/research/language-abstractions/drawing_tasks_stimuli/{to_test.DialProgramsTasksGenerator.name}"  # Internal for testing purposes.


generator = TasksGeneratorRegistry[to_test.DialProgramsTasksGenerator.name]

#  TODO: copy tests from the original dial programs.
def test_generate_bases_strings():
    test_strokes = []
    test_stroke_strings = []
    for base_columns in ["1", "2", "3"]:
        for max_rows in ["1", "2"]:
            for n_tiers in ["1", "2"]:
                for base_end_filials in [False, True]:
                    (
                        strokes,
                        stroke_strings,
                        _,
                        _,
                        synthetic_dict,
                    ) = generator._generate_bases_string(
                        base_columns=base_columns,
                        max_rows=max_rows,
                        n_tiers=n_tiers,
                        base_end_filials=base_end_filials,
                    )
                    test_strokes += [strokes]
                    test_stroke_strings.append(stroke_strings)

    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
    _test_parse_render_save_programs(
        program_strings=test_stroke_strings, tmpdir=DESKTOP
    )


def test_add_antenna_to_stimuli():
    test_strokes = []
    test_stroke_strings = []
    test_stroke_dicts = []
    for base_columns in ["1", "2", "3"]:
        for max_rows in ["1", "2"]:
            for n_tiers in ["1", "2"]:
                for base_end_filials in [False, True]:
                    (
                        strokes,
                        stroke_strings,
                        base_width,
                        base_height,
                        base_dict,
                    ) = generator._generate_bases_string(
                        base_columns=base_columns,
                        max_rows=max_rows,
                        n_tiers=n_tiers,
                        base_end_filials=base_end_filials,
                    )

                    antenna_stimuli = generator._add_antenna_to_stimuli(
                        strokes,
                        stroke_strings,
                        base_width,
                        base_height,
                        generation_probability=1.0,
                        antenna_generation_probability=1.0,
                        add_double_antenna=True,
                        add_side_antenna=True,
                        stimuli_synthetic_dict=base_dict,
                    )
                    if antenna_stimuli is not None:
                        strokes, stroke_strings, stroke_dicts = antenna_stimuli
                    test_strokes += strokes
                    test_stroke_strings += stroke_strings
                    test_stroke_dicts += stroke_dicts

    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
    _test_parse_render_save_programs(
        program_strings=test_stroke_strings, tmpdir=DESKTOP
    )


def test_generate_nested_circle_dials_string():
    test_strokes, test_stroke_strings = [], []

    # No specification.
    for dial_size in [str(SMALL), str(LARGE)]:
        for dial_angle in [STR_VERTICAL, STR_RIGHT]:
            for shape_specification in [
                None,
                [c_string, r_string],
                [c_string, c_string],
            ]:
                if dial_size == str(LARGE) and dial_angle == STR_VERTICAL:
                    continue
                (
                    strokes,
                    stroke_strings,
                    synthetic_dict,
                ) = generator._generate_nested_circle_dials_string(
                    dial_size=dial_size,
                    dial_angle=dial_angle,
                    shape_specification=shape_specification,
                )
                test_strokes += strokes
                test_stroke_strings.append(stroke_strings)

    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
    _test_parse_render_save_programs(
        program_strings=test_stroke_strings, tmpdir=DESKTOP
    )


def test_generate_row_of_dials():
    test_strokes, test_stroke_strings = [], []

    # No specification.
    for dial_size in [str(SMALL), str(LARGE)]:
        for dial_angle in [STR_VERTICAL, STR_RIGHT]:
            for shape_specification in [
                None,
                [c_string, r_string],
                [c_string, c_string],
            ]:
                if dial_size == str(LARGE) and dial_angle == STR_VERTICAL:
                    continue
                (
                    strokes,
                    stroke_strings,
                    dial_synthetic_dict,
                ) = generator._generate_nested_circle_dials_string(
                    dial_size=dial_size,
                    dial_angle=dial_angle,
                    shape_specification=shape_specification,
                )

                for n_dial_rows in ["1", "2"]:
                    for n_dials in ["1", "3"]:
                        (
                            strokes,
                            stroke_strings,
                            synthetic_dict,
                        ) = generator._generate_rows_of_dials(
                            n_dial_rows,
                            n_dials,
                            dial_shape=strokes,
                            dial_shape_string=stroke_strings,
                            dial_synthetic_dict=dial_synthetic_dict,
                        )
                        test_strokes += [strokes]
                        test_stroke_strings.append(stroke_strings)
                        import pdb

                        pdb.set_trace()
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
    _test_parse_render_save_programs(
        program_strings=test_stroke_strings, tmpdir=DESKTOP
    )


def test_generate_stacked_antenna_strings():
    test_strokes, test_stroke_strings = [], []
    for n_wires in ["1", "2", "3"]:
        for scale_wires in [True, False]:
            for end_shape in [None, c_string, r_string]:
                (
                    strokes,
                    stroke_strings,
                    _,
                ) = generator._generate_stacked_antenna_strings(
                    n_wires=n_wires, scale_wires=scale_wires, end_shape=end_shape
                )
                test_strokes += strokes
                test_stroke_strings.append(stroke_strings)
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
    _test_parse_render_save_programs(
        program_strings=test_stroke_strings, tmpdir=DESKTOP
    )


def test_generate_strokes_strings_for_stimuli():
    generator = TasksGeneratorRegistry[to_test.DialProgramsTasksGenerator.name]
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_strokes_strings_for_stimuli(train_ratio=0.8)
    for split, objects, test_stroke_strings in [
        ("train", train, train_strings),
        ("test", test, test_strings),
    ]:
        # _test_render_save_programs(
        #     stroke_arrays=objects, export_dir=DESKTOP, no_blanks=False, split=split
        # )
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP, split=split
        )


def test_generate_parts_strings_for_stimuli():
    generator = TasksGeneratorRegistry[to_test.DialProgramsTasksGenerator.name]
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_parts_strings_for_stimuli(train_ratio=1.0)
    for split, objects, test_stroke_strings in [
        ("train", train, train_strings),
        ("test", test, test_strings),
    ]:
        _test_render_save_programs(
            stroke_arrays=objects, export_dir=DESKTOP, no_blanks=False, split=split
        )
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP, split=split
        )
