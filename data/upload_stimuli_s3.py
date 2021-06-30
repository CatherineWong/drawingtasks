"""
upload_stimuli_s3.py | Author: Catherine Wong

Utility script to upload datasets of stimuli to an AWS S3 bucket that will serve as a permanent public repository for these datasets.

Usage:
    python data/upload_stimuli_s3.py
        --stimuli_export_dir: top-level directory for the stimuli to upload.
        --curriculum_export_dir: top-level directory containing the JSON curriculum file we will use.
        --curriculum: the specific curriculum JSON file to use for uploading. 
"""
import os, json, argparse

DEFAULT_EXPORT_DIR = "data"
DEFAULT_RENDERS_SUBDIR = "renders"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--stimuli_export_dir",
    default=os.path.join(DEFAULT_EXPORT_DIR, DEFAULT_RENDERS_SUBDIR),
    help="Top level directory to export stimuli data.",
)
parser.add_argument(
    "--curriculum_export_dir",
    default=DEFAULT_EXPORT_DIR,
    help="Top level directory where curriculum JSON files are located.",
)
parser.add_argument(
    "--curriculum",
    required=True,
    help="Name of the curriculum file. Must be in the curriculum export dir.",
)


def main(args):
    stim_paths_to_upload = get_stim_paths_from_curriculum(args)
    upload_stimuli_to_s3(args, stim_paths_to_upload)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
