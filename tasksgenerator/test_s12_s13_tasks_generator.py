"""
test_s12_s13_tasks_generator.py | Author: Catherine Wong
"""
import os
import numpy as np
from tasksgenerator.tasks_generator import TasksGeneratorRegistry
import tasksgenerator.s12_s13_tasks_generator as to_test
import primitives.object_primitives as object_primitives

DESKTOP = "/Users/catwong/Desktop"  # Debugging only
TOTAL_TEST_STIMULI = 13


def _test_render_save_programs(stroke_arrays, export_dir):
    for program_id, s in enumerate(stroke_arrays):
        # Can it render the program?
        rendered = object_primitives.render_stroke_arrays_to_canvas(s)
        assert rendered.shape == (
            object_primitives.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT,
            object_primitives.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT,
        )
        assert np.sum(rendered) > 0
        # Can it save the program?
        saved_file = object_primitives.export_rendered_program(
            rendered, program_id, export_dir=export_dir
        )
        assert os.path.exists(saved_file)


def _test_save_tasks(tasks, export_dir):
    for program_id, task in enumerate(tasks):
        saved_file = object_primitives.export_rendered_program(
            task.rendering, task.name, export_dir=export_dir
        )
        assert os.path.exists(saved_file)


def test_graphics_primitives(tmpdir):
    primitives = [
        to_test.long_vline,
        to_test.make_vertical_grating(n=4),
        to_test.make_grating_with_objects(objects=[object_primitives._circle]),
    ]
    _test_render_save_programs(stroke_arrays=primitives, export_dir=tmpdir)


def test_s12_s13_tasks_generator_generate_test_strokes_for_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S12S13TestTasksGenerator.name]
    test_strokes = generator._generate_test_strokes_for_stimuli()
    assert len(test_strokes) == TOTAL_TEST_STIMULI
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=tmpdir)


def test_s12_s13_tasks_generator_generate_test_strokes_for_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S12S13TestTasksGenerator.name]
    test_tasks = generator._generate_test_tasks()
    assert len(test_tasks) == TOTAL_TEST_STIMULI

    _test_save_tasks(test_tasks, export_dir=DESKTOP)
