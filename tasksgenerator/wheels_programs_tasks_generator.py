"""
wheels_programs_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that produce gadget tasks with wheels on them.
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
from tasksgenerator.abstract_bases_parts_programs_tasks_generator import *

from tasksgenerator.s12_s13_tasks_generator import RANDOM_SEED
from tasksgenerator.nuts_bolts_programs_tasks_generator import *


@TasksGeneratorRegistry.register
class WheelsProgramsTasksGenerator(AbstractBasesAndPartsProgramsTasksGenerator):
    name = "wheels_programs"

    def __init__(self):
        super().__init__(grammar=constants + some_none + objects + transformations)

    def _generate_row_of_wheels_strings(
        self,
        outer_shapes,
        outer_shapes_min_size,
        inner_shapes,
        inner_shapes_max_size,
        n_decorators,
        n_spokes,
        min_x,
        max_x,
        paired_wheels,
        n_wheels,
        wheel_scale=1.0,
        float_location=FLOAT_BOTTOM,
    ):
        nuts_bolts_generator = NutsBoltsProgramsTasksGenerator()
        (
            base_wheel,
            base_wheel_string,
            wheel_height,
            wheel_height_string,
        ) = nuts_bolts_generator._generate_perforated_shapes_string(
            outer_shapes=outer_shapes,
            outer_shapes_min_size=f"(* {outer_shapes_min_size} {wheel_scale})",
            inner_shapes=inner_shapes,
            inner_shapes_max_size=f"(* {inner_shapes_max_size} {wheel_scale})",
            nesting_scale_unit=str(SCALE_UNIT),
            decorator_shape=c_string,
            n_decorators=str(n_decorators),
            n_spokes=n_spokes,  # This is never used.
            spoke_angle=np.pi,  # This is never used.
            spoke_length=outer_shapes_min_size
            * 0.5
            * wheel_scale,  # This is never used.
        )

        # TODO: implement paired wheels.
        min_x = f"(+ {min_x} (* 0.5 {wheel_height})"
        max_x = f"(- {max_x} (* 0.5 {wheel_height})"
        return self._generate_n_objects_on_grid_x_y_limits_string(
            object=base_wheel[0],
            object_string=base_wheel_string,
            object_center=(STR_ZERO, STR_ZERO),
            object_height=wheel_height,
            object_width=wheel_height,
            min_x=min_x,
            max_x=max_x,
            min_y=STR_ZERO,
            max_y=STR_ZERO,
            n_rows=1,
            n_columns=n_wheels if not paired_wheels else n_wheels * 2,
            float_location=float_location,
        )
