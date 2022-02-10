"""
test_nuts_bolts_synthetic_tasks_generator.py | Author : Catherine Wong
"""
import os
import numpy as np
from primitives.gadgets_primitives import *
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
from primitives.test_object_primitives import _test_parse_render_save_shape_programs

from tasksgenerator.bases_parts_tasks_generator import *

import tasksgenerator.nuts_bolts_synthetic_language_tasks_generator as to_test

DESKTOP = f"/Users/catwong/Desktop/zyzzyva/research/lax-language-abstractions/drawing_tasks_stimuli/{to_test.NutsBoltsSyntheticLanguageTasksGenerator.name}"  # Internal for testing purposes.

generator = TasksGeneratorRegistry[
    to_test.NutsBoltsSyntheticLanguageTasksGenerator.name
]


def test_generate_simple_nuts_stimuli_shapes(tmpdir):
    generator = TasksGeneratorRegistry[
        to_test.NutsBoltsSyntheticLanguageTasksGenerator.name
    ]
    (
        train,
        test,
        train_shapes,
        test_shapes,
    ) = generator._generate_simple_nuts_stimuli_shapes(train_ratio=0.8)
    for (split, shapes) in [
        ("train", train_shapes),
        ("test", test_shapes),
    ]:
        # Print all of the whats.
        for idx, s in enumerate(shapes):
            print(f"{split} {idx}")
            s._print_language()

        # Save all of the shapes
        _test_parse_render_save_shape_programs(shapes, DESKTOP, split=split)

