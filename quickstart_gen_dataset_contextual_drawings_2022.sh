# Requirements
source activate drawingtasks


#### Running these commands generates the stimuli and programs for the dataset.
# Generate the context programs.
python generate_drawing_tasks.py --tasks_generator dials_context_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries 
# Use stroke_width_height = 6 * XYLIM in render_parsed_program, in object_primitives.py

python generate_drawing_tasks.py --tasks_generator furniture_context_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries # Use stroke_width_height = 12 * XYLIM in render_parsed_program

python generate_drawing_tasks.py --tasks_generator wheels_context_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries

# Create targets and upload. This needs to be RE-RUN for the 
python upload_context_stimuli.py --task_generators wheels_context_programs dials_context_programs furniture_context_programs --generate_v2_random_contexts 