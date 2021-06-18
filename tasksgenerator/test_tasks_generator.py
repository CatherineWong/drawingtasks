"""test_tasks_generator.py | Author: Catherine Wong"""

import tasksgenerator.tasks_generator as to_test
from dreamcoder.program import Program
from dreamcoder.grammar import Grammar
import primitives.object_primitives as object_primitives


DEFAULT_TEST_TASK_ID = "test_tasks"
DEFAULT_TEST_TASK_GENERATOR = "test_tasks_generator"


@to_test.TasksGeneratorRegistry.register
class TestTasksGenerator(to_test.AbstractTasksGenerator):
    name = DEFAULT_TEST_TASK_GENERATOR

    def __init__(self):
        grammar = Grammar.uniform(object_primitives.objects)
        super(TestTasksGenerator, self).__init__(grammar=grammar)

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


def _build_default_tasks():
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
    return [test_task]


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
