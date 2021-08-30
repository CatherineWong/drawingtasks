"""generate_drawing_tasks.py | Author : Catherine Wong

Commandline utility for generating curricula of drawing tasks. Calls predefined TaskGenerators to jointly generate DrawingTasks for program synthesis, and corresponding images for human experiments.

By default, it exports:
	A set of Tasks to TASK_EXPORT_DIR/synthesis
	A set of images to TASK_EXPORT_DIR/human
    A tasks_curriculum_metadata.json file to TASK_EXPORT_DIR that contains the Curriculum and metadata.

Usage:
    python generate_drawing_tasks.py
            --task_export_dir: where to write out the tasks; by default it writes out to subdirectories called synthesis/ and human/ where human contains the high-resolution images.
            
            --synthesis_export_dir: where to write out the synthesis tasks, if not the task_export_dir.
    		--renders_export_subdir: where to write out the images, if not the task_export_dir.

    		--tasks_generator : name of the task generator to use.
    		--num_tasks_per_condition: if included, enumerate only a set number of tasks from the generator.	
            --no_render: if included, does not render any images (and leaves the human directory blank.)
"""

import os, json, argparse, dill
import pathlib
import tasksgenerator.tasks_generator as tasks_generator
from primitives.object_primitives import export_rendered_program

import tasksgenerator.s12_s13_tasks_generator
import tasksgenerator.s14_s15_tasks_generator
import tasksgenerator.s16_s17_tasks_generator

import tasksgenerator.nuts_bolts_tasks_generator
import tasksgenerator.wheels_tasks_generator

DEFAULT_EXPORT_DIR = "data"
DEFAULT_SYNTHESIS_TASKS_SUBDIR = "synthesis"
DEFAULT_RENDERS_SUBDIR = "renders"
GENERATING_COMMAND = "generating_command"
COMMAND_PREFIX = "python generate_drawing_tasks.py "

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
    "--no_render",
    action="store_true",
    help="If included, does not render any images.",
)


def generate_tasks_curriculum(args):
    print(f"Generating task curriculum from: {args.tasks_generator}...")
    print(f"Generating {args.num_tasks_per_condition} tasks per condition...")
    generator = tasks_generator.TasksGeneratorRegistry[args.tasks_generator]
    tasks_curriculum = generator.generate_tasks_curriculum(
        args.num_tasks_per_condition, float(args.train_ratio)
    )
    return tasks_curriculum


def build_generating_command_string(args):
    command_string = " ".join(
        [f"--{arg_name} {arg_val}" for (arg_name, arg_val) in vars(args).items()]
    )
    return COMMAND_PREFIX + command_string


def export_curriculum_summary(args, tasks_curriculum):
    pathlib.Path(args.task_export_dir).mkdir(parents=True, exist_ok=True)
    curriculum_summary = tasks_curriculum.get_curriculum_summary()
    curriculum_summary[tasks_generator.TaskCurriculum.METADATA][
        GENERATING_COMMAND
    ] = build_generating_command_string(args)
    num_tasks = args.num_tasks_per_condition
    curriculum_summary_name = f"{args.tasks_generator}_{num_tasks}"
    curriculum_summary_file = os.path.join(
        args.task_export_dir, curriculum_summary_name + ".json"
    )
    with open(curriculum_summary_file, "w") as f:
        json.dump(curriculum_summary, f, indent="")
    return curriculum_summary_file


def export_tasks(args, tasks_curriculum):
    synthesis_export_dir = (
        args.synthesis_export_dir
        if args.synthesis_export_dir
        else os.path.join(args.task_export_dir, DEFAULT_SYNTHESIS_TASKS_SUBDIR)
    )
    pathlib.Path(synthesis_export_dir).mkdir(parents=True, exist_ok=True)
    curriculum_tasks = tasks_curriculum.get_all_tasks()
    print(
        f"Writing {len(curriculum_tasks)} synthesis tasks out to: {synthesis_export_dir}"
    )
    for task in curriculum_tasks:
        task_export_name = os.path.join(synthesis_export_dir, task.name + ".pkl")
        with open(task_export_name, "wb") as f:
            dill.dump(task, f)
    return synthesis_export_dir


def export_rendered_images(args, tasks_curriculum):
    renders_export_dir = (
        args.renders_export_dir
        if args.renders_export_dir
        else os.path.join(args.task_export_dir, DEFAULT_RENDERS_SUBDIR)
    )
    pathlib.Path(renders_export_dir).mkdir(parents=True, exist_ok=True)
    curriculum_tasks = tasks_curriculum.get_all_tasks()
    print(f"Writing {len(curriculum_tasks)} renders out to: {renders_export_dir}")
    for task in curriculum_tasks:
        export_rendered_program(task.rendering, task.name, renders_export_dir)
    return renders_export_dir


def export_tasks_curriculum_data(args, tasks_curriculum):
    export_curriculum_summary(args, tasks_curriculum)

    if not args.no_synthesis_tasks:
        export_tasks(args, tasks_curriculum)

    if not args.no_render:
        export_rendered_images(args, tasks_curriculum)


def main(args):
    tasks_curriculum = generate_tasks_curriculum(args)
    export_tasks_curriculum_data(args, tasks_curriculum)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
