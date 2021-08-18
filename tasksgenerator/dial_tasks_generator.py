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
)

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

random.seed(RANDOM_SEED)

# Size constants
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

    def _generate_nested_circle_dials(
        self,
        n_objects=3,
        n_circles=1,
        circle_size=DIAL_SMALL,
        dial_size=DIAL_SMALL,
        dial_angle=DIAL_VERTICAL,
    ):
        # Circular dials: number of dials to draw left to right, n-nested circles, radius of inner-most circle, length of the dial hand (or NONE), and angle of the dial hand.
        x_grid = make_x_grid(
            n=n_objects * 2,
            x_min=-(n_objects * DIAL_SCALE_UNIT),
            x_shift=DIAL_SCALE_UNIT,
        )

        c = object_primitives._circle
        l = short_hline

        object_strokes = []

        if circle_size > DIAL_NONE:
            for circle_idx in range(n_circles):
                circle = T(c, s=circle_size + (circle_idx * DIAL_SCALE_UNIT))
                # object_strokes += T_grid_idx(circle, 0, x_grid=x_grid)
                object_strokes += circle

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
    ):
        strokes = []
        margins = 4 * DIAL_SCALE_UNIT
        for tier_idx in range(n_tiers):
            tier_width = base_columns * (base_width + DIAL_SCALE_UNIT) + margins
            tier_height = max_rows * (base_height + DIAL_SCALE_UNIT) + margins

            strokes += T(
                object_primitives.rectangle(width=tier_width, height=tier_height),
                y=0.5 * BASE_CENTER,
            )
        return strokes, tier_width, tier_height

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

    def _generate_strokes_for_stimuli(
        self, max_dials=3, spacing=DIAL_LARGE + DIAL_SCALE_UNIT
    ):
        assert max_dials <= 3
        n_grating = max_dials * 2
        x_grid = make_x_grid(n=n_grating)

        strokes = []

        def place_n_dials(
            n_dials,
            n_circles,
            circle_size,
            dial_size,
            dial_angle,
            n_dial_rows=1,
            base_width=DIAL_LARGE,
            base_height=DIAL_LARGE,
            base_columns=max_dials,
            n_base_tiers=1,
            centered=False,
        ):
            x_locations = self._generate_centered_grid_locations(
                max_objects=max_dials, spacing=spacing, centered=centered
            )

            stimuli = make_grating_with_objects(
                [[] for _ in range(n_grating)], n_vertical_grating_lines=0
            )

            row_locations = self._generate_centered_grid_locations(
                max_objects=n_dial_rows
            )

            base, base_width, base_height = self._generate_bases(
                base_width=base_width,
                base_height=base_height,
                base_columns=base_columns,
                max_rows=n_dial_rows,
            )
            stimuli += base

            row_y_offset = BASE_CENTER
            if n_dial_rows > 1:
                row_y_offset += -(spacing * 0.5)

            for row_idx in range(n_dial_rows):
                for dial_idx in range(total_dials):
                    nested_circles = n_circles
                    if type(n_circles) is not int:
                        nested_circles = n_circles(dial_idx)
                    base_dial = self._generate_nested_circle_dials(
                        n_circles=nested_circles,
                        circle_size=circle_size,
                        dial_size=dial_size,
                        dial_angle=dial_angle,
                    )[0]

                    stimuli += T(
                        base_dial,
                        y=row_y_offset + row_locations[row_idx],
                        x=x_locations[dial_idx],
                    )
            return stimuli

        for total_dials in range(1, max_dials + 1):
            # Varying bases for the single small dials.
            for base_columns in [1, max_dials]:
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
                                if (
                                    dial_size == DIAL_LARGE
                                    and dial_angle == DIAL_VERTICAL
                                ):
                                    continue
                                stimuli = place_n_dials(
                                    n_dials=total_dials,
                                    n_circles=1,
                                    dial_size=dial_size,
                                    circle_size=dial_size,
                                    dial_angle=dial_angle,
                                    base_columns=base_columns,
                                    base_height=base_height,
                                    centered=centered,
                                    n_dial_rows=rows,
                                )
                                strokes.append(stimuli)
                        # Large dials with a contained lever.
                        stimuli = place_n_dials(
                            n_dials=total_dials,
                            n_circles=1,
                            dial_size=DIAL_SMALL,
                            circle_size=DIAL_LARGE,
                            dial_angle=DIAL_LEFT,
                            base_columns=base_columns,
                            base_height=base_height,
                            centered=centered,
                            n_dial_rows=rows,
                        )
                        strokes.append(stimuli)

                        # Nested circles
                        for n_circles in range(2, max_dials + 1):
                            dial_size = DIAL_SMALL if n_circles <= 2 else DIAL_MEDIUM
                            stimuli = place_n_dials(
                                n_dials=total_dials,
                                n_circles=n_circles,
                                circle_size=DIAL_SMALL,
                                dial_size=dial_size,
                                dial_angle=DIAL_RIGHT,
                                base_columns=base_columns,
                                base_height=base_height,
                                centered=centered,
                                n_dial_rows=rows,
                            )
                            strokes.append(stimuli)

                        # Nested dials without hands in reverse order.
                        centered = True if total_dials == 1 else False
                        stimuli = place_n_dials(
                            n_dials=total_dials,
                            n_circles=lambda n: n + 1,
                            dial_size=DIAL_NONE,
                            circle_size=DIAL_SMALL,
                            dial_angle=DIAL_LEFT,
                            base_columns=base_columns,
                            base_height=base_height,
                            n_dial_rows=rows,
                            centered=centered,
                        )
                        strokes.append(stimuli)
                        stimuli = place_n_dials(
                            n_dials=total_dials,
                            n_circles=lambda n: max_dials - n,
                            dial_size=DIAL_NONE,
                            circle_size=DIAL_SMALL,
                            dial_angle=DIAL_LEFT,
                            base_columns=base_columns,
                            base_height=base_height,
                            n_dial_rows=rows,
                            centered=centered,
                        )
                        strokes.append(stimuli)

        return strokes
