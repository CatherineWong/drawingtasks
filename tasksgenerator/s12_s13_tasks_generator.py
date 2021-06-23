"""s12_s13_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that reproduce the S12 and S13 stimuli used in Tian et. al 2021. 

Draws from the original source at: https://github.com/lucast4/drawgood/blob/main_language/code/python/stimLibCode/libraries.py 
"""
import math
import primitives.object_primitives as object_primitives
from dreamcoder.grammar import Grammar
from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
    TasksGeneratorRegistry,
    TaskCurriculum,
    DrawingTask,
)

### Graphics utilities for drawing the common skewers and gratings primitives.
X_MIN, X_SHIFT = -1.5, 1.0
LONG_LINE_LENGTH = 4.0


T = object_primitives.transform

# Long vertical line
long_vline = T(object_primitives._line, theta=math.pi / 2, s=LONG_LINE_LENGTH, y=-2.0)
# Short horizontal line
short_hline = T(object_primitives._line, x=-0.5)


def T_y(p, y):
    return T(p, y=y)


def make_vertical_grating(n, x_left=X_MIN, x_shift=X_SHIFT):
    """Draws n vertical lines in a vertical grating."""
    return object_primitives._repeat(
        T(long_vline, x=x_left), n, object_primitives._makeAffine(x=x_shift)
    )


def make_x_grid(n, x_min=X_MIN, x_shift=X_SHIFT):
    """:ret: grid of N evenly spaced values"""
    x_grid = [x_min + n_idx * x_shift for n_idx in range(n)]
    return x_grid


def make_grating_with_objects(
    objects, n_vertical_grating_lines=4, x_left=X_MIN, x_shift=X_SHIFT
):
    """Makes a vertical grating by adding a list of objects to it."""
    x_grid = make_x_grid(n=n_vertical_grating_lines)
    strokes = make_vertical_grating(
        n_vertical_grating_lines, x_left=x_left, x_shift=x_shift
    )
    for idx, object in enumerate(objects):
        if len(object) > 0:
            strokes = strokes + T(object, x=x_grid[idx])
    return strokes


@TasksGeneratorRegistry.register
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

    def _generate_test_strokes_for_stimuli(self):
        c = object_primitives._circle
        l = short_hline
        return [
            make_grating_with_objects(
                [T(l, y=1) + l + T(c, y=-1), c, [], T(c, y=1) + l + T(l, y=-1)]
            ),
            make_grating_with_objects(
                [[], c + T(c, -1), l + T_y(l, -1), c + T_y(c, -1)]
            ),
            make_grating_with_objects(
                [
                    T_y(c, 1) + c,
                    T_y(l, 1) + l + T_y(c, -1),
                    T_y(l, 1) + T_y(l, -1),
                    T_y(c, 1) + T_y(c, -1),
                ]
            ),
            make_grating_with_objects(
                [T_y(c, 1), T_y(l, 1) + l + T_y(l, -1), T_y(c, -1), []]
            ),
            make_grating_with_objects(
                [
                    [],
                    T_y(l, 1) + c + T_y(c, -1),
                    T_y(l, 1) + l + T_y(l, -1),
                    T_y(c, 1) + T_y(c, -1),
                ]
            ),
            make_grating_with_objects(
                [T_y(c, 1) + c + T_y(c, -1), T_y(l, -1) + l, T_y(c, -1), []]
            ),
            make_grating_with_objects(
                [T_y(c, 1) + T_y(c, -1), T_y(l, 1), T_y(l, 1) + c + T_y(l, -1), []]
            ),
            make_grating_with_objects([[], T_y(c, 1) + c, T_y(l, 1) + l, l]),
            make_grating_with_objects(
                [T_y(c, 1) + c + T_y(c, -1), l + T_y(l, -1), T_y(c, 1) + c + T_y(c, -1)]
            ),
            make_grating_with_objects(
                [[], T_y(c, 1) + c + T_y(l, -1), l + T_y(c, -1), c]
            ),
            make_grating_with_objects(
                [T_y(c, 1) + l + T_y(c, -1), T_y(l, 1) + c + T_y(l, -1), [], []]
            ),
            make_grating_with_objects([[], l + T_y(c, -1), c + T_y(c, 1), T_y(l, 1)]),
            make_grating_with_objects(
                [[], T_y(c, 1) + c + T_y(c, -1), T_y(l, 1), T_y(l, 1)]
            ),
        ]

    def _generate_test_tasks(self):
        test_strokes_for_stimuli = self._generate_test_strokes_for_stimuli()
        test_tasks = [
            DrawingTask(
                task_id=test_idx,
                request=object_primitives.tstroke,
                ground_truth_strokes=test_strokes,
                render_strokes_fn=object_primitives.render_stroke_arrays_to_canvas,
                task_generator_name=S12S13TestTasksGenerator.name,
            )
            for (test_idx, test_strokes) in enumerate(test_strokes_for_stimuli)
        ]
        return test_tasks

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        """:ret: a curriculum for both conditions containing a single test block."""

        task_curriculum = TaskCurriculum(
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
