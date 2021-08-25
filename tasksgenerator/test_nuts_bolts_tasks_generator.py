"""
test_nuts_bolts_tasks_generator.py | Author : Catherine Wong
"""
import os
import numpy as np
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
import primitives.object_primitives as object_primitives
import tasksgenerator.nuts_bolts_tasks_generator as to_test

DESKTOP = "/Users/catwong/Desktop/nuts_bolts"  # Internal for testing purposes.


def _test_render_save_programs(stroke_arrays, export_dir, no_blanks=True):
    for program_id, s in enumerate(stroke_arrays):
        # Can it render the program?

        canvas_size = object_primitives.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT
        rendered = object_primitives.render_stroke_arrays_to_canvas(
            s,
            stroke_width_height=3 * object_primitives.XYLIM,
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


# def test_nutsbolts_tasks_generator_generate_simple_nuts_stimuli(tmpdir):
#     generator = TasksGeneratorRegistry[to_test.NutsBoltsTasksGenerator.name]
#     all_objects = generator._generate_simple_nuts_stimuli()
#     _test_render_save_programs(
#         stroke_arrays=all_objects, export_dir=DESKTOP, no_blanks=False
#     )


# def test_nutsbolts_tasks_generator_generate_perforated_nuts_stimuli(tmpdir):
#     generator = TasksGeneratorRegistry[to_test.NutsBoltsTasksGenerator.name]
#     all_objects = generator._generate_perforated_nuts_stimuli()
#     _test_render_save_programs(
#         stroke_arrays=all_objects, export_dir=DESKTOP, no_blanks=False
#     )


def test_nutsbolts_tasks_generator_generate_strokes_for_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.NutsBoltsTasksGenerator.name]
    all_objects = generator._generate_strokes_for_stimuli()
    _test_render_save_programs(
        stroke_arrays=all_objects, export_dir=DESKTOP, no_blanks=False
    )
