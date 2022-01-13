"""
generate_libraries.py | Author: Catherine Wong.

Utility script to generate libraries over program domains.
Augments the summary file with additional library columns and writes out libraries (and metadata) to data/libraries.

Usage:
    python data/generate_libraries.py
        --task_summaries nuts_bolts_programs_all
        --program_column dreamcoder_program_dsl_0
        --pretty_print_program_columns
"""

import random
import itertools
import csv, os, json, argparse, sys
from dreamcoder.task import Task
from dreamcoder.frontier import Frontier
from dreamcoder.compression import ocamlInduce
from dreamcoder.utilities import get_root_dir
import numpy as np

from primitives.gadgets_primitives import *
from dreamcoder.grammar import Grammar
from dreamcoder.program import Program, prettyProgram

random.seed(0)
np.random.seed(0)

DEFAULT_DATA_DIR = "data"
DEFAULT_LIBRARIES_DIR = f"{DEFAULT_DATA_DIR}/libraries"
DEFAULT_SUMMARIES_DIR = f"{DEFAULT_DATA_DIR}/summaries"
DEFAULT_TASK_SUMMARIES_TASK_COLUMN = "s3_stimuli"
FIELDNAMES = "fieldnames"

DEFAULT_PROGRAM_COLUMN = "dreamcoder_program_dsl_0"
LIBRARY = "library"
DEFAULT_MAX_LIBRARIES = 5
METADATA = "metadata"
COMPRESSION_ARGS = "compression_args"
MASKED_TO_ORIGINAL = "masked_to_original"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--export_dir",
    default=DEFAULT_LIBRARIES_DIR,
    help="If provided, alternate directory to export the library results.",
)
parser.add_argument(
    "--task_summaries_dir",
    default=DEFAULT_SUMMARIES_DIR,
    help="If provided, alternate directory to read in summaries of tasks.",
)
parser.add_argument(
    "--task_summaries",
    required=True,
    help="Original CSV containing task summaries data.",
)
parser.add_argument(
    "--task_summaries_task_column",
    default=DEFAULT_TASK_SUMMARIES_TASK_COLUMN,
    help="Column in the task summaries CSV containing the task name to join on.",
)
parser.add_argument(
    "--program_column",
    default=DEFAULT_PROGRAM_COLUMN,
    help="Column in the task summaries CSV containing the program to begin compression from.",
)
parser.add_argument(
    "--program_columns",
    nargs="+",
    default=[DEFAULT_PROGRAM_COLUMN],
    help="Column in the task summaries CSV containing the program to begin compression from.",
)
parser.add_argument(
    "--max_libraries",
    type=int,
    default=DEFAULT_MAX_LIBRARIES,
    help="How many libraries to generate.",
)
parser.add_argument(
    "--pretty_print_program_columns",
    action="store_true",
    help="If true, just writes out a summaries dict with pretty printed columns attached.",
)


def get_summaries_dict(args):
    task_csv = os.path.join(args.task_summaries_dir, args.task_summaries + ".csv")
    summaries_dict = {}
    with open(task_csv) as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            task = row[args.task_summaries_task_column]
            summaries_dict[task] = dict(row)
    print(f"...read summary rows from {len(summaries_dict)} tasks.")
    fieldnames = csv_reader.fieldnames
    return summaries_dict, fieldnames


def get_libraries_dict(args):
    libraries_dict = {}
    for program_column in args.program_columns:
        summaries_name = args.task_summaries.replace("_libraries", "")
        library_json = f"{summaries_name}_{program_column}.json"
        with open(os.path.join(args.export_dir, library_json)) as f:
            library_dict = json.load(f)
        libraries_dict[program_column] = library_dict
    print(f"...read libraries for {len(libraries_dict)} libraries.")
    return libraries_dict


def get_pretty_printed_program(program, library):
    substitution_dict = {v: k for (k, v) in library["masked_to_original"].items()}

    # Is this insane?
    for k in sorted(substitution_dict.keys(), key=lambda k: -len(k)):
        program = program.replace(k, substitution_dict[k])
    return program


def pretty_print_program_columns(args, summaries_dict, libraries_dict, fieldnames):
    for program_column in args.program_columns:
        for task in summaries_dict:
            pretty_print_program = get_pretty_printed_program(
                summaries_dict[task][program_column], libraries_dict[program_column]
            )
            pretty_name = (
                program_column.split("_")[:-1]
                + ["pretty"]
                + [program_column.split("_")[-1]]
            )
            pretty_name = "_".join(pretty_name)
            summaries_dict[task][f"{pretty_name}"] = pretty_print_program
        if pretty_name not in fieldnames:
            fieldnames += [pretty_name]

    # Export the summary.
    task_csv = os.path.join(args.task_summaries_dir, args.task_summaries + ".csv")
    with open(task_csv, "w") as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        for task in summaries_dict:
            csv_writer.writerow(summaries_dict[task])

    print(f"...wrote summary to {task_csv}.")
    return summaries_dict, fieldnames


def build_frontier_from_summary_row(row):
    program = row[args.program_column]
    program = Program.parse(program)
    program_type = program.infer()

    # Construct task.
    task = Task(
        name=row[args.task_summaries_task_column], request=program_type, examples=[]
    )
    # Construct frontier
    frontier = Frontier.dummy(program=program, tp=program_type)
    frontier.task = task
    return frontier


def get_frontier_program(frontier):
    return frontier.entries[0].program


def get_initial_frontiers_and_library(args, summaries_dict):  # Load the library.
    library_json = f"{args.task_summaries}_{args.program_column}.json"
    with open(os.path.join(args.export_dir, library_json)) as f:
        libraries_dict = json.load(f)
    libraries_dict[LIBRARY] = Grammar.fromJson(libraries_dict[LIBRARY])

    # Build generic tasks from all of the programs.
    tasks_dict = {}
    for task, row in summaries_dict.items():
        tasks_dict[task] = build_frontier_from_summary_row(row)

    print("Initial library: ")
    print(libraries_dict[LIBRARY])

    print(f"...Loaded {len(tasks_dict)} initial tasks.")
    return tasks_dict, libraries_dict


def combined_libraries(libraries):
    productions = set(
        itertools.chain.from_iterable(
            [[p for (_, _, p) in library.productions] for library in libraries]
        )
    )
    print(f"Combining into a total of {len(productions)} productions.")
    return Grammar.uniform(productions)


def run_iteration_library_compression(
    args,
    tasks_dict,
    library_dict,
    parallel_bucket_size=5,
    max_cutoff=250,
    timeout_mins=10,
):
    shuffled_tasks = sorted(list(tasks_dict.keys()))[:max_cutoff]
    # random.shuffle(shuffled_tasks)
    sorted_frontiers = [tasks_dict[t] for t in shuffled_tasks][:max_cutoff]

    num_buckets = int(len(shuffled_tasks) / parallel_bucket_size)

    bucketized_frontiers = np.array_split(sorted_frontiers, num_buckets)

    new_libraries = []
    for idx, bucket_frontiers in enumerate(bucketized_frontiers):
        print(
            f"Now on bucket: {idx}/{len(bucketized_frontiers)}: of {len(bucket_frontiers)} frontiers. Timeout mins: {timeout_mins}"
        )
        new_library, new_frontiers = ocamlInduce(
            g=library_dict[LIBRARY],
            frontiers=bucket_frontiers,
            **library_dict[METADATA][COMPRESSION_ARGS],
            timeout=timeout_mins * 60,
        )
        for f in new_frontiers:
            tasks_dict[f.task.name] = f
        new_libraries.append(new_library)
    # Finally, coalesce all of the batched libraries.
    library_dict[LIBRARY] = combined_libraries(new_libraries)
    return tasks_dict, library_dict


def get_iteration_program_column(args, iteration):
    next_iteration_program_column = "_".join(
        args.program_column.split("_")[:-1] + [str(iteration)]
    )
    return next_iteration_program_column


def export_library(args, library_dict, iteration):
    next_iteration_program_column = get_iteration_program_column(args, iteration)
    library_json = f"{args.task_summaries}_{next_iteration_program_column}.json"

    # Write the original JSON grammar.
    original_grammar = library_dict[LIBRARY]
    library_dict[LIBRARY] = library_dict[LIBRARY].json()
    with open(os.path.join(args.export_dir, library_json), "w") as f:
        json.dump(library_dict, f)
    print(f"...exported library to: {library_json}")

    library_dict[LIBRARY] = original_grammar


def export_summary(
    args, summaries_dict, library_dict, frontiers_dict, iteration, fieldnames
):
    for task in frontiers_dict:
        next_iteration_program_column = get_iteration_program_column(args, iteration)
        task_program = get_frontier_program(frontiers_dict[task])
        summaries_dict[task][
            next_iteration_program_column
        ] = task_program  # TODO: escape.
        summaries_dict[task][next_iteration_program_column + "_tokens"] = library_dict[
            LIBRARY
        ].mask_invention_tokens(task_program.left_order_tokens())

    # Modify the summaries.
    task_csv = os.path.join(
        args.task_summaries_dir, args.task_summaries + "_libraries.csv"
    )
    fieldnames += [
        next_iteration_program_column,
        next_iteration_program_column + "_tokens",
    ]
    with open(task_csv, "w") as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        for task in summaries_dict:
            csv_writer.writerow(summaries_dict[task])

    print(f"...wrote summary to {task_csv}.")
    return summaries_dict, fieldnames


def run_and_export_all_library_compression(
    args, summaries_dict, frontiers_dict, library_dict, fieldnames
):
    print(
        f"...Running compressor with kwargs: {library_dict[METADATA][COMPRESSION_ARGS]}"
    )
    for library_iteration in range(1, args.max_libraries + 1):
        print(f"...running library compression at iteration: {library_iteration}")
        frontiers_dict, library_dict = run_iteration_library_compression(
            args,
            frontiers_dict,
            library_dict,
        )
        # Rewrite all of the library functions under new tokens.
        library_dict[MASKED_TO_ORIGINAL] = library_dict[LIBRARY].masked_to_original

        export_library(args, library_dict, library_iteration)
        summaries_dict, fieldnames = export_summary(
            args,
            summaries_dict,
            library_dict,
            frontiers_dict,
            library_iteration,
            fieldnames,
        )


def main(args):
    summaries_dict, fieldnames = get_summaries_dict(args)
    libraries_dict = get_libraries_dict(args)

    if args.pretty_print_program_columns:
        pretty_print_program_columns(args, summaries_dict, libraries_dict, fieldnames)
        sys.exit(0)

    frontiers_dict, library_dict = get_initial_frontiers_and_library(
        args, summaries_dict
    )
    run_and_export_all_library_compression(
        args, summaries_dict, frontiers_dict, library_dict, fieldnames
    )


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
