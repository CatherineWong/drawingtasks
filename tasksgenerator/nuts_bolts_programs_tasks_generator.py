"""
nuts_bolts_programs_tasks_generator.py | Author : Catherine Wong
Defines TasksGenerators that produce gadget tasks that look like nuts and bolts.

Threads program string generating logic through the generation.
"""
import math, random, itertools, copy
from primitives.gadgets_primitives import *
from dreamcoder.grammar import Grammar
from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
    ManualCurriculumTasksGenerator,
    TasksGeneratorRegistry,
    TaskCurriculum,
    DrawingTask,
    random_sample_ratio_ordered_array,
)
from tasksgenerator.bases_parts_tasks_generator import *
from tasksgenerator.s12_s13_tasks_generator import RANDOM_SEED


@TasksGeneratorRegistry.register
class NutsBoltsProgramsTasksGenerator(AbstractTasksGenerator):
    """Generates gadget tasks containing a base and a set of 'dials' placed at positions along the base."""

    name = "nuts_bolts_programs"

    def __init__(self):
        super().__init__(grammar=constants + some_none + objects + transformations)

    def _generate_simple_nuts_stimuli_strings(self, train_ratio):
        """Generates simple nuts: up to two nested shapes on the outer edge, and no perforations. Generates train and test. Also generates strings. See: nuts_bolts_tasks_generator._generate_simple_nuts_stimuli for original implementation."""
        all_strokes = []
        all_strokes_strings = []
        base_size = LARGE
        for outer_shapes in [
            [cc_string],
            [cc_string, cc_string],
            [hexagon_string],
            [hexagon_string, hexagon_string],
            [octagon_string],
        ]:
            # Note: in theory we could thread these calculations through as strings. For now we do not.
            for outer_shapes_min_size in [base_size * n for n in [1, 2]]:
                for inner_shapes in [[cc_string], [hexagon_string], [r_string]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        (
                            object_strokes,
                            stroke_strings,
                            height,
                            height_strings,
                        ) = self._generate_perforated_shapes_string(
                            outer_shapes=outer_shapes,
                            outer_shapes_min_size=f"{outer_shapes_min_size:g}",
                            inner_shapes=inner_shapes,
                            inner_shapes_max_size=f"{inner_shapes_max_size:g}",
                            n_decorators=str(0),
                        )
                        all_strokes += object_strokes
                        all_strokes_strings.append(stroke_strings)

        return random_sample_ratio_ordered_array(
            all_strokes, train_ratio, strings_array=all_strokes_strings
        )

    def _generate_perforated_nuts_stimuli_strings(self, train_ratio):
        """Generates nuts with perforated 'decorators' around the center. Also generates strings. See: nuts_bolts_tasks_generator._generate_perforated_nuts_stimuli for original implementation."""
        all_strokes = []
        all_strokes_strings = []
        base_size = LARGE
        for outer_shapes in [
            [cc_string],
            [hexagon_string],
            [octagon_string],
            [hexagon_string, hexagon_string],
        ]:
            for outer_shapes_min_size in [base_size * n for n in [2]]:
                for inner_shapes in [[cc_string], [hexagon_string], [r_string]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        for decorator_shape in [c_string, r_string]:
                            for decorator_size in [SCALE_UNIT]:
                                for n_decorators in [2, 4, 6, 8]:
                                    decorator_displacement = (
                                        f"(* {inner_shapes_max_size:g} {MEDIUM})"
                                    )
                                    (
                                        object_strokes,
                                        stroke_strings,
                                        height,
                                        height_strings,
                                    ) = self._generate_perforated_shapes_string(
                                        outer_shapes=outer_shapes,
                                        outer_shapes_min_size=f"{outer_shapes_min_size:g}",
                                        inner_shapes=inner_shapes,
                                        inner_shapes_max_size=f"{inner_shapes_max_size:g}",
                                        n_decorators=str(n_decorators),
                                        decorator_shape=decorator_shape,
                                        decorator_size=f"{decorator_size:g}",
                                        decorator_displacement=decorator_displacement,
                                    )
                                    all_strokes += object_strokes
                                    all_strokes_strings.append(stroke_strings)

        return random_sample_ratio_ordered_array(
            all_strokes, train_ratio, strings_array=all_strokes_strings
        )

    def _generate_perforated_shapes_string(
        self,
        outer_shapes=[c_string],
        outer_shapes_min_size=str(LARGE),
        inner_shapes=[c_string],
        inner_shapes_max_size=str(SMALL),
        nesting_scale_unit=str(0.25),
        decorator_shape=c_string,
        n_decorators=str(4),
        decorator_size=str(0.25),
        decorator_displacement=str(0.75),
        decorator_start_angle="(/ pi 4)",
        n_spokes=str(0),
        spoke_angle="(/ pi 4)",
        spoke_length=str(0),
    ):
        """Generates perforated shapes and a string program that can be evaluated to generate the perforated shape. See dial_tasks_generator._generate_perforated_shapes for the original implementation.

        :ret: object_strokes, stroke_string, height, height_string.

        """
        object_strokes, object_strings = [], []

        # Place outer shapes.
        # # Note: catwong: we don't currently express the looped computation in loop.
        outer_shape_size = peval(outer_shapes_min_size)
        outer_strings = []
        for i, (shape, shape_string) in enumerate(outer_shapes):
            object_stroke, object_string = T_string(
                shape, shape_string, s=str(outer_shape_size)
            )

            object_strokes += object_stroke
            outer_strings.append(object_string)
            outer_shape_size += peval(nesting_scale_unit)
        outer_shape_string = connect_strokes(outer_strings)
        object_strings.append(outer_shape_string)

        # Place inner shapes
        inner_shape_size = peval(inner_shapes_max_size)
        inner_strings = []
        for i, (shape, shape_string) in enumerate(inner_shapes):
            object_stroke, object_string = T_string(
                shape, shape_string, s=str(inner_shape_size)
            )
            object_strokes += object_stroke
            inner_shape_size -= peval(nesting_scale_unit)
            inner_strings.append(object_string)
        inner_shape_string = connect_strokes(inner_strings)
        object_strings.append(inner_shape_string)

        # Place decorators along evenly divided segments of a circle.
        # Note that this does not perfectly replicate the for-loop behavior in the original.
        decorator_shape, decorator_string = T_string(
            decorator_shape[0], decorator_shape[-1], s=decorator_size
        )
        decorator_strokes, decorator_string = rotation_string(
            decorator_shape,
            decorator_string,
            n_decorators,
            decorator_displacement,
            decorator_start_angle,
        )
        object_strokes += decorator_strokes
        object_strings.append(decorator_string)

        height, height_string = outer_shape_size, str(outer_shape_size)
        return [object_strokes], connect_strokes(object_strings), height, height_string
