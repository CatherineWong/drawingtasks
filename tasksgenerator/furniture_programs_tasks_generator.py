"""
furniture_programs_tasks_generator.py | Author: Catherine Wong.

Defines TaskGenerators that produce tasks for furniture drawings.

Threads program string generating logic through the generation.
"""
import math, random, itertools, copy
from primitives.gadgets_primitives import *
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

from tasksgenerator.s12_s13_tasks_generator import RANDOM_SEED


@TasksGeneratorRegistry.register
class FurnitureProgramsTasksGenerator(AbstractTasksGenerator):
    name = "furniture_programs"

    def __init__(self):
        super().__init__(grammar=constants + some_none + objects + transformations)
