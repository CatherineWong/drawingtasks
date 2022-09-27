"""
generate_structures_summary.py | Author: Catherine Wong

Utility script to pre-process the structures summaries into the standardized form.

Usage:
    python generate_structures_summary.py
        --summaries_export_dir : where to write out the summaries.
        --task_import_dir ../lax/stimuli/towers
        --task_csv df_structures_topdownabs.csv
"""
import csv, os, json, argparse
import pandas as pd
import ast
from data.build_bitext import DEFAULT_SUMMARIES_DIR

from primitives.gadgets_primitives import *
from primitives.structures_primitives import *
from dreamcoder_programs.program import *
from tasksgenerator.tasks_generator import *
from dreamcoder_programs.grammar import *


DEFAULT_SUMMARIES_SUBDIR = "data/summaries"
DEFAULT_IMPORT_DIR = "../lax/stimuli/towers"

DEFAULT_STRUCTURES_NAME = "{}_programs_all"
DEFAULT_PROGRAM_COLUMN = "dreamcoder_program"
DEFAULT_OUTPUT_COLUMN = "dreamcoder_program_dsl_0_tokens"
STIMULI_ID = "s3_stimuli"

TOWER_LEVEL_PARTS, TOWER_LEVEL_PARAMS = (
    "tower_level_part_types",
    "tower_level_part_params",
)
SUBDOMAINS = ["bridge", "castle", "city", "house"]

parser = argparse.ArgumentParser()
parser.add_argument(
    "--task_import_dir",
    default=DEFAULT_IMPORT_DIR,
    help="Top level directory to import task data.",
)
parser.add_argument(
    "--task_csv", default=None, required=True, help="File name of initial CSV.",
)
parser.add_argument(
    "--summaries_export_dir",
    default=DEFAULT_SUMMARIES_DIR,
    help="If provided, alternate directory to write out summaries of tasks.",
)
parser.add_argument(
    "--program_column",
    default=DEFAULT_PROGRAM_COLUMN,
    help="Column in the task summaries CSV containing the program.",
)


def load_initial_task_csv(args):
    task_file = os.path.join(f"{args.task_import_dir}", args.task_csv)
    with open(task_file) as f:
        initial_summary = pd.read_csv(f)
    return initial_summary


def parse_and_tokenize_structures_programs(program):
    program = program.replace("h", "2x1")
    program = program.replace("t", "1x2")
    program = Program.parse(program)
    return program.left_order_tokens()


def stimId_to_s3URL(domain, subdomain, stimID):
    url = "https://lax-{}-{}-all.s3.amazonaws.com/".format(
        domain, subdomain
    ) + "lax-{}-{}-{}-all.png".format(domain, subdomain, str(stimID).zfill(3))
    return url


def eval_list_or_empty(l):
    try:
        return ast.literal_eval(l)
    except:
        return []


def export_processed_task_summary(args, task_summary):
    # Add the correct stimuli ID.
    task_summary[STIMULI_ID] = task_summary.apply(
        lambda x: stimId_to_s3URL(
            domain="structures",
            subdomain=x["structure_type"],
            stimID=x["structure_number"],
        ),
        axis=1,
    )

    # Add the DC tokens.
    task_summary.loc[:, DEFAULT_OUTPUT_COLUMN] = task_summary[
        args.program_column
    ].apply(parse_and_tokenize_structures_programs)

    # Add the concatenated columns.
    for params in [
        LOW_LEVEL_PARAMS,
        MID_LEVEL_PARAMS,
        HIGH_LEVEL_PARAMS,
        TOWER_LEVEL_PARAMS,
    ]:
        task_summary.loc[:, params] = task_summary[params].apply(eval_list_or_empty)
    for parts in [
        LOW_LEVEL,
        MID_LEVEL,
        HIGH_LEVEL,
        LOW_LEVEL_PARTS,
        MID_LEVEL_PARTS,
        HIGH_LEVEL_PARTS,
        TOWER_LEVEL_PARTS,
    ]:
        # First, convert them into lists
        task_summary.loc[:, parts] = task_summary[parts].apply(eval_list_or_empty)
        for params in [LOW_LEVEL_PARAMS, MID_LEVEL_PARAMS, HIGH_LEVEL_PARAMS]:
            if parts.split("_")[:2] == params.split("_")[:2]:
                task_summary.loc[:, parts + "_with_params"] = (
                    task_summary[parts] + task_summary[params]
                )
    # Finally, write out the subdomains to separate summaries.
    for subdomain in SUBDOMAINS:
        subdomain_df = task_summary.loc[task_summary["structure_type"] == subdomain]
        task_summary_file = DEFAULT_STRUCTURES_NAME.format(subdomain) + ".csv"
        with open(os.path.join(args.summaries_export_dir, task_summary_file), "w") as f:
            subdomain_df.to_csv(f)


def main(args):
    task_summary = load_initial_task_csv(args)
    export_processed_task_summary(args, task_summary)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
