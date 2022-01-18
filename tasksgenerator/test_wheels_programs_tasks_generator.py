"""test_wheels_programs_tasks_generator | Author: Catherine Wong"""

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
import tasksgenerator.wheels_programs_tasks_generator as to_test
from tasksgenerator.dial_programs_task_generator import *

DESKTOP = f"/Users/catherinewong/Desktop/zyzzyva/research/language-abstractions/drawing_tasks_stimuli/{to_test.WheelsProgramsTasksGenerator.name}"  # Internal for testing purposes.


def test_wheeled_vehicles_tasks_generator_generate_truck_bases():
    test_strokes, test_stroke_strings = [], []
    generator = TasksGeneratorRegistry[to_test.WheelsProgramsTasksGenerator.name]

    for head_width in [str(SMALL)]:
        for head_height in [str(SMALL)]:
            for body_width in [f"(* {LARGE} {scale})" for scale in range(4, 7)]:
                for body_height in [str(MEDIUM)]:
                    for nose_scale in [str(0.5), str(0.25)]:
                        for reverse in [True, False]:
                            (
                                strokes,
                                stroke_strings,
                                min_x,
                                max_x,
                                min_y,
                                max_y,
                            ) = generator._generate_truck_bases_strings(
                                head_width=head_width,
                                head_height=head_height,
                                body_width=body_width,
                                body_height=body_height,
                                nose_scale=nose_scale,
                                reverse=reverse,
                            )
                            test_strokes += strokes
                            test_stroke_strings.append(stroke_strings)

        # _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP
        )


def test_wheeled_vehicles_tasks_generator_generate_train_bases():
    test_strokes, test_stroke_strings = [], []
    generator = TasksGeneratorRegistry[to_test.WheelsProgramsTasksGenerator.name]

    caboose_primitives, caboose_heights, caboose_widths, caboose_floats = (
        [RECTANGLE, RECTANGLE],
        [f"(* {MEDIUM} {THREE_QUARTER_SCALE})", str(MEDIUM)],
        [str(MEDIUM), str(MEDIUM)],
        [FLOAT_TOP, FLOAT_TOP],
    )

    for body_heights in [str(MEDIUM), str(LARGE)]:
        for body_widths in [str(LARGE * 2), str(LARGE * 3)]:
            for body_repetitions in [1, 2, 3]:
                for car_margins in [str(0.25), str(0.5)]:
                    (
                        strokes,
                        stroke_strings,
                        min_x,
                        max_x,
                        min_y,
                        max_y,
                    ) = generator._generate_train_bases_strings(
                        caboose_primitives=caboose_primitives,
                        caboose_heights=caboose_heights,
                        caboose_widths=caboose_widths,
                        caboose_floats=caboose_floats,
                        reflect_caboose_for_head=True,
                        body_primitives=[RECTANGLE],
                        body_heights=[body_heights],
                        body_widths=[body_widths],
                        body_floats=[FLOAT_TOP],
                        body_repetitions=body_repetitions,
                        car_margins=car_margins,
                    )
                    test_strokes += strokes
                    test_stroke_strings.append(stroke_strings)

        # _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP
        )


def test_wheeled_vehicles_tasks_generator_generate_buggy_bases():
    antenna_generator = DialProgramsTasksGenerator()
    n_wires = 3
    (
        antenna_object,
        antenna_string,
        antenna_dict,
    ) = antenna_generator._generate_stacked_antenna_strings(
        n_wires=n_wires,
        scale_wires=False,
        end_shape=None,
    )
    antenna_object = antenna_object[0]

    antenna_base_height = 3
    antenna_height = antenna_base_height + (SMALL * (n_wires - 1))

    test_strokes, test_stroke_strings = [], []
    generator = TasksGeneratorRegistry[to_test.WheelsProgramsTasksGenerator.name]
    for first_tier_height in [SMALL, MEDIUM, LARGE]:
        for first_tier_width in [LARGE * n for n in range(5, 8)]:
            for second_tier_height in [SMALL, MEDIUM, LARGE]:
                for second_tier_width in [LARGE * n for n in range(1, 4)]:
                    for antenna in [(antenna_object, antenna_string), None]:
                        (
                            strokes,
                            stroke_strings,
                            min_x,
                            max_x,
                            min_y,
                            max_y,
                        ) = generator._generate_buggy_bases_strings(
                            tier_heights=[first_tier_height, second_tier_height],
                            tier_widths=[first_tier_width, second_tier_width],
                            antenna=antenna,
                            antenna_height=antenna_height,
                        )
                        test_strokes += strokes
                        test_stroke_strings.append(stroke_strings)

    # _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
    _test_parse_render_save_programs(
        program_strings=test_stroke_strings, tmpdir=DESKTOP
    )


def test_wheels_tasks_generator_generate_parts_for_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.WheelsProgramsTasksGenerator.name]
    (
        train,
        test,
        train_strings,
        test_strings,
    ) = generator._generate_parts_stimuli_strings(train_ratio=1.0)
    for split, objects, test_stroke_strings in [
        ("train", train, train_strings),
        ("test", test, test_strings),
    ]:
        # _test_render_save_programs(
        #     stroke_arrays=objects, export_dir=DESKTOP, no_blanks=False, split=split
        # )
        _test_parse_render_save_programs(
            program_strings=test_stroke_strings, tmpdir=DESKTOP, split=split
        )
