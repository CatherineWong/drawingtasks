"""
test_nuts_bolts_programs_tasks_generator.py | Author : Catherine Wong
"""
import os
import numpy as np
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
from primitives.test_object_primitives import (
    _test_parse_render_save_programs,
)

import tasksgenerator.nuts_bolts_programs_tasks_generator as to_test

DESKTOP = f"/Users/catwong/Desktop/zyzzyva/research/language-abstractions/drawing_tasks_stimuli/{to_test.NutsBoltsProgramsTasksGenerator.name}"  # Internal for testing purposes.

generator = TasksGeneratorRegistry[to_test.NutsBoltsProgramsTasksGenerator.name]


def test_generate_simple_nuts_stimuli_strings(tmpdir):
    generator = TasksGeneratorRegistry[to_test.NutsBoltsProgramsTasksGenerator.name]
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_simple_nuts_stimuli_strings(train_ratio=0.8)
    for split, objects in [("train", train_strings), ("test", test_strings)]:
        _test_parse_render_save_programs(
            program_strings=objects, tmpdir=DESKTOP, split=split
        )


def test_generate_perforated_nuts_stimuli_strings(tmpdir):
    generator = TasksGeneratorRegistry[to_test.NutsBoltsProgramsTasksGenerator.name]
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_perforated_nuts_stimuli_strings(train_ratio=0.8)
    for split, objects in [("train", train_strings), ("test", test_strings)]:
        _test_parse_render_save_programs(
            program_strings=objects, tmpdir=DESKTOP, split=split
        )
