"""
test_furniture_programs_tasks_generator.py | Author : Catherine Wong.
"""
import os
import numpy as np
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)

from tasksgenerator.bases_parts_tasks_generator import *

from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
from primitives.gadgets_primitives import *
from primitives.test_object_primitives import (
    _test_parse_render_save_programs,
    _test_render_save_programs,
)
import tasksgenerator.furniture_programs_tasks_generator as to_test

DESKTOP = f"/Users/catherinewong/Desktop/zyzzyva/research/language-abstractions/drawing_tasks_stimuli/{to_test.FurnitureProgramsTasksGenerator.name}"  # Internal for testing purposes.


generator = TasksGeneratorRegistry[to_test.FurnitureProgramsTasksGenerator.name]


def test_furniture_tasks_generator_generate_drawers_iterator():
    test_strokes, test_stroke_strings = [], []
    for n_drawers in [2, 4]:
        for float_location in [FLOAT_CENTER, FLOAT_TOP, FLOAT_BOTTOM]:
            for (
                drawer_strokes,
                drawer_stroke_strings,
                enclosure_min_x,
                enclosure_max_x,
                enclosure_min_y,
                enclosure_max_y,
            ) in generator._generate_drawers_strings_iterator(
                n_drawers=n_drawers, stack_float_locations=float_location
            ):
                test_strokes += drawer_strokes
                test_stroke_strings.append(drawer_stroke_strings)
    # _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
    _test_parse_render_save_programs(
        program_strings=test_stroke_strings, tmpdir=DESKTOP
    )
