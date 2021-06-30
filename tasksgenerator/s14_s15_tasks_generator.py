"""
s14_s15_tasks_generator.py | Author : Catherine Wong.
Defines TasksGenerators that produce simplified and compositional stimuli similar to those used in Tian et. al 2020.
"""
import math, random, itertools
import primitives.object_primitives as object_primitives
from dreamcoder.grammar import Grammar
from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
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


@TasksGeneratorRegistry.register
class S14TasksGenerator(AbstractTasksGenerator):
    """Generates tasks with 'vertical skewer objects' placed at positions along with a verticla grating.
    This generator is closely modeled on the S12 vertical objects model from Tian et. al 2020. However, it uses a more limited basic set of vertical object primitives, and enumerates them deterministically over a cross product of spatial locations.
    """

    name = "S14"

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super().__init__(
            grammar=object_primitives.constants
            + object_primitives.some_none
            + object_primitives.objects
            + object_primitives.transformations
        )

    def _generate_vertical_object_primitives(self, n_objects=4):
        # Generates the library of base vertical objects.
        x_grid = make_x_grid(n=4)
        c = object_primitives._circle
        l = short_hline

        cross = [
            T_grid_idx(l, 0, y=1.0, x_grid=x_grid)
            + make_grating_with_objects(
                [[] for _ in range(n_objects)], n_vertical_grating_lines=1
            )
        ]
        eight = [
            T_grid_idx(c, 0, y=0.0, x_grid=x_grid)
            + T_grid_idx(c, 0, y=1.0, x_grid=x_grid)
            + make_grating_with_objects(
                [[] for _ in range(n_objects)], n_vertical_grating_lines=1
            )
        ]
        scarecrow = [
            T_grid_idx(l, 0, y=0.0, x_grid=x_grid)
            + T_grid_idx(c, 0, y=1.0, x_grid=x_grid)
            + make_grating_with_objects(
                [[] for _ in range(n_objects)], n_vertical_grating_lines=1
            )
        ]
        telephone = [
            T_grid_idx(l, 0, y=0.0, x_grid=x_grid)
            + T_grid_idx(l, 0, y=1.0, x_grid=x_grid)
            + T_grid_idx(l, 0, y=-1.0, x_grid=x_grid)
            + make_grating_with_objects(
                [[] for _ in range(n_objects)], n_vertical_grating_lines=1
            )
        ]
        return cross + eight + scarecrow + telephone

    def _generate_strokes_for_stimuli(self, max_vertical_objects=2, max_skewers=3):
        assert max_skewers <= 4
        n_grating = 4
        vertical_objects = self._generate_vertical_object_primitives()
        x_grid = make_x_grid(n=4)

        def _build_vertical_object_sets(x_positions=[0, 1]):
            # Places permutations of vertial objects at locations.
            strokes = []
            for n_vertical_objects in range(1, max_vertical_objects + 1):
                vertical_object_sets = list(
                    itertools.product(vertical_objects, repeat=n_vertical_objects)
                )
                x_position_sets = list(
                    itertools.combinations(x_positions, n_vertical_objects)
                )
                # Each vertical object set = a permutation of stimuli to be placed
                for vertical_object_set in vertical_object_sets:
                    for x_position in x_position_sets[: len(vertical_object_set)]:
                        stimuli = make_grating_with_objects(
                            [[] for _ in range(n_grating)], n_vertical_grating_lines=0
                        )
                        for (idx, vertical_object) in enumerate(vertical_object_set):
                            stimuli += T(vertical_object, x=x_position[idx], y=0)
                        strokes.append(stimuli)
            return strokes

        def _build_vertical_object_sets_with_gratings(n_lines, x_skewer_positions):
            vertical_object_sets = _build_vertical_object_sets(
                x_positions=x_skewer_positions
            )
            for vertical_object_set in vertical_object_sets:
                vertical_object_set += make_grating_with_objects(
                    [[] for _ in range(n_grating)], n_vertical_grating_lines=n_lines
                )
            return vertical_object_sets

        strokes = []
        # No skewers
        strokes += vertical_objects

        for num_skewers in range(2, max_skewers + 1):
            strokes += _build_vertical_object_sets_with_gratings(
                n_lines=num_skewers, x_skewer_positions=[0, 1]
            )
            if num_skewers > 2:
                strokes += _build_vertical_object_sets_with_gratings(
                    n_lines=num_skewers,
                    x_skewer_positions=[0, (num_skewers - 1) * X_SHIFT],
                )

        return strokes

    def _generate_tasks(self, num_tasks_to_generate_per_condition):
        # Currently generates all tasks as single entities. Does not generate a curriculum.
        return self._generate_drawing_tasks_from_strokes(
            num_tasks_to_generate_per_condition,
            request_type=object_primitives.tstroke,
            render_strokes_fn=object_primitives.render_stroke_arrays_to_canvas,
            task_generator_name=self.name,
        )

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        """:ret: a curriculum for single condition containing a single train block."""
        (
            num_tasks_to_generate_per_condition,
            human_readable,
        ) = self._get_number_tasks_to_generate_per_condition(
            num_tasks_to_generate_per_condition
        )
        task_curriculum = TaskCurriculum(
            curriculum_id=human_readable,
            task_generator_name=self.name,
        )

        task_curriculum.add_tasks(
            split=TaskCurriculum.SPLIT_TRAIN,
            condition=self.name,
            curriculum_block=0,
            tasks=self._generate_tasks(num_tasks_to_generate_per_condition),
        )
        return task_curriculum


@TasksGeneratorRegistry.register
class S15TasksGenerator(AbstractTasksGenerator):
    """Generates tasks with 'horizontal objects' placed at positions on a vertical grating.
    This generator is closely modeled on the S13 horizontal objects model from Tian et. al 2020. However, it uses a more limited basic set of horizontal object primitives, and enumerates them deterministically over a cross product of spatial locations.
    """

    name = "S15"

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super().__init__(
            grammar=object_primitives.constants
            + object_primitives.some_none
            + object_primitives.objects
            + object_primitives.transformations
        )

    def _generate_horizontal_object_primitives(self):
        # Generates the library of base horizontal objects that can be placed on skewers.
        x_grid = make_x_grid(n=4)
        c = object_primitives._circle
        l = short_hline

        lollipop = [T_grid_idx(c, 0, x_grid=x_grid) + T_grid_idx(l, 1, x_grid=x_grid)]
        short_dumbell = [
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(c, 2, x_grid=x_grid)
        ]
        glasses = [T_grid_idx(c, 0, x_grid=x_grid) + T_grid_idx(c, 1, x_grid=x_grid)]

        return lollipop + short_dumbell + glasses

    def _generate_strokes_for_stimuli(self, max_skewers=3, max_horizontal_objects=2):
        # Generates the
        assert max_skewers <= 4
        n_grating = 4
        horizontal_objects = self._generate_horizontal_object_primitives()
        x_grid = make_x_grid(n=4)

        def _build_horizontal_object_sets(x_positions=[0], y_positions=[1, 0]):
            # Places permutations of horizontal objects at locations.
            strokes = []
            for n_horizontal_objects in range(1, max_horizontal_objects + 1):
                horizontal_object_sets = list(
                    itertools.product(horizontal_objects, repeat=n_horizontal_objects)
                )
                x_position_sets = list(
                    itertools.combinations(x_positions, n_horizontal_objects)
                )
                # Each horizontal object set = a permutation of stimuli to be placed
                for horizontal_object_set in horizontal_object_sets:
                    for x_position in x_position_sets[: len(horizontal_object_set)]:
                        stimuli = make_grating_with_objects(
                            [[] for _ in range(n_grating)], n_vertical_grating_lines=0
                        )
                        for (idx, horizontal_object) in enumerate(
                            horizontal_object_set
                        ):
                            stimuli += T(
                                horizontal_object, x=x_position[idx], y=y_positions[idx]
                            )
                        strokes.append(stimuli)
            return strokes

        def _build_horizontal_object_sets_with_gratings(n_lines, x_skewer_positions):
            horizontal_object_sets = _build_horizontal_object_sets(
                x_positions=[
                    x_pos - 1 * X_SHIFT if x_pos > 0 else x_pos
                    for x_pos in x_skewer_positions
                ],
                y_positions=[1, 0],
            )
            for horizontal_object_set in horizontal_object_sets:
                horizontal_object_set += make_grating_with_objects(
                    [[] for _ in range(n_grating)], n_vertical_grating_lines=n_lines
                )
            return horizontal_object_sets

        strokes = []
        # No skewers
        strokes += _build_horizontal_object_sets(x_positions=[0, 0])

        for num_skewers in range(1, max_skewers + 1):
            strokes += _build_horizontal_object_sets_with_gratings(
                n_lines=num_skewers, x_skewer_positions=[0, 0]
            )
            if num_skewers > 1:
                strokes += _build_horizontal_object_sets_with_gratings(
                    n_lines=num_skewers, x_skewer_positions=[num_skewers, num_skewers]
                )

        return strokes

    def _generate_tasks(self, num_tasks_to_generate_per_condition):
        # Currently generates all tasks as single entities. Does not generate a curriculum.
        return self._generate_drawing_tasks_from_strokes(
            num_tasks_to_generate_per_condition,
            request_type=object_primitives.tstroke,
            render_strokes_fn=object_primitives.render_stroke_arrays_to_canvas,
            task_generator_name=self.name,
        )

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        """:ret: a curriculum for single condition containing a single train block."""
        (
            num_tasks_to_generate_per_condition,
            human_readable,
        ) = self._get_number_tasks_to_generate_per_condition(
            num_tasks_to_generate_per_condition
        )
        task_curriculum = TaskCurriculum(
            curriculum_id=human_readable,
            task_generator_name=self.name,
        )

        task_curriculum.add_tasks(
            split=TaskCurriculum.SPLIT_TRAIN,
            condition=self.name,
            curriculum_block=0,
            tasks=self._generate_tasks(num_tasks_to_generate_per_condition),
        )
        return task_curriculum
