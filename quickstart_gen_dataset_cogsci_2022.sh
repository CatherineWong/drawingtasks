# Generates four technical drawing subdomains used in the CogSci 2022 dataset.
python generate_drawing_tasks.py --tasks_generator nuts_bolts_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries
python generate_drawing_tasks.py --tasks_generator dials_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries 
python generate_drawing_tasks.py --tasks_generator wheels_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries 
python generate_drawing_tasks.py --tasks_generator furniture_programs --num_tasks_per_condition all --train_ratio 0.8 --task_summaries