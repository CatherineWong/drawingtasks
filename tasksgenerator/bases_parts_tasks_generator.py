"""
bases_parts_tasks_generator.py | Author : Catherine Wong.
Defines an abstract bases generator that creates classes of common reusable parts.
"""
import math, random, itertools
import primitives.object_primitives as object_primitives
from dreamcoder.grammar import Grammar
from tasksgenerator.dial_tasks_generator import BASE_CENTER
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

CIRCLE, RECTANGLE, LINE = ("CIRCLE", "RECTANGLE", "LINE")
FLOAT_TOP, FLOAT_CENTER, FLOAT_BOTTOM = "FLOAT_TOP", "FLOAT_CENTER", "FLOAT_BOTTOM"
BASE_CENTER=0

NONE, SMALL, MEDIUM, LARGE = 0, 1, 1.5, 2
SCALE_UNIT = 0.5
QUARTER_SCALE = 0.25
THREE_QUARTER_SCALE = 0.75
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
        scale_special_shapes=True,
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
                if scale_special_shapes:
                    scaled_primitive = T(shape_primitive, s=width)
                else:
                    scaled_primitive = shape_primitive

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

    def _calculate_float_offset(
        self, object_center, object_height, object_width, float_location
    ):
        """Utility function for calculating float offsets. Currently supports vertical floating: CENTER, TOP, BOTTOM"""
        object_center_x, object_center_y = object_center
        if float_location == FLOAT_CENTER:
            float_offset = -object_center_y
            object_max_y, object_min_y = object_height * 0.5, -object_height * 0.5
        elif float_location == FLOAT_TOP:
            float_offset = -object_center_y + (object_height * 0.5)
            object_max_y, object_min_y = object_height, 0
        elif float_location == FLOAT_BOTTOM:
            float_offset = -object_center_y + (object_height * -0.5)
            object_max_y, object_min_y = 0, -object_height
        else:
            assert False

        return float_offset, object_max_y, object_min_y

    def _generate_object_on_location(
        self,
        object,
        object_center,
        object_height,
        object_width,
        location,
        float_location,
        x_margin,
        y_margin,
    ):
        """
        Utility function for transforming an object to place it at a location. Currently supports y_floating and places objects so that they are x_centered.
        This is specified via:
            object: the strokes to be placed.
            object_center, object_height, object_width: (x,y tuple); float, float.
            location: (x, y) tuple for placing the object.
            float_location [TOP, CENTER, BOTTOM]: where to float the object wrt the location.
            x_margin, y_margin: float, float for adding an additional margin wrt the location.
        Returns:
            strokes, min_x, max_x, min_y, max_y of the strokes. If a margin is specified this will return the coordinates of the object, not including the margin.
        """
        all_strokes = []

        location_x, location_y = location
        # Calculate the float offset.
        y_float_offset, object_max_y, object_min_y = self._calculate_float_offset(
            object_center, object_height, object_width, float_location
        )

        x_value = location_x + x_margin
        y_value = location_y + y_float_offset + y_margin
        placed_primitive = T(object, x=x_value, y=y_value)

        all_strokes += placed_primitive

        min_y = object_min_y + location_y + y_margin
        max_y = object_max_y + location_y + y_margin
        min_x, max_x = x_value - (object_width * 0.5), x_value + (object_width * 0.5)

        return [all_strokes], min_x, max_x, min_y, max_y

    def _generate_n_objects_on_grid_x_y_limits(
        self,
        object,
        object_center,
        object_height,
        object_width,
        min_x,
        max_x,
        min_y,
        max_y,
        n_rows,
        n_columns,
        float_location,
        grid_indices,
    ):
        """
        Utility function for placing n objects on the indices of a grid. Currently supports y_floating and places objects so that they are x_centered.
        This is specified via:
            object: the strokes to be placed.
            object_center, object_height, object_width: (x,y tuple); float, float.
            min_x, max_x, min_y, max_y: the x and y limits of the desired grid.
            n_rows, n_columns: (int, int). number of rows and columns for the grid.
            float_location: [TOP, CENTER, BOTTOM]: where to float the object wrt the coordinates of the grid.
            grid_indices: array of the numbered indices on the grid to place the object, ordered from 0 ... n_rows x n_columns moving L-> R and top to bottom.
        Returns:
            strokes, min_x, max_x, min_y, max_y of the strokes.
        """
        all_strokes = []
        min_x, max_x, min_y, max_y = min_x, max_x, min_y, max_y

        # Generate the base grid locations
        x_locations = np.linspace(start=min_x, stop=max_x, num=n_columns)
        y_locations = np.linspace(start=min_y, stop=max_y, num=n_rows)

        # Calculate the float offset.
        y_float_offset, object_max_y, object_min_y = self._calculate_float_offset(
            object_center, object_height, object_width, float_location
        )

        for x_idx, x_value in enumerate(x_locations):
            for y_idx, y_value in enumerate(y_locations):
                grid_idx = int((y_idx * len(y_locations)) + x_idx)
                if not grid_idx in grid_indices:
                    continue
                y_value += y_float_offset

                grid_primitive = T(object, x=x_value, y=y_value)

                object_max_y += y_value
                object_min_y += y_value
                object_min_x = x_value - (0.5 * object_width)
                object_max_x = x_value + (0.5 * object_width)

                all_strokes += grid_primitive

                min_x = min(object_min_x, min_x)
                max_x = max(object_max_x, max_x)
                min_y = min(object_min_y, min_y)
                max_y = max(object_max_y, max_y)

        return [all_strokes], min_x, max_x, min_y, max_y
