"""
abstract_bases_parts_programs_tasks_generator.py | Author: Catherine Wong.

Implements the bases_parts_tasks_generator with program string generation.
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
from tasksgenerator.tasks_generator import *

from tasksgenerator.bases_parts_tasks_generator import *


@TasksGeneratorRegistry.register
class AbstractBasesAndPartsProgramsTasksGenerator(AbstractTasksGenerator):
    name = "abstract_bases_parts_programs"

    def __init__(self):
        super().__init__(grammar=constants + some_none + objects + transformations)

    def _generate_basic_n_segment_bases_string(
        self,
        primitives=[RECTANGLE],
        heights=[str(SMALL)],
        widths=[str(LARGE)],
        float_locations=[FLOAT_TOP],
        right_margins=[STR_ZERO],
        scale_special_shapes=True,
    ):
        """See bases_parts_tasks_generator for initial implementation."""
        strokes, stroke_strings = [], []
        synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
        # For now, we do this in the most naive way possible. The looping structure is external to the
        # DreamCoder string program.

        # We keep this calculation out of the DreamCoder program.

        total_width = sum([peval(w) for w in widths]) + sum(
            [peval(r) for r in right_margins]
        )
        min_x, max_x = -(total_width / 2), -(total_width / 2)
        min_y, max_y = 0, 0

        curr_end_x = min_x

        base_shapes_to_counts = defaultdict(int)
        for idx, shape_primitive in enumerate(primitives):
            height, width, float_location, right_margin = (
                heights[idx],
                widths[idx],
                float_locations[idx],
                right_margins[idx],
            )
            # Generate the base primitive.
            if shape_primitive == CIRCLE:
                initial_shape = c_string
                scaled_primitive = T_string(initial_shape[0], initial_shape[1], s=width)

                height = width
            elif shape_primitive == RECTANGLE:
                initial_shape = "r_s"
                scaled_primitive = scaled_rectangle_string(w=width, h=height)

            else:
                if scale_special_shapes:
                    initial_shape = shape_primitive
                    scaled_primitive = T_string(
                        shape_primitive[0], shape_primitive[1], s=width
                    )
                else:
                    scaled_primitive = shape_primitive

            # Add a low-level circle for each item
            initial_shape = (
                initial_shape if type(initial_shape) == str else initial_shape[-1]
            )
            shape_abstraction = "base_shape"
            synthetic_dict[LOW_LEVEL] += [shape_abstraction]
            synthetic_dict[LOW_LEVEL_PARTS] += [initial_shape]

            synthetic_dict[LOW_LEVEL_PARAMS].append(str(peval(width)))

            base_shapes_to_counts[(scaled_primitive[-1], initial_shape)] += 1

            # Add unique shapes for each mid-level item with a different scale.
            synthetic_dict[MID_LEVEL_PARAMS].append(str(peval(width)))

            # Float it to the right location.
            if float_location == FLOAT_CENTER:
                float_offset = 0
                curr_max_y, curr_min_y = f"(* {height} 0.5)", f"(* {height} -0.5)"

            elif float_location == FLOAT_TOP:
                float_offset = f"(* {height} 0.5)"
                curr_max_y, curr_min_y = height, STR_ZERO
            elif float_location == FLOAT_BOTTOM:
                float_offset = f"(* {height} -0.5)"
                curr_max_y, curr_min_y = 0, f"(- 0 {height})"
            else:
                assert False
            scaled_primitive = T_string(
                scaled_primitive[0], scaled_primitive[-1], y=float_offset
            )

            # Place its rightmost corner at the last end_x
            shift_offset = f"(+ {curr_end_x} (* 0.5 {width}))"
            scaled_primitive = T_string(
                scaled_primitive[0], scaled_primitive[1], x=shift_offset
            )  # We choose to keep this out of DC program.

            # Increment the end_x to the shape width + the right margin; recalculate the max and min.
            curr_end_x += peval(width) + peval(right_margin)
            max_x = curr_end_x
            min_y = min(peval(curr_min_y), min_y)
            max_y = max(peval(curr_max_y), max_y)

            strokes += scaled_primitive[0]
            stroke_strings.append(scaled_primitive[1])

        # Add unique shapes for each of the base shapes.
        for base_shape, count in base_shapes_to_counts.items():
            shape_abstraction = "base_shape"
            synthetic_dict[MID_LEVEL] += [shape_abstraction]
            synthetic_dict[MID_LEVEL_PARTS] += [base_shape[-1]]

            synthetic_dict[LOW_LEVEL_PARAMS].append(str(count))

        base_string = connect_strokes(stroke_strings)

        # Add the whole base as a high-level abstraction.
        shape_abstraction = "whole_base"
        synthetic_dict[HIGH_LEVEL].append(shape_abstraction)
        synthetic_dict[HIGH_LEVEL_PARTS].append(base_string)

        return [strokes], base_string, synthetic_dict, min_x, max_x, min_y, max_y

    def _generate_object_on_location_string(
        self,
        object,
        object_string,
        object_center,
        object_height,
        object_width,
        location,
        float_location,
        x_margin,
        y_margin,
        object_synthetic_dict=None,
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
        strokes = []

        location_x, location_y = location
        # Calculate the float offset.
        (
            y_float_offset,
            object_max_y,
            object_min_y,
        ) = self._calculate_float_offset_string(
            object_center, object_height, object_width, float_location
        )

        x_value = f"(+ {location_x} {x_margin})"
        y_value = f"(+ (+ {location_y} {y_float_offset}) {y_margin})"
        placed_primitive = T_string(object, object_string, x=x_value, y=y_value)

        strokes += placed_primitive[0]
        stroke_string = placed_primitive[-1]

        min_y = peval(object_min_y) + peval(location_y) + peval(y_margin)
        max_y = peval(object_max_y) + peval(location_y) + peval(y_margin)

        min_x = f"(- {x_value} (* {object_width} 0.5))"
        max_x = f"(+ {x_value} (* {object_width} 0.5))"

        return [strokes], stroke_string, min_x, max_x, min_y, max_y

    def _calculate_float_offset_string(
        self, object_center, object_height, object_width, float_location
    ):
        """Utility function for calculating float offsets as strings. Only supports vertical floating."""
        object_center_x, object_center_y = object_center
        if float_location == FLOAT_CENTER:
            float_offset = f"(- 0 {object_center_y})"
            object_max_y, object_min_y = (
                f"(* {object_height} 0.5)",
                f"(* (- 0 {object_height}) 0.5)",
            )
        elif float_location == FLOAT_TOP:
            float_offset = -object_center_y + (object_height * 0.5)
            float_offset = f"(+ (- 0 {object_center_y}) (* {object_height} 0.5))"
            object_max_y, object_min_y = object_height, STR_ZERO
        elif float_location == FLOAT_BOTTOM:
            float_offset = f"(+ (- 0 {object_center_y}) (* {object_height} (- 0 0.5)))"
            object_max_y, object_min_y = STR_ZERO, -object_height
        else:
            assert False

        return float_offset, object_max_y, object_min_y

    def _generate_n_objects_on_grid_x_y_limits_string(
        self,
        object,
        object_string,
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
        grid_indices=None,  # Note: we cannot replicate this logic cleanly.
        object_synthetic_dict=None,
    ):
        """
        See original implementation in: bases_parts_tasks_generator.

        Note that: we do not re-implement the grid index functionality. Rather, we simply replicate
        a grid and shift it accordingly.
        """
        strokes, stroke_strings = [], []

        # Calculate the float offset.
        if peval(n_rows) * peval(n_columns) == 0:
            return (
                [[]],
                "empt",
                min_x,
                max_x,
                min_y,
                max_y,
            )

        (
            y_float_offset,
            object_max_y,
            object_min_y,
        ) = self._calculate_float_offset_string(
            object_center, object_height, object_width, float_location
        )
        if peval(n_columns) == 1:
            x_spacing = 0
        else:
            x_spacing = f"(/ (- {max_x} {min_x}) {n_columns - 1})"
        y_spacing = f"(+ (/ (- {max_y} {min_y}) {n_rows}) {y_float_offset})"
        _, x_shift = M_string(x=x_spacing)
        _, y_shift = M_string(y=y_spacing)
        row_of_objects_string = f"(repeat {object_string} {n_columns} {x_shift})"
        row_of_rows_string = f"(repeat {row_of_objects_string} {n_rows} {y_shift})"

        x_shift = f"(/ (- {max_x} {min_x}) -2)"
        y_shift = f"(+ (+ (/ (- {max_y} {min_y}) -2) {y_float_offset}) {min_y})"

        row_of_rows, row_of_rows_string = T_string(
            peval(row_of_rows_string), row_of_rows_string, x=x_shift, y=y_shift
        )

        # Add a low-level abstraction for each object.
        object_synthetic_dict[LOW_LEVEL] = object_synthetic_dict[LOW_LEVEL] * int(
            peval(f"(* {n_rows} {n_columns})")
        )
        object_synthetic_dict[LOW_LEVEL_PARTS] = object_synthetic_dict[
            LOW_LEVEL_PARTS
        ] * int(peval(f"(* {n_rows} {n_columns})"))

        # Add a mid-level abstraction for the repetition and a parameter.
        object_synthetic_dict[MID_LEVEL] = [
            "repeat_x",
            "repeat_y",
        ] + object_synthetic_dict[MID_LEVEL]
        object_synthetic_dict[MID_LEVEL_PARTS] = [
            "repeat_x",
            "repeat_y",
        ] + object_synthetic_dict[MID_LEVEL_PARTS]
        object_synthetic_dict[MID_LEVEL_PARAMS] = [
            str(peval(n_rows)),
            str(peval(n_columns)),
        ] + object_synthetic_dict[MID_LEVEL_PARAMS]

        object_synthetic_dict[HIGH_LEVEL] = ["repeated_grid"]
        object_synthetic_dict[HIGH_LEVEL_PARTS] = [row_of_rows_string]

        max_y = max(peval(max_y), peval(object_max_y))
        max_y = f"{max_y:g}"
        return (
            [row_of_rows],
            row_of_rows_string,
            object_synthetic_dict,
            min_x,
            max_x,
            min_y,
            max_y,
        )
