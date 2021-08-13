"""
test_s16_s17_tasks_generator.py | Author : Catherine Wong.
"""
import os
import numpy as np
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
import tasksgenerator.s16_s17_tasks_generator as to_test
import primitives.object_primitives as object_primitives

DESKTOP = "/Users/catwong/Desktop/test"  # Internal for testing purposes.


def _test_render_save_programs(stroke_arrays, export_dir, no_blanks=True):
    for program_id, s in enumerate(stroke_arrays):
        # Can it render the program?
        rendered = object_primitives.render_stroke_arrays_to_canvas(s)
        assert rendered.shape == (
            object_primitives.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT,
            object_primitives.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT,
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


def test_s16_generate_vertical_object_primitives(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S16TasksGenerator.name]
    all_objects = generator._generate_vertical_object_primitives()

    _test_render_save_programs(
        stroke_arrays=all_objects,
        export_dir=tmpdir,
        no_blanks=False,
    )


def test_s16_generate_strokes_for_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S16TasksGenerator.name]
    all_objects = generator._generate_strokes_for_stimuli()
    _test_render_save_programs(
        stroke_arrays=all_objects, export_dir=tmpdir, no_blanks=False
    )


def test_s17_generate_horizontal_object_primitives(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S17TasksGenerator.name]
    all_objects = generator._generate_horizontal_object_primitives()
    _test_render_save_programs(
        stroke_arrays=all_objects, export_dir=tmpdir, no_blanks=False
    )


def test_s17_generate_strokes_for_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S17TasksGenerator.name]
    all_objects = generator._generate_strokes_for_stimuli()
    _test_render_save_programs(
        stroke_arrays=all_objects, export_dir=DESKTOP, no_blanks=False
    )
