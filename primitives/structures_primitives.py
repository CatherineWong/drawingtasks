"""
structures_primitives.py | Author: Catherine Wong.
Structures primitives for generating block structures.

Credit: builds on primitives designed by Kevin Ellis; and structuers primitives designed by Will McCarthy.
"""
import os
import imageio
import block_utils.blockworld_utils as blockworld_utils
from dreamcoder.domains.tower.makeTowerTasks import SupervisedTower

from primitives.block_dict_to_input_program import convert
from dreamcoder.domains.tower.towerPrimitives import *
from dreamcoder.domains.tower.tower_common import renderPlan
from dreamcoder.domains.tower.makeTowerTasks import *


def render_block_jsons_to_canvas(block_json):
    program = convert(block_json, whole_squares=False)
    # McCarthy et. al use 2x1 and 1x2 blocks, unlike the DC 3x1 and 1x3 blocks
    program = program.replace("h", "2x1")
    program = program.replace("t", "1x2")
    return render_parsed_program(program)


def render_parsed_program(program):
    tower_task = SupervisedTower(name=None, program=program)
    return tower_task.getImage()


def export_rendered_program(rendered_array, export_id, export_dir):
    filename = os.path.join(export_dir, f"{export_id}.png")
    imageio.imwrite(filename, rendered_array)
    return filename
