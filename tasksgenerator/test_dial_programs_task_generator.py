"""
test_dial_programs_tasks_generator.py | Author: Catherine Wong
"""
import os
import numpy as np
from tasksgenerator.bases_parts_tasks_generator import LARGE, SMALL, STR_RIGHT, STR_VERTICAL, STR_ZERO
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
from primitives.gadgets_primitives import *
from primitives.test_object_primitives import (
    _test_parse_render_save_programs,
    _test_render_save_programs
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
                    strokes, stroke_strings, _, _ = generator._generate_bases_string(base_columns=base_columns, max_rows=max_rows, n_tiers=n_tiers, base_end_filials=base_end_filials)
                    test_strokes += [strokes]
                    test_stroke_strings.append(stroke_strings)
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
    _test_parse_render_save_programs(program_strings=test_stroke_strings,tmpdir=DESKTOP)

def test_generate_nested_circle_dials_string():
    test_strokes, test_stroke_strings = [], []

    # No specification.
    for dial_size in [str(SMALL), str(LARGE)]:
        for dial_angle in [STR_VERTICAL, STR_RIGHT]:
            for shape_specification in [
                None, 
                [c_string, r_string],
                [c_string, c_string]
            ]:
                if (
                    dial_size == str(LARGE)
                    and dial_angle == STR_VERTICAL
                ):
                    continue
                strokes, stroke_strings = generator._generate_nested_circle_dials_string(
                    dial_size=dial_size,
                    dial_angle=dial_angle,
                    shape_specification=shape_specification
                )
                test_strokes += strokes
                test_stroke_strings.append(stroke_strings)
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
    _test_parse_render_save_programs(program_strings=test_stroke_strings,tmpdir=DESKTOP)




    # With specification.