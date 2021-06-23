"""s12_s13_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that reproduce the S12 and S13 stimuli used in Tian et. al 2021. 

Draws from the original source at: https://github.com/lucast4/drawgood/blob/main_language/code/python/stimLibCode/libraries.py 
"""

import primitives.object_primitives as object_primitives
from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
    TasksGeneratorRegistry,
    TaskCurriculum,
)

# Graphics utilities for drawing the common skewers and gratings primitives.
X_MIN, X_SHIFT = -1.75, 1.1
LONG_LINE_LENGTH = 4.0


T = object_primitives.transform

# Long vertical line
long_vline = T(object_primitives.line, theta=math.pi / 2, s=LONG_LINE_LENGTH, y=-2.0)
# Short horizontal line
short_hline = T(object_primitives.line, x=-0.5)


def vertical_grating(n, xleft=-1.5, xshift=1):
    pass
    # TODO: repeat
    # return repeat(T(ll, x=xleft), n, makeAffine(x=xshift))


def make_x_grid(n, x_min=X_MIN, x_shift=X_SHIFT):
    """:ret: grid of N evenly spaced values"""
    x_grid = [x_min + n_idx * x_shift for n_idx in range(n)]
    return x_grid


@AbstractTasksGenerator.register
class S12S13TestTasksGenerator(AbstractTasksGenerator):
    """Generates the tasks in the common test set between the S12 and S13 generative models. This forms the common test set used in Tian et. al 2020."""

    name = "S12_S13_test"

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super(S12S13TestTasksGenerator, self).__init__(
            grammar=object_primitives.constants
            + object_primitives.some_none
            + object_primitives.objects
            + object_primitives.transformations
        )

    def _generate_test_tasks(self):
        return []

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        """:ret: a curriculum for both conditions containing a single test block."""

        task_curriculum = to_test.TaskCurriculum(
            curriculum_id=S12S13TestTasksGenerator.name,
            task_generator_name=S12S13TestTasksGenerator.name,
        )

        task_curriculum.add_tasks(
            split=TaskCurriculum.SPLIT_TEST,
            condition=TaskCurriculum.CONDITION_ALL,
            curriculum_block=0,
            tasks=self._generate_test_tasks(),
        )
        return task_curriculum
