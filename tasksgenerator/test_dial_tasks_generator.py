"""
test_dial_tasks_generator.py | Author : Catherine Wong.
"""

import os
import numpy as np
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
import tasksgenerator.dial_tasks_generator as to_test
import primitives.object_primitives as object_primitives

DESKTOP = "/Users/catwong/Desktop/test"  # Internal for testing purposes.


def _test_render_save_programs(stroke_arrays, export_dir, no_blanks=True):
    for program_id, s in enumerate(stroke_arrays):
        # Can it render the program?

        canvas_size = object_primitives.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT
        rendered = object_primitives.render_stroke_arrays_to_canvas(
            s,
            stroke_width_height=6 * object_primitives.XYLIM,
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


def test_dial_tasks_generator_generate_nested_circle_dials(tmpdir):
    test_strokes = []

    generator = TasksGeneratorRegistry[to_test.SimpleDialTasksGenerator.name]

    for n_circles in [1, 2, 3]:
        for dial_size in [to_test.DIAL_SMALL, to_test.DIAL_MEDIUM, to_test.DIAL_LARGE]:
            for dial_angle in [
                to_test.DIAL_VERTICAL,
                to_test.DIAL_RIGHT,
                to_test.DIAL_LEFT,
            ]:
                test_strokes += generator._generate_nested_circle_dials(
                    n_circles=n_circles, dial_size=dial_size, dial_angle=dial_angle
                )

    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=tmpdir)


def test_complex_dial_tasks_generator_generate_strokes_for_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.ComplexDialTasksGenerator.name]
    all_objects = generator._generate_strokes_for_stimuli()
    _test_render_save_programs(
        stroke_arrays=all_objects, export_dir=DESKTOP, no_blanks=False
    )
