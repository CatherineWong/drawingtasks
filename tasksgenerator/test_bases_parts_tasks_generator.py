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


def test_bases_parts_tasks_generator_generate_basic_n_segment_bases(tmpdir):
    test_strokes = []
    generator = TasksGeneratorRegistry[to_test.AbstractBasesAndPartsTasksGenerator.name]
    for filial_primitives in [
        [to_test.RECTANGLE],
        [to_test.CIRCLE],
    ]:
        for base_primitives in [
            [to_test.RECTANGLE],
            [to_test.CIRCLE],
        ]:
            for base_widths in [[to_test.LARGE]]:
                for base_heights in [[to_test.MEDIUM]]:
                    for filial_widths in [[to_test.LARGE]]:
                        for filial_heights in [[to_test.MEDIUM]]:
                            for base_float_locations in [
                                [to_test.FLOAT_TOP],
                                [to_test.FLOAT_CENTER],
                                [to_test.FLOAT_BOTTOM],
                            ]:
                                for filial_float_locations in [
                                    [to_test.FLOAT_TOP],
                                    [to_test.FLOAT_CENTER],
                                    [to_test.FLOAT_BOTTOM],
                                ]:
                                    for base_margins in [[0]]:
                                        for filial_margins in [[0]]:
                                            for base_repetitions in [2, 3]:
                                                for filial_repetitions in [0, 1, 2]:
                                                    primitives = (
                                                        filial_primitives
                                                        * filial_repetitions
                                                        + base_primitives
                                                        * base_repetitions
                                                        + filial_primitives
                                                        * filial_repetitions
                                                    )
                                                    widths = (
                                                        filial_widths
                                                        * filial_repetitions
                                                        + base_widths * base_repetitions
                                                        + filial_widths
                                                        * filial_repetitions
                                                    )
                                                    heights = (
                                                        filial_heights
                                                        * filial_repetitions
                                                        + base_heights
                                                        * base_repetitions
                                                        + filial_heights
                                                        * filial_repetitions
                                                    )
                                                    float_locations = (
                                                        filial_float_locations
                                                        * filial_repetitions
                                                        + base_float_locations
                                                        * base_repetitions
                                                        + filial_float_locations
                                                        * filial_repetitions
                                                    )
                                                    margins = (
                                                        filial_margins
                                                        * filial_repetitions
                                                        + base_margins
                                                        * base_repetitions
                                                        + filial_margins
                                                        * filial_repetitions
                                                    )

                                                    (
                                                        strokes,
                                                        min_x,
                                                        max_x,
                                                        min_y,
                                                        max_y,
                                                    ) = generator._generate_basic_n_segment_bases(
                                                        primitives=primitives,
                                                        widths=widths,
                                                        heights=heights,
                                                        float_locations=float_locations,
                                                        right_margins=margins,
                                                    )
                                                    test_strokes += strokes
    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)
