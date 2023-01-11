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
A script to run these commands directly is at `quickstart_gen_dataset_cogsci_2022.sh`.
1. Run the following to generate all four of the technical drawing stimuli (and programs) used in the CogSci 2022 dataset:
`python generate_drawing_tasks.py --tasks_generator nuts_bolts_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries; python generate_drawing_tasks.py --tasks_generator dials_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries ; python generate_drawing_tasks.py --tasks_generator wheels_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries ; python generate_drawing_tasks.py --tasks_generator furniture_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries `
2. This will generate the following outputs:
    - *Images* written to `data/renders`
    - *Base DSL libraries* written to `data/libraries`
    - *CSV summary* containing the task ID and metadata (including hand-coded program abstractions and a DSL program) in `data/summaries`. 

### Quickstart: generating the contextual drawings dataset.
A script to run these commands directly is at `quickstart_gen_dataset_contextual_drawings_2022.sh`.
1. Activate a working conda environment.
2. Run the following to generate the contextual drawings stimuli (and programs) used for the contextual drawings dataset. You can modify the `stroke_width_height` argument of `render_parsed_program` in object_primitives.py to contorl the size of the images. The script contains a note on the argument size we used.
```
python generate_drawing_tasks.py --tasks_generator dials_context_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries 

python generate_drawing_tasks.py --tasks_generator furniture_context_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries 

python generate_drawing_tasks.py --tasks_generator wheels_context_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries
```

3. Run the final line of the script to generate randomly selected target and context batches, and to upload the dataset to the AWS bucket. This creates a local JSON file containing the batches at `data/lax-drawing-context-library-v2.json`. This requires a local AWS login to be set; see the AWS/boto3 documentation to set this.
```
python upload_context_stimuli.py --task_generators wheels_context_programs dials_context_programs furniture_context_programs --generate_v2_random_contexts
```
These should upload the stimuli to: `https://lax-context-stimuli.s3.amazonaws.com/`. These stimuli have the same names as the local file paths.

The outputs of the task generator are the same as those in the CogSci 2022 dataset. 
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

### Generating the contextual drawing stimuli.
This section describes how we defined the generative model that creates the contextual stimuli, using the `furniture` example. Follow along with this example in `tasksgenerator\furniture_context_tasks_generator.py`.

1. Each of these generative models is directly based on the logic from the corresponding CogSci 2022 generator, which is defined at `tasksgenerator\{domain}_programs_tasks_generator.py`.
2. Each of these base generative models calls a main function, `_generate_strokes_strings_for_stimuli`, that generates string programs corresponding to stimuli tasks and executes them to create images. This main function in turn calls a number of nested subtyped functions, such as `_generate_stacked_drawers_stimuli_strings`, that contain manually defined iterators over the cross-product of parameters (sizes, substroke types for drawer knobs, numbers of feet) that vary across the stimuli.  To create the contextual stimuli, these iterators have been parameterized according to a `context` argument, and the main function now generates separate stimuli for each context.
3. Take a look at the `_generate_stacked_drawers_stimuli_strings` function as an example of how we manually define the logic for generating contextual stimuli, such that the larger context (`CONTEXT_LARGE_ABSTRACTIONS`) is definitionally a subset with less parameter variation than the stimuli generated in the support of the smaller context (`CONTEXT_SMALL_ABSTRACTIONS`). This is fairly simple, if manual: at the top of each function, we simply case on the context, and set the space of variable parametesr (eg. `possible_feet_heights`: the list of heights for bookcase feet that will be iterated over in this stimuli generator). We simply define these parameters such that the `CONTEXT_LARGE_ABSTRACTIONS` parameter sets are a strict subset of the ones for the smaller abstractions -- now, iterating over the cross product of these parameters will produce less parameter variation in the generated stimuli.