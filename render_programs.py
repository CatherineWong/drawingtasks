"""
render_programs.py | Author : Catherine Wong.

Demo utility for rendering gadgets and structures programs.

Usage:
python render_programs.py
"""
import csv, os, json, argparse, sys
import struct
from dreamcoder.program import Program
import primitives.object_primitives as object_primitives
import primitives.gadgets_primitives as gadgets_primitives
import primitives.structures_primitives as structures_primitives

DEFAULT_DATA_DIR = "data"
DEFAULT_RENDERS_DIR = f"{DEFAULT_DATA_DIR}/renders"
RENDER_FILEPATH = "render_{}"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--programs_file", required=True, help="JSON file containing programs to render.",
)

parser.add_argument(
    "--export_dir",
    default=DEFAULT_RENDERS_DIR,
    help="If provided, alternate directory to export the library results.",
)


def render_structures_drawings_program(args, idx, p_string):
    try:
        p = Program.parse(p_string)
        image = object_primitives.render_parsed_program(p)
        filename = object_primitives.export_rendered_program(
            image, RENDER_FILEPATH.format(idx), export_dir=args.export_dir
        )
    except:
        print(f"Error parsing {p_string}")
    print(f"Writing out program ==> {filename}")


def main(args):
    with open(args.programs_file) as f:
        programs = json.load(f)
    for idx, p in enumerate(programs):
        render_structures_drawings_program(args, idx, p)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
