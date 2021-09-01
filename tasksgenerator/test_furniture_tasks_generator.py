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

from tasksgenerator.bases_parts_tasks_generator import *

DESKTOP = "/Users/catwong/Desktop/zyzzyva/research/language-abstractions/drawing_tasks_stimuli/furniture"  # Internal for testing purposes.

SMALL, MEDIUM, LARGE, THREE_QUARTER_SCALE = (
    bases_parts_tasks_generator.SMALL,
    bases_parts_tasks_generator.MEDIUM,
    bases_parts_tasks_generator.LARGE,
    bases_parts_tasks_generator.THREE_QUARTER_SCALE,
)


def _test_render_save_programs(
    stroke_arrays, export_dir, no_blanks=True, split="train"
):
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
            rendered, f"{split}_{program_id}", export_dir=export_dir
        )
        print(f"Saving to id {program_id}")
        assert os.path.exists(saved_file)


def _test_save_tasks(tasks, export_dir):
    for program_id, task in enumerate(tasks):
        saved_file = object_primitives.export_rendered_program(
            task.rendering, task.name, export_dir=export_dir
        )
        assert os.path.exists(saved_file)


def test_furniture_tasks_generator_generate_drawers_iterator():
    generator = TasksGeneratorRegistry[to_test.FurnitureTasksGenerator.name]
    test_strokes = []
    for n_drawers in [1, 2]:
        for float_location in [FLOAT_CENTER, FLOAT_TOP, FLOAT_BOTTOM]:
            for (
                drawer_strokes,
                enclosure_min_x,
                enclosure_max_x,
                enclosure_min_y,
                enclosure_max_y,
            ) in generator._generate_drawers_iterator(
                n_drawers=n_drawers, stack_float_locations=float_location
            ):
                test_strokes += drawer_strokes
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)


def test_furniture_tasks_generator_generate_stacked_drawers_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.FurnitureTasksGenerator.name]
    train, test = generator._generate_stacked_drawers_stimuli(train_ratio=1.0)
    for split, objects in [("train", train), ("test", test)]:
        _test_render_save_programs(
            stroke_arrays=objects, export_dir=DESKTOP, no_blanks=False, split=split
        )


def test_furniture_tasks_generator_generate_lounges_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.FurnitureTasksGenerator.name]
    train, test = generator._generate_lounges_stimuli(train_ratio=1.0)
    for split, objects in [("train", train), ("test", test)]:
        _test_render_save_programs(
            stroke_arrays=objects, export_dir=DESKTOP, no_blanks=False, split=split
        )


def test_furniture_tasks_generator_generate_seat_drawers_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.FurnitureTasksGenerator.name]
    train, test = generator._generate_seat_drawers_stimuli(train_ratio=1.0)
    for split, objects in [("train", train), ("test", test)]:
        _test_render_save_programs(
            stroke_arrays=objects, export_dir=DESKTOP, no_blanks=False, split=split
        )


def test_furniture_tasks_generator_generate_strokes_for_stimuli():
    generator = TasksGeneratorRegistry[to_test.FurnitureTasksGenerator.name]
    train, test = generator._generate_strokes_for_stimuli(train_ratio=0.8)
    for split, objects in [("train", train), ("test", test)]:
        _test_render_save_programs(
            stroke_arrays=objects, export_dir=DESKTOP, no_blanks=False, split=split
        )
