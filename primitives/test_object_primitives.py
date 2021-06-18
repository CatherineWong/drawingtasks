"""test_object_primitives.py | Author : Catherine Wong"""

import os
import numpy as np
from dreamcoder.program import Program
import primitives.object_primitives as to_test

SIMPLE_OBJECT_PROGRAMS = ["(line)", "(circle)"]


def _test_parse_render_save_programs(program_strings, tmpdir):
    export_dir = "/Users/catwong/Desktop"
    for program_id, program_string in enumerate(program_strings):
        try:
            # Can it parse the program?
            p = Program.parse(program_string)
            # Can it render the program?
            rendered = to_test.render_parsed_program(p)
            assert rendered.shape == (
                to_test.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT,
                to_test.SYNTHESIS_TASK_CANVAS_WIDTH_HEIGHT,
            )
            assert np.sum(rendered) > 0
            # Can it save the program?
            saved_file = to_test.export_rendered_program(
                rendered, program_id, export_dir=export_dir
            )
            assert os.path.exists(saved_file)
        except:
            print("Failed to evaluate: (program_string)")
            assert False


def test_parse_render_save_simple_objects(tmpdir):
    _test_parse_render_save_programs(SIMPLE_OBJECT_PROGRAMS, tmpdir)
