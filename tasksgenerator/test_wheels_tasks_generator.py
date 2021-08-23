"""
test_wheels_tasks_generator.py | Author : Catherine Wong.
"""
import os
import numpy as np
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
import primitives.object_primitives as object_primitives
import tasksgenerator.wheels_tasks_generator as to_test

import tasksgenerator.bases_parts_tasks_generator as bases_parts_tasks_generator
import tasksgenerator.dial_tasks_generator as dial_tasks_generator
import tasksgenerator.antenna_tasks_generator as antenna_tasks_generator

DESKTOP = "/Users/catwong/Desktop/wheels"  # Internal for testing purposes.

SMALL, MEDIUM, LARGE = (
    bases_parts_tasks_generator.SMALL,
    bases_parts_tasks_generator.MEDIUM,
    bases_parts_tasks_generator.LARGE,
)


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


def test_wheeled_vehicles_tasks_generator_generate_truck_bases():
    test_strokes = []
    generator = TasksGeneratorRegistry[to_test.WheeledVehiclesTasksGenerator.name]

    for head_width in [SMALL]:
        for head_height in [SMALL]:
            for body_width in [LARGE * scale for scale in range(3, 7)]:
                for body_height in [MEDIUM]:
                    for nose_scale in [0.5, 0.25]:
                        (
                            strokes,
                            min_x,
                            max_x,
                            min_y,
                            max_y,
                        ) = generator._generate_truck_bases(
                            head_width=head_width,
                            head_height=head_height,
                            body_width=body_width,
                            body_height=body_height,
                            nose_scale=nose_scale,
                        )
                        test_strokes += strokes

        _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
