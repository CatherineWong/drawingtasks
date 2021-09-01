"""
furniture_tasks_generator.py | Author: Yoni Friedman and Catherine Wong
Defines TasksGenerators that produce tasks for furniture drawings.
"""
import math, random, itertools, copy

from numpy.core.fromnumeric import repeat
import primitives.object_primitives as object_primitives
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
    """Generates furniture tasks."""

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

    def _generate_drawers_iterator(
        self,
        n_drawers=1,
        base_heights_and_widths=[
            (SMALL * 3, MEDIUM * 9),
            (SMALL * 4, SMALL * 9),
            (SMALL * 5, SMALL * 12),
        ],
        stack_float_locations=FLOAT_CENTER,
        generation_probability=1.0,
    ):
        # Generates strokes for drawers with and without drawer pulls. Returns strokes at the center.
        for (base_height, base_width) in base_heights_and_widths:
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
            drawn_blank = False
            for n_drawer_pulls in [0, 2]:
                for (
                    drawer_pull_strokes,
                    drawer_pull_strokes_min_x,
                    drawer_pull_strokes_max_x,
                    drawer_pull_strokes_min_y,
                    drawer_pull_strokes_max_y,
                ) in self._generate_drawer_pulls_iterator(
                    min_x=base_min_x + (base_width * QUARTER_SCALE),
                    max_x=base_max_x - (base_width * QUARTER_SCALE),
                    n_drawer_pulls=n_drawer_pulls,
                    float_location=FLOAT_CENTER,
                    drawer_pull_scale=SCALE_UNIT,
                ):
                    drawer_spacing = base_height * QUARTER_SCALE
                    if drawer_pull_strokes_max_y >= (
                        base_max_y - (drawer_spacing)
                    ) or drawer_pull_strokes_max_x >= (base_max_x - (drawer_spacing)):
                        continue

                    if n_drawer_pulls < 1 and drawn_blank:
                        continue

                    drawer_strokes = [base_strokes[0] + drawer_pull_strokes[0]]

                    if n_drawer_pulls < 1:
                        drawn_blank = True

                    # Draw the grid of drawers.
                    total_height = (n_drawers - 1) * (base_height + drawer_spacing)
                    if stack_float_locations == FLOAT_CENTER:
                        min_y, max_y = (
                            -total_height * 0.5,
                            total_height * 0.5,
                        )
                    elif stack_float_locations == FLOAT_TOP:
                        min_y, max_y = drawer_spacing, total_height + drawer_spacing
                    else:
                        min_y, max_y = -total_height - drawer_spacing, -drawer_spacing

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
                        min_y=min_y,
                        max_y=max_y,
                        n_rows=n_drawers,
                        n_columns=1,
                        float_location=stack_float_locations,
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
                        float_locations=[stack_float_locations],
                    )
                    drawer_strokes = [drawer_stack_strokes[0] + enclosure_strokes[0]]

                    if random.uniform(0, 1) > generation_probability:
                        continue

                    yield (
                        drawer_strokes,
                        enclosure_min_x,
                        enclosure_max_x,
                        enclosure_min_y,
                        enclosure_max_y,
                    )

    def _generate_feet_iterator(
        self,
        n_feet,
        min_x,
        max_x,
        min_y,
        max_y,
        feet_heights=[SMALL, MEDIUM * 2, MEDIUM * 4],
        generation_probability=1.0,
    ):
        short_v_line = T(short_hline, theta=math.pi / 2)
        # Adds a row of feet to the object. These can be short or tall.
        for foot_primitive in [RECTANGLE, LINE]:
            for foot_height in feet_heights:
                if foot_primitive == RECTANGLE:
                    foot_width = SMALL
                    foot = object_primitives.rectangle(
                        height=foot_height, width=foot_width
                    )
                    if n_feet > 2:
                        continue
                else:
                    foot_width = 0
                    foot = T(short_v_line, s=foot_height)
                (
                    feet_strokes,
                    feet_strokes_min_x,
                    feet_strokes_max_x,
                    feet_strokes_min_y,
                    feet_strokes_max_y,
                ) = self._generate_n_objects_on_grid_x_y_limits(
                    object=foot,
                    object_center=(0, 0),
                    object_height=foot_height,
                    object_width=foot_width if foot_width > 0 else 1,
                    min_x=min_x + (foot_width * 0.5),
                    max_x=max_x - (foot_width * 0.5),
                    min_y=min_y,
                    max_y=min_y,
                    n_rows=1,
                    n_columns=n_feet,
                    float_location=FLOAT_BOTTOM,
                    grid_indices=range(n_feet),
                )
                if random.uniform(0, 1) > generation_probability:
                    continue
                yield feet_strokes

    def _generate_stacked_drawers_stimuli(
        self, total_drawers=4, train_ratio=1.0, generation_probability=1.0
    ):
        stimuli_strokes = []
        # Draw stacked bookshelves with no legs.
        for n_drawers in range(2, total_drawers + 1):
            for (
                drawer_strokes,
                enclosure_min_x,
                enclosure_max_x,
                enclosure_min_y,
                enclosure_max_y,
            ) in self._generate_drawers_iterator(
                n_drawers=n_drawers,
                generation_probability=generation_probability,
            ):
                if drawer_strokes:
                    stimuli_strokes += drawer_strokes

        # Draw short drawers with long legs.
        max_short_drawers = 2
        for n_drawers in range(1, max_short_drawers + 1):
            base_heights_and_widths = [
                (SMALL * 3, MEDIUM * 9),
            ]
            for (
                enclosure_strokes,
                enclosure_min_x,
                enclosure_max_x,
                enclosure_min_y,
                enclosure_max_y,
            ) in self._generate_drawers_iterator(
                n_drawers=n_drawers,
                base_heights_and_widths=base_heights_and_widths,
                stack_float_locations=FLOAT_TOP,
                generation_probability=generation_probability,
            ):
                if drawer_strokes:
                    for n_feet in [2, 3, 4]:
                        for feet_strokes in self._generate_feet_iterator(
                            n_feet=n_feet,
                            min_x=enclosure_min_x,
                            max_x=enclosure_max_x,
                            min_y=enclosure_min_y,
                            max_y=enclosure_max_y,
                            feet_heights=[SMALL, MEDIUM * 2, MEDIUM * 4],
                            generation_probability=generation_probability,
                        ):
                            drawer_strokes = [enclosure_strokes[0] + feet_strokes[0]]
                            stimuli_strokes += drawer_strokes

        # Shuffle before returning.
        random.shuffle(stimuli_strokes)
        return random_sample_ratio_ordered_array(stimuli_strokes, train_ratio)

    def _generate_lounges_stimuli(self, train_ratio=1.0, generation_probability=1.0):
        # Generates lounges containing a large base and one or more rectangular pillows on top. Lounges may or may not have an inset drawer.
        # Grab the drawer stack enclosure and add pillows, etc.
        stimuli_strokes = []
        # Draw short drawers with long legs.
        base_heights_and_widths = [
            (SMALL * 3, MEDIUM * 9),
            (SMALL * 3, MEDIUM * 10),
        ]
        for (
            enclosure_strokes,
            enclosure_min_x,
            enclosure_max_x,
            enclosure_min_y,
            enclosure_max_y,
        ) in self._generate_drawers_iterator(
            n_drawers=1,
            base_heights_and_widths=base_heights_and_widths,
            stack_float_locations=FLOAT_BOTTOM,
            generation_probability=1.0,
        ):
            enclosure_width = enclosure_max_x - enclosure_min_x
            if enclosure_strokes:
                # Now add pillows.
                all_seat_back_primitives = [
                    [CIRCLE, CIRCLE, []],
                    [RECTANGLE, [], RECTANGLE],
                    [RECTANGLE, CIRCLE, [], RECTANGLE],
                ]
                for seat_back_primitives in all_seat_back_primitives:
                    for base_height in [MEDIUM, MEDIUM * 2]:
                        n_segments = len(seat_back_primitives)
                        shape_heights = [base_height] * n_segments

                        def get_width(shape, base_height):
                            if type(shape) == type([]):
                                return 0
                            elif shape == RECTANGLE:
                                return base_height * 0.5
                            else:
                                return base_height

                        shape_widths = [
                            get_width(shape, base_height)
                            for shape in seat_back_primitives
                        ]

                        seat_spacer_width = enclosure_width - np.sum(shape_widths)

                        shape_widths = [
                            w if w > 0 else seat_spacer_width for w in shape_widths
                        ]

                        (
                            seat_back_strokes,
                            _,
                            _,
                            _,
                            _,
                        ) = self._generate_basic_n_segment_bases(
                            primitives=seat_back_primitives,
                            heights=shape_heights,
                            widths=shape_widths,
                            float_locations=[FLOAT_TOP for x in range(n_segments)],
                            right_margins=[0 for x in range(n_segments)],
                        )

                        for n_feet in [2, 3, 4]:
                            for feet_strokes in self._generate_feet_iterator(
                                n_feet=n_feet,
                                min_x=enclosure_min_x,
                                max_x=enclosure_max_x,
                                min_y=enclosure_min_y,
                                max_y=enclosure_max_y,
                                feet_heights=[SMALL, MEDIUM * 2],
                                generation_probability=1.0,
                            ):
                                drawer_strokes = [
                                    seat_back_strokes[0]
                                    + enclosure_strokes[0]
                                    + feet_strokes[0]
                                ]
                                if random.uniform(0, 1) > generation_probability:
                                    continue

                                stimuli_strokes += drawer_strokes

        # Shuffle before returning.
        random.shuffle(stimuli_strokes)
        return random_sample_ratio_ordered_array(stimuli_strokes, train_ratio)

    def _generate_seat_drawers_stimuli(self):
        # Generates seats with a drawer and one or more pillows to the side.
        # Grab the drawer stack enclosure and add pillows, etc.
        pass
