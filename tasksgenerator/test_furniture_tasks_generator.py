"""
test_furniture_tasks_generator.py | Author: Yoni Friedman and Catherine Wong.
"""
import os
import numpy as np
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
import primitives.object_primitives as object_primitives
import tasksgenerator.furniture_tasks_generator as to_test

import tasksgenerator.bases_parts_tasks_generator as bases_parts_tasks_generator

DESKTOP = "/Users/catwong/Desktop/furniture"  # Internal for testing purposes.

SMALL, MEDIUM, LARGE, THREE_QUARTER_SCALE = (
    bases_parts_tasks_generator.SMALL,
    bases_parts_tasks_generator.MEDIUM,
    bases_parts_tasks_generator.LARGE,
    bases_parts_tasks_generator.THREE_QUARTER_SCALE,
)


def _test_render_save_programs(stroke_arrays, export_dir, no_blanks=True):
    for program_id, s in enumerate(stroke_arrays):
        # Can it render the program?

        canvas_size = object_primitives.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT
        rendered = object_primitives.render_stroke_arrays_to_canvas(
            s,
            stroke_width_height=8 * object_primitives.XYLIM,
            canvas_width_height=canvas_size,
        )
        assert not no_blanks or np.sum(rendered) > 0
        # Can it save the program?
        saved_file = object_primitives.export_rendered_program(
            rendered, program_id, export_dir=export_dir
        )
        print(f"Saving to id {program_id}")
        assert os.path.exists(saved_file)


def _test_save_tasks(tasks, export_dir):
    for program_id, task in enumerate(tasks):
        saved_file = object_primitives.export_rendered_program(
            task.rendering, task.name, export_dir=export_dir
        )
        assert os.path.exists(saved_file)


def test_furniture_tasks_generator_generate_drawer_pulls_iterator():
    generator = TasksGeneratorRegistry[to_test.FurnitureTasksGenerator.name]
    test_strokes = []
    for n_drawer_pulls in [2, 3]:
        for (
            strokes,
            min_x,
            max_x,
            min_y,
            max_y,
        ) in generator._generate_drawer_pulls_iterator(
            min_x=-5, max_x=5, n_drawer_pulls=n_drawer_pulls
        ):
            test_strokes += strokes
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)


def test_furniture_tasks_generator_generate_drawers_iterator():
    generator = TasksGeneratorRegistry[to_test.FurnitureTasksGenerator.name]
    test_strokes = []
    for strokes in generator._generate_drawers_iterator(total_n_drawers=1):
        test_strokes += strokes
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
