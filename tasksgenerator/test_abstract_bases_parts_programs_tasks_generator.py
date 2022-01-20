"""test_abstract_bases_parts_programs_tasks_generator | AuthorL Catherine Wong"""

import os
import numpy as np
from tasksgenerator.bases_parts_tasks_generator import *
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
from primitives.gadgets_primitives import *
from primitives.test_object_primitives import (
    _test_parse_render_save_programs,
    _test_render_save_programs,
)

import tasksgenerator.abstract_bases_parts_programs_tasks_generator as to_test

DESKTOP = f"/Users/catherinewong/Desktop/zyzzyva/research/language-abstractions/drawing_tasks_stimuli/{to_test.AbstractBasesAndPartsProgramsTasksGenerator.name}"  # Internal for testing purposes.


def test_abstract_generate_n_objects_on_grid_x_y_limits_string():
    test_strokes, test_stroke_strings = [], []
    generator = TasksGeneratorRegistry[
        to_test.AbstractBasesAndPartsProgramsTasksGenerator.name
    ]

    base_heights_and_widths = [
        (SMALL * 3, MEDIUM * 9),
    ]
    total_drawers = 4
    for stack_float_locations in [FLOAT_BOTTOM, FLOAT_TOP, FLOAT_CENTER]:
        for n_drawers in range(1, total_drawers + 1):
            for (base_height, base_width) in base_heights_and_widths:
                if base_height > SMALL * 4 and n_drawers > 3:
                    continue
                (
                    base_strokes,
                    base_stroke_strings,
                    synthetic_dict,
                    base_min_x,
                    base_max_x,
                    base_min_y,
                    base_max_y,
                ) = generator._generate_basic_n_segment_bases_string(
                    primitives=[RECTANGLE],
                    heights=[base_height],
                    widths=[base_width],
                    float_locations=[FLOAT_CENTER],
                )
                drawer_spacing = base_height * QUARTER_SCALE
                total_height = (n_drawers - 1) * (base_height + drawer_spacing)
                min_y, max_y = (
                    -total_height * 0.5,
                    total_height * 0.5,
                )

                (
                    drawer_stack_strokes,
                    drawer_stack_stroke_strings,
                    synthetic_dict,
                    drawer_stack_strokes_min_x,
                    drawer_stack_strokes_max_x,
                    drawer_stack_strokes_min_y,
                    drawer_stack_strokes_max_y,
                ) = generator._generate_n_objects_on_grid_x_y_limits_string(
                    object=base_strokes[0],
                    object_string=base_stroke_strings,
                    object_center=(0, 0),
                    object_height=base_height,
                    object_width=base_width,
                    min_x=0,
                    max_x=0,
                    min_y=min_y,
                    max_y=max_y,
                    n_rows=n_drawers,
                    n_columns=1,
                    float_location=stack_float_locations,
                    grid_indices=range(n_drawers * n_drawers),
                    object_synthetic_dict=synthetic_dict,
                )

                strokes = drawer_stack_strokes
                stroke_strings = drawer_stack_stroke_strings

                test_strokes += strokes
                test_stroke_strings.append(stroke_strings)

    # _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
    _test_parse_render_save_programs(
        program_strings=test_stroke_strings, tmpdir=DESKTOP
    )
