"""
test_wheels_tasks_generator.py | Author : Catherine Wong.
"""
import os
import numpy as np
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
import primitives.object_primitives as object_primitives
import tasksgenerator.wheels_tasks_generator as to_test

import tasksgenerator.bases_parts_tasks_generator as bases_parts_tasks_generator
import tasksgenerator.dial_tasks_generator as dial_tasks_generator
import tasksgenerator.antenna_tasks_generator as antenna_tasks_generator

DESKTOP = "/Users/catwong/Desktop/wheels"  # Internal for testing purposes.

SMALL, MEDIUM, LARGE, THREE_QUARTER_SCALE = (
    bases_parts_tasks_generator.SMALL,
    bases_parts_tasks_generator.MEDIUM,
    bases_parts_tasks_generator.LARGE,
    bases_parts_tasks_generator.THREE_QUARTER_SCALE,
)


def _test_render_save_programs(stroke_arrays, export_dir, no_blanks=True):
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


def test_wheeled_vehicles_tasks_generator_generate_train_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.WheeledVehiclesTasksGenerator.name]
    all_objects = generator._generate_train_stimuli()
    _test_render_save_programs(
        stroke_arrays=all_objects, export_dir=DESKTOP, no_blanks=False
    )


def test_wheeled_vehicles_tasks_generator_generate_truck_stimuli(tmpdir):
    generator = TasksGeneratorRegistry[to_test.WheeledVehiclesTasksGenerator.name]
    all_objects = generator._generate_truck_stimuli()
    _test_render_save_programs(
        stroke_arrays=all_objects, export_dir=DESKTOP, no_blanks=False
    )


#
# def test_wheeled_vehicles_tasks_generator_generate_buggy_stimuli(tmpdir):
#     generator = TasksGeneratorRegistry[to_test.WheeledVehiclesTasksGenerator.name]
#     all_objects = generator._generate_buggy_stimuli()
#     _test_render_save_programs(
#         stroke_arrays=all_objects, export_dir=DESKTOP, no_blanks=False
#     )


# def test_wheeled_vehicles_tasks_generator_generate_row_of_wheels():
#     c = object_primitives._circle
#     r = object_primitives._rectangle
#     test_strokes = []
#     generator = TasksGeneratorRegistry[to_test.WheeledVehiclesTasksGenerator.name]
#     for outer_shapes in [[c], [c, c]]:
#         for outer_shapes_min_size in [LARGE * MEDIUM, LARGE * LARGE]:
#             for inner_shapes in [[c], [r]]:
#                 for inner_shapes_max_size in [SMALL]:
#                     for n_decorators in [0, 4, 8]:
#                         for n_spokes in [0, 2, 6]:
#                             (
#                                 strokes,
#                                 min_x,
#                                 max_x,
#                                 min_y,
#                                 max_y,
#                             ) = generator._generate_row_of_wheels(
#                                 outer_shapes=outer_shapes,
#                                 outer_shapes_min_size=outer_shapes_min_size,
#                                 inner_shapes=inner_shapes,
#                                 inner_shapes_max_size=inner_shapes_max_size,
#                                 n_decorators=n_decorators,
#                                 n_spokes=n_spokes,
#                                 min_x=-5,
#                                 max_x=5,
#                                 paired_wheels=False,
#                                 n_wheels=5,
#                             )
#                             test_strokes += strokes
#
#     _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
#

# def test_wheeled_vehicles_tasks_generator_generate_buggy_bases():
#     antenna_generator = antenna_tasks_generator.SimpleAntennaTasksGenerator()
#     n_wires = 3
#     antenna_object = antenna_generator._generate_stacked_antenna(
#         n_wires=n_wires,
#         scale_wires=False,
#         end_shape=None,
#     )[0]
#     antenna_height = antenna_tasks_generator.ANTENNA_BASE_HEIGHT + (
#         antenna_tasks_generator.ANTENNA_SMALL * (n_wires - 1)
#     )
#
#     test_strokes = []
#     generator = TasksGeneratorRegistry[to_test.WheeledVehiclesTasksGenerator.name]
#     for first_tier_height in [SMALL, MEDIUM, LARGE]:
#         for first_tier_width in [LARGE * n for n in range(5, 8)]:
#             for second_tier_height in [SMALL, MEDIUM, LARGE]:
#                 for second_tier_width in [LARGE * n for n in range(1, 4)]:
#                     for antenna in [antenna_object, None]:
#                         (
#                             strokes,
#                             min_x,
#                             max_x,
#                             min_y,
#                             max_y,
#                         ) = generator._generate_buggy_bases(
#                             tier_heights=[first_tier_height, second_tier_height],
#                             tier_widths=[first_tier_width, second_tier_width],
#                             antenna=antenna,
#                             antenna_height=antenna_height,
#                         )
#                         test_strokes += strokes
#
#     _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)


# def test_wheeled_vehicles_tasks_generator_generate_truck_bases():
#     test_strokes = []
#     generator = TasksGeneratorRegistry[to_test.WheeledVehiclesTasksGenerator.name]
#
#     for head_width in [SMALL]:
#         for head_height in [SMALL]:
#             for body_width in [LARGE * scale for scale in range(4, 7)]:
#                 for body_height in [MEDIUM]:
#                     for nose_scale in [0.5, 0.25]:
#                         for reverse in [True, False]:
#                             (
#                                 strokes,
#                                 min_x,
#                                 max_x,
#                                 min_y,
#                                 max_y,
#                             ) = generator._generate_truck_bases(
#                                 head_width=head_width,
#                                 head_height=head_height,
#                                 body_width=body_width,
#                                 body_height=body_height,
#                                 nose_scale=nose_scale,
#                                 reverse=reverse,
#                             )
#                             test_strokes += strokes
#
#         _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)


# def test_wheeled_vehicles_tasks_generator_generate_train_bases():
#     test_strokes = []
#     generator = TasksGeneratorRegistry[to_test.WheeledVehiclesTasksGenerator.name]
#
#     caboose_primitives, caboose_heights, caboose_widths, caboose_floats = (
#         [bases_parts_tasks_generator.RECTANGLE, bases_parts_tasks_generator.RECTANGLE],
#         [MEDIUM * THREE_QUARTER_SCALE, MEDIUM],
#         [MEDIUM, MEDIUM],
#         [bases_parts_tasks_generator.FLOAT_TOP, bases_parts_tasks_generator.FLOAT_TOP],
#     )
#
#     for body_heights in [MEDIUM, LARGE]:
#         for body_widths in [LARGE * 2, LARGE * 3]:
#             for body_repetitions in [1, 2, 3]:
#                 for car_margins in [0.25, 0.5]:
#                     (
#                         strokes,
#                         min_x,
#                         max_x,
#                         min_y,
#                         max_y,
#                     ) = generator._generate_train_bases(
#                         caboose_primitives=caboose_primitives,
#                         caboose_heights=caboose_heights,
#                         caboose_widths=caboose_widths,
#                         caboose_floats=caboose_floats,
#                         reflect_caboose_for_head=True,
#                         body_primitives=[bases_parts_tasks_generator.RECTANGLE],
#                         body_heights=[body_heights],
#                         body_widths=[body_widths],
#                         body_floats=[bases_parts_tasks_generator.FLOAT_TOP],
#                         body_repetitions=body_repetitions,
#                         car_margins=car_margins,
#                     )
#                     test_strokes += strokes
#
#         _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
