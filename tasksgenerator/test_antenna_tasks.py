import os
import numpy as np
from tasksgenerator.tasks_generator import (
    TasksGeneratorRegistry,
    AbstractTasksGenerator,
)
import tasksgenerator.antenna_tasks_generator as to_test
import primitives.object_primitives as object_primitives
import tasksgenerator.dial_tasks_generator as to_test_2

DESKTOP = "/Users/yoni/Desktop/test"  # Internal for testing purposes.


def _test_render_save_programs(stroke_arrays, export_dir, no_blanks=True):
    for program_id, s in enumerate(stroke_arrays):
        # Can it render the program?

        canvas_size = object_primitives.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT
        rendered = object_primitives.render_stroke_arrays_to_canvas(
            s,
            stroke_width_height=4 * object_primitives.XYLIM,
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


def test_perforated_shapes():
    test_strokes = []
    generator = TasksGeneratorRegistry[to_test_2.SimpleDialTasksGenerator.name]

    c = object_primitives._circle
    r = object_primitives._rectangle
    p = object_primitives.polygon(n=6)

    for outer_rim in ([c], [r], [p], [c, c], [r, r], [p, p]):
        for inner_rim in ([c], [r], [p], [c, c], [r, r]):
            for n_decorators in [2, 4, 8]:
                for n_spokes in [0, 1, 4, 8]:
                    strokes = generator._generate_perforated_shapes(
                        outer_shapes=outer_rim,
                        inner_shapes=inner_rim,
                        n_spokes=n_spokes,
                        n_decorators=n_decorators,
                    )

                    test_strokes += strokes

    _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)


# def test_antenna_tasks_generator_generate_stacked_antenna():
#     test_strokes = []

#     generator = TasksGeneratorRegistry[to_test.SimpleAntennaTasksGenerator.name]

#     for n_wires in range(1, 4):
#         for antenna_size in [
#             to_test.ANTENNA_SMALL,
#             to_test.ANTENNA_MEDIUM,
#             to_test.ANTENNA_LARGE,
#         ]:
#             for scale_wires in [True, False]:
#                 for primitive in [
#                     None,
#                     object_primitives._circle,
#                     object_primitives._rectangle,
#                 ]:
#                     test_strokes += generator._generate_stacked_antenna(
#                         n_wires=n_wires,
#                         antenna_size=antenna_size,
#                         scale_wires=scale_wires,
#                         end_shape=primitive,
#                     )

#     _test_render_save_programs(stroke_arrays=test_strokes, export_dir=DESKTOP)

