## LAX (Language and Abstraction Experiments) - Technical Drawing Stimuli
This repository is the official implementation for the dataset of technical drawing stimuli used in the CogSci 2022 paper.

It contains the following key subdirectories for generating drawing stimuli and 
- `data`: This contains scripts for operating over program and language data, as well as inputs/outputs for those scripts.
- `primitives`: This contains the base program primitives (used in the base DSL, `L0`) for the technical drawings domain.
- `tasksgenerator`: This contains the stimulus generative models used to procedurally construct all programs for each subdomain of technical drawing stimuli.


******
### Setting up.
This set up has been tested on a Mac OS X running Mac OS X Monterey. A setup script to run these commands directly is at `setup_osx.sh`.

1. Download submodules. `git submodule update --init --recursive
` 
2. Create a new Conda environment called `laps` with Python 3.7.7. `conda env create -f environment.yml ; conda activate laps`
3. Install the NLTK word tokenize package. `python -m nltk.downloader 'punkt'`

### Quickstart: generating the CogSci 2022 dataset.
A script these commands directly is at `quickstart_gen_dataset_cogsci_2022.sh`.
1. Run the following to generate all four of the technical drawing stimuli (and programs) used in the CogSci 2022 dataset:
`python generate_drawing_tasks.py --tasks_generator nuts_bolts_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries; python generate_drawing_tasks.py --tasks_generator dials_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries ; python generate_drawing_tasks.py --tasks_generator wheels_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries ; python generate_drawing_tasks.py --tasks_generator furniture_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries `
2. This will generate the following outputs:
    - *Images* written to `data/renders`
    - *Base DSL libraries* written to `data/libraries`
    - *CSV summary* containing the task ID and metadata (including hand-coded program abstractions and a DSL program) in `data/summaries`. 

### Quickstart: running the language-program alignment model.
A script these commands directly on both domains is at `quickstart_run_experiments_cogsci_2022.sh `.

The following is a step by step set of commands for running the experiment pipeline on a single demonstration domain, `nuts_bolts`.
We use the following DSLs, which correspond (respectively) to L0, L1, L2, L3 in the CogSci paper: `dreamcoder_program_dsl_0_tokens`,  `low_level_part_types_with_params`, `mid_level_part_types_with_params`, `high_level_part_types_with_params`

1. Generate language-program bitexts: `python data/build_bitext.py --task_summaries dials_programs_all --language_column lemmatized_whats --program_column dreamcoder_program_dsl_0_tokens low_level_part_types_with_params mid_level_part_types_with_params high_level_part_types_with_params`
2. Run the IBM model: `python data/ibm_model.py --task_summaries dials_programs_all --language_column lemmatized_whats --random_likelihood_baseline --program_column dreamcoder_program_dsl_0_tokens low_level_part_types mid_level_part_types high_level_part_types low_level_part_types_with_params mid_level_part_types_with_params high_level_part_types_with_params`
3. Generate the plots:  `python data/program_language_plots.py --task_summaries dials_programs_all --language_column lemmatized_whats --program_column dreamcoder_program_dsl_0_tokens low_level_part_types mid_level_part_types high_level_part_types low_level_part_types_with_params mid_level_part_types_with_params high_level_part_types_with_params`

### Generating new drawing stimuli.
This section describes how to define a generative model that jointly outputs programs and images, using the `nuts_bolts` example.

1. Define base primitives. The base DSL used for the technical drawings domain is in `primitives/gadgets_primitives.py`. We use the `dreamcoder` library (imported as a submodule) to parse and execute programs.
2. Define a `TaskGenerator`. All of the generative models derive from the `AbstractTasksGenerator` class in `tasksgenerator/tasks_generator.py`. In our running example, the nuts_bolts tasks generator is defined in `nuts_bolts_programs_tasks_generator.py`. The task generators are designed to simultaneously generate the following for each stimulus:
    - A 'stroke array' consisting of the numpy-matrix pixel arrays which are added together to generate the image.
    - A 'stroke string' with an executable string program that can be parsed under the DreamCoder library to generate the same image.
    - A dictionary class containing the 'hand-coded abstractions' (named `synthetic_dict` in the released code) at different tokenized levels corresponding to different program abstractions.
We define corresponding tests for each generative model.
3. Run the generative model. We use the `generate_drawing_tasks.py` script as an entrypoint into all of the generative models. For now, you need to import the task generator class manually at the top of this file (or you could add it to an __init__.py).
