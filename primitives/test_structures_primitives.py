"""
test_structures_primitives.py | Author: Catherine Wong.
"""
import os
import primitives.structures_primitives as to_test

DESKTOP = f"/Users/catherinewong/Desktop/zyzzyva/research/language-abstractions/drawing_tasks_stimuli/structures"  # Internal for testing purposes.


def _test_render_save_programs(blocks, export_dir, no_blanks=True, split="train"):
    for program_id, b in enumerate(blocks):
        # Can it render the program?
        rendered = to_test.render_block_jsons_to_canvas(b)
        # Can it save the program?
        saved_file = to_test.export_rendered_program(
            rendered, f"{split}_{program_id}_blocks", export_dir=export_dir
        )
        print(f"Saving to id {program_id}")
        assert os.path.exists(saved_file)


def test_render_parsed_jsons_to_canvas():
    test_block_dict = [
        {"x": 0, "y": 0, "height": 1, "width": 2},
        {"x": 2, "y": 0, "height": 1, "width": 2},
        {"x": 0, "y": 1, "height": 2, "width": 1},
        {"x": 3, "y": 1, "height": 2, "width": 1},
        {"x": 0, "y": 3, "height": 1, "width": 2},
        {"x": 2, "y": 3, "height": 1, "width": 2},
        {"x": 0, "y": 4, "height": 1, "width": 2},
        {"x": 2, "y": 4, "height": 1, "width": 2},
        {"x": 1, "y": 5, "height": 1, "width": 2},
    ]

    _test_render_save_programs(
        [test_block_dict], export_dir=DESKTOP, no_blanks=True, split="train"
    )
