"""
program_language_plots.py | Catherine Wong.

Utility script to run plotted analyses over tasks and output metrics.

Usage:
    python data/program_language_plots.py
        --task_summaries nuts_bolts_programs_all_libraries 
        --language_column lemmatized_whats
        --program_column dreamcoder_program_dsl_0_tokens dreamcoder_program_dsl_1_tokens dreamcoder_program_dsl_2_tokens dreamcoder_program_dsl_3_tokens dreamcoder_program_dsl_4_tokens dreamcoder_program_dsl_5_tokens
"""
import csv, os, json, argparse
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


LIBRARY = "library"

DEFAULT_DATA_DIR = "data"
DEFAULT_ANALYSES_DIR = f"{DEFAULT_DATA_DIR}/analyses"
DEFAULT_LIBRARIES_DIR = f"{DEFAULT_DATA_DIR}/libraries"

DEFAULT_TRANSLATIONS_DIR = f"{DEFAULT_DATA_DIR}/translations"
DEFAULT_LANGUAGE_DIR = f"{DEFAULT_DATA_DIR}/language"
DEFAULT_SUMMARIES_DIR = f"{DEFAULT_DATA_DIR}/summaries"
DEFAULT_PROGRAM_COLUMN = "dreamcoder_program_dsl_0_tokens"
LEMMATIZED_WHATS = "lemmatized_whats"
LEMMATIZED_WHATS_WHERES = "lemmatized_whats_wheres"
RAW_WHATS_WHERES = "raw_whats_wheres"
DEFAULT_LANGUAGE_COLUMN = LEMMATIZED_WHATS
DEFAULT_TASK_SUMMARIES_TASK_COLUMN = "s3_stimuli"

PROGRAM_TOKENS, LANGUAGE_TOKENS = "program_tokens", "language_tokens"
TRANSLATION_MARGINAL_LOG_LIKELIHOODS = "translation_log_likelihoods"
RANDOM_TRANSLATION_MARGINAL_LOG_LIKELIHOODS = "random_translation_log_likelihoods"

TOKENS_SUFFIX = "_tokens"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--export_dir",
    default=DEFAULT_ANALYSES_DIR,
    help="If provided, alternate directory to export the translation results.",
)
parser.add_argument(
    "--translations_dir",
    default=DEFAULT_TRANSLATIONS_DIR,
    help="If provided, alternate directory to export the library results.",
)
parser.add_argument(
    "--libraries_dir",
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
    nargs="+",
    default=[DEFAULT_PROGRAM_COLUMN],
    help="Column in the task summaries CSV containing the program.",
)
parser.add_argument(
    "--language_dir",
    default=DEFAULT_LANGUAGE_DIR,
    help="If provided, alternate directory to read in language data.",
)
parser.add_argument(
    "--language_column",
    default=DEFAULT_LANGUAGE_COLUMN,
    help="Column in the language CSV containing which language to use.",
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
    for program_column in args.program_column:
        summaries_name = args.task_summaries.replace("_libraries", "")
        col_name = program_column.replace(TOKENS_SUFFIX, "")
        library_json = f"{summaries_name}_{col_name}.json"
        with open(os.path.join(args.libraries_dir, library_json)) as f:
            library_dict = json.load(f)
        libraries_dict[program_column] = library_dict
    print(f"...read libraries for {len(libraries_dict)} libraries.")
    return libraries_dict


def get_translations(args):
    translations_dict = {}
    for program_column in args.program_column:
        task_translations_file_base = (
            f"ibm_1_{args.task_summaries}_{program_column}_{args.language_column}"
        )
        task_translations_file = os.path.join(
            args.translations_dir, task_translations_file_base + ".json"
        )
        try:
            with open(task_translations_file) as f:
                translation_dict = json.load(f)
        except:
            print("Error reading: " + task_translations_file)
        translations_dict[program_column] = translation_dict
    print(f"...read translations info for {len(translations_dict)} libraries.")
    return translations_dict


def generate_program_length_plots(args, summaries_dict, libraries_dict):
    # X is: size of program library.
    # Y is: length of program.
    library_sizes, program_sizes = [], []
    for program_column in args.program_column:
        # Get the library size.
        library_size = len(libraries_dict[program_column][LIBRARY]["productions"])
        for task_name in summaries_dict:
            library_sizes.append(library_size)
            program_sizes.append(len(eval(summaries_dict[task_name][program_column])))
    ax = sns.regplot(
        x=library_sizes,
        y=program_sizes,
        x_estimator=np.mean,
        scatter_kws={"color": "black"},
    )
    fig = ax.get_figure()

    output_plot = f"{args.task_summaries}_{args.program_column[-1]}_{args.language_column}_lengths.png"
    output = os.path.join(args.export_dir, output_plot)

    plt.title(f"{args.task_summaries}")
    plt.xlabel("|DSL|")
    plt.ylabel("|Program|")

    fig.savefig(output)
    print(f"...saved lengths plot to {output}.")


def generate_program_likelihood_plots(
    args, summaries_dict, libraries_dict, translations_dict
):
    library_sizes, translation_probabilities, random_probabilities = [], [], []
    for program_column in args.program_column:
        # Get the library size.
        library_size = len(libraries_dict[program_column][LIBRARY]["productions"])
        for task_name in translations_dict[program_column]:
            for likelihood in translations_dict[program_column][task_name][
                TRANSLATION_MARGINAL_LOG_LIKELIHOODS
            ]:
                library_sizes.append(library_size)
                translation_probabilities.append(likelihood)
            for likelihood in translations_dict[program_column][task_name][
                RANDOM_TRANSLATION_MARGINAL_LOG_LIKELIHOODS
            ]:
                random_probabilities.append(likelihood)
    plt.clf()
    ax = sns.regplot(
        x=library_sizes,
        y=translation_probabilities,
        x_estimator=np.mean,
        scatter_kws={"color": "black"},
        label="Translation",
    )
    ax = sns.regplot(
        x=library_sizes,
        y=random_probabilities,
        x_estimator=np.mean,
        scatter_kws={"color": "black"},
        label="Random",
    )
    fig = ax.get_figure()

    output_plot = f"{args.task_summaries}_{args.program_column[-1]}_{args.language_column}_ibm.png"
    output = os.path.join(args.export_dir, output_plot)

    plt.title(f"{args.task_summaries}")
    plt.xlabel("P(language | program)")
    plt.ylabel("|Program|")

    fig.savefig(output)
    print(f"...saved lengths plot to {output}.")


def main(args):
    summaries_dict, fieldnames = get_summaries_dict(args)
    libraries_dict = get_libraries_dict(args)
    translations_dict = get_translations(args)

    generate_program_length_plots(args, summaries_dict, libraries_dict)
    generate_program_likelihood_plots(
        args, summaries_dict, libraries_dict, translations_dict
    )


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
