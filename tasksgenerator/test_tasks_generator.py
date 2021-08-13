"""test_tasks_generator.py | Author: Catherine Wong"""

import tasksgenerator.tasks_generator as to_test
from dreamcoder.program import Program
from dreamcoder.grammar import Grammar
import primitives.object_primitives as object_primitives


DEFAULT_TEST_TASK_ID = "0"
DEFAULT_TEST_TASK_GENERATOR = "test_tasks_generator"
DEFAULT_MANUAL_CURRICULUM_TASK_GENERATOR = "test_manual_curriculum_tasks_generator"


@to_test.TasksGeneratorRegistry.register
class TestTasksGenerator(to_test.AbstractTasksGenerator):
    name = DEFAULT_TEST_TASK_GENERATOR

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super(TestTasksGenerator, self).__init__(grammar=grammar)

    def _generate_tasks(self):
        return _build_default_tasks()

    def _generate_strokes_for_stimuli(self):
        return [t.rendering for t in self._generate_tasks()]

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        test_curriculum_id = "test_id"
        task_curriculum = to_test.TaskCurriculum(
            curriculum_id=test_curriculum_id,
            task_generator_name=TestTasksGenerator.name,
        )

        test_split = to_test.TaskCurriculum.SPLIT_TRAIN
        test_condition = "test_condition"
        test_curriculum_block = "test_block"
        test_tasks = _build_default_tasks()
        task_curriculum.add_tasks(
            split=test_split,
            condition=test_condition,
            curriculum_block=test_curriculum_block,
            tasks=test_tasks,
        )
        return task_curriculum


@to_test.TasksGeneratorRegistry.register
class TestManualCurriculumTasksGenerator(to_test.ManualCurriculumTasksGenerator):
    name = DEFAULT_MANUAL_CURRICULUM_TASK_GENERATOR

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super().__init__(grammar=grammar)


def test_drawing_task_from_program():
    test_task_id = DEFAULT_TEST_TASK_ID
    test_ground_truth_program = Program.parse("(line)")
    ground_truth_render = object_primitives.render_parsed_program(
        test_ground_truth_program
    )

    test_task = to_test.DrawingTask(
        task_id=test_task_id,
        request=object_primitives.tstroke,
        ground_truth_program=test_ground_truth_program,
        render_parsed_program_fn=object_primitives.render_parsed_program,
        task_generator_name=DEFAULT_TEST_TASK_GENERATOR,
    )
    assert test_task.logLikelihood(test_ground_truth_program) == 0.0
    assert test_task_id in test_task.name
    assert DEFAULT_TEST_TASK_GENERATOR in test_task.name


def test_drawing_task_from_strokes():
    test_task_id = DEFAULT_TEST_TASK_ID
    test_ground_truth_program = Program.parse("(line)")
    test_ground_truth_strokes = test_ground_truth_program.evaluate([])
    ground_truth_render = object_primitives.render_stroke_arrays_to_canvas(
        test_ground_truth_strokes
    )

    test_task = to_test.DrawingTask(
        task_id=test_task_id,
        request=object_primitives.tstroke,
        ground_truth_strokes=test_ground_truth_strokes,
        render_strokes_fn=object_primitives.render_stroke_arrays_to_canvas,
        task_generator_name=DEFAULT_TEST_TASK_GENERATOR,
    )
    assert test_task.logLikelihood(test_ground_truth_program) == 0.0
    assert test_task_id in test_task.name
    assert DEFAULT_TEST_TASK_GENERATOR in test_task.name


def _build_default_tasks(
    test_task_id=DEFAULT_TEST_TASK_ID, task_generator_name=DEFAULT_TEST_TASK_GENERATOR
):
    test_ground_truth_program = Program.parse("(line)")
    ground_truth_render = object_primitives.render_parsed_program(
        test_ground_truth_program
    )

    test_task = to_test.DrawingTask(
        task_id=test_task_id,
        request=object_primitives.tstroke,
        ground_truth_program=test_ground_truth_program,
        render_parsed_program_fn=object_primitives.render_parsed_program,
        task_generator_name=task_generator_name,
    )
    return [test_task]


def test_task_curriculum_get_all_tasks():
    test_curriculum_id = "test_id"
    task_curriculum = to_test.TaskCurriculum(
        curriculum_id=test_curriculum_id,
        task_generator_name=DEFAULT_TEST_TASK_GENERATOR,
    )

    test_split = to_test.TaskCurriculum.SPLIT_TRAIN
    test_condition = "test_condition"
    test_curriculum_block = "test_block"
    test_tasks = _build_default_tasks()
    task_curriculum.add_tasks(
        split=test_split,
        condition=test_condition,
        curriculum_block=test_curriculum_block,
        tasks=test_tasks,
    )
    assert len(task_curriculum.get_all_tasks()) == len(test_tasks)


def test_task_curriculum_get_curriculum_summary():
    test_curriculum_id = "test_id"
    task_curriculum = to_test.TaskCurriculum(
        curriculum_id=test_curriculum_id,
        task_generator_name=DEFAULT_TEST_TASK_GENERATOR,
    )

    test_split = to_test.TaskCurriculum.SPLIT_TRAIN
    test_condition = "test_condition"
    test_curriculum_block = "test_block"
    test_tasks = _build_default_tasks()
    task_curriculum.add_tasks(
        split=test_split,
        condition=test_condition,
        curriculum_block=test_curriculum_block,
        tasks=test_tasks,
    )

    summary = task_curriculum.get_curriculum_summary()
    for split in task_curriculum.curriculum:
        assert split == test_split
        for condition in task_curriculum.curriculum[split]:
            assert test_condition in condition
            for curriculum_block in task_curriculum.curriculum[split][condition]:
                assert test_curriculum_block in curriculum_block
                task_image_names = summary[split][condition][curriculum_block]
                assert len(test_tasks) == len(task_image_names)
                for test_task in test_tasks:
                    assert test_task.name + ".png" in task_image_names


def test_tasks_generator():
    task_generator = to_test.TasksGeneratorRegistry[DEFAULT_TEST_TASK_GENERATOR]

    task_curriculum = task_generator.generate_tasks_curriculum(
        num_tasks_to_generate_per_condition=1
    )
    test_tasks = _build_default_tasks()
    for split in task_curriculum.curriculum:
        for condition in task_curriculum.curriculum[split]:
            for curriculum_block in task_curriculum.curriculum[split][condition]:
                curriculum_tasks = task_curriculum.curriculum[split][condition][
                    curriculum_block
                ]
                assert len(test_tasks) == len(curriculum_tasks)
                for idx, test_task in enumerate(test_tasks):
                    assert test_task.name == curriculum_tasks[idx].name


def test_tasks_generator_get_number_tasks_to_generate_per_condition():
    task_generator = to_test.TasksGeneratorRegistry[DEFAULT_TEST_TASK_GENERATOR]
    test_number_tasks_to_generate_per_condition = [
        (
            len(task_generator._generate_strokes_for_stimuli()),
            to_test.AbstractTasksGenerator.GENERATE_ALL,
        ),
        (1, 1),
        (5, 5),
    ]

    for (
        test_num_to_generate,
        test_human_readable_num_to_generate,
    ) in test_number_tasks_to_generate_per_condition:
        (
            num_to_generate,
            human_readable_num_to_generate,
        ) = task_generator._get_number_tasks_to_generate_per_condition(
            test_human_readable_num_to_generate
        )
        assert test_num_to_generate == num_to_generate
        assert test_human_readable_num_to_generate == human_readable_num_to_generate


def test_manual_curriculum_tasks_generator_load_tasks_from_existing_generator():
    existing_generator = to_test.TasksGeneratorRegistry[DEFAULT_TEST_TASK_GENERATOR]
    manual_generator = to_test.TasksGeneratorRegistry[
        DEFAULT_MANUAL_CURRICULUM_TASK_GENERATOR
    ]

    existing_tasks = existing_generator._generate_tasks()

    def check_same_tasks(tasks_array_1, tasks_array_2):
        for task_1, task_2 in zip(tasks_array_1, tasks_array_2):
            assert task_1 == task_2

    # Test load ALL
    all_tasks = manual_generator._load_tasks_from_existing_generator(
        existing_generator_name=DEFAULT_TEST_TASK_GENERATOR,
        task_ids=to_test.AbstractTasksGenerator.GENERATE_ALL,
    )
    check_same_tasks(existing_tasks, all_tasks)

    # Test load 1
    some_tasks = manual_generator._load_tasks_from_existing_generator(
        existing_generator_name=DEFAULT_TEST_TASK_GENERATOR, task_ids=[0]
    )
    check_same_tasks([existing_tasks[0]], all_tasks)


def test_intersect_numpy_array_renders_for_tasks():
    default_generator_1 = DEFAULT_TEST_TASK_GENERATOR + "1"
    default_generator_2 = DEFAULT_TEST_TASK_GENERATOR + "2"
    test_tasks_1 = _build_default_tasks(
        test_task_id=DEFAULT_TEST_TASK_ID, task_generator_name=default_generator_1
    )
    test_tasks_2 = _build_default_tasks(
        test_task_id=DEFAULT_TEST_TASK_ID, task_generator_name=default_generator_2
    )
    manual_generator = to_test.TasksGeneratorRegistry[
        DEFAULT_MANUAL_CURRICULUM_TASK_GENERATOR
    ]
    sets_to_intersect = [test_tasks_1, test_tasks_2]
    intersecting_tasks = manual_generator._intersect_numpy_array_renders_for_tasks(
        sets_to_intersect
    )

    assert len(intersecting_tasks) == len(test_tasks_1)
    for task in intersecting_tasks:
        assert len(task.possible_ground_truth_strokes) == len(sets_to_intersect)
        assert len(task.possible_ground_truth_programs) == len(sets_to_intersect)
        assert to_test.AbstractTasksGenerator.INTERSECT in task.name
        assert default_generator_1 in task.name
        assert default_generator_2 in task.name
