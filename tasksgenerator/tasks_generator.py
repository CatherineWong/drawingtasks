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

DEFAULT_DRAWING_TASK_GENERATOR = "drawing"

TasksGeneratorRegistry = ClassRegistry("name", unique=True)


class AbstractTasksGenerator:
    """TasksGenerators should define the 'name' class attribute and register using TasksGeneratoryRegistry.register"""

    def __init__(self, grammar):
        self.grammar = grammar

    def generate_tasks_curriculum(self, num_tasks_to_generate_per_condition):
        """:ret: TaskCurriculum"""
        raise NotImplementedError


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
        task_name = f"{task_generator_name}_{task_id}"
        super(DrawingTask, self).__init__(task_name, request, examples=[], features=[])

        self.ground_truth_program = ground_truth_program
        self.ground_truth_strokes = ground_truth_strokes
        self.rendering = rendering
        self.render_parsed_program = render_parsed_program_fn
        if self.rendering is None:
            if self.ground_truth_program is not None:
                self.rendering = render_parsed_program_fn(ground_truth_program)
            elif self.ground_truth_strokes is not None:
                self.rendering = render_strokes_fn(ground_truth_strokes)
        assert self.rendering is not None

    def _normalized_pixel_loss(self, img1, img2):
        return np.linalg.norm(img2 - img1)

    def logLikelihood(self, parsed_program, timeout=None):
        if not hasattr(parsed_program, "rendering"):
            parsed_program.rendering = self.render_parsed_program(parsed_program)

        loss = self._normalized_pixel_loss(self.rendering, parsed_program.rendering)
        if loss > 0.1:
            return NEGATIVEINFINITY
        else:
            return 0.0


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
