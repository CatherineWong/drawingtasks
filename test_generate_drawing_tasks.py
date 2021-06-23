"""test_generate_drawing_tasks.py | Author : Catherine Wong"""


import os
from types import SimpleNamespace as MockArgs

from tasksgenerator.test_tasks_generator import TestTasksGenerator
import src.generate_drawing_tasks as to_test


def test_generate_tasks_curriculum():
    mock_args = MockArgs(
        tasks_generator=TestTasksGenerator.name, num_tasks_per_condition=None
    )
    tasks_curriculum = to_test.generate_tasks_curriculum(mock_args)
    assert TestTasksGenerator.name in tasks_curriculum.name


def test_export_curriculum_summary(tmpdir):
    export_dir = tmpdir
    mock_args = MockArgs(
        task_export_dir=export_dir,
        tasks_generator=TestTasksGenerator.name,
        num_tasks_per_condition=None,
    )
    tasks_curriculum = to_test.generate_tasks_curriculum(mock_args)
    curriculum_summary_file = to_test.export_curriculum_summary(
        mock_args, tasks_curriculum
    )
    assert os.path.exists(curriculum_summary_file)


def test_build_generating_command_string():
    mock_args = MockArgs(
        test_args="test",
    )
    built_command = to_test.build_generating_command_string(mock_args)
    assert built_command == to_test.COMMAND_PREFIX + "--test_args test"


def test_export_tasks(tmpdir):
    export_dir = tmpdir
    mock_args = MockArgs(
        task_export_dir=export_dir,
        synthesis_export_dir=None,
        tasks_generator=TestTasksGenerator.name,
        num_tasks_per_condition=None,
    )
    tasks_curriculum = to_test.generate_tasks_curriculum(mock_args)
    synthesis_export_dir = to_test.export_tasks(mock_args, tasks_curriculum)
    for task in tasks_curriculum.get_all_tasks():
        task_file = os.path.join(synthesis_export_dir, task.name + ".pkl")
        assert os.path.exists(task_file)


def test_export_rendered_images(tmpdir):
    export_dir = tmpdir
    mock_args = MockArgs(
        task_export_dir=export_dir,
        renders_export_dir=None,
        tasks_generator=TestTasksGenerator.name,
        num_tasks_per_condition=None,
    )
    tasks_curriculum = to_test.generate_tasks_curriculum(mock_args)
    renders_export_dir = to_test.export_rendered_images(mock_args, tasks_curriculum)
    for task in tasks_curriculum.get_all_tasks():
        task_image_name = os.path.join(renders_export_dir, task.name + ".png")
        assert os.path.exists(task_image_name)
