"""
nuts_bolts_tasks_generator.py | Author : Catherine Wong
Defines TasksGenerators that produce gadget tasks that look like nuts and bolts.
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
    random_sample_ratio_ordered_array,
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

c = object_primitives._circle
cc = T(object_primitives._circle, s=2)  # Double scaled circle
r = object_primitives._rectangle
hexagon = object_primitives.polygon(n=6)
octagon = object_primitives.polygon(n=8)


@TasksGeneratorRegistry.register
class NutsBoltsTasksGenerator(SimpleDialTasksGenerator):
    """Generates gadget tasks containing a base and a set of 'dials' placed at positions along the base."""

    name = "nuts_bolts"

    def _generate_simple_nuts_stimuli(self, train_ratio):
        """Generates simple nuts: up to two nested shapes on the outer edge, and no perforations. Generates train and test."""
        all_strokes = []
        base_size = LARGE
        for outer_shapes in [[cc], [cc, cc], [hexagon], [hexagon, hexagon], [octagon]]:
            for outer_shapes_min_size in [base_size * n for n in [1, 2]]:
                for inner_shapes in [[cc], [hexagon], [r]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        object_strokes, height = self._generate_perforated_shapes(
                            outer_shapes=outer_shapes,
                            outer_shapes_min_size=outer_shapes_min_size,
                            inner_shapes=inner_shapes,
                            inner_shapes_max_size=inner_shapes_max_size,
                            n_decorators=0,
                        )
                        all_strokes += object_strokes

        return random_sample_ratio_ordered_array(all_strokes, train_ratio)

    def _generate_perforated_nuts_stimuli(self, train_ratio):
        """Generates nuts with perforated 'decorators' around the center."""
        all_strokes = []
        base_size = LARGE
        for outer_shapes in [[cc], [hexagon], [octagon], [hexagon, hexagon]]:
            for outer_shapes_min_size in [base_size * n for n in [2]]:
                for inner_shapes in [[cc], [hexagon], [r]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        for decorator_shape in [c, r]:
                            for decorator_size in [SCALE_UNIT]:
                                for n_decorators in [2, 4, 6, 8]:
                                    decorator_displacement = (
                                        inner_shapes_max_size
                                    ) * MEDIUM
                                    (
                                        object_strokes,
                                        height,
                                    ) = self._generate_perforated_shapes(
                                        outer_shapes=outer_shapes,
                                        outer_shapes_min_size=outer_shapes_min_size,
                                        inner_shapes=inner_shapes,
                                        inner_shapes_max_size=inner_shapes_max_size,
                                        n_decorators=n_decorators,
                                        decorator_shape=decorator_shape,
                                        decorator_size=decorator_size,
                                        decorator_displacement=decorator_displacement,
                                    )
                                    all_strokes += object_strokes
        return random_sample_ratio_ordered_array(all_strokes, train_ratio)

    def _generate_strokes_for_stimuli(self, train_ratio):
        """Main generator function. Returns a list of all stimuli from this generative model as sets of strokes."""
        simple_train, simple_test = self._generate_simple_nuts_stimuli(train_ratio)
        perforated_train, perforated_test = self._generate_perforated_nuts_stimuli(
            train_ratio
        )
        return simple_train + perforated_train, simple_test + perforated_test

    def _generate_train_test_tasks(
        self,
        num_tasks_to_generate_per_condition=AbstractTasksGenerator.GENERATE_ALL,
        train_ratio=0.8,
        max_train=200,
        max_test=50,
    ):
        # Currently generates all tasks as single entities. Does not generate a curriculum.
        train_tasks, test_tasks = self._generate_drawing_tasks_from_strokes(
            num_tasks_to_generate_per_condition,
            request_type=object_primitives.tstroke,
            render_strokes_fn=object_primitives.render_stroke_arrays_to_canvas,
            task_generator_name=self.name,
            train_ratio=train_ratio,
        )
        max_train = len(train_tasks) if max_train == None else max_train
        max_test = len(test_tasks) if max_test == None else max_test
        return train_tasks[:max_train], test_tasks[:max_test]

    def generate_tasks_curriculum(
        self, num_tasks_to_generate_per_condition, train_ratio=0.8
    ):
        """:ret: a curriculum that randomly samples among the train ratio for the simple and complex stimuli."""
        (
            num_tasks_to_generate_per_condition,
            human_readable,
        ) = self._get_number_tasks_to_generate_per_condition(
            num_tasks_to_generate_per_condition, train_ratio
        )
        task_curriculum = TaskCurriculum(
            curriculum_id=human_readable,
            task_generator_name=self.name,
        )

        train_tasks, test_tasks = self._generate_train_test_tasks(
            num_tasks_to_generate_per_condition, train_ratio=train_ratio
        )

        # Add the train tasks.
        task_curriculum.add_tasks(
            split=TaskCurriculum.SPLIT_TRAIN,
            condition=self.name,
            curriculum_block=0,
            tasks=train_tasks,
        )

        # Add the train tasks.
        task_curriculum.add_tasks(
            split=TaskCurriculum.SPLIT_TEST,
            condition=self.name,
            curriculum_block=0,
            tasks=test_tasks,
        )
        return task_curriculum
