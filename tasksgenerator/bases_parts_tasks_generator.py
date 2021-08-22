"""
bases_parts_tasks_generator.py | Author : Catherine Wong.
Defines an abstract bases generator that creates classes of common reusable parts.
"""
import math, random, itertools
import primitives.object_primitives as object_primitives
from dreamcoder.grammar import Grammar
from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
    ManualCurriculumTasksGenerator,
    TasksGeneratorRegistry,
    TaskCurriculum,
    DrawingTask,
)
import numpy as np

# Graphics primitives.
from tasksgenerator.s12_s13_tasks_generator import (
    RANDOM_SEED,
    rand_choice,
    X_MIN,
    X_SHIFT,
    LONG_LINE_LENGTH,
    T,
    long_vline,
    short_hline,
    T_y,
    make_vertical_grating,
    make_x_grid,
    make_grating_with_objects,
    _make_grating_with_objects,
    DEFAULT_X_GRID,
    T_grid_idx,
    hl,
)

CIRCLE, RECTANGLE, = (
    "CIRCLE",
    "RECTANGLE",
)
FLOAT_TOP, FLOAT_CENTER, FLOAT_BOTTOM = "FLOAT_TOP", "FLOAT_CENTER", "FLOAT_BOTTOM"

NONE, SMALL, MEDIUM, LARGE = 0.0, 1.0, 1.5, 2.0
SCALE_UNIT = 0.5
VERTICAL, RIGHT, LEFT = (
    math.pi / 2,
    math.pi / 4,
    math.pi - (math.pi / 4),
)
short_hline = T(object_primitives._line, x=-0.5)


@TasksGeneratorRegistry.register
class AbstractBasesAndPartsTasksGenerator(AbstractTasksGenerator):
    """Helper function for generating tasks containg a variety of rectangular bases and convenience functions for using bases."""

    name = "abstract_bases_parts"

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super().__init__(
            grammar=object_primitives.constants
            + object_primitives.some_none
            + object_primitives.objects
            + object_primitives.transformations
        )

    def _generate_basic_n_segment_bases(
        self,
        primitives=[RECTANGLE],
        heights=[SMALL],
        widths=[LARGE],
        float_locations=[FLOAT_TOP],
        right_margins=[0],
    ):
        """
        Generates a base comprised of n segments. This can be used as a tier in multi-tiered bases (eg. chairs, trucks, and robots). The base will be generated from left to right starting from the - TOTAL_WIDTH / 2 position (so symmetrical bases will be centered automatically.)

        The base is specified as follows
            primitives [array] - None, CIRCLE, or RECTANGLE

            widths [array] -  scaling factor for the parts. Will be diameter for circles.

            heights [array] - this will be ignored if part is a circle.


            float_locations [TOP, CENTER, BOTTOM] - where to float the parts wrt to the center axis.

            right_margins - [array] - spacing to place to the right of the shape.

        Returns:
            strokes, min_x, max_x, min_y (location of the minimum y location of the base), max_y (location of the maximum y location of the base)
        """

        all_strokes = []
        total_width = sum(widths) + sum(right_margins)
        min_x, max_x = -(total_width / 2), -(total_width / 2)
        min_y, max_y = 0, 0

        curr_end_x = min_x

        for idx, shape_primitive in enumerate(primitives):
            height, width, float_location, right_margin = (
                heights[idx],
                widths[idx],
                float_locations[idx],
                right_margins[idx],
            )
            # Generate the base primitive.
            if shape_primitive == CIRCLE:
                scaled_primitive = T(object_primitives._circle, s=width)
                height = width
            elif shape_primitive == RECTANGLE:
                scaled_primitive = object_primitives.rectangle(
                    width=width, height=height
                )
            else:
                assert False

            # Float it to the right location.
            if float_location == FLOAT_CENTER:
                float_offset = 0
                curr_max_y, curr_min_y = height * 0.5, -height * 0.5
            elif float_location == FLOAT_TOP:
                float_offset = height * 0.5
                curr_max_y, curr_min_y = height, 0
            elif float_location == FLOAT_BOTTOM:
                float_offset = height * -0.5
                curr_max_y, curr_min_y = 0, -height
            else:
                assert False
            scaled_primitive = T(scaled_primitive, y=float_offset)

            # Place its rightmost corner at the last end_x
            shift_offset = curr_end_x + (0.5 * width)
            scaled_primitive = T(scaled_primitive, x=shift_offset)

            # Increment the end_x to the shape width + the right margin; recalculate the max and min.
            curr_end_x += width + right_margin
            max_x = curr_end_x
            min_y = min(curr_min_y, min_y)
            max_y = max(curr_max_y, max_y)

            all_strokes += scaled_primitive

        return [all_strokes], min_x, max_x, min_y, max_y

    def _generate_two_tiered_bases():
        pass

    def _generate_nested_part_rows_on_base():
        """
        Given a base and a nested part, generates a repetitive set of nested parts on it in common locations.
        (eg. for handles or radio dials.)
        """
        pass

    def _generate_nested_parts_below_base():
        """Generalized wheels and legs?"""
        pass
