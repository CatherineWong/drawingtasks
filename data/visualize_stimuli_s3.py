"""
visualize_stimuli_s3.py  | Author: Catherine Wong.

Utility script to generate visualizers of stimuli from the AWS S3 bucket. Assumes a file called .aws/credentials with appropriate credentials in the home directory.

Usage: 
    python data/visualize_stimuli_s3.py
        --stimuli_export_dir: top-level directory for the stimuli to upload / download.
        --curriculum: nuts-bolts-all # The specific JSON file associated with the dataset.
"""
import os, json, argparse
import urllib.request
import cv2
from imutils import build_montages

DEFAULT_EXPORT_DIR = "data"
DEFAULT_RENDERS_SUBDIR = "renders"
DEFAULT_EXPERIMENT_NAME = "lax"
DEFAULT_DOMAIN_NAME = "drawing"

DEFAULT_NUM_TRAIN_STIMULI, DEFAULT_NUM_TEST_STIMULI = 200, 50
DEFAULT_NUM_PER_ROW = 10

DEFAULT_S3_BUCKET_TEMPLATE = (
    "https://{}-{}-{}.s3.amazonaws.com/"  # {EXPERIMENT}-{DOMAIN}-{CURRICULUM}
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--stimuli_export_dir",
    default=os.path.join(DEFAULT_EXPORT_DIR, DEFAULT_RENDERS_SUBDIR),
    help="Top level directory to export stimuli data.",
)
parser.add_argument(
    "--experiment_name",
    default=DEFAULT_EXPERIMENT_NAME,
)
parser.add_argument(
    "--domain_name",
    default=DEFAULT_DOMAIN_NAME,
)
parser.add_argument(
    "--curriculum",
    required=True,
    help="Name of the curriculum file. Must be in the curriculum export dir.",
)
parser.add_argument(
    "--num_train_stimuli",
    default=DEFAULT_NUM_TRAIN_STIMULI,
    type=int,
    help="How many train stimuli.",
)
parser.add_argument(
    "--num_test_stimuli",
    default=DEFAULT_NUM_TEST_STIMULI,
    type=int,
    help="How many train stimuli.",
)
parser.add_argument(
    "--skip_download",
    action="store_true",
    help="Whether to skip data download and only generate a manifest.",
)


def get_stimuli_name(args, index_number):
    padded_index = str.zfill(str(index_number), 3)
    cleaned_curriculum_name = args.curriculum
    return f"{args.experiment_name}-{args.domain_name}-{cleaned_curriculum_name}-{padded_index}.png"


def get_montage_name(args, index_number):
    padded_index = str.zfill(str(index_number), 3)
    cleaned_curriculum_name = args.curriculum
    return f"{args.experiment_name}-{args.domain_name}-{cleaned_curriculum_name}-montage-{padded_index}.png"


def build_stim_paths_to_download(args):
    all_stimuli_paths = []
    s3_bucket_path = DEFAULT_S3_BUCKET_TEMPLATE.format(
        args.experiment_name, args.domain_name, args.curriculum
    )
    for idx in range(args.num_train_stimuli + args.num_test_stimuli):
        stimuli_name = get_stimuli_name(args, idx)
        stimuli_url = os.path.join(s3_bucket_path, stimuli_name)
        stimuli_download_path = os.path.join(args.stimuli_export_dir, stimuli_name)
        all_stimuli_paths.append((stimuli_url, stimuli_download_path))
    return all_stimuli_paths


def download_stim_paths(stim_paths_to_download, args):
    if args.skip_download:
        return
    for (idx, (stimuli_url, stimuli_path)) in enumerate(stim_paths_to_download):
        print(
            f"Downloading {idx}/{len(stim_paths_to_download)}: {stimuli_url} ==> {stimuli_path}"
        )
        urllib.request.urlretrieve(stimuli_url, stimuli_path)


def make_image_montage(stim_paths_to_download, args):
    images = []
    for (_, stimuli_path) in stim_paths_to_download:
        image = cv2.imread(stimuli_path)
        images.append(image)
    num_rows = len(stim_paths_to_download) / DEFAULT_NUM_PER_ROW
    montages = build_montages(images, (200, 200), (DEFAULT_NUM_PER_ROW, int(num_rows)))

    # May write multiple montages if rows x columns too small
    for idx, montage in enumerate(montages):
        montage_filename = get_montage_name(args, idx)

        montage_filename = os.path.join(args.stimuli_export_dir, montage_filename)
        cv2.imwrite(montage_filename, montage)


def main(args):
    stim_paths_to_download = build_stim_paths_to_download(args)
    download_stim_paths(stim_paths_to_download, args)
    make_image_montage(stim_paths_to_download, args)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
