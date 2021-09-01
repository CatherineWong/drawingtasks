"""
wheels_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that produce gadget tasks with wheels on them.
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
    random_sample_ratio_ordered_array,
)

from tasksgenerator.bases_parts_tasks_generator import *
from tasksgenerator.dial_tasks_generator import *

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

    name = "wheels"

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

    def _generate_train_bases(
        self,
        caboose_primitives,
        caboose_heights,
        caboose_widths,
        caboose_floats,
        reflect_caboose_for_head,
        body_primitives,
        body_heights,
        body_widths,
        body_floats,
        body_repetitions,
        car_margins,
        show_doors=False,
    ):
        """Generates 'trains' comprised of a caboose at each end and one or more repeated body segments.
        reflect_caboose_for_head: we reverse the order of the head.
        car_margins: scalar value for spacing.
        """
        head_primitives, head_heights, head_widths, head_floats = (
            copy.deepcopy(caboose_primitives),
            copy.deepcopy(caboose_heights),
            copy.deepcopy(caboose_widths),
            copy.deepcopy(caboose_floats),
        )
        if reflect_caboose_for_head:
            head_primitives.reverse()
            head_heights.reverse()
            head_widths.reverse()
            head_floats.reverse()

        n_segments = 2 * len(caboose_primitives) + body_repetitions * len(
            body_primitives
        )

        # Tricky: we only want spacing between the cars, not between the segments of the body.
        caboose_margin = [0] * (len(caboose_primitives) - 1) + [car_margins]
        body_margin = ([0] * (len(body_primitives) - 1)) + [
            car_margins
        ] * body_repetitions
        head_margin = [0] * len(caboose_primitives)

        (strokes, min_x, max_x, min_y, max_y,) = self._generate_basic_n_segment_bases(
            primitives=caboose_primitives
            + body_primitives * body_repetitions
            + head_primitives,
            heights=caboose_heights + body_heights * body_repetitions + head_heights,
            widths=caboose_widths + body_widths * body_repetitions + head_widths,
            float_locations=caboose_floats
            + body_floats * body_repetitions
            + head_floats,
            right_margins=caboose_margin + body_margin + head_margin,
        )

        if show_doors:
            window = T(object_primitives._rectangle, s=(MEDIUM))
            n_windows = 2 * body_repetitions
            (new_strokes, _, _, _, _,) = self._generate_n_objects_on_grid_x_y_limits(
                object=window,
                object_center=(0, 0),
                object_height=1,
                object_width=1,
                min_x=-body_widths[0] * body_repetitions * 0.5 + MEDIUM,
                max_x=body_widths[0] * body_repetitions * 0.5 - MEDIUM,
                min_y=body_heights[0] * 0.5,
                max_y=body_heights[0] * 0.5,
                n_rows=1,
                n_columns=n_windows,
                float_location=FLOAT_CENTER,
                grid_indices=range(n_windows),
            )
            strokes = [strokes[0] + new_strokes[0]]

        return strokes, min_x, max_x, min_y, max_y

    def _generate_buggy_bases(
        self,
        tier_heights,
        tier_widths,
        nose_tail_heights=[0],
        nose_tail_widths=[0],
        antenna=None,
        antenna_height=None,
        n_windows=0,
    ):
        """Generates 'buggies' consisting of one or more tiers of cars and an optional antenna and windows."""
        nose_tail_primitives = [RECTANGLE]
        if nose_tail_heights[0] <= 0:
            nose_tail_primitives, nose_tail_heights, nose_tail_widths = [], [], []
        # First tier is a base.
        base_primitives = nose_tail_primitives + [RECTANGLE] + nose_tail_primitives
        base_heights = nose_tail_heights + [tier_heights[0]] + nose_tail_heights
        base_widths = nose_tail_widths + [tier_widths[0]] + nose_tail_widths
        base_float_locations = [FLOAT_TOP] * len(base_primitives)
        base_right_margins = [0] * len(base_primitives)
        (strokes, min_x, max_x, min_y, max_y,) = self._generate_basic_n_segment_bases(
            primitives=base_primitives,
            heights=base_heights,
            widths=base_widths,
            float_locations=base_float_locations,
            right_margins=base_right_margins,
        )
        # Add additional tiers.
        if len(tier_heights) > 1:
            for tier_height, tier_width in zip(tier_heights[1:], tier_widths[1:]):
                object = object_primitives.rectangle(
                    width=tier_width, height=tier_height
                )
                (
                    new_strokes,
                    new_min_x,
                    new_max_x,
                    new_min_y,
                    new_max_y,
                ) = self._generate_object_on_location(
                    object=object,
                    object_center=(0, 0),
                    object_height=tier_height,
                    object_width=tier_width,
                    location=(0, max_y),
                    float_location=FLOAT_TOP,
                    x_margin=0,
                    y_margin=0,
                )
                max_y += tier_height
                strokes = [strokes[0] + new_strokes[0]]
                min_x, max_x = min(min_x, new_min_x), max(new_max_x, max_x)
        # Add optional windows.
        if n_windows > 0:
            window = T(object_primitives._rectangle, s=(MEDIUM))
            (new_strokes, _, _, _, _,) = self._generate_n_objects_on_grid_x_y_limits(
                object=window,
                object_center=(0, 0),
                object_height=1,
                object_width=1,
                min_x=-tier_widths[0] * 0.5 * THREE_QUARTER_SCALE,
                max_x=tier_widths[0] * 0.5 * THREE_QUARTER_SCALE,
                min_y=tier_heights[0] * 0.5,
                max_y=tier_heights[0] * 0.5,
                n_rows=1,
                n_columns=n_windows,
                float_location=FLOAT_CENTER,
                grid_indices=range(n_windows),
            )
            strokes = [strokes[0] + new_strokes[0]]

        # Add optional antenna.
        if antenna is not None:
            (
                new_strokes,
                new_min_x,
                new_max_x,
                new_min_y,
                new_max_y,
            ) = self._generate_object_on_location(
                object=antenna,
                object_center=(0, 0),
                object_height=antenna_height,
                object_width=1,
                location=(0, max_y),
                float_location=FLOAT_TOP,
                x_margin=0,
                y_margin=0,
            )
            max_y += antenna_height
            strokes = [strokes[0] + new_strokes[0]]
            min_x, max_x = min(min_x, new_min_x), max(new_max_x, max_x)

        return strokes, min_x, max_x, min_y, max_y

    def _generate_row_of_wheels(
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
        """Generates a row of wheels floated below the central axis."""
        dialgenerator = SimpleDialTasksGenerator()
        base_wheel, wheel_height = dialgenerator._generate_perforated_shapes(
            outer_shapes=outer_shapes,
            outer_shapes_min_size=outer_shapes_min_size * wheel_scale,
            inner_shapes=inner_shapes,
            inner_shapes_max_size=inner_shapes_max_size * wheel_scale,
            nesting_scale_unit=0.5,
            decorator_shape=object_primitives._circle,
            n_decorators=n_decorators,
            n_spokes=n_spokes,
            spoke_angle=np.pi,
            spoke_length=outer_shapes_min_size * 0.5 * wheel_scale,
        )

        grid_indices = (
            range(n_wheels)
            if not paired_wheels
            else [x for x in range(int(n_wheels / 2))]
            + list(range(n_wheels * 2))[-int(n_wheels / 2) :]
        )
        return self._generate_n_objects_on_grid_x_y_limits(
            object=base_wheel[0],
            object_center=(0, 0),
            object_height=wheel_height,
            object_width=wheel_height,
            min_x=min_x + wheel_height * 0.5,
            max_x=max_x - wheel_height * 0.5,
            min_y=0,
            max_y=0,
            n_rows=1,
            n_columns=n_wheels if not paired_wheels else n_wheels * 2,
            float_location=float_location,
            grid_indices=grid_indices,
        )

    def _generate_wheels_iterator(
        self,
        min_x,
        max_x,
        n_wheels,
        paired_wheels=False,
        float_location=FLOAT_BOTTOM,
        wheel_scale=1.0,
    ):
        c = object_primitives._circle
        r = object_primitives._rectangle
        for outer_shapes in [[c], [c, c]]:
            for outer_shapes_min_size in [MEDIUM * MEDIUM]:
                for inner_shapes in [[c], [r]]:
                    for inner_shapes_max_size in [SMALL * SCALE_UNIT]:
                        for n_decorators in [4, 8]:
                            yield self._generate_row_of_wheels(
                                outer_shapes=outer_shapes,
                                outer_shapes_min_size=outer_shapes_min_size,
                                inner_shapes=inner_shapes,
                                inner_shapes_max_size=inner_shapes_max_size,
                                n_decorators=n_decorators,
                                n_spokes=0,
                                min_x=min_x,
                                max_x=max_x,
                                paired_wheels=paired_wheels,
                                n_wheels=n_wheels,
                                float_location=float_location,
                                wheel_scale=wheel_scale,
                            )

    def _generate_parts_stimuli(self, train_ratio=1.0):
        all_parts_stimuli = []
        # Generate wheels.
        n_wheels_types = [1, 4]
        for n_wheels in n_wheels_types:
            wheels_iterator = self._generate_wheels_iterator(
                -LARGE * 4,
                LARGE * 4,
                n_wheels=n_wheels,
                float_location=FLOAT_CENTER,
                paired_wheels=False,
            )
            for (
                wheels_strokes,
                wheels_min_x,
                wheels_max_x,
                wheels_min_y,
                wheels_max_y,
            ) in wheels_iterator:
                all_parts_stimuli += wheels_strokes
        for scale_wires in [True, False]:
            antenna_generator = antenna_tasks_generator.SimpleAntennaTasksGenerator()
            n_wires = 3
            antenna_object = antenna_generator._generate_stacked_antenna(
                n_wires=n_wires,
                scale_wires=scale_wires,
                end_shape=None,
            )
            all_parts_stimuli += antenna_object
        return random_sample_ratio_ordered_array(all_parts_stimuli, train_ratio)

    def _generate_truck_stimuli(self, train_ratio=1.0):
        big_width = LARGE * 8
        all_truck_stimuli = []
        for head_width in [LARGE]:
            for head_height in [LARGE * 2]:
                for body_width, body_height in [
                    (LARGE * 8, LARGE * 4),
                    (LARGE * 10, LARGE * 3),
                ]:
                    reverse = False
                    nose_scale = THREE_QUARTER_SCALE
                    (
                        base_strokes,
                        base_min_x,
                        base_max_x,
                        base_min_y,
                        base_max_y,
                    ) = self._generate_truck_bases(
                        head_width=head_width,
                        head_height=body_height * THREE_QUARTER_SCALE,
                        body_width=body_width,
                        body_height=body_height,
                        nose_scale=nose_scale,
                        reverse=reverse,
                    )
                    n_wheels_types = [2, 4]
                    for n_wheels in n_wheels_types:
                        wheels_iterator = self._generate_wheels_iterator(
                            base_min_x,
                            base_max_x,
                            n_wheels=n_wheels,
                            float_location=FLOAT_CENTER,
                            paired_wheels=True,
                        )
                        for (
                            wheels_strokes,
                            wheels_min_x,
                            wheels_max_x,
                            wheels_min_y,
                            wheels_max_y,
                        ) in wheels_iterator:
                            truck_strokes = [base_strokes[0] + wheels_strokes[0]]
                            all_truck_stimuli += truck_strokes
        return random_sample_ratio_ordered_array(all_truck_stimuli, train_ratio)

    def _generate_train_stimuli(self, train_ratio=1.0):
        all_train_stimuli = []

        body_height = SMALL * 5
        caboose_width = MEDIUM
        caboose_height = body_height * THREE_QUARTER_SCALE
        caboose_primitives, caboose_heights, caboose_widths, caboose_floats = (
            [
                RECTANGLE,
            ],
            [caboose_height],
            [caboose_width],
            [
                FLOAT_TOP,
            ],
        )

        small_width, large_width = SMALL * 7, SMALL * 9
        for body_heights in [body_height]:
            for body_widths in [small_width, large_width]:
                body_repetitions = [2] if body_widths > small_width else [2, 3]
                for body_repetitions in body_repetitions:
                    for car_margins in [QUARTER_SCALE]:
                        for show_doors in [True, False]:
                            (
                                base_strokes,
                                base_min_x,
                                base_max_x,
                                base_min_y,
                                base_max_y,
                            ) = self._generate_train_bases(
                                caboose_primitives=caboose_primitives,
                                caboose_heights=caboose_heights,
                                caboose_widths=caboose_widths,
                                caboose_floats=caboose_floats,
                                reflect_caboose_for_head=True,
                                body_primitives=[RECTANGLE],
                                body_heights=[body_heights],
                                body_widths=[body_widths],
                                body_floats=[FLOAT_TOP],
                                body_repetitions=body_repetitions,
                                car_margins=car_margins,
                                show_doors=show_doors,
                            )
                            n_wheels_types = [
                                body_repetitions * 2,
                                body_repetitions * 3,
                            ]
                            for n_wheels in n_wheels_types:
                                wheels_iterator = self._generate_wheels_iterator(
                                    base_min_x,
                                    base_max_x,
                                    n_wheels=n_wheels,
                                    float_location=FLOAT_CENTER,
                                    wheel_scale=THREE_QUARTER_SCALE,
                                )
                                for (
                                    wheels_strokes,
                                    wheels_min_x,
                                    wheels_max_x,
                                    wheels_min_y,
                                    wheels_max_y,
                                ) in wheels_iterator:
                                    train_strokes = [
                                        base_strokes[0] + wheels_strokes[0]
                                    ]
                                    all_train_stimuli += train_strokes
        return random_sample_ratio_ordered_array(all_train_stimuli, train_ratio)

    def _generate_buggy_stimuli(self, train_ratio=1.0, generation_probability=0.80):

        buggy_stimuli = []
        for scale_wires in [True, False]:
            antenna_generator = antenna_tasks_generator.SimpleAntennaTasksGenerator()
            n_wires = 3
            antenna_object = antenna_generator._generate_stacked_antenna(
                n_wires=n_wires,
                scale_wires=scale_wires,
                end_shape=None,
            )[0]
            antenna_height = antenna_tasks_generator.ANTENNA_BASE_HEIGHT + (
                antenna_tasks_generator.ANTENNA_SMALL * (n_wires - 1)
            )

            for first_tier_height, second_tier_height in [
                (MEDIUM * 3, SMALL),
            ]:
                small_width = LARGE * 7
                for first_tier_width in [LARGE * n for n in [5, 8]]:
                    for nose_tail_heights, nose_tail_widths in [
                        (0, 0),
                        (
                            first_tier_height * THREE_QUARTER_SCALE,
                            LARGE,
                        ),
                    ]:
                        for antenna in [antenna_object, None]:
                            n_wheel_sets = (
                                [2] if first_tier_width <= small_width else [2, 6]
                            )
                            for n_wheels in n_wheel_sets:
                                (
                                    base_strokes,
                                    base_min_x,
                                    base_max_x,
                                    base_min_y,
                                    base_max_y,
                                ) = self._generate_buggy_bases(
                                    tier_heights=[
                                        first_tier_height,
                                        second_tier_height,
                                    ],
                                    tier_widths=[
                                        first_tier_width,
                                        first_tier_width * THREE_QUARTER_SCALE,
                                    ],
                                    nose_tail_heights=[nose_tail_heights],
                                    nose_tail_widths=[nose_tail_widths],
                                    antenna=antenna,
                                    antenna_height=antenna_height,
                                    n_windows=0,
                                )
                                wheels_iterator = self._generate_wheels_iterator(
                                    base_min_x + nose_tail_widths,
                                    base_max_x - nose_tail_widths,
                                    n_wheels=n_wheels,
                                    float_location=FLOAT_CENTER,
                                )
                                for (
                                    wheels_strokes,
                                    wheels_min_x,
                                    wheels_max_x,
                                    wheels_min_y,
                                    wheels_max_y,
                                ) in wheels_iterator:
                                    buggy_strokes = [
                                        base_strokes[0] + wheels_strokes[0]
                                    ]
                                    if random.uniform(0, 1) > generation_probability:
                                        continue
                                    buggy_stimuli += buggy_strokes

        return random_sample_ratio_ordered_array(buggy_stimuli, train_ratio)

    def _generate_strokes_for_stimuli(
        self,
        train_ratio=0.8,
        generation_probability=1.0,  # Probabilistically generate from space
    ):
        """Main generator function. Returns a list of all stimuli from this generative model as sets of strokes."""
        train, test = [], []
        for generator_fn in [
            self._generate_parts_stimuli,
            self._generate_truck_stimuli,
            self._generate_train_stimuli,
            self._generate_buggy_stimuli,
        ]:
            generator_train, generator_test = generator_fn(train_ratio)
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
            curriculum_id=human_readable,
            task_generator_name=self.name,
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
