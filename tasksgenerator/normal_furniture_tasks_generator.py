"""
normal_furniture_tasks_generator.py | Author: Yoni Friedman and Catherine Wong
Defines TasksGenerators that produce tasks for furniture drawings.
"""
import math, random, itertools, copy

import primitives.object_primitives as object_primitives
from dreamcoder_programs.grammar import Grammar
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
class NormalFurnitureTasksGenerator(AbstractBasesAndPartsTasksGenerator):
    """Generates furniture tasks. We generate bookshelves/drawers and tables/benches/seats."""

    name = "normal_furniture"

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
        self, n_drawers, draw_feet=False, generation_probability=1.0
    ):
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
                        if random.uniform(0, 1) > generation_probability:
                            continue
                        drawer_strokes = [drawer_strokes[0] + feet_strokes[0]]

                        yield drawer_strokes

    def _generate_parts_stimuli(self, train_ratio=1.0):
        all_parts_stimuli = []
        # Generate wheels.
        n_drawer_pulls = [1, 2]
        for n_pulls in n_drawer_pulls:
            for (
                drawer_pull_strokes,
                drawer_pull_strokes_min_x,
                drawer_pull_strokes_max_x,
                drawer_pull_strokes_min_y,
                drawer_pull_strokes_max_y,
            ) in self._generate_drawer_pulls_iterator(
                min_x=-LARGE * 4,
                max_x=LARGE * 4,
                n_drawer_pulls=n_pulls,
                float_location=FLOAT_CENTER,
                drawer_pull_scale=SCALE_UNIT,
            ):
                all_parts_stimuli += drawer_pull_strokes
        return random_sample_ratio_ordered_array(all_parts_stimuli, train_ratio)

    def _generate_drawer_stimuli(
        self, total_drawers=4, train_ratio=1.0, generation_probability=1.0
    ):
        stimuli_strokes = []
        for n_drawers in range(1, total_drawers + 1):
            for draw_feet in [True, False]:
                for drawer_strokes in self._generate_drawers_iterator(
                    n_drawers=n_drawers,
                    draw_feet=draw_feet,
                    generation_probability=generation_probability,
                ):
                    stimuli_strokes += drawer_strokes
        return random_sample_ratio_ordered_array(stimuli_strokes, train_ratio)

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
            float_locations=[FLOAT_TOP for x in range(n_segments)],
            right_margins=[0 for x in range(n_segments)],
        )

    def _generate_seat_back_permutations(self, seat_width):
        all_strokes = []
        n_segments = [5]
        heights = [MEDIUM, LARGE]

        # Evenly spaced bars
        for n in n_segments:
            for primitive in [RECTANGLE]:
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
                    all_strokes += [base_strokes]

        # Backs with smaller side-arms
        seat_back_primitives = [
            [[], [], []],
            [[], RECTANGLE, []],
            [RECTANGLE, [], []],
            [[], [], RECTANGLE],
            [RECTANGLE, RECTANGLE, RECTANGLE],
            [CIRCLE, RECTANGLE, CIRCLE],
            [CIRCLE, [], CIRCLE],
        ]

        for seat_back in seat_back_primitives:
            for n_side_arms in [1, 2]:
                if seat_back == [[], [], []] and n_side_arms == 2:
                    continue
                if seat_width <= MEDIUM and n_side_arms > 1:
                    continue

                if n_side_arms == 2:
                    side_arm_left = seat_back[0]
                    side_arm_right = seat_back[2]
                    central_section = seat_back[1]
                    seat_back = (
                        [side_arm_left] * 2 + [central_section] + [side_arm_right] * 2
                    )

                side_arm_widths = [seat_width / 6 for i in range(n_side_arms)]
                seat_back_widths = (
                    side_arm_widths
                    + [4 / n_side_arms * seat_width / 6]
                    + side_arm_widths
                )

                seat_back_heights = [height for i in range(n_side_arms * 2 + 1)]
                (
                    base_strokes,
                    base_min_x,
                    base_max_x,
                    base_min_y,
                    base_max_y,
                ) = self._generate_seat_back(
                    n_side_arms * 2 + 1, seat_back, seat_back_heights, seat_back_widths,
                )
                all_strokes += [base_strokes]

        return all_strokes

    def _generate_seat_stimuli(
        self, train_ratio=1.0, generation_probability=0.7, scale=2.0
    ):
        all_strokes = []
        EVEN_LARGER = LARGE * 2
        JUST_MASSIVE = LARGE * 4
        seat_base_widths = [MEDIUM, EVEN_LARGER, JUST_MASSIVE]
        seat_height = MEDIUM

        for seat_width in seat_base_widths:
            seat_backs = self._generate_seat_back_permutations(seat_width)
            (
                seat_base_strokes,
                seat_base_min_x,
                seat_base_max_x,
                seat_base_min_y,
                seat_base_max_y,
            ) = self._generate_basic_n_segment_bases(
                [RECTANGLE],
                heights=[seat_height],
                widths=[seat_width],
                float_locations=[FLOAT_BOTTOM],
            )

            for seat_back in seat_backs:
                for n_legs in [2, 3, 4]:
                    # Place Legs
                    leg_lengths = [SMALL / 2]
                    for leg_length in leg_lengths:
                        leg_primitives = [
                            T(long_vline, s=leg_length / 4),
                            object_primitives.rectangle(leg_length / 2, leg_length),
                        ]
                        for leg in leg_primitives:

                            (
                                leg_strokes,
                                leg_strokes_min_x,
                                leg_max_x,
                                leg_min_y,
                                leg_max_y,
                            ) = self._generate_n_objects_on_grid_x_y_limits(
                                object=leg,
                                object_center=(0, 0),
                                object_height=leg_length,
                                object_width=seat_width,
                                min_x=seat_base_min_x + leg_length * 0.25,
                                max_x=seat_base_max_x - leg_length * 0.25,
                                min_y=seat_base_min_y,
                                max_y=seat_base_min_y - 0.5,
                                n_rows=1,
                                n_columns=n_legs,
                                float_location=FLOAT_BOTTOM,
                                grid_indices=range(n_legs),
                            )
                            chair = T(
                                [seat_base_strokes[0] + seat_back[0] + leg_strokes[0]],
                                s=scale,
                            )
                            if random.uniform(0, 1) > generation_probability:
                                continue
                            all_strokes += chair

        return random_sample_ratio_ordered_array(all_strokes, train_ratio)

    def _generate_strokes_for_stimuli(
        self,
        train_ratio=1.0,
        generation_probability=1.0,  # Probabilistically generate from space
    ):
        """Main generator function. Returns a list of all stimuli from this generative model as sets of strokes."""
        train, test = [], []
        for generator_fn in [
            self._generate_parts_stimuli,
            self._generate_drawer_stimuli,
            self._generate_seat_stimuli,
        ]:
            generator_train, generator_test = generator_fn(train_ratio=train_ratio)
            train += generator_train
            test += generator_test

        return train, test

    def _generate_train_test_tasks(
        self,
        num_tasks_to_generate_per_condition=AbstractTasksGenerator.GENERATE_ALL,
        train_ratio=0.8,
        max_train=200,
        max_test=50,
    ):
        # Currently generates all tasks as single entities. Does not generate a curriculum.
        train_tasks, test_tasks = self._generate_drawing_tasks_from_strokes(
            num_tasks_to_generate_per_condition,
            request_type=object_primitives.tstroke,
            render_strokes_fn=object_primitives.render_stroke_arrays_to_canvas,
            task_generator_name=self.name,
            train_ratio=train_ratio,
        )
        max_train = len(train_tasks) if max_train == None else max_train
        max_test = len(test_tasks) if max_test == None else max_test
        return train_tasks[:max_train], test_tasks[:max_test]

    def generate_tasks_curriculum(
        self, num_tasks_to_generate_per_condition, train_ratio=0.8
    ):
        """:ret: a curriculum that randomly samples among the train ratio for the simple and complex stimuli."""
        (
            num_tasks_to_generate_per_condition,
            human_readable,
        ) = self._get_number_tasks_to_generate_per_condition(
            num_tasks_to_generate_per_condition, train_ratio
        )
        task_curriculum = TaskCurriculum(
            curriculum_id=human_readable, task_generator_name=self.name,
        )

        train_tasks, test_tasks = self._generate_train_test_tasks(
            num_tasks_to_generate_per_condition, train_ratio=train_ratio
        )

        # Add the train tasks.
        task_curriculum.add_tasks(
            split=TaskCurriculum.SPLIT_TRAIN,
            condition=self.name,
            curriculum_block=0,
            tasks=train_tasks,
        )

        # Add the train tasks.
        task_curriculum.add_tasks(
            split=TaskCurriculum.SPLIT_TEST,
            condition=self.name,
            curriculum_block=0,
            tasks=test_tasks,
        )
        return task_curriculum
