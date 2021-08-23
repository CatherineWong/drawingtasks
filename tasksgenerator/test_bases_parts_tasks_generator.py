"""
test_bases_parts_tasks_generator.py | Author : Catherine Wong.
"""
import os
import numpy as np
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
import primitives.object_primitives as object_primitives
import tasksgenerator.bases_parts_tasks_generator as to_test
import tasksgenerator.dial_tasks_generator as dial_tasks_generator

DESKTOP = "/Users/catwong/Desktop/output"  # Internal for testing purposes.


def _test_render_save_programs(stroke_arrays, export_dir, no_blanks=True):
    for program_id, s in enumerate(stroke_arrays):
        # Can it render the program?

        canvas_size = object_primitives.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT
        rendered = object_primitives.render_stroke_arrays_to_canvas(
            s,
            stroke_width_height=6 * object_primitives.XYLIM,
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


def test_bases_parts_tasks_generator_generate_n_objects_on_grid_x_y_limits(tmpdir):
    test_strokes = []
    generator = TasksGeneratorRegistry[to_test.AbstractBasesAndPartsTasksGenerator.name]

    c = object_primitives._circle
    r = object_primitives._rectangle

    dial_generator = TasksGeneratorRegistry[
        dial_tasks_generator.SimpleDialTasksGenerator.name
    ]
    dial = dial_generator._generate_nested_circle_dials(
        n_circles=2,
        dial_size=dial_tasks_generator.DIAL_LARGE,
        dial_angle=dial_tasks_generator.DIAL_VERTICAL,
        shape_specification=[c, r],
    )

    objects = [
        object_primitives._circle,
        object_primitives.rectangle(width=1, height=1),
        dial[0],
    ]

    for object in objects:
        for n_columns in [3, 5]:
            for n_rows in [3]:
                for grid_indices in [
                    range(val) for val in range(1, n_columns * n_rows)
                ]:
                    for float_location in [
                        to_test.FLOAT_BOTTOM,
                    ]:

                        (
                            base_strokes,
                            min_x,
                            max_x,
                            min_y,
                            max_y,
                        ) = generator._generate_basic_n_segment_bases(
                            primitives=[to_test.RECTANGLE],
                            widths=[10],
                            heights=[5],
                            float_locations=[to_test.FLOAT_TOP],
                            right_margins=[0],
                        )

                        (
                            grid_strokes,
                            min_x,
                            max_x,
                            min_y,
                            max_y,
                        ) = generator._generate_n_objects_on_grid_x_y_limits(
                            object=object,
                            object_center=(0.0, 0.0),
                            object_height=1,
                            object_width=1,
                            min_x=min_x,
                            max_x=max_x,
                            min_y=min_y,
                            max_y=max_y,
                            n_rows=n_rows,
                            n_columns=n_columns,
                            float_location=float_location,
                            grid_indices=grid_indices,
                        )

                        strokes = [base_strokes[0] + grid_strokes[0]]
                        test_strokes += strokes
                    _test_render_save_programs(
                        stroke_arrays=test_strokes, export_dir=DESKTOP
                    )


# def test_bases_parts_tasks_generator_generate_basic_n_segment_bases(tmpdir):
#     test_strokes = []
#     generator = TasksGeneratorRegistry[to_test.AbstractBasesAndPartsTasksGenerator.name]
#     for filial_primitives in [
#         [to_test.RECTANGLE],
#         [to_test.CIRCLE],
#     ]:
#         for base_primitives in [
#             [to_test.RECTANGLE],
#             [to_test.CIRCLE],
#         ]:
#             for base_widths in [[to_test.SMALL], [to_test.LARGE], [to_test.LARGE * 2]]:
#                 for base_heights in [[to_test.MEDIUM]]:
#                     for filial_widths in [[to_test.SMALL], [to_test.LARGE]]:
#                         for filial_heights in [[to_test.MEDIUM]]:
#                             for base_float_locations in [
#                                 [to_test.FLOAT_TOP],
#                                 [to_test.FLOAT_CENTER],
#                                 [to_test.FLOAT_BOTTOM],
#                             ]:
#                                 for filial_float_locations in [
#                                     [to_test.FLOAT_TOP],
#                                     [to_test.FLOAT_CENTER],
#                                     [to_test.FLOAT_BOTTOM],
#                                 ]:
#                                     for base_margins in [[0]]:
#                                         for filial_margins in [[0]]:
#                                             for base_repetitions in [2, 3]:
#                                                 for filial_repetitions in [0, 1, 2]:
#                                                     primitives = (
#                                                         filial_primitives
#                                                         * filial_repetitions
#                                                         + base_primitives
#                                                         * base_repetitions
#                                                         + filial_primitives
#                                                         * filial_repetitions
#                                                     )
#                                                     widths = (
#                                                         filial_widths
#                                                         * filial_repetitions
#                                                         + base_widths * base_repetitions
#                                                         + filial_widths
#                                                         * filial_repetitions
#                                                     )
#                                                     heights = (
#                                                         filial_heights
#                                                         * filial_repetitions
#                                                         + base_heights
#                                                         * base_repetitions
#                                                         + filial_heights
#                                                         * filial_repetitions
#                                                     )
#                                                     float_locations = (
#                                                         filial_float_locations
#                                                         * filial_repetitions
#                                                         + base_float_locations
#                                                         * base_repetitions
#                                                         + filial_float_locations
#                                                         * filial_repetitions
#                                                     )
#                                                     margins = (
#                                                         filial_margins
#                                                         * filial_repetitions
#                                                         + base_margins
#                                                         * base_repetitions
#                                                         + filial_margins
#                                                         * filial_repetitions
#                                                     )
#
#                                                     (
#                                                         strokes,
#                                                         min_x,
#                                                         max_x,
#                                                         min_y,
#                                                         max_y,
#                                                     ) = generator._generate_basic_n_segment_bases(
#                                                         primitives=primitives,
#                                                         widths=widths,
#                                                         heights=heights,
#                                                         float_locations=float_locations,
#                                                         right_margins=margins,
#                                                     )
#                                                     test_strokes += strokes
#     _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
