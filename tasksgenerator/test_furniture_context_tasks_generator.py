"""
test_furniture_context_tasks_generator.py | Author : Catherine Wong.
"""

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
    DESKTOP,
    _test_parse_render_save_programs,
    _test_render_save_programs,
)
import tasksgenerator.furniture_context_tasks_generator as to_test

DESKTOP = f"/Users/catwong/Desktop/zyzzyva/research/lax-language-abstractions/drawing_tasks_stimuli/{to_test.FurnitureContextTasksGenerator.name}"  # Internal for testing purposes.

generator = TasksGeneratorRegistry[to_test.FurnitureContextTasksGenerator.name]


def test_furniture_tasks_generator_generate_parts_for_stimuli(tmpdir):
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_parts_stimuli_strings(train_ratio=1.0)
    for split, objects, test_stroke_strings in [
        ("train", train, train_strings),
    ]:
        test_stroke_strings, synthetic = zip(*test_stroke_strings)

        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP, split=split
        )


def test_furniture_tasks_generator_generate_stacked_drawers_stimuli_strings(tmpdir):
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_stacked_drawers_stimuli_strings(
        train_ratio=1.0, context=CONTEXT_LARGE_ABSTRACTIONS
    )
    for split, objects, test_stroke_strings in [
        (CONTEXT_LARGE_ABSTRACTIONS + "_stacked", train, train_strings),
    ]:
        test_stroke_strings, synthetic = zip(*test_stroke_strings)
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP, split=split
        )

    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_stacked_drawers_stimuli_strings(
        train_ratio=1.0, context=CONTEXT_SMALL_ABSTRACTIONS
    )
    for split, objects, test_stroke_strings in [
        (CONTEXT_SMALL_ABSTRACTIONS + "_stacked", train, train_strings),
    ]:
        test_stroke_strings, synthetic = zip(*test_stroke_strings)
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP, split=split
        )


def test_generate_lounges_stimuli_strings(tmpdir):
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_lounges_stimuli_strings(
        train_ratio=1.0, context=CONTEXT_LARGE_ABSTRACTIONS
    )
    for split, objects, test_stroke_strings in [
        (CONTEXT_LARGE_ABSTRACTIONS + "_lounge", train, train_strings),
    ]:
        test_stroke_strings, synthetic = zip(*test_stroke_strings)
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP, split=split
        )

    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_lounges_stimuli_strings(
        train_ratio=1.0, context=CONTEXT_SMALL_ABSTRACTIONS
    )
    for split, objects, test_stroke_strings in [
        (CONTEXT_SMALL_ABSTRACTIONS + "_lounge", train, train_strings),
    ]:
        test_stroke_strings, synthetic = zip(*test_stroke_strings)
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP, split=split
        )


def test_generate_seat_drawers_stimuli_strings(tmpdir):
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_seat_drawers_stimuli_strings(
        train_ratio=1.0, context=CONTEXT_LARGE_ABSTRACTIONS
    )
    for split, objects, test_stroke_strings in [
        (CONTEXT_LARGE_ABSTRACTIONS + "_seat", train, train_strings),
    ]:
        test_stroke_strings, synthetic = zip(*test_stroke_strings)
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP, split=split
        )

    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_seat_drawers_stimuli_strings(
        train_ratio=1.0, context=CONTEXT_SMALL_ABSTRACTIONS
    )
    for split, objects, test_stroke_strings in [
        (CONTEXT_SMALL_ABSTRACTIONS + "_seat", train, train_strings),
    ]:
        test_stroke_strings, synthetic = zip(*test_stroke_strings)
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP, split=split
        )
