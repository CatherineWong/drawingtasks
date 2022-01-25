"""
program_language_plots.py | Catherine Wong.

Utility script to run plotted analyses over tasks and output metrics.

Usage:
    python data/program_language_plots.py
        --task_summaries nuts_bolts_programs_all_libraries 
        --language_column lemmatized_whats
        --program_column dreamcoder_program_dsl_0_tokens dreamcoder_program_dsl_1_tokens dreamcoder_program_dsl_2_tokens dreamcoder_program_dsl_3_tokens dreamcoder_program_dsl_4_tokens dreamcoder_program_dsl_5_tokens
"""
from collections import defaultdict
import csv, os, json, argparse
import itertools

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


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
TRANSLATION_BEST_LOG_LIKELIHOODS = "translation_best_log_likelihoods"
RANDOM_TRANSLATION_MARGINAL_LOG_LIKELIHOODS = "random_translation_log_likelihoods"
RANDOM_TRANSLATION_BEST_LOG_LIKELIHOODS = "random_translation_best_log_likelihoods"


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
parser.add_argument(
    "--use_base_dsl_bitext",
    action="store_true",
    help="If included, uses a bitext for the base DSL.",
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


def get_bitext_unique_program_tokens(bitext):
    return set(
        itertools.chain.from_iterable(
            [bitext[task]["program_tokens"] for task in bitext]
        )
    )


def get_bitexts_dict(args):
    bitexts_dict = {}
    for program_column in args.program_column:
        summaries_name = args.task_summaries.replace("_libraries", "")
        bitext_json = f"{summaries_name}_{program_column}_{args.language_column}"
        try:
            with open(os.path.join(args.language_dir, bitext_json)) as f:
                bitext = json.load(f)
            bitexts_dict[program_column] = get_bitext_unique_program_tokens(bitext)
        except:
            print(f"Not found: bitext for: {program_column}")
    print(f"...read bitexts for {len(bitexts_dict)} bitexts.")
    return bitexts_dict


def get_libraries_dict(args, bitexts_dict):
    libraries_dict = {}
    for program_column in args.program_column:
        summaries_name = args.task_summaries.replace("_libraries", "")
        col_name = program_column.replace(TOKENS_SUFFIX, "")
        library_json = f"{summaries_name}_{col_name}.json"
        try:
            with open(os.path.join(args.libraries_dir, library_json)) as f:
                library_dict = json.load(f)
            libraries_dict[program_column] = library_dict
        except:
            print(f"Not found: library for: {col_name}")
    print(f"...read libraries for {len(libraries_dict)} libraries.")

    # If this is structures, use the base DSL as as as library.
    if args.use_base_dsl_bitext:
        libraries_dict[DEFAULT_PROGRAM_COLUMN] = {
            "library": {"productions": bitexts_dict[DEFAULT_PROGRAM_COLUMN]}
        }

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


def generate_program_length_plots(args, summaries_dict, libraries_dict, bitexts_dict):
    # X is: size of program library.
    # Y is: length of program.
    library_sizes, program_sizes = [], []
    for program_column in args.program_column:
        # Get the library size.
        if program_column in libraries_dict:
            library_size = len(libraries_dict[program_column][LIBRARY]["productions"])
        else:
            library_size = len(bitexts_dict[program_column]) + len(
                libraries_dict[DEFAULT_PROGRAM_COLUMN][LIBRARY]["productions"]
            )
        print(program_column, library_size)
        for task_name in summaries_dict:
            library_sizes.append(np.log(library_size))

            program_size = len(eval(summaries_dict[task_name][program_column]))
            program_and_library_size = np.log(library_size + program_size)
            program_sizes.append(program_and_library_size)
    plt.figure(figsize=(3, 2))
    ax = sns.lineplot(
        x=library_sizes,
        y=program_sizes,
        err_style="bars",
        # x_estimator=np.mean,
        ci=95,
        color="red",
    )
    fig = ax.get_figure()

    output_plot = f"{args.task_summaries}_{args.program_column[-1]}_{args.language_column}_lengths.png"
    output = os.path.join(args.export_dir, output_plot)
    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: "{:,.1f}".format(x))
    )
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: "{:,.1f}".format(x))
    )
    # plt.title(f"{get_subdomain_name(args.task_summaries)}")
    # plt.xlabel("log(|DSL|)")
    # plt.ylabel("log(|Program|)")

    fig.savefig(output)
    print(f"...saved lengths plot to {output}.")


def generate_program_likelihood_plots(
    args, summaries_dict, libraries_dict, translations_dict, bitexts_dict
):
    library_sizes, translation_probabilities, random_probabilities = [], [], []
    library_to_translation_probabilities = defaultdict(list)
    for program_column in args.program_column:
        # Get the library size.
        if program_column in libraries_dict:
            library_size = len(libraries_dict[program_column][LIBRARY]["productions"])
        else:
            library_size = len(bitexts_dict[program_column]) + len(
                libraries_dict[DEFAULT_PROGRAM_COLUMN][LIBRARY]["productions"]
            )
        for task_name in translations_dict[program_column]:
            for likelihood in translations_dict[program_column][task_name][
                TRANSLATION_BEST_LOG_LIKELIHOODS
            ]:
                library_sizes.append(np.log(library_size))
                translation_probabilities.append(likelihood)
                library_to_translation_probabilities[np.log(library_size)].append(
                    likelihood
                )
            for likelihood in translations_dict[program_column][task_name][
                RANDOM_TRANSLATION_BEST_LOG_LIKELIHOODS
            ]:
                random_probabilities.append(likelihood)
    plt.clf()
    plt.figure(figsize=(3, 2))
    ax = sns.lineplot(
        x=library_sizes,
        y=translation_probabilities,
        err_style="bars",
        # x_estimator=np.mean,
        # label="Translation",
        ci=95,
    )
    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: "{:,.1f}".format(x))
    )
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: "{:,.1f}".format(x))
    )
    # ax = sns.regplot(
    #     x=library_sizes,
    #     y=random_probabilities,
    #     x_estimator=np.mean,
    #     label="Random",
    #     order=2,
    # )
    # ax.legend()
    fig = ax.get_figure()

    output_plot = f"{args.task_summaries}_{args.program_column[-1]}_{args.language_column}_ibm.png"
    output = os.path.join(args.export_dir, output_plot)

    # plt.title(f"{get_subdomain_name(args.task_summaries)}")
    # plt.ylabel("P(language | program, T, DSL)")
    # plt.xlabel("log(|DSL|)")

    fig.savefig(output)
    print(f"...saved lengths plot to {output}.")

    # Now, run an ANOVA to determine that there is a meaningful mean.
    from scipy.stats import f_oneway

    translation_probs = [
        library_to_translation_probabilities[size]
        for size in sorted(list(library_to_translation_probabilities.keys()))
    ]
    F, p = f_oneway(*translation_probs)
    print(f"F one way results: F: {F}; {p}")

    # Now, run a nested linear model to determine that there is a non-linear mean in each.
    from sklearn.linear_model import LinearRegression
    import statsmodels.api as sm
    import scipy

    # Compare full model w. polynomial term.
    y = np.array([translation_probabilities]).T
    x_linear = np.array([library_sizes]).T  # Linear
    x_polynomial = np.hstack((x_linear, np.square(x_linear)))

    poly_model = sm.OLS(y, x_polynomial).fit()
    linear_model = sm.OLS(y, x_linear).fit()

    LR_statistic = -2 * (linear_model.llf - poly_model.llf)
    p_val = scipy.stats.chi2.sf(LR_statistic, 2)
    print(f"LR statistic x^2 model vs. linear: {LR_statistic}; p_val: {p_val}")


def get_subdomain_name(task_summaries_name):
    subdomain_name = task_summaries_name.split("_")[:-2]
    subdomain_name = "&".join([t.capitalize() for t in subdomain_name])
    return subdomain_name


def main(args):
    summaries_dict, fieldnames = get_summaries_dict(args)
    bitexts_dict = get_bitexts_dict(args)
    libraries_dict = get_libraries_dict(args, bitexts_dict)
    translations_dict = get_translations(args)

    generate_program_length_plots(args, summaries_dict, libraries_dict, bitexts_dict)
    generate_program_likelihood_plots(
        args, summaries_dict, libraries_dict, translations_dict, bitexts_dict
    )


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
