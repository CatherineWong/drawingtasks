# Requirements
source activate drawingtasks

# Generate the context programs.
python generate_drawing_tasks.py --tasks_generator dials_context_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries 
# Use stroke_width_height = 6 * XYLIM in render_parsed_program

python generate_drawing_tasks.py --tasks_generator furniture_context_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries # Use stroke_width_height = 12 * XYLIM in render_parsed_program

python generate_drawing_tasks.py --tasks_generator wheels_context_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries
