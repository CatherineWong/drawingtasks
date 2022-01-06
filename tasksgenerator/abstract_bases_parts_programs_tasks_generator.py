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
from tasksgenerator.bases_parts_tasks_generator import *


@TasksGeneratorRegistry.register
class AbstractBasesAndPartsProgramsTasksGenerator(AbstractTasksGenerator):
    name = "abstract_bases_parts_programs"

    def __init__(self):
        super().__init__(grammar=constants + some_none + objects + transformations)

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
    ):
        """
        See original implementation in: bases_parts_tasks_generator.

        Note that: we do not re-implement the grid index functionality. Rather, we simply replicate
        a grid and shift it accordingly.
        """
        strokes, stroke_strings = [], []

        # Calculate the float offset.
        y_float_offset, object_max_y, object_min_y = self._calculate_float_offset(
            object_center, object_height, object_width, float_location
        )

        x_spacing = f"(/ (- {max_x} {min_x}) {n_columns})"
        y_spacing = f"(+ (/ (- {max_y} {min_y}) {n_rows}) {y_float_offset})"
        _, x_shift = M_string(x=x_spacing)
        _, y_shift = M_string(y=y_spacing)
        row_of_objects_string = f"(repeat {object_string} {n_columns} {x_shift})"
        row_of_rows_string = f"(repeat {row_of_objects_string} {n_rows} {y_shift})"

        # Shift the whole thing into the right location.
        # TBD.
        return peval(row_of_rows_string), row_of_rows_string
