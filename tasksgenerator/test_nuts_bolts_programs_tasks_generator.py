"""
test_nuts_bolts_programs_tasks_generator.py | Author : Catherine Wong
"""
import os
import numpy as np
from primitives.gadgets_primitives import *
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
from primitives.test_object_primitives import (
    _test_parse_render_save_programs,
    _test_render_save_programs,
)
from tasksgenerator.bases_parts_tasks_generator import *

import tasksgenerator.nuts_bolts_programs_tasks_generator as to_test

DESKTOP = f"/Users/catwong/Desktop/zyzzyva/research/lax-language-abstractions/drawing_tasks_stimuli/{to_test.NutsBoltsProgramsTasksGenerator.name}"  # Internal for testing purposes.

generator = TasksGeneratorRegistry[to_test.NutsBoltsProgramsTasksGenerator.name]


def test_generate_simple_nuts_stimuli_strings(tmpdir):
    generator = TasksGeneratorRegistry[to_test.NutsBoltsProgramsTasksGenerator.name]
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_simple_nuts_stimuli_strings(train_ratio=0.8)
    for (split, strings) in [
        ("train", train_strings),
        ("test", test_strings),
    ]:
        objects, synthetic = zip(*strings)
        _test_parse_render_save_programs(
            program_strings=objects, tmpdir=DESKTOP, split=split
        )
        print(f"Total string length: {np.sum([len(o) for o in objects])}")


def test_generate_perforated_nuts_stimuli_strings(tmpdir):
    generator = TasksGeneratorRegistry[to_test.NutsBoltsProgramsTasksGenerator.name]
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_perforated_nuts_stimuli_strings(train_ratio=0.8)
    for split, strings in [("train", train_strings), ("test", test_strings)]:
        objects, synthetic = zip(*strings)
        _test_parse_render_save_programs(
            program_strings=objects, tmpdir=DESKTOP, split=split
        )
        print(f"Total string length: {np.sum([len(o) for o in objects])}")


def test_generate_dsl_primitives():
    # Low-level DSL
    test_strings = [
        p_string
        for (p, p_string) in [
            T_string(c_string[0], c_string[-1], s=""),
            polygon_string(7),
            hexagon_string,
            octagon_string,
            r_string,
        ]
    ]
    _test_parse_render_save_programs(
        program_strings=test_strings, tmpdir=DESKTOP, split="l1"
    )


def test_generate_mid_dsl_primitives(tmpdir):
    generator = TasksGeneratorRegistry[to_test.NutsBoltsProgramsTasksGenerator.name]
    (train, test, train_strings, test_strings,) = generator._generate_dsl_primitives(
        train_ratio=0.8
    )
    for split, strings in [("train", train_strings), ("test", test_strings)]:
        objects, synthetic = zip(*strings)
        _test_parse_render_save_programs(
            program_strings=objects, tmpdir=DESKTOP, split="l2"
        )
        print(f"Total string length: {np.sum([len(o) for o in objects])}")
