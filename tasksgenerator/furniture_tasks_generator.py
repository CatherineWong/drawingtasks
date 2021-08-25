"""
furniture_tasks_generator.py | Author: Yoni Friedman and Catherine Wong
Defines TasksGenerators that produce tasks for furniture drawings.
"""
import math, random, itertools, copy
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
from tasksgenerator.dial_tasks_generator import *
from tasksgenerator.wheels_tasks_generator import *

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


cc = T(object_primitives._circle, s=2)  # Double scaled circle
octagon = T(object_primitives.polygon(n=8), s=THREE_QUARTER_SCALE)


@TasksGeneratorRegistry.register
class FurnitureTasksGenerator(AbstractBasesAndPartsTasksGenerator):
    """Generates furniture tasks. We generate bookshelves/drawers and tables/benches/seats."""

    name = "furniture"

    def __init__(self):
        super().__init__()

    def _generate_drawer_pulls_iterator(
        self,
        min_x,
        max_x,
        n_drawer_pulls,
        float_location=FLOAT_CENTER,
        drawer_pull_scale=SCALE_UNIT,
    ):
        wheels_generator = WheeledVehiclesTasksGenerator()

        base_min_size = MEDIUM * MEDIUM
        c = object_primitives._circle
        r = object_primitives._rectangle
        for outer_shapes in [[cc], [cc, cc], [r], [octagon]]:
            for outer_shapes_min_size in [base_min_size]:
                for inner_shapes in [[c], [r]]:
                    for inner_shapes_max_size in [base_min_size * THREE_QUARTER_SCALE]:
                        for n_decorators in [0]:
                            if outer_shapes + inner_shapes == [r, r]:
                                continue
                            # Row of wheels is very similar to a set of drawer pulls.
                            yield wheels_generator._generate_row_of_wheels(
                                outer_shapes=outer_shapes,
                                outer_shapes_min_size=outer_shapes_min_size,
                                inner_shapes=inner_shapes,
                                inner_shapes_max_size=inner_shapes_max_size,
                                n_decorators=n_decorators,
                                n_spokes=0,
                                min_x=min_x,
                                max_x=max_x,
                                paired_wheels=False,
                                n_wheels=n_drawer_pulls,
                                float_location=float_location,
                                wheel_scale=drawer_pull_scale,
                            )

    def _generate_drawers_iterator(self, total_n_drawers):
        # Generate the base drawers.
        for (base_height, base_width) in [
            (SMALL * 5, SMALL * 12),
            (MEDIUM * 4, LARGE * 10),
        ]:
            (
                base_strokes,
                base_min_x,
                base_max_x,
                base_min_y,
                base_max_y,
            ) = self._generate_basic_n_segment_bases(
                primitives=[RECTANGLE],
                heights=[base_height],
                widths=[base_width],
                float_locations=[FLOAT_CENTER],
            )
            for (
                drawer_pull_strokes,
                drawer_pull_strokes_min_x,
                drawer_pull_strokes_max_x,
                drawer_pull_strokes_min_y,
                drawer_pull_strokes_max_y,
            ) in self._generate_drawer_pulls_iterator(
                min_x=base_min_x + (base_width * QUARTER_SCALE),
                max_x=base_max_x - (base_width * QUARTER_SCALE),
                n_drawer_pulls=2,
                float_location=FLOAT_CENTER,
                drawer_pull_scale=SCALE_UNIT,
            ):
                drawer_strokes = [base_strokes[0] + drawer_pull_strokes[0]]
                yield drawer_strokes

    def _generate_drawer_stimuli(self):
        pass
