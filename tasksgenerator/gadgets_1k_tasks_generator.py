"""
gadgets_1k_tasks_generator.py | Author : Catherine Wong and Yoni Friedman.
Defines a TaskGenerator that produces compositional gadget stimuli. This generator has four separate subclasses: nuts_bolts, furniture, dials, and wheeled_vehicles.

Each subclass has 250 total stimuli: 200 train, and 50 test. 
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

random.seed(RANDOM_SEED)


@TasksGeneratorRegistry.register
class Gadgets1KTasksGenerator(AbstractTasksGenerator):
    """Combines tasks from each of the task subgenerators."""

    name = "gadgets_1k"

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super().__init__(
            grammar=object_primitives.constants
            + object_primitives.some_none
            + object_primitives.objects
            + object_primitives.transformations
        )

        self.subgenerator_names = []

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        task_curriculum = TaskCurriculum(
            curriculum_id=AbstractTasksGenerator.GENERATE_ALL,
            task_generator_name=self.name,
        )

        for subgenerator_name in self.subgenerator_names:
            subgenerator = TasksGeneratorRegistry[subgenerator_name]
