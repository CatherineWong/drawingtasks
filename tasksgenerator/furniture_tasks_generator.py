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
class FurnitureTasksGenerator(AbstractBasesAndPartsTasksGenerator):
    """Generates furniture tasks. We generate bookshelves/drawers and tables/benches/seats."""

    name = "furniture"

    def __init__(self):
        super().__init__()
