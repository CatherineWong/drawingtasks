"""
ANTENNA_tasks_generator.py | Author: Yoni Friedman / Catherine Wong.
Defines TasksGenerators that produce gadget tasks with a ANTENNA on them.
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
ANTENNA_NONE, ANTENNA_SMALL, ANTENNA_MEDIUM, ANTENNA_LARGE = 0.0, 1.0, 1.5, 2.0
ANTENNA_SCALE_UNIT = 0.5
ANTENNA_VERTICAL, ANTENNA_RIGHT, ANTENNA_LEFT = (
    math.pi / 2,
    math.pi / 4,
    2 * math.pi - (math.pi / 4),
)

# Long vertical line
long_vline = T(object_primitives._line, theta=math.pi / 2, s=LONG_LINE_LENGTH, y=-2.0)
# Short horizontal line
short_hline = T(object_primitives._line, x=-0.5)


@TasksGeneratorRegistry.register
class SimpleAntennaTasksGenerator(AbstractTasksGenerator):
    """Generates gadget tasks containing a base and a set of 'antenna' placed at positions along the base."""

    name = "simple_antenna"

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super().__init__(
            grammar=object_primitives.constants
            + object_primitives.some_none
            + object_primitives.objects
            + object_primitives.transformations
        )

    def _generate_stacked_antenna(
        self, n_wires=3, antenna_size=ANTENNA_SMALL,
    ):
        x_grid = make_x_grid(n=4)

        l = long_vline
        w = short_hline

        object_strokes = []

        if antenna_size > ANTENNA_NONE:
            line = T(l, s=antenna_size)
            object_strokes += T_grid_idx(line, 0, x_grid=x_grid)

            for a_idx in range(n_objects):
                antenna_length = antenna_size
                antenna_wires = T(w, s=antenna_length - a_idx + 1)
                object_strokes += T_grid_idx(
                    antenna_wires, 0, y=antenna_length * 2 - a_idx, x_grid=x_grid
                )

        return [object_strokes]

    def _generate_stacked_antenna_with_end_shapes(
        self,
        n_objects=4,
        n_lines=1,
        antenna_size=ANTENNA_SMALL,
        end_shape=object_primitives._circle,
        antenna_angle=ANTENNA_VERTICAL,
    ):
        x_grid = make_x_grid(n=4)

        l = long_vline
        w = short_hline

        object_strokes = []

        if antenna_size > ANTENNA_NONE:
            line = T(l, s=antenna_size)
            object_strokes += T_grid_idx(line, 0, x_grid=x_grid)

            for a_idx in range(n_objects):
                antenna_length = antenna_size
                antenna_wires = T(w, s=antenna_length / (a_idx + 1) * 2)
                object_strokes += T_grid_idx(
                    antenna_wires, 0, y=antenna_length * 2 - a_idx, x_grid=x_grid
                )

                if a_idx == 0:
                    end_shapes = (
                        T(end_shape, x=-antenna_length - 0.5, y=antenna_length),
                        T(end_shape, x=antenna_length + 0.5, y=antenna_length),
                    )
                    object_strokes += T_grid_idx(
                        end_shapes[0], 0, y=antenna_length, x_grid=x_grid
                    )
                    object_strokes += T_grid_idx(
                        end_shapes[1], 0, y=antenna_length, x_grid=x_grid
                    )

        return [object_strokes]

