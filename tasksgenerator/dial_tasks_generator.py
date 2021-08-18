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
        x_grid = make_x_grid(n=n_objects * 2, x_min=DIAL_X_MIN, x_shift=DIAL_SCALE_UNIT)

        c = object_primitives._circle
        l = short_hline

        object_strokes = []

        if circle_size > DIAL_NONE:
            for circle_idx in range(n_circles):
                circle = T(c, s=circle_size + (circle_idx * DIAL_SCALE_UNIT))
                object_strokes += T_grid_idx(circle, 0, x_grid=x_grid)

        if dial_size > DIAL_NONE:
            dial_length = dial_size
            dial_hand = T(l, theta=dial_angle, s=dial_length)
            dial_hand = T(
                dial_hand,
                x=dial_length * 0.5 * math.cos(dial_angle),
                y=dial_length * 0.5 * math.sin(dial_angle),
            )
            object_strokes += T_grid_idx(dial_hand, 0, x_grid=x_grid)

        return [object_strokes]

    def _generate_strokes_for_stimuli(self, max_dials=3):
        assert max_dials <= 3
        n_grating = max_dials * 2
        x_grid = make_x_grid(n=n_grating)

        # TODO
        BASE_CENTER = -4.0

        strokes = []

        def place_n_dials(
            n_dials, n_circles, circle_size, dial_size, dial_angle, n_dial_rows=1
        ):
            stimuli = make_grating_with_objects(
                [[] for _ in range(n_grating)], n_vertical_grating_lines=0
            )
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
                        y=BASE_CENTER + row_idx * (DIAL_LARGE + DIAL_SCALE_UNIT),
                        x=dial_idx * (DIAL_LARGE + DIAL_SCALE_UNIT),
                    )
            return stimuli

        # Small and large dials with the lever sticking out.
        for dial_size in [DIAL_SMALL, DIAL_LARGE]:
            for dial_angle in [DIAL_VERTICAL, DIAL_RIGHT]:
                for total_dials in range(1, max_dials + 1):
                    stimuli = place_n_dials(
                        n_dials=total_dials,
                        n_circles=1,
                        dial_size=dial_size,
                        circle_size=dial_size,
                        dial_angle=dial_angle,
                    )
                    strokes.append(stimuli)

        # Large dials with the lever contained.
        for total_dials in range(1, max_dials + 1):
            stimuli = place_n_dials(
                n_dials=total_dials,
                n_circles=1,
                dial_size=DIAL_SMALL,
                circle_size=DIAL_LARGE,
                dial_angle=DIAL_LEFT,
            )
            strokes.append(stimuli)
            if total_dials >= max_dials:
                stimuli = place_n_dials(
                    n_dials=total_dials,
                    n_circles=1,
                    dial_size=DIAL_SMALL,
                    circle_size=DIAL_LARGE,
                    dial_angle=DIAL_LEFT,
                    n_dial_rows=2,
                )
                strokes.append(stimuli)

        # Nested dials of the same size -- something weird with the nesting
        for n_circles in range(2, max_dials + 1):
            for total_dials in range(1, max_dials + 1):
                dial_size = DIAL_SMALL if n_circles <= 2 else DIAL_MEDIUM
                stimuli = place_n_dials(
                    n_dials=total_dials,
                    n_circles=n_circles,
                    circle_size=DIAL_SMALL,
                    dial_size=dial_size,
                    dial_angle=DIAL_RIGHT,
                )
                strokes.append(stimuli)
                if total_dials >= max_dials:
                    stimuli = place_n_dials(
                        n_dials=total_dials,
                        n_circles=n_circles,
                        circle_size=DIAL_SMALL,
                        dial_size=dial_size,
                        dial_angle=DIAL_RIGHT,
                        n_dial_rows=2,
                    )
                    strokes.append(stimuli)

        # Nested dials without hands in reverse order.
        for total_dials in range(1, max_dials + 1):
            stimuli = place_n_dials(
                n_dials=total_dials,
                n_circles=lambda n: n + 1,
                dial_size=DIAL_NONE,
                circle_size=DIAL_SMALL,
                dial_angle=DIAL_LEFT,
            )
            strokes.append(stimuli)
            stimuli = place_n_dials(
                n_dials=total_dials,
                n_circles=lambda n: max_dials - n,
                dial_size=DIAL_NONE,
                circle_size=DIAL_SMALL,
                dial_angle=DIAL_LEFT,
            )
            strokes.append(stimuli)

        return strokes
