"""
wheels_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that produce gadget tasks with wheels on them.
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

from tasksgenerator.bases_parts_tasks_generator import *

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


@TasksGeneratorRegistry.register
class WheeledVehiclesTasksGenerator(AbstractBasesAndPartsTasksGenerator):
    """Generates vehicle tasks consisting of a base and a set of wheels placed at positions along the base. We generate trains, cars, and buggies."""

    name = "wheeled_vehicles"

    def __init__(self):
        super().__init__()

    def _generate_truck_bases(
        self,
        head_width,
        head_height,
        body_width,
        body_height,
        nose_scale=0.5,
        reverse=False,
    ):
        """Generates 'trucks' comprised of a head (with a 'nose') and a body. Trucks can face left or right."""

        n_segments = 3

        heights = [body_height, head_height, head_height * nose_scale]
        widths = [body_width, head_width, head_width * nose_scale]

        if reverse:
            heights.reverse()
            widths.reverse()

        return self._generate_basic_n_segment_bases(
            primitives=[RECTANGLE] * n_segments,
            heights=heights,
            widths=widths,
            float_locations=[FLOAT_TOP] * n_segments,
            right_margins=[0] * n_segments,
        )

    def _generate_train_bases():
        """Generates 'trains' comprised of a tail, one or more train segments, and a head. Trains can optionally also have windows on each car."""
        # Trains have windows.
        pass

    def _generate_buggy_bases():
        """Generates 'buggies' consisting of one or more tiers of cars and an antenna."""
        pass

    def _generate_paired_wheels():
        pass

    def _generate_row_of_wheels():
        pass
