"""
test_s12_s13_tasks_generator.py | Author: Catherine Wong
"""
import os
import numpy as np
from tasksgenerator.tasks_generator import TasksGeneratorRegistry
import tasksgenerator.s12_s13_tasks_generator as to_test
import primitives.object_primitives as object_primitives

TOTAL_TEST_STIMULI = 13


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


def test_s12_s13_tasks_generator_generate_test_tasks(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S12S13TestTasksGenerator.name]
    test_tasks = generator._generate_test_tasks()
    assert len(test_tasks) == TOTAL_TEST_STIMULI

    _test_save_tasks(test_tasks, export_dir=tmpdir)


def test_s13_generate_horizontal_object_primitives(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S13StochasticTasksGenerator.name]

    (
        line_objects,
        line_circle_objects,
        circle_line_circle_objects,
        shorter_objects,
    ) = generator._generate_horizontal_object_primitives()

    all_objects = (
        line_objects
        + line_circle_objects
        + circle_line_circle_objects
        + shorter_objects
    )

    assert len(all_objects) == 53
    _test_render_save_programs(
        stroke_arrays=all_objects, export_dir=tmpdir, no_blanks=False
    )


def test_s13_generate_strokes_for_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S13StochasticTasksGenerator.name]
    total_stimuli = 20
    strokes_for_stimuli = generator._generate_strokes_for_stimuli(total_stimuli)
    assert len(strokes_for_stimuli) == total_stimuli

    _test_render_save_programs(
        stroke_arrays=strokes_for_stimuli, export_dir=tmpdir, no_blanks=True
    )


def test_s13_tasks_generator_generate_tasks(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S13StochasticTasksGenerator.name]

    num_to_generate = 10
    tasks = generator._generate_tasks(num_to_generate)
    assert len(tasks) == num_to_generate

    _test_save_tasks(tasks, export_dir=tmpdir)


def test_s12_generate_vertical_object_primitives(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S12StochasticTasksGenerator.name]
    skewer_generator_fns = generator._generate_vertical_object_primitives()

    strokes_to_render = []
    for idx, generator_fn in enumerate(skewer_generator_fns):
        strokes = generator_fn()
        n_objects = idx + 1  # There are 1, 2, 3 objects that go on the skewer
        assert len(strokes) == n_objects
        strokes_to_render.append(strokes)

    _test_render_save_programs(
        stroke_arrays=strokes_to_render, export_dir=tmpdir, no_blanks=False
    )


def test_s12_generate_test_strokes_for_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S12StochasticTasksGenerator.name]
    strokes_to_render = generator._generate_strokes_for_stimuli(min_stimuli_per_class=3)
    _test_render_save_programs(
        stroke_arrays=strokes_to_render, export_dir=tmpdir, no_blanks=False
    )


def test_s12_generate_tasks(tmpdir):
    generator = TasksGeneratorRegistry[to_test.S12StochasticTasksGenerator.name]

    num_to_generate = 20
    tasks = generator._generate_tasks(num_to_generate)
    assert len(tasks) == num_to_generate

    _test_save_tasks(tasks, export_dir=tmpdir)
