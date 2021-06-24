"""s12_s13_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that reproduce the S12 and S13 stimuli used in Tian et. al 2021. 

Draws from the original source at: https://github.com/lucast4/drawgood/blob/main_language/code/python/stimLibCode/libraries.py 
"""
import math, random
import primitives.object_primitives as object_primitives
from dreamcoder.grammar import Grammar
from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
    TasksGeneratorRegistry,
    TaskCurriculum,
    DrawingTask,
)

### Graphics utilities for drawing the common skewers and gratings primitives.
RANDOM_SEED = 0
random.seed(RANDOM_SEED)


def rand_choice(input_list):
    return input_list[random.randrange(len(input_list))]


X_MIN, X_SHIFT = -1.5, 1.0
LONG_LINE_LENGTH = 4.0


T = object_primitives.transform

# Long vertical line
long_vline = T(object_primitives._line, theta=math.pi / 2, s=LONG_LINE_LENGTH, y=-2.0)
# Short horizontal line
short_hline = T(object_primitives._line, x=-0.5)


def T_y(p, y):  # Wrapper to translate to y
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


def _make_grating_with_objects(
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
    return strokes, x_grid[:n_vertical_grating_lines]  # Also return partial grating.


def make_grating_with_objects(
    objects, n_vertical_grating_lines=4, x_left=X_MIN, x_shift=X_SHIFT
):
    """Makes a vertical grating by adding a list of objects to it."""
    strokes, _ = _make_grating_with_objects(
        objects, n_vertical_grating_lines, x_left, x_shift
    )
    return strokes


DEFAULT_X_GRID = make_x_grid(n=4)


def T_grid_idx(p, grid_idx, x_grid=DEFAULT_X_GRID):
    # Place an object at a horizontal grating position.
    return T(p, x=x_grid[grid_idx])


def hl(n_lines, x_shift=0, x_grid=DEFAULT_X_GRID):
    # Draw n short horizontal lines.
    p = []
    for n in range(n_lines):
        p.extend(T(short_hline, x=x_grid[n + x_shift]))
    return p


@TasksGeneratorRegistry.register
class S12StochasticTasksGenerator(AbstractTasksGenerator):
    """Generates the tasks used in the S12 generative model. This forms the 'vertical skewers' training set used in Tian et. al 2020.
    This is a stochastic model -- it cannot be used to exactly replicate the stimuli in the S13 generator unless properly seeded.
    """

    name = "S12_stochastic"

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super().__init__(
            grammar=object_primitives.constants
            + object_primitives.some_none
            + object_primitives.objects
            + object_primitives.transformations
        )

    def _generate_vertical_object_primitives(self):
        # Generates the library of object generators that can be stacked vertically onto skewers. Functions are themselves stochastic.
        c = object_primitives._circle
        l = short_hline

        circle_line_distribution = [c, c, c, l, l, l, l]

        # Number of objects on the skewer
        def skewer_objects_generator_1():
            y = random.randint(-1, 1)
            single_shape = rand_choice(circle_line_distribution)
            return T(single_shape, y=y)

        def skewer_objects_generator_2():
            y = [-1, 0, 1]
            random.shuffle(y)
            p = [rand_choice(circle_line_distribution) for _ in range(2)]
            return T(p[0], y=y[0]) + T(p[1], y=y[1])

        def skewer_objects_generator_3():
            y = [-1, 0, 1]
            random.shuffle(y)
            p = [rand_choice(circle_line_distribution) for _ in range(3)]
            return T(p[0], y=y[0]) + T(p[1], y=y[1]) + T(p[2], y=y[2])

        return (
            skewer_objects_generator_1,
            skewer_objects_generator_2,
            skewer_objects_generator_3,
        )

    def _generate_strokes_for_stimuli(self, min_stimuli_per_class=25):
        (
            skewer_objects_generator_1,
            skewer_objects_generator_2,
            skewer_objects_generator_3,
        ) = self._generate_vertical_object_primitives()
        skewer_objects_distribution = [
            skewer_objects_generator_1,
            skewer_objects_generator_1,
            skewer_objects_generator_2,
            skewer_objects_generator_2,
            skewer_objects_generator_3,
            skewer_objects_generator_3,
        ]

        # How many skewers to actually populate with objects?
        def make_stimuli_n_skewers_generator(n_skewers):
            def make_stimuli_n_skewer(n_grating):
                assert n_grating in [2, 3, 4]
                grating, partial_x_grid = _make_grating_with_objects(
                    [[] for _ in range(n_grating)], n_grating
                )
                random.shuffle(partial_x_grid)
                skewer_objects = [
                    rand_choice(skewer_objects_distribution)() for _ in range(n_skewers)
                ]

                strokes = grating
                for n_idx in range(n_skewers):
                    strokes += T(skewer_objects[n_idx], x=partial_x_grid[n_idx])
                return strokes

            return make_stimuli_n_skewer

        def generate_stroke_stimuli(n_skewers, n_stimuli_and_n_gratings):
            # n_skewers: for a given grating, how many skewers to actually add
            # n_stimuli_and_n_gratings: [(n_stimuli to generate, n_gratings to have inthe background)]
            stroke_stimuli = []
            skewer_generator_fn = make_stimuli_n_skewers_generator(n_skewers=n_skewers)
            for (n_stimuli, n_grating) in n_stimuli_and_n_gratings:
                for _ in range(n_stimuli):
                    stroke_stimuli.append(skewer_generator_fn(n_grating=n_grating))
            return stroke_stimuli

        stroke_stimuli = []
        # Single skewer
        n_stimuli_and_n_gratings = [
            (min_stimuli_per_class, 2),
            (min_stimuli_per_class, 3),
            (min_stimuli_per_class * 2, 4),
        ]
        stroke_stimuli += generate_stroke_stimuli(
            n_skewers=1, n_stimuli_and_n_gratings=n_stimuli_and_n_gratings
        )

        # Two skewer
        n_stimuli_and_n_gratings = [
            (min_stimuli_per_class, 2),
            (min_stimuli_per_class, 3),
            (min_stimuli_per_class * 2, 4),
        ]
        stroke_stimuli += generate_stroke_stimuli(
            n_skewers=2, n_stimuli_and_n_gratings=n_stimuli_and_n_gratings
        )

        # Three skewer
        n_stimuli_and_n_gratings = [
            (min_stimuli_per_class, 3),
            (min_stimuli_per_class * 2, 4),
        ]
        stroke_stimuli += generate_stroke_stimuli(
            n_skewers=3, n_stimuli_and_n_gratings=n_stimuli_and_n_gratings
        )

        # Four skewer
        n_stimuli_and_n_gratings = [(min_stimuli_per_class * 2, 4)]
        stroke_stimuli += generate_stroke_stimuli(
            n_skewers=4, n_stimuli_and_n_gratings=n_stimuli_and_n_gratings
        )

        return stroke_stimuli

    def _generate_tasks(self, num_tasks_to_generate_per_condition):
        # Call super helper method to enerate drawing tasks
        return self._generate_drawing_tasks_from_strokes(
            num_tasks_to_generate_per_condition,
            request_type=object_primitives.tstroke,
            render_strokes_fn=object_primitives.render_stroke_arrays_to_canvas,
            task_generator_name=self.name,
        )

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        """:ret: a curriculum for both conditions containing a single test block."""

        task_curriculum = TaskCurriculum(
            curriculum_id=self.name,
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
class S13StochasticTasksGenerator(AbstractTasksGenerator):
    """Generates the tasks in the S13 generative model. This forms the 'horizontal dumbbell' training set used in Tian et. al 2020.
    This is a stochastic model -- it cannot be used to exactly replicate the stimuli in the S13 generator unless properly seeded.
    """

    name = "S13_stochastic"

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super().__init__(
            grammar=object_primitives.constants
            + object_primitives.some_none
            + object_primitives.objects
            + object_primitives.transformations
        )

    #
    def _generate_horizontal_object_primitives(self):
        # Generates the library of lollipop and dumbbell objects.
        x_grid = make_x_grid(n=4)
        c = object_primitives._circle
        l = short_hline

        # Horizontal line objects.
        line_objects = [
            hl(1, 0, x_grid=x_grid),
            hl(1, 1, x_grid=x_grid),
            hl(1, 2, x_grid=x_grid),
            hl(1, 3, x_grid=x_grid),
            hl(2, 0, x_grid=x_grid),
            hl(2, 1, x_grid=x_grid),
            hl(2, 2, x_grid=x_grid),
            hl(3, 0, x_grid=x_grid),
            hl(3, 1, x_grid=x_grid),
            hl(4, 0, x_grid=x_grid),
        ]
        # Horizontal line-circle ('lollipops')
        line_circle_objects = [
            T_grid_idx(c, 0, x_grid=x_grid) + T_grid_idx(l, 1, x_grid=x_grid),
            T_grid_idx(c, 1, x_grid=x_grid) + T_grid_idx(l, 2, x_grid=x_grid),
            T_grid_idx(c, 2, x_grid=x_grid) + T_grid_idx(l, 3, x_grid=x_grid),
            T_grid_idx(c, 3, x_grid=x_grid) + T_grid_idx(l, 2, x_grid=x_grid),
            T_grid_idx(c, 2, x_grid=x_grid) + T_grid_idx(l, 1, x_grid=x_grid),
            T_grid_idx(c, 1, x_grid=x_grid) + T_grid_idx(l, 0, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid),
            T_grid_idx(c, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid)
            + T_grid_idx(l, 3, x_grid=x_grid),
            T_grid_idx(c, 3, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid),
            T_grid_idx(c, 2, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 0, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid)
            + T_grid_idx(l, 3, x_grid=x_grid),
            T_grid_idx(c, 3, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid)
            + T_grid_idx(l, 0, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid)
            + T_grid_idx(l, 3, x_grid=x_grid),
            T_grid_idx(c, 3, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid)
            + T_grid_idx(l, 0, x_grid=x_grid),
        ]

        # Horizontal circle-line-circle (dumbbell)
        circle_line_circle_objects = [
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(c, 2, x_grid=x_grid),
            T_grid_idx(c, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid)
            + T_grid_idx(c, 3, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid)
            + T_grid_idx(c, 3, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid)
            + T_grid_idx(c, 3, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid)
            + T_grid_idx(c, 3, x_grid=x_grid),
        ]

        # Shorter object primitives, used with gratings with < 4 vlines.
        shorter_objects = [
            hl(1, 0, x_grid=x_grid),
            hl(1, 1, x_grid=x_grid),
            hl(1, 2, x_grid=x_grid),
            hl(2, 0, x_grid=x_grid),
            hl(2, 1, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid) + T_grid_idx(l, 1, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid) + T_grid_idx(l, 1, x_grid=x_grid),
            T_grid_idx(c, 1, x_grid=x_grid) + T_grid_idx(l, 2, x_grid=x_grid),
            T_grid_idx(c, 2, x_grid=x_grid) + T_grid_idx(l, 1, x_grid=x_grid),
            T_grid_idx(c, 1, x_grid=x_grid) + T_grid_idx(l, 0, x_grid=x_grid),
            T_grid_idx(c, 1, x_grid=x_grid) + T_grid_idx(l, 0, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 2, x_grid=x_grid),
            T_grid_idx(c, 2, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(l, 0, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(c, 2, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(c, 2, x_grid=x_grid),
            T_grid_idx(c, 0, x_grid=x_grid)
            + T_grid_idx(l, 1, x_grid=x_grid)
            + T_grid_idx(c, 2, x_grid=x_grid),
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        ]
        return (
            line_objects,
            line_circle_objects,
            circle_line_circle_objects,
            shorter_objects,
        )

    def _generate_strokes_for_stimuli(self, total_stimuli=300):
        (
            line_objects,
            line_circle_objects,
            circle_line_circle_objects,
            shorter_objects,
        ) = self._generate_horizontal_object_primitives()

        def rep_list(input_list, n):
            return [e for e in input_list for _ in range(n)]

        long_object_distribution = (
            line_objects
            + rep_list(line_circle_objects, n=2)
            + rep_list(circle_line_circle_objects, n=6)
            + [[] for _ in range(15)]
        )  # Blank objects

        def _sample_grating_with_horizontal_objects(n_grating):
            strokes = []
            if n_grating < 4:
                horizontal_objects = shorter_objects
            else:
                horizontal_objects = long_object_distribution

            # Sample horizontal objects.
            for i in range(3):
                if i == 1:
                    horizontal_object_choices = horizontal_objects + [
                        [] for _ in range(math.ceil(len(horizontal_objects) / 4))
                    ]  # Upweight likelihood of blanks in center row
                else:
                    horizontal_object_choices = horizontal_objects
                strokes.extend(T(rand_choice(horizontal_object_choices), y=-1 + i))

            # Sample vertical strokes.
            strokes.extend(
                make_grating_with_objects([[] for _ in range(n_grating)], n_grating)
            )
            return strokes

        all_stroke_sets = []
        for _ in range(int(total_stimuli / 4)):
            all_stroke_sets.append(_sample_grating_with_horizontal_objects(n_grating=2))
        for _ in range(int(total_stimuli / 4)):
            all_stroke_sets.append(_sample_grating_with_horizontal_objects(n_grating=3))
        for _ in range(int(total_stimuli / 2)):
            all_stroke_sets.append(_sample_grating_with_horizontal_objects(n_grating=4))

        return all_stroke_sets

    def _generate_tasks(self, num_tasks_to_generate_per_condition):
        # Call super helper method to enerate drawing tasks
        return self._generate_drawing_tasks_from_strokes(
            num_tasks_to_generate_per_condition,
            request_type=object_primitives.tstroke,
            render_strokes_fn=object_primitives.render_stroke_arrays_to_canvas,
            task_generator_name=self.name,
        )

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        """:ret: a curriculum for both conditions containing a single test block."""

        task_curriculum = TaskCurriculum(
            curriculum_id=self.name,
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
class S12S13TestTasksGenerator(AbstractTasksGenerator):
    """Generates the tasks in the common test set between the S12 and S13 generative models. This forms the common test set used in Tian et. al 2020."""

    name = "S12_S13_test"

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super().__init__(
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
                task_generator_name=self.name,
            )
            for (test_idx, test_strokes) in enumerate(test_strokes_for_stimuli)
        ]
        return test_tasks

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        """:ret: a curriculum for both conditions containing a single test block."""

        task_curriculum = TaskCurriculum(
            curriculum_id=self.name,
            task_generator_name=self.name,
        )

        task_curriculum.add_tasks(
            split=TaskCurriculum.SPLIT_TEST,
            condition=TaskCurriculum.CONDITION_ALL,
            curriculum_block=0,
            tasks=self._generate_test_tasks(),
        )
        return task_curriculum
