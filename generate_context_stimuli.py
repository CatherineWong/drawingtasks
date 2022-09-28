import tasksgenerator.furniture_context_tasks_generator
import os, json, argparse, dill
import pathlib
import tasksgenerator.tasks_generator as tasks_generator
from primitives.object_primitives import export_rendered_program

import tasksgenerator.s12_s13_tasks_generator
import tasksgenerator.s14_s15_tasks_generator
import tasksgenerator.s16_s17_tasks_generator

import tasksgenerator.nuts_bolts_tasks_generator
import tasksgenerator.wheels_tasks_generator
import tasksgenerator.furniture_tasks_generator

import tasksgenerator.dial_programs_task_generator
import tasksgenerator.nuts_bolts_programs_tasks_generator
import tasksgenerator.wheels_programs_tasks_generator
import tasksgenerator.furniture_programs_tasks_generator

import tasksgenerator.nuts_bolts_synthetic_language_tasks_generator

import tasksgenerator.furniture_context_tasks_generator

DEFAULT_EXPORT_DIR = "data"
DEFAULT_SUMMARIES_SUBDIR = "summaries"
DEFAULT_SYNTHESIS_TASKS_SUBDIR = "synthesis"
DEFAULT_RENDERS_SUBDIR = "renders"
GENERATING_COMMAND = "generating_command"
COMMAND_PREFIX = "python generate_drawing_tasks.py "
DEFAULT_LIBRARIES_DIR = f"{DEFAULT_EXPORT_DIR}/libraries"


parser = argparse.ArgumentParser()
parser.add_argument(
    "--task_export_dir",
    default=DEFAULT_EXPORT_DIR,
    help="Top level directory to export task data.",
)
parser.add_argument(
    "--synthesis_export_dir",
    default=None,
    help="If provided, alternate directory to write out the synthesis tasks.",
)
parser.add_argument(
    "--summaries_export_dir",
    default=None,
    help="If provided, alternate directory to write out summaries of tasks.",
)
parser.add_argument(
    "--libraries_export_dir",
    default=DEFAULT_LIBRARIES_DIR,
    help="If provided, alternate directory to export the library results.",
)
parser.add_argument(
    "--renders_export_dir",
    default=None,
    help="If provided, alternate directory to write out the rendered images.",
)
parser.add_argument(
    "--tasks_generator",
    required=True,
    help="Name of the tasks generator. Must be a registered generator.",
)
parser.add_argument(
    "--num_tasks_per_condition",
    default=tasks_generator.AbstractTasksGenerator.GENERATE_ALL,
    help="If included, enumerate only a set number of tasks from the generator.",
)
parser.add_argument(
    "--train_ratio",
    default=1.0,
    help="If included, split between train and test qt thsi ratio.",
)
parser.add_argument(
    "--no_synthesis_tasks",
    action="store_true",
    help="If included, does not export any synthesis tasks.",
)
parser.add_argument(
    "--no_render", action="store_true", help="If included, does not render any images.",
)
parser.add_argument(
    "--task_summaries",
    action="store_true",
    help="If included, writes out a task summary csv.",
)


def generate_tasks_curriculum(args):
    print(f"Generating task curriculum from: {args.tasks_generator}...")
    print(f"Generating {args.num_tasks_per_condition} tasks per condition...")
    generator = tasks_generator.TasksGeneratorRegistry[args.tasks_generator]
    tasks_curriculum = generator.generate_tasks_curriculum(
        args.num_tasks_per_condition, float(args.train_ratio)
    )
    return tasks_curriculum


def main(args):
    generate_tasks_curriculum(args)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
