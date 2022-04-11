"""
codex_model.py | Author : Catherine Wong.

Utility script for using codex to do paired (language, program)  evaluations. Runs leave-N-out likelihood evaluations over paired language and program bitexts.

Uses language edit distance for similarity.

Usage:
python data/codex_model.py
    --task_summaries nuts_bolts_synthetic_all
    --language_column synthetic_language_whats
    --program_column dreamcoder_program_dsl_0_unfolded_verbosity_1
    --prompt_examples random near # How to choose paired examples.
    --observe program language # Which direction to run in P(p | l) or P(l | p)
    --baseline_examples random near far
"""
import random
import csv, os, json, argparse

from click import prompt

random.seed(0)

DEFAULT_DATA_DIR = "data"
DEFAULT_TRANSLATIONS_DIR = f"{DEFAULT_DATA_DIR}/translations"
DEFAULT_SUMMARIES_DIR = f"{DEFAULT_DATA_DIR}/summaries"
DEFAULT_LANGUAGE_DIR = f"{DEFAULT_DATA_DIR}/language"

DEFAULT_LANGUAGE_COLUMN = "synthetic_language_whats"
DEFAULT_PROGRAM_COLUMN = "dreamcoder_program_dsl_0_unfolded_verbosity_1"
RANDOM, NEAR, FAR = "random", "near", "far"
PROGRAM, LANGUAGE = "program", "language"
EDIT_DISTANCES = "edit_distances"
PROGRAM_TOKENS, LANGUAGE_TOKENS = "program_tokens", "language_tokens"


CHARS_PER_TOKEN = 2.25
MAX_TOKENS = 4096
MAX_CHARS = int(MAX_TOKENS * CHARS_PER_TOKEN)

MAIN, BASELINE = "main", "baseline"
MEAN_LOG_LIKELIHOOD = "mean_log_likelihood"

# Initialize model
from transformers import AutoModelForCausalLM, AutoTokenizer, FlaxAutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("flax-community/gpt-neo-125M-code-clippy")
tokenizer = AutoTokenizer.from_pretrained("flax-community/gpt-neo-125M-code-clippy")


parser = argparse.ArgumentParser()
parser.add_argument(
    "--export_dir",
    default=DEFAULT_TRANSLATIONS_DIR,
    help="If provided, alternate directory to export the translation results.",
)
parser.add_argument(
    "--language_dir",
    default=DEFAULT_LANGUAGE_DIR,
    help="If provided, alternate directory to read in language data.",
)
parser.add_argument(
    "--task_summaries",
    required=True,
    help="Original CSV containing task summaries data.",
)
parser.add_argument(
    "--program_column",
    nargs="+",
    default=[DEFAULT_PROGRAM_COLUMN],
    help="Column in the task summaries CSV containing the program.",
)
parser.add_argument(
    "--language_column",
    default=DEFAULT_LANGUAGE_COLUMN,
    help="Column in the language CSV containing which language to use.",
)
parser.add_argument(
    "--prompt_examples",
    nargs="+",
    default=[RANDOM, NEAR],
    help="How to choose prompt examples.",
)
parser.add_argument(
    "--baseline_examples",
    nargs="+",
    default=[RANDOM, NEAR, FAR],
    help="How to choose baseline examples.",
)
parser.add_argument(
    "--observe", nargs="+", default=[PROGRAM, LANGUAGE],
)


def get_task_to_tokens_dict(args, program_column_idx):
    task_tokens_file = f"{args.task_summaries}_{args.program_column[program_column_idx]}_{args.language_column}"
    task_tokens_file = os.path.join(args.language_dir, task_tokens_file)
    with open(task_tokens_file) as f:
        task_to_tokens_dict = json.load(f)

    print(f"...Read in {len(task_to_tokens_dict)} tasks from {task_tokens_file}.")
    return task_to_tokens_dict


def get_baseline_task(baseline_type, task, example_tasks, task_to_tokens_dict):
    # TBD: we need to make sure its not IN the example tasks.
    heldouts = [task] + example_tasks
    if baseline_type == NEAR:
        return task_to_tokens_dict[task][EDIT_DISTANCES][0][0]
    elif baseline_type == FAR:
        return task_to_tokens_dict[task][EDIT_DISTANCES][-1][0]
    elif baseline_type == RANDOM:
        return random.choice([t for t in task_to_tokens_dict if t not in heldouts])
    else:
        assert False


def get_example_tasks(prompt_type, task, task_to_tokens_dict, n_examples=20):
    if prompt_type == NEAR:
        return [
            t[0] for t in task_to_tokens_dict[task][EDIT_DISTANCES][1 : n_examples + 1]
        ]
    elif prompt_type == FAR:
        return [
            t[0]
            for t in task_to_tokens_dict[task][EDIT_DISTANCES][-(n_examples + 1) : -1]
        ]
    elif prompt == RANDOM:
        return random.sample([t for t in task_to_tokens_dict if t is not task])
    else:
        assert False


def format_program(program_raw):
    if type(program_raw[0]) == list:
        program_raw = program_raw[0]

    return f"PROGRAM: {', '.join(program_raw)}"


def format_language(language_raw):
    if type(language_raw[0]) == list:
        language_raw = language_raw[0]
    ls = f"DESCRIPTION: An image containing: {', '.join(language_raw)}"
    return ls


def get_prompt_pair(observation_type, task, task_to_tokens_dict):
    program_raw = task_to_tokens_dict[task][PROGRAM_TOKENS]
    language_raw = task_to_tokens_dict[task][LANGUAGE_TOKENS]
    if observation_type == LANGUAGE:
        prompt_pair = [format_language(language_raw), format_program(program_raw)]
    else:
        prompt_pair = [format_program(program_raw), format_language(language_raw)]
    return "\n".join(prompt_pair), prompt_pair


def build_prompt(
    prompt_type,
    observation_type,
    task,
    task_to_tokens_dict,
    original_prompt_pair,
    example_tasks=None,
):
    if original_prompt_pair:
        # Create a swapped one.
        prompt, prompt_pair = get_prompt_pair(
            observation_type, task, task_to_tokens_dict
        )
        prompt_pair = [original_prompt_pair[0], prompt_pair[-1]]
        prompt = "\n".join(prompt_pair)
    if not example_tasks:
        example_tasks = get_example_tasks(prompt_type, task, task_to_tokens_dict)
    for i, example_task in enumerate(example_tasks):
        example_prompt, _ = get_prompt_pair(
            observation_type, example_task, task_to_tokens_dict
        )
        prompt_buf = example_prompt + "\n" + prompt
        if len(prompt_buf) < MAX_CHARS:
            prompt = prompt_buf
        else:
            example_tasks = example_tasks[:i]
            break
    return prompt, prompt_pair, example_tasks


def get_task_perplexity(prompt, task_prompt_pair):
    query_model(prompt)


def query_model(prompt_str: str, temperature: int = 0):
    pass


def run_all_leave_n_out(args, task_to_tokens_dict, print_every=10, max_cutoff=250):
    # Sort task keys.
    task_keys = sorted(list(task_to_tokens_dict.keys()))[:max_cutoff]
    for idx, task in enumerate(task_keys):
        if idx % print_every == 0:
            print(f"...fitting on iteration {idx}/{len(task_keys)}")

        for prompt_type in args.prompt_examples:
            for observation_type in args.observe:

                task_prompt, task_prompt_pair, example_tasks = build_prompt(
                    prompt_type, observation_type, task, task_to_tokens_dict
                )
                task_perplexity = get_task_perplexity(task_prompt, task_prompt_pair)
                # task_to_tokens_dict[task][
                #     (MAIN, observation_type, MEAN_LOG_LIKELIHOOD, prompt_type, "")
                # ] = task_perplexity
                for baseline_type in args.baseline_examples:
                    baseline_task = get_baseline_task(
                        baseline_type, task, example_tasks, task_to_tokens_dict
                    )
                    (
                        baseline_prompt,
                        baseline_prompt_pair,
                        baseline_example_tasks,
                    ) = build_prompt(
                        prompt_type,
                        observation_type,
                        baseline_task,
                        task_to_tokens_dict,
                        original_prompt_pair=task_prompt_pair,
                        example_tasks=example_tasks,
                    )

                    # baseline_perplexity = get_task_perplexity(
                    #     baseline_prompt, baseline_completion_idx
                    # )
                    # task_to_tokens_dict[task][
                    #     (
                    #         BASELINE,
                    #         observation_type,
                    #         MEAN_LOG_LIKELIHOOD,
                    #         prompt_type,
                    #         baseline_type,
                    #         baseline_task,
                    #     )
                    # ] = baseline_perplexity
    return task_to_tokens_dict


def export_task_to_likelihoods_summary(
    args, task_to_likelihoods_dict, ibm_model, program_column_idx
):
    pass


def main(args):
    for program_column_idx in range(len(args.program_column)):
        task_to_tokens_dict = get_task_to_tokens_dict(args, program_column_idx)
        task_to_likelihoods_dict = run_all_leave_n_out(args, task_to_tokens_dict)
        export_task_to_likelihoods_summary(
            args, task_to_likelihoods_dict, program_column_idx
        )


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
