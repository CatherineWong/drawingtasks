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
long_vline = T(
    object_primitives._line, theta=math.pi / 2, s=LONG_LINE_LENGTH * 0.75, y=-2.0
)
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
        self, n_wires=3, antenna_size=ANTENNA_SMALL, scale_wires=True, end_shape=None,
    ):
        l = long_vline
        w = short_hline

        object_strokes = []

        if antenna_size > ANTENNA_NONE:
            line = T(l, s=antenna_size, x=0)
            object_strokes += T(line, x=0)

            for a_idx in range(n_wires):
                antenna_length = antenna_size
                antenna_height = antenna_size * 0.5
                if scale_wires == True:
                    s = antenna_length * 2 - a_idx
                else:
                    s = antenna_length * 2

                antenna_wires = T(w, s=s)
                object_strokes += T(antenna_wires, y=antenna_height * 2 - a_idx)

        if end_shape:
            end_shapes_strokes = (
                T(end_shape, x=-antenna_length - 0.5, y=antenna_height),
                T(end_shape, x=antenna_length + 0.5, y=antenna_height),
            )
            object_strokes += T(end_shapes_strokes[0], y=antenna_height)
            object_strokes += T(end_shapes_strokes[1], y=antenna_height)

        return [object_strokes]
