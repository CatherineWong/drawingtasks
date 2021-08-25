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

        return self._generate_basic_n_segment_bases(
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

    def _generate_buggy_bases(
        self, tier_heights, tier_widths, antenna=None, antenna_height=None
    ):
        """Generates 'buggies' consisting of one or more tiers of cars and an optional antenna."""
        # First tier is a base.
        (strokes, min_x, max_x, min_y, max_y,) = self._generate_basic_n_segment_bases(
            primitives=[RECTANGLE],
            heights=[tier_heights[0]],
            widths=[tier_widths[0]],
            float_locations=[FLOAT_TOP],
            right_margins=[0],
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
    ):
        """Generates a row of wheels floated below the central axis."""
        dialgenerator = SimpleDialTasksGenerator()
        base_wheel, wheel_height = dialgenerator._generate_perforated_shapes(
            outer_shapes=outer_shapes,
            outer_shapes_min_size=outer_shapes_min_size,
            inner_shapes=inner_shapes,
            inner_shapes_max_size=inner_shapes_max_size,
            nesting_scale_unit=0.5,
            decorator_shape=object_primitives._circle,
            n_decorators=n_decorators,
            n_spokes=n_spokes,
            spoke_angle=np.pi,
            spoke_length=outer_shapes_min_size * 0.5,
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
            n_columns=n_wheels,
            float_location=FLOAT_BOTTOM,
            grid_indices=range(n_wheels),
        )

    def _generate_wheels_iterator(self, min_x, max_x, n_wheels):
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
                                paired_wheels=False,
                                n_wheels=n_wheels,
                            )

    def _generate_truck_stimuli(self):
        all_truck_stimuli = []
        for head_width in [SMALL]:
            for head_height in [SMALL]:
                for body_width in [LARGE * scale for scale in range(4, 7)]:
                    for body_height in [LARGE * LARGE]:
                        for nose_scale in [0.5, 0.25]:
                            for reverse in [True, False]:
                                (
                                    base_strokes,
                                    base_min_x,
                                    base_max_x,
                                    base_min_y,
                                    base_max_y,
                                ) = self._generate_truck_bases(
                                    head_width=head_width,
                                    head_height=head_height,
                                    body_width=body_width,
                                    body_height=body_height,
                                    nose_scale=nose_scale,
                                    reverse=reverse,
                                )
                                wheels_iterator = self._generate_wheels_iterator(
                                    base_min_x, base_max_x, n_wheels=5
                                )
                                for (
                                    wheels_strokes,
                                    wheels_min_x,
                                    wheels_max_x,
                                    wheels_min_y,
                                    wheels_max_y,
                                ) in wheels_iterator:
                                    truck_strokes = [
                                        base_strokes[0] + wheels_strokes[0]
                                    ]
                                    all_truck_stimuli += truck_strokes
        return all_truck_stimuli

    def _generate_train_stimuli(self):
        pass

    def _generate_buggy_stimuli(self):
        antenna_generator = antenna_tasks_generator.SimpleAntennaTasksGenerator()
        n_wires = 3
        antenna_object = antenna_generator._generate_stacked_antenna(
            n_wires=n_wires,
            scale_wires=False,
            end_shape=None,
        )[0]
        antenna_height = antenna_tasks_generator.ANTENNA_BASE_HEIGHT + (
            antenna_tasks_generator.ANTENNA_SMALL * (n_wires - 1)
        )

        buggy_stimuli = []
        for first_tier_height in [LARGE * 2]:
            for first_tier_width in [LARGE * n for n in [8, 9]]:
                for second_tier_height in [SMALL]:
                    for antenna in [antenna_object, None]:
                        for n_wheels in [2, 6]:
                            (
                                base_strokes,
                                base_min_x,
                                base_max_x,
                                base_min_y,
                                base_max_y,
                            ) = self._generate_buggy_bases(
                                tier_heights=[first_tier_height, second_tier_height],
                                tier_widths=[
                                    first_tier_width,
                                    first_tier_width * THREE_QUARTER_SCALE,
                                ],
                                antenna=antenna,
                                antenna_height=antenna_height,
                            )
                            wheels_iterator = self._generate_wheels_iterator(
                                base_min_x, base_max_x, n_wheels=n_wheels
                            )
                            for (
                                wheels_strokes,
                                wheels_min_x,
                                wheels_max_x,
                                wheels_min_y,
                                wheels_max_y,
                            ) in wheels_iterator:
                                buggy_strokes = [base_strokes[0] + wheels_strokes[0]]
                                buggy_stimuli += buggy_strokes
        return buggy_stimuli
