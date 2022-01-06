"""
dial_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that produce gadget tasks with a dial on them.
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
    random_sample_ratio_ordered_array,
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

import tasksgenerator.antenna_tasks_generator as antenna_tasks_generator

random.seed(RANDOM_SEED)

# Size constants
RECTANGLE_SHORT, RECTANGLE_MEDIUM, RECTANGLE_LARGE = 0.5, 1.25, 2.0

DIAL_NONE, DIAL_SMALL, DIAL_MEDIUM, DIAL_LARGE = 0.0, 1.0, 1.5, 2.0
DIAL_SCALE_UNIT = 0.5
DIAL_VERTICAL, DIAL_RIGHT, DIAL_LEFT = (
    math.pi / 2,
    math.pi / 4,
    math.pi - (math.pi / 4),
)
DIAL_X_MIN = -3.0

# Long vertical line
long_vline = T(object_primitives._line, theta=math.pi / 2, s=LONG_LINE_LENGTH, y=-2.0)
# Short horizontal line
short_hline = T(object_primitives._line, x=-0.5)

BASE_CENTER = 0.0
ANTENNA_DIAL_SCALE_DOWN = 0.25

MAX_ANTENNA_WIRES = 4


@TasksGeneratorRegistry.register
class SimpleDialTasksGenerator(AbstractTasksGenerator):
    """Generates gadget tasks containing a base and a set of 'dials' placed at positions along the base."""

    name = "simple_dial"

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super().__init__(
            grammar=object_primitives.constants
            + object_primitives.some_none
            + object_primitives.objects
            + object_primitives.transformations
        )

    def _generate_perforated_shapes(
        self,
        outer_shapes=[object_primitives._circle],
        outer_shapes_min_size=DIAL_LARGE,
        inner_shapes=[object_primitives._circle],
        inner_shapes_max_size=DIAL_SMALL,
        nesting_scale_unit=0.25,
        decorator_shape=object_primitives._circle,
        n_decorators=4,
        decorator_size=0.25,
        decorator_displacement=0.75,
        decorator_start_angle=np.pi / 4,
        n_spokes=0,
        spoke_angle=np.pi / 4,
        spoke_length=1.0,
    ):
        """Generates primitive parts for nested shapes
        with holes in the center, and optional decorator
        shapes in the remaining area.

        outer_shapes (list): list of shapes to nest on the outer rim
        outer_shapes_min_size (float): min size of outer rim
        inner_shapes (list): list of shapes to nest on the inner rim
        inner_shape_max_size (float): max size of inner rim
        nesting_scale_unit (float): how much space to leave between nested shapes
        decorator_shape (generator): type of shape to decorate area between inner and outer rim
        n_decorators (int): how many decorators to place
        decorator_size (float): size of decorators
        decorator_displacement (float): how close/far to place the decorators relative to the center of the shape,
        decorator_start_angle (float): starting point to place decorators -- will be placed with radial symmetry from there
        n_spokes (int): lines pointing out of the outer rim
        spoke_angle (float): starting point to place spokes -- will be placed with radial symmetry from there
        spoke_length (float): length of spokes
        """

        object_strokes = []

        # Place outer shapes
        outer_shape_size = outer_shapes_min_size
        for i, shape in enumerate(outer_shapes):
            object_strokes += T(shape, s=outer_shape_size)
            outer_shape_size += nesting_scale_unit

        # Place inner shapes
        inner_shape_size = inner_shapes_max_size
        for i, shape in enumerate(inner_shapes):
            object_strokes += T(shape, s=inner_shape_size)
            inner_shape_size -= nesting_scale_unit

        # Place decorators and spokes along evenly divided segments of a circle
        decorator_angle = decorator_start_angle
        decorator_surface = outer_shapes_min_size - inner_shapes_max_size
        for i in range(n_decorators):
            object_strokes += T(
                decorator_shape,
                s=decorator_size,
                x=np.cos(decorator_angle) * decorator_displacement,
                y=np.sin(decorator_angle) * decorator_displacement,
            )

            decorator_angle = (decorator_angle + 2 * np.pi / n_decorators) % (2 * np.pi)

        # Place spokes
        l = short_hline
        if spoke_length > DIAL_NONE:
            for i in range(n_spokes):
                spoke = T(l, theta=spoke_angle, s=spoke_length)
                spoke = T(
                    spoke,
                    x=spoke_length * 0.5 * math.cos(spoke_angle),
                    y=spoke_length * 0.5 * math.sin(spoke_angle),
                )

                spoke_angle = (spoke_angle + 2 * np.pi / n_spokes) % (2 * np.pi)

                object_strokes += spoke

        height = outer_shape_size
        return [object_strokes], height

    def _generate_nested_circle_dials(
        self,
        n_objects=3,
        n_circles=1,
        circle_size=DIAL_SMALL,
        dial_size=DIAL_SMALL,
        dial_angle=DIAL_VERTICAL,
        shape_specification=None,
    ):
        """Generates primitive parts for circular dials: parameterized by
        number of dials to draw left to right, n-nested circles, radius of inner-most circle,
        length of the dial hand (or NONE), and angle of the dial hand.
        Shape specification: array of shapes to draw the dial from.
        """
        x_grid = make_x_grid(
            n=n_objects * 2,
            x_min=-(n_objects * DIAL_SCALE_UNIT),
            x_shift=DIAL_SCALE_UNIT,
        )

        c = object_primitives._circle
        l = short_hline
        r = object_primitives._rectangle

        object_strokes = []

        if circle_size > DIAL_NONE and not shape_specification:
            for circle_idx in range(n_circles):
                circle = T(c, s=circle_size + (circle_idx * DIAL_SCALE_UNIT))
                # object_strokes += T_grid_idx(circle, 0, x_grid=x_grid)
                object_strokes += circle
        if shape_specification:
            for circle_idx, shape_spec in enumerate(shape_specification):
                stroke = T(shape_spec, s=circle_size + (circle_idx * DIAL_SCALE_UNIT))
                object_strokes += stroke

        if dial_size > DIAL_NONE:
            dial_length = dial_size
            dial_hand = T(l, theta=dial_angle, s=dial_length)
            dial_hand = T(
                dial_hand,
                x=dial_length * 0.5 * math.cos(dial_angle),
                y=dial_length * 0.5 * math.sin(dial_angle),
            )
            # object_strokes += T_grid_idx(dial_hand, 0, x_grid=x_grid)
            object_strokes += dial_hand

        return [object_strokes]

    def _generate_bases(
        self,
        base_columns=3,
        max_rows=1,
        base_width=DIAL_LARGE,
        base_height=DIAL_LARGE,
        n_tiers=1,
        base_center=BASE_CENTER,
        tier_scaling=DIAL_SCALE_UNIT,
        base_end_filials=False,
    ):
        """Generates bases. Adds multiple tiers and returns the total height and width of the base."""

        strokes = []
        margins = 4 * DIAL_SCALE_UNIT
        total_base_height = 0
        total_base_width = 0
        tier_offset = 0

        first_tier_width, first_tier_height = None, None
        for tier_idx in range(n_tiers):
            tier_width = base_columns * (base_width + DIAL_SCALE_UNIT) + margins
            tier_width -= tier_idx * margins
            tier_height = max_rows * (base_height + DIAL_SCALE_UNIT) + margins
            tier_height *= (tier_scaling) ** tier_idx

            # Hacky: only allows two tiers
            if tier_idx > 0:
                tier_offset = 0.5 * (tier_height + first_tier_height)
            strokes += T(
                object_primitives.rectangle(width=tier_width, height=tier_height),
                y=(0.5 * BASE_CENTER) + tier_offset,
            )

            total_base_width = max(total_base_width, tier_width)

            if tier_idx == 0:
                first_tier_width, first_tier_height = tier_width, tier_height
                total_base_height += 0.5 * tier_height
            else:
                total_base_height += tier_height

        # Add decorative 'filials' to the end of the first base.
        if base_end_filials:
            filial_width = 2 * DIAL_SCALE_UNIT
            strokes += T(
                object_primitives.rectangle(
                    width=2 * DIAL_SCALE_UNIT,
                    height=first_tier_height * DIAL_SCALE_UNIT,
                ),
                x=(first_tier_width + filial_width) * 0.5,
            )
            strokes += T(
                object_primitives.rectangle(
                    width=2 * DIAL_SCALE_UNIT,
                    height=first_tier_height * DIAL_SCALE_UNIT,
                ),
                x=-(first_tier_width + filial_width) * 0.5,
            )
            total_base_width += 2 * (2 * DIAL_SCALE_UNIT)

        return strokes, total_base_width, total_base_height

    def _generate_centered_grid_locations(
        self, max_objects=3, spacing=DIAL_LARGE + DIAL_SCALE_UNIT, centered=False
    ):
        """Generates a grid of x_locations consistent with alternatingly placing objects at spacing distances around the center."""
        x_locations = []
        for obj_idx in range(max_objects):
            # Alternate placing them over the center.
            x_offset = -obj_idx / 2 if obj_idx % 2 == 0 else int(obj_idx / 2) + 1
            x_location = x_offset * spacing
            x_locations.append(x_location)

        if centered:
            return x_locations
        else:
            return sorted(x_locations)


@TasksGeneratorRegistry.register
class DialsTasksGenerator(SimpleDialTasksGenerator):
    """Generates gadget tasks containing a base and a set of 'dials' placed at positions along the base."""

    name = "dials"

    def _add_antenna_to_stimuli(
        self,
        stimuli,
        base_width,
        base_height,
        n_antenna=3,
        spacing=DIAL_LARGE + DIAL_SCALE_UNIT,
        antenna_scale=ANTENNA_DIAL_SCALE_DOWN,
        max_antenna_wires=MAX_ANTENNA_WIRES,
        antenna_end_shapes=[
            None,
            object_primitives._circle,
            object_primitives._rectangle,
        ],
        add_double_antenna=False,
        add_side_antenna=False,
        generation_probability=1.0,
        antenna_generation_probability=0.25,
    ):
        if random.uniform(0, 1) > generation_probability:
            return None
        antenna_generator = antenna_tasks_generator.SimpleAntennaTasksGenerator()

        generation_probability *= antenna_generation_probability

        stimuli_with_antenna = []

        x_locations = self._generate_centered_grid_locations(
            max_objects=3, spacing=(base_width * 0.25), centered=False
        )

        antenna_primitives = []
        for n_wires in [1, 2, 3]:
            for scale_wires in [True, False]:
                for end_shape in antenna_end_shapes:
                    antenna_primitives += antenna_generator._generate_stacked_antenna(
                        n_wires=n_wires,
                        scale_wires=scale_wires,
                        end_shape=end_shape,
                    )

        sideways_antenna_primitives = []
        for n_wires in [2, 3]:
            sideways_antenna_primitives += antenna_generator._generate_stacked_antenna(
                n_wires=n_wires,
                scale_wires=False,
                end_shape=None,
            )

        for base_antenna_primitive in antenna_primitives:
            y_shift = antenna_tasks_generator.ANTENNA_LARGE + base_height
            antenna_primitive = T(base_antenna_primitive, y=y_shift)
            if random.uniform(0, 1) < generation_probability:
                stimuli_with_antenna.append(stimuli + antenna_primitive)
            if random.uniform(0, 1) < generation_probability:
                if base_width > base_height and add_double_antenna:
                    stimuli_with_antenna.append(
                        stimuli
                        + T(base_antenna_primitive, y=y_shift, x=x_locations[0])
                        + T(base_antenna_primitive, y=y_shift, x=x_locations[-1]),
                    )
            if random.uniform(0, 1) < generation_probability:
                if add_side_antenna:
                    for base_sideways in sideways_antenna_primitives:
                        sideways_antenna_primitive = T(
                            base_sideways, theta=-DIAL_VERTICAL
                        )
                        sideways_antenna_primitive = T(
                            sideways_antenna_primitive,
                            x=antenna_tasks_generator.ANTENNA_LARGE
                            + (0.5 * base_width),
                        )
                        stimuli_with_antenna.append(
                            stimuli + antenna_primitive + sideways_antenna_primitive
                        )

        if len(stimuli_with_antenna) < 1:
            return None
        return stimuli_with_antenna

    def _generate_base_with_dials(
        self,
        n_dials,
        n_circles,
        circle_size,
        dial_size,
        dial_angle,
        n_dial_rows=1,
        spacing=DIAL_LARGE + DIAL_SCALE_UNIT,
        base_width=DIAL_LARGE,
        base_height=DIAL_LARGE,
        base_columns=None,
        n_base_tiers=1,
        centered=False,
        max_dials=3,
        base_end_filials=False,
        shape_specification=None,
        no_base=False,
    ):
        n_grating = max_dials * 2
        x_grid = make_x_grid(n=n_grating)
        stimuli = make_grating_with_objects(
            [[] for _ in range(n_grating)], n_vertical_grating_lines=0
        )

        # x-locations for the dials
        x_locations = self._generate_centered_grid_locations(
            max_objects=max_dials, spacing=spacing, centered=centered
        )

        # y-locations for the rows of dials
        row_locations = self._generate_centered_grid_locations(max_objects=n_dial_rows)
        row_y_offset = BASE_CENTER  # Offset wrt. the location of the base.
        if n_dial_rows > 1:
            row_y_offset += -(spacing * 0.5)

        if not no_base:
            base, base_width, base_height = self._generate_bases(
                base_width=base_width,
                base_height=base_height,
                base_columns=base_columns,
                max_rows=n_dial_rows,
                n_tiers=n_base_tiers,
                base_end_filials=base_end_filials,
            )
            stimuli += base

        for row_idx in range(n_dial_rows):
            for dial_idx in range(n_dials):
                nested_circles = n_circles
                if type(n_circles) is not int:
                    nested_circles = n_circles(dial_idx)
                base_dial = self._generate_nested_circle_dials(
                    n_circles=nested_circles,
                    circle_size=circle_size,
                    dial_size=dial_size,
                    dial_angle=dial_angle,
                    shape_specification=shape_specification,
                )[0]

                stimuli += T(
                    base_dial,
                    y=row_y_offset + row_locations[row_idx],
                    x=x_locations[dial_idx],
                )
        return stimuli, base_width, base_height

    def _generate_parts_stimuli(
        self,
        max_dials=5,
        train_ratio=1.0,
        spacing=DIAL_LARGE + DIAL_SCALE_UNIT,
        generation_probability=0.2,
    ):
        c = object_primitives._circle
        r = object_primitives._rectangle

        all_parts_stimuli = []
        # Generate antenna.
        antenna_generator = antenna_tasks_generator.SimpleAntennaTasksGenerator()

        stimuli_with_antenna = []

        antenna_end_shapes = [
            None,
            object_primitives._circle,
            object_primitives._rectangle,
        ]

        antenna_primitives = []
        for n_wires in [1, 2, 3]:
            for scale_wires in [True, False]:
                for end_shape in antenna_end_shapes:
                    all_parts_stimuli += antenna_generator._generate_stacked_antenna(
                        n_wires=n_wires,
                        scale_wires=scale_wires,
                        end_shape=end_shape,
                    )

        # Generate dials
        for total_dials in [1, max_dials + 1]:
            # Varying bases for the single small dials.
            for base_columns in [1, max_dials + 1]:
                for base_heights in [1, max_dials]:
                    for rows in [1, 2]:
                        if base_heights < rows:
                            continue
                        base_height = base_heights * DIAL_LARGE
                        if rows > 1:  # We already take care of sizing the rows.
                            base_height = DIAL_LARGE
                        if base_columns < total_dials:
                            continue

                        centered = total_dials % 2 != 0

                        # Small and large dials with the lever sticking out
                        for dial_size in [DIAL_SMALL, DIAL_LARGE]:
                            for dial_angle in [DIAL_VERTICAL, DIAL_RIGHT]:
                                for shape_specification in [
                                    None,
                                    [c, r],
                                    [c, c],
                                ]:
                                    if (
                                        dial_size == DIAL_LARGE
                                        and dial_angle == DIAL_VERTICAL
                                    ):
                                        continue
                                    if (
                                        dial_size == DIAL_LARGE
                                        and shape_specification == [c, c, c]
                                    ):
                                        continue

                                    (
                                        stimuli,
                                        total_base_width,
                                        total_base_height,
                                    ) = self._generate_base_with_dials(
                                        max_dials=total_dials,
                                        n_dials=total_dials,
                                        n_circles=1,
                                        dial_size=dial_size,
                                        circle_size=dial_size,
                                        dial_angle=dial_angle,
                                        base_columns=base_columns,
                                        base_height=base_height,
                                        centered=centered,
                                        n_dial_rows=rows,
                                        n_base_tiers=0,
                                        spacing=spacing,
                                        base_end_filials=False,
                                        shape_specification=shape_specification,
                                        no_base=True,
                                    )
                                    if total_dials > 1 or rows > 1:
                                        if (
                                            random.uniform(0, 1)
                                            > generation_probability
                                        ):
                                            continue

                                    all_parts_stimuli.append(stimuli)

        return random_sample_ratio_ordered_array(all_parts_stimuli, train_ratio)

    def _generate_strokes_for_stimuli(
        self,
        train_ratio=1.0,
        max_dials=5,
        spacing=DIAL_LARGE + DIAL_SCALE_UNIT,
        generation_probability=0.14,  # Probabilistically generate from space
    ):
        """Main generator function. Returns a list of all stimuli from this generative model as sets of strokes."""

        strokes = []
        c = object_primitives._circle
        r = object_primitives._rectangle

        MAX_BASE_COLUMNS_FOR_ANTENNA = 3

        # Loop over the full cross product of dials / antenna / stimuli / tiers
        total_dials_range = list(range(1, max_dials + 1))
        random.shuffle(total_dials_range)
        for total_dials in total_dials_range:
            total_columns_range = list(range(1, max_dials + 1, 2))
            random.shuffle(total_columns_range)
            # Varying bases for the single small dials.
            for base_columns in total_columns_range:
                for base_heights in [1, max_dials]:
                    for rows in [1, 2]:
                        for tiers in [1, 2]:
                            for base_end_filials in [True, False]:
                                can_add_tiers = rows <= 1 and base_heights <= 1
                                if tiers > 1 and not can_add_tiers:
                                    continue

                                if base_heights < rows:
                                    continue
                                base_height = base_heights * DIAL_LARGE
                                if rows > 1:  # We already take care of sizing the rows.
                                    base_height = DIAL_LARGE
                                if base_columns < total_dials:
                                    continue

                                centered = total_dials % 2 != 0

                                add_side_antenna = (
                                    base_columns < MAX_BASE_COLUMNS_FOR_ANTENNA
                                )
                                add_double_antenna = (
                                    base_columns > MAX_BASE_COLUMNS_FOR_ANTENNA
                                )

                                # Blank bases with antenna.
                                # if (
                                #     can_add_tiers
                                #     and rows == 1
                                #     and tiers == 1
                                #     and total_dials == 1
                                # ):
                                #     (
                                #         stimuli,
                                #         total_base_width,
                                #         total_base_height,
                                #     ) = self._generate_base_with_dials(
                                #         n_dials=0,
                                #         n_circles=1,
                                #         dial_size=DIAL_NONE,
                                #         circle_size=DIAL_NONE,
                                #         dial_angle=DIAL_NONE,
                                #         base_columns=base_columns,
                                #         base_height=base_height,
                                #         centered=centered,
                                #         n_dial_rows=rows,
                                #     )
                                #     antenna_stimuli = self._add_antenna_to_stimuli(
                                #         stimuli,
                                #         n_antenna=1,
                                #         base_width=total_base_width,
                                #         base_height=total_base_height,
                                #         spacing=DIAL_LARGE + DIAL_SCALE_UNIT,
                                #         generation_probability=1.0,
                                #         antenna_generation_probability=0.5,
                                #     )
                                #     if antenna_stimuli is not None:
                                #         strokes += antenna_stimuli

                                # Small and large dials with the lever sticking out
                                for dial_size in [DIAL_SMALL, DIAL_LARGE]:
                                    for dial_angle in [DIAL_VERTICAL, DIAL_RIGHT]:
                                        for shape_specification in [
                                            None,
                                            [c, r],
                                            [c, c],
                                        ]:
                                            if (
                                                dial_size == DIAL_LARGE
                                                and dial_angle == DIAL_VERTICAL
                                            ):
                                                continue
                                            if (
                                                dial_size == DIAL_LARGE
                                                and shape_specification == [c, c, c]
                                            ):
                                                continue

                                            (
                                                stimuli,
                                                total_base_width,
                                                total_base_height,
                                            ) = self._generate_base_with_dials(
                                                max_dials=total_dials,
                                                n_dials=total_dials,
                                                n_circles=1,
                                                dial_size=dial_size,
                                                circle_size=dial_size,
                                                dial_angle=dial_angle,
                                                base_columns=base_columns,
                                                base_height=base_height,
                                                centered=centered,
                                                n_dial_rows=rows,
                                                n_base_tiers=tiers,
                                                spacing=spacing,
                                                base_end_filials=base_end_filials,
                                                shape_specification=shape_specification,
                                            )
                                            if (
                                                random.uniform(0, 1)
                                                < generation_probability
                                            ):
                                                strokes.append(stimuli)

                                            # add_side_antenna = (
                                            #     base_columns
                                            #     < MAX_BASE_COLUMNS_FOR_ANTENNA
                                            # )
                                            # add_double_antenna = (
                                            #     base_columns
                                            #     > MAX_BASE_COLUMNS_FOR_ANTENNA
                                            # )

                                            # antenna_stimuli = self._add_antenna_to_stimuli(
                                            #     stimuli,
                                            #     n_antenna=1,
                                            #     base_width=total_base_width,
                                            #     base_height=total_base_height,
                                            #     spacing=DIAL_LARGE + DIAL_SCALE_UNIT,
                                            #     add_double_antenna=add_double_antenna,
                                            #     add_side_antenna=add_side_antenna,
                                            #     generation_probability=generation_probability,
                                            # )
                                            # if antenna_stimuli is not None:
                                            #     strokes += antenna_stimuli

        # train_parts, test_parts = self._generate_parts_stimuli(
        #     train_ratio=0.95
        # )  # Mostly in training.
        train_parts, test_parts = [], []

        train_main, test_main = random_sample_ratio_ordered_array(strokes, train_ratio)

        return train_parts + train_main, test_parts + test_main

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
