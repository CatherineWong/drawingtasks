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
        for outer_shapes in [[cc], [cc, cc], [r], [octagon], []]:
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

    def _generate_drawers_iterator(self, n_drawers, draw_feet=False):
        # Generate the base drawers.
        for (base_height, base_width) in [
            (SMALL * 3, MEDIUM * 9),
            (SMALL * 4, SMALL * 9),
            (SMALL * 5, SMALL * 12),
        ]:
            if base_height > SMALL * 4 and n_drawers > 3:
                continue

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
                drawer_spacing = base_height * QUARTER_SCALE
                if drawer_pull_strokes_max_y >= (
                    base_max_y - (drawer_spacing)
                ) or drawer_pull_strokes_max_x >= (base_max_x - (drawer_spacing)):
                    continue

                drawer_strokes = [base_strokes[0] + drawer_pull_strokes[0]]

                # Draw the grid of drawers.
                total_height = (n_drawers - 1) * (base_height + drawer_spacing)
                (
                    drawer_stack_strokes,
                    drawer_stack_strokes_min_x,
                    drawer_stack_strokes_max_x,
                    drawer_stack_strokes_min_y,
                    drawer_stack_strokes_max_y,
                ) = self._generate_n_objects_on_grid_x_y_limits(
                    object=drawer_strokes[0],
                    object_center=(0, 0),
                    object_height=base_height,
                    object_width=base_width,
                    min_x=0,
                    max_x=0,
                    min_y=-total_height * 0.5,
                    max_y=total_height * 0.5,
                    n_rows=n_drawers,
                    n_columns=1,
                    float_location=FLOAT_CENTER,
                    grid_indices=range(n_drawers * n_drawers),
                )
                # Draw the enclosing around them.
                total_height = (n_drawers * base_height) + (
                    (n_drawers + 1) * drawer_spacing
                )
                enclosure_width = base_width + (2 * drawer_spacing)
                (
                    enclosure_strokes,
                    enclosure_min_x,
                    enclosure_max_x,
                    enclosure_min_y,
                    enclosure_max_y,
                ) = self._generate_basic_n_segment_bases(
                    primitives=[RECTANGLE],
                    heights=[total_height],
                    widths=[enclosure_width],
                    float_locations=[FLOAT_CENTER],
                )
                drawer_strokes = [drawer_stack_strokes[0] + enclosure_strokes[0]]

                # Draw feet.
                if draw_feet:
                    foot_size = SMALL
                    foot = object_primitives.rectangle(
                        height=foot_size, width=foot_size
                    )
                    (
                        feet_strokes,
                        feet_strokes_min_x,
                        feet_strokes_max_x,
                        feet_strokes_min_y,
                        feet_strokes_max_y,
                    ) = self._generate_n_objects_on_grid_x_y_limits(
                        object=foot,
                        object_center=(0, 0),
                        object_height=foot_size,
                        object_width=foot_size,
                        min_x=enclosure_min_x + (foot_size * 0.5),
                        max_x=enclosure_max_x - (foot_size * 0.5),
                        min_y=enclosure_min_y,
                        max_y=enclosure_min_y,
                        n_rows=1,
                        n_columns=2,
                        float_location=FLOAT_BOTTOM,
                        grid_indices=range(2),
                    )
                    drawer_strokes = [drawer_strokes[0] + feet_strokes[0]]

                yield drawer_strokes

    def _generate_drawer_stimuli(self, total_drawers=4):
        stimuli_strokes = []
        for n_drawers in range(1, total_drawers + 1):
            for draw_feet in [True, False]:
                for drawer_strokes in self._generate_drawers_iterator(
                    n_drawers=n_drawers, draw_feet=draw_feet
                ):
                    stimuli_strokes += drawer_strokes
        return stimuli_strokes

    def _generate_strokes_for_stimuli(
        self, generation_probability=1.0,  # Probabilistically generate from space
    ):
        """Main generator function. Returns a list of all stimuli from this generative model as sets of strokes."""
        all_drawer_stimuli = self._generate_drawer_stimuli()
        ## You can add other functions here for chairs, etc.

        all_stimuli = all_drawer_stimuli

        return all_stimuli

    def _generate_seat_back(
        self, n_segments, segment_shapes, segment_heights, segment_widths
    ):
        if len(segment_shapes) < n_segments:
            repeat_shape = segment_shapes[0]
            segment_shapes = [repeat_shape for x in range(n_segments)]

        if len(segment_heights) < n_segments:
            repeat_height = segment_heights[0]
            segment_heights = [repeat_height for x in range(n_segments)]

        if len(segment_widths) < n_segments:
            repeat_width = segment_widths[0]
            segment_widths = [repeat_width for x in range(n_segments)]

        return self._generate_basic_n_segment_bases(
            primitives=segment_shapes,
            heights=segment_heights,
            widths=segment_widths,
            float_locations=[FLOAT_BOTTOM],
        )

    def _generate_seat_back_permutations(self, seat_width):
        all_strokes = []
        n_segments = [1, 3, 5]
        heights = [SMALL, MEDIUM, LARGE]

        for n in n_segments:
            for primitive in [RECTANGLE, CIRCLE]:
                segment_width = seat_width / n
                for height in heights:
                    (
                        base_strokes,
                        base_min_x,
                        base_max_x,
                        base_min_y,
                        base_max_y,
                    ) = self._generate_seat_back(
                        n, [primitive], [height], [segment_width]
                    )
                    all_strokes += base_strokes

        return all_strokes

    def _generate_seats(self):
        all_strokes = []
        seat_base_widths = [SMALL, MEDIUM, LARGE]
        seat_base_heights = [SMALL, MEDIUM]

        for height in seat_base_heights:
            for width in seat_base_widths:
                (
                    seat_base_strokes,
                    min_x,
                    max_x,
                    min_y,
                    max_y,
                ) = self._generate_basic_n_segment_bases(
                    [RECTANGLE],
                    heights=[height],
                    widths=[width],
                    float_locations=[FLOAT_CENTER],
                )

                seat_backs = self._generate_seat_back_permutations(width)

                for seat_back in seat_backs:
                    chair = seat_base_strokes + seat_back

