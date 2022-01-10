"""tasks_generator.py | Author: Catherine Wong

Defines the AbstractTasksGenerator class for generative models that return curricula of DrawingTasks.
Defines the TasksGeneratorRegistry for registering and using new TasksGenerators.

Defines the DrawingTask and DrawingTaskCurriculum classes.
"""
import datetime
import numpy as np
from collections import defaultdict
from class_registry import ClassRegistry
from dreamcoder.utilities import NEGATIVEINFINITY
from dreamcoder.task import Task
from dreamcoder.program import Program
import math, random, itertools, copy

DEFAULT_DRAWING_TASK_GENERATOR = "drawing"
PROGRAMS_NAME = "programs"  # If in name, this has programs.

TasksGeneratorRegistry = ClassRegistry("name", unique=True)

RANDOM_SEED = 0
random.seed(RANDOM_SEED)


def random_sample_ratio_ordered_array(array, train_ratio, strings_array=None):
    """Utility function to randomly sample a ratio from an ordered array, preserving order.
    Optionally can be paseed a set of strings as well.
    Returns [train], [test]"""
    sample_size = int(len(array) * train_ratio)
    indices_to_sample = sorted(random.sample(range(len(array)), sample_size))
    train, test = [], []
    train_strings, test_strings = [], []
    for i in range(len(array)):
        if i in indices_to_sample:
            train.append(array[i])
            if strings_array is not None:
                train_strings.append(strings_array[i])
        else:
            test.append(array[i])
            if strings_array is not None:
                test_strings.append(strings_array[i])
    if strings_array is not None:
        return train, test, train_strings, test_strings

    return train, test


class TaskCurriculum:
    """
    TaskCurriculum: data structure for curricula of tasks.
    curriculum : {
        split : { condition :
            curriculum_block : [array of tasks]
            }
    }
    """

    CURRICULUM_BLOCK_PREFIX = "curriculum"
    CONDITION_BLOCK_PREFIX = "condition"
    CONDITION_ALL = "all"
    SPLIT_TRAIN, SPLIT_TEST = "train", "test"
    METADATA = "metadata"

    def __init__(
        self, curriculum_id=None, task_generator_name=DEFAULT_DRAWING_TASK_GENERATOR
    ):
        timestamp = datetime.datetime.now().isoformat()
        # Escape the timestamp.
        timestamp = timestamp.replace(":", "-")
        timestamp = timestamp.replace(".", "-")

        self.name = f"{task_generator_name}_{curriculum_id}"
        self.timestamp = timestamp
        self.curriculum = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    def add_tasks(self, split, condition, curriculum_block, tasks):
        condition = f"{TaskCurriculum.CONDITION_BLOCK_PREFIX}_{condition}"
        curriculum_block = (
            f"{TaskCurriculum.CURRICULUM_BLOCK_PREFIX}_{curriculum_block}"
        )

        self.curriculum[split][condition][curriculum_block] += tasks

    def get_curriculum(self):
        return self.curriculum

    def get_all_tasks(self):
        tasks_set = set()
        for split in self.curriculum:
            for condition in self.curriculum[split]:
                for curriculum_block in self.curriculum[split][condition]:
                    block_tasks = self.curriculum[split][condition][curriculum_block]
                    tasks_set.update(block_tasks)
        return tasks_set

    def get_curriculum_summary(self):
        metadata = {"name": self.name, "timestamp": self.timestamp}

        curriculum_summary = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for split in self.curriculum:
            for condition in self.curriculum[split]:
                for curriculum_block in self.curriculum[split][condition]:
                    tasks = self.curriculum[split][condition][curriculum_block]
                    task_image_names = [task.name + ".png" for task in tasks]
                    curriculum_summary[split][condition][
                        curriculum_block
                    ] += task_image_names
        curriculum_summary[TaskCurriculum.METADATA] = metadata
        return curriculum_summary

    def cleaned_name(self, name):
        # Cleans characters for S3.
        name = name.lower()
        for escaped_character in ["_", ","]:
            name = name.replace(escaped_character, "-")
        return name

    def get_curriculum_tasks_csv_summary(self):
        """
        Generates a flattened summary of the tasks that can be written out to a CSV. This contains information specific to the upload version on S3.
        """
        domain = self.cleaned_name(self.name.split(f"_{PROGRAMS_NAME}")[0])
        s3_domain = f"https://lax-drawing-{domain}-all.s3.amazonaws.com/"
        all_tasks = []
        for split in ["test", "train"]:
            for condition in self.curriculum[split]:
                for curriculum_block in self.curriculum[split][condition]:
                    tasks = self.curriculum[split][condition][curriculum_block]
                    task_summaries = [task.task_summary() for task in tasks]
                    all_tasks += task_summaries
        # FWIW, add back in the canonical indexing from S3.
        for idx, task_dict in enumerate(all_tasks):
            s3_idx = str.zfill(str(idx), 3)
            s3_name = s3_domain + f"lax-drawing-{domain}-all-{s3_idx}.png"
            task_dict["s3_stimuli"] = s3_name
        return all_tasks


class AbstractTasksGenerator:
    """TasksGenerators should define the 'name' class attribute and register using TasksGeneratoryRegistry.register"""

    GENERATE_ALL = "all"
    INTERSECT = "intersect"

    def __init__(self, grammar):
        self.grammar = grammar

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        """:ret: TaskCurriculum"""
        raise NotImplementedError

    def _generate_strokes_for_stimuli(self):
        """Helper method that generates an array of stimuli as stroke arrays."""
        raise NotImplementedError

    def _get_number_tasks_to_generate_per_condition(
        self, num_tasks_to_generate_per_condition, train_ratio
    ):
        """Helper method that returns the true number of tasks to generate and a human readable name. Generator must have defined an _generate_strokes_for_stimuli function."""
        if PROGRAMS_NAME in self.name:
            train, test, _, _ = self._generate_strokes_strings_for_stimuli(train_ratio)
        else:
            train, test = self._generate_strokes_for_stimuli(train_ratio)
        num_total_tasks = len(train + test)
        num_to_generate = (
            num_tasks_to_generate_per_condition
            if num_tasks_to_generate_per_condition
            != AbstractTasksGenerator.GENERATE_ALL
            else num_total_tasks
        )
        human_readable_num_to_generate = num_tasks_to_generate_per_condition
        return num_to_generate, human_readable_num_to_generate

    def _generate_drawing_tasks_from_strokes(
        self,
        num_tasks_to_generate_per_condition,
        request_type,
        render_strokes_fn=None,
        task_generator_name=None,
        train_ratio=1.0,
        render_parsed_program_fn=None,
    ):
        """Helper method to generate Drawing Tasks from strokes arrays. Deprecated: number to generate."""
        (
            num_to_generate,
            human_readable_num_to_generate,
        ) = self._get_number_tasks_to_generate_per_condition(
            num_tasks_to_generate_per_condition, train_ratio
        )

        if render_parsed_program_fn is None:
            # No program; generate from strokes.
            train_tasks, test_tasks = self._generate_strokes_for_stimuli(train_ratio)
            train_tasks = [
                DrawingTask(
                    task_id=task_idx,
                    request=request_type,
                    ground_truth_strokes=task_strokes,
                    render_strokes_fn=render_strokes_fn,
                    task_generator_name=task_generator_name
                    + f"_{TaskCurriculum.SPLIT_TRAIN}",
                    render_parsed_program_fn=render_parsed_program_fn,
                )
                for (task_idx, task_strokes) in enumerate(train_tasks)
            ]

            test_tasks = [
                DrawingTask(
                    task_id=task_idx,
                    request=request_type,
                    ground_truth_strokes=task_strokes,
                    render_strokes_fn=render_strokes_fn,
                    task_generator_name=task_generator_name
                    + f"_{TaskCurriculum.SPLIT_TEST}",
                    render_parsed_program_fn=render_parsed_program_fn,
                )
                for (task_idx, task_strokes) in enumerate(test_tasks)
            ]
        else:
            (
                train_tasks,
                test_tasks,
                train_strings,
                test_strings,
            ) = self._generate_strokes_strings_for_stimuli(train_ratio)

            train_tasks = [
                DrawingTask(
                    task_id=task_idx,
                    request=request_type,
                    ground_truth_strokes=task_strokes,
                    ground_truth_program=task_program,
                    render_strokes_fn=render_strokes_fn,
                    task_generator_name=task_generator_name
                    + f"_{TaskCurriculum.SPLIT_TRAIN}",
                    render_parsed_program_fn=render_parsed_program_fn,
                )
                for (task_idx, (task_strokes, task_program)) in enumerate(
                    zip(train_tasks, train_strings)
                )
            ]

            test_tasks = [
                DrawingTask(
                    task_id=task_idx,
                    request=request_type,
                    ground_truth_strokes=task_strokes,
                    ground_truth_program=task_program,
                    render_strokes_fn=render_strokes_fn,
                    task_generator_name=task_generator_name
                    + f"_{TaskCurriculum.SPLIT_TEST}",
                    render_parsed_program_fn=render_parsed_program_fn,
                )
                for (task_idx, (task_strokes, task_program)) in enumerate(
                    zip(test_tasks, test_strings)
                )
            ]

        return train_tasks, test_tasks


class ManualCurriculumTasksGenerator(AbstractTasksGenerator):
    """TaskGenerator with utility functions for loading and creating task curricula based on other task generators."""

    def __init__(self, grammar):
        super().__init__(grammar=grammar)

    def _load_tasks_from_existing_generator(self, existing_generator_name, task_ids):
        """Loads task_ids (or ALL if task_ids is ALL) from the generator with existing_generator_name in the registry. Generator must have a _generate_tasks function that returns ID-d tasks."""
        existing_generator = TasksGeneratorRegistry[existing_generator_name]
        existing_tasks = existing_generator._generate_tasks()
        if task_ids == AbstractTasksGenerator.GENERATE_ALL:
            return existing_tasks
        else:
            return [existing_tasks[id] for id in task_ids]

    def _intersect_numpy_array_renders_for_tasks(self, task_sets):
        """Generates new tasks based on those that have intersecting renderings. Returns [array of DrawingTasks] with the name intersect_[generator_0]_[generator_1]... based on the intersection. Assumes renders are a numpy array and looks for an exact intersection."""

        def get_intersected_generator_name_for_tasks(tasks):
            task_generators = sorted(list(set([t.task_generator_name for t in tasks])))
            intersect_generator_name = (
                AbstractTasksGenerator.INTERSECT + "_" + "_".join(task_generators)
            )
            return intersect_generator_name

        rendering_intersection = defaultdict(list)

        for task_set in task_sets:
            for task in task_set:
                hashable_rendering = task.rendering.tostring()
                rendering_intersection[hashable_rendering].append(task)
        new_intersected_tasks = []
        for _, same_rendering_tasks in rendering_intersection.items():
            if len(same_rendering_tasks) < 2:
                continue
            else:
                intersected_task_idx = len(new_intersected_tasks)
                original_base_task = same_rendering_tasks[0]
                new_base_task = DrawingTask(
                    task_id=intersected_task_idx,
                    request=original_base_task.request,
                    ground_truth_program=original_base_task.ground_truth_program,
                    render_parsed_program_fn=original_base_task.render_parsed_program,
                    render_strokes_fn=original_base_task.render_strokes,
                    rendering=original_base_task.rendering,
                    task_generator_name=get_intersected_generator_name_for_tasks(
                        same_rendering_tasks
                    ),
                )
                new_base_task.possible_ground_truth_programs = [
                    t.ground_truth_program for t in same_rendering_tasks
                ]
                new_base_task.possible_ground_truth_strokes = [
                    t.ground_truth_strokes for t in same_rendering_tasks
                ]
                new_intersected_tasks.append(new_base_task)
        return new_intersected_tasks


class DrawingTask(Task):
    def __init__(
        self,
        task_id,
        request,
        ground_truth_program=None,
        ground_truth_strokes=None,
        render_parsed_program_fn=None,
        render_strokes_fn=None,
        rendering=None,
        task_generator_name=DEFAULT_DRAWING_TASK_GENERATOR,
    ):
        padded_index = str.zfill(str(task_id), 3)

        if PROGRAMS_NAME in task_generator_name:
            task_name = task_generator_name.split(f"_{PROGRAMS_NAME}")[0]
            task_name = f"{task_name}_{padded_index}"
        else:
            task_name = f"{task_generator_name}_{padded_index}"
        super(DrawingTask, self).__init__(task_name, request, examples=[], features=[])

        self.task_generator_name = task_generator_name
        self.ground_truth_program = (
            ground_truth_program  # Single canonical ground truth program
        )
        self.ground_truth_strokes = (
            ground_truth_strokes  # Single canonical ground truth strokes
        )
        self.possible_ground_truth_programs = [
            ground_truth_program
        ]  # For multiple ambiguous parses.
        self.possible_ground_truth_strokes = [ground_truth_strokes]
        self.rendering = rendering
        self.render_parsed_program = render_parsed_program_fn
        self.render_strokes = render_strokes_fn
        if self.rendering is None:
            if self.ground_truth_program is not None:
                self.rendering = render_parsed_program_fn(ground_truth_program)
            elif self.ground_truth_strokes is not None:
                self.rendering = render_strokes_fn(ground_truth_strokes)
        assert self.rendering is not None

    def task_summary(self):
        strokes = (
            self.ground_truth_strokes if self.ground_truth_strokes is not None else []
        )
        program = (
            self.ground_truth_program if self.ground_truth_program is not None else ""
        )
        program_tokens = self._tokenize_program(program)
        return {
            "task_name": self.name,
            "task_generator": self.task_generator_name,
            "dreamcoder_program_dsl_0": str(program),
            "dreamcoder_program_dsl_0_tokens": program_tokens,
            "ground_truth_strokes": [strokes],
            "n_strokes": len(strokes),
        }

    def _tokenize_program(self, program):
        if program == "":
            return program
        if type(program) == str:
            program = Program.parse(program)
        return program.left_order_tokens(show_vars=True)

    def _normalized_pixel_loss(self, img1, img2):
        return np.linalg.norm(img2 - img1)

    def logLikelihood(
        self,
        parsed_program,
        timeout=None,
        loss_fn=None,
        min_threshold=0.1,
    ):
        """Log likelihood function for programs."""
        if not hasattr(parsed_program, "rendering"):
            parsed_program.rendering = self.render_parsed_program(parsed_program)

        loss = loss_fn(self.rendering, parsed_program.rendering)
        if loss > min_threshold:
            return NEGATIVEINFINITY
        else:
            return 0.0

    def _show_and_evaluate_program_for_task(
        self,
        parsed_program_or_program_string,
        timeout=None,
        loss_fn=None,
        min_threshold=0.1,
        output_directory=None,
    ):
        """Helper function for verifying potential programs for a task."""
        # TODO
        pass
