"""
upload_stimuli_s3.py | Author: Catherine Wong

Utility script to upload datasets of stimuli to an AWS S3 bucket that will serve as a permanent public repository for these datasets.

Assumes a file called .aws/credentials with appropriate credentials in the home directory.

Usage:
    python data/upload_stimuli_s3.py
        --stimuli_export_dir: top-level directory for the stimuli to upload.
        --curriculum_export_dir: top-level directory containing the JSON curriculum file we will use.
        --curriculum: the specific curriculum JSON file to use for uploading. 
"""
import os, json, argparse
import boto3

DEFAULT_EXPORT_DIR = "data"
DEFAULT_RENDERS_SUBDIR = "renders"

SPLITS = ["train", "test"]
EXPERIMENT_NAME = "lax"
DOMAIN_NAME = "drawing"
CURRICULUM_METADATA = "metadata"
CURRICULUM_NAME = "name"

DEFAULT_BASE_CONFIG = "base_experiment_config.json"
CONFIG_NAME = "config_name"
CONFIG_EXP_PARAMETERS = "experiment_parameters"
S3_BUCKET = "s3_bucket"
S3_BUCKET_TOTAL_STIMULI = "s3_bucket_total_stimuli"
S3_STIMULI_PATH_FORMAT = "s3_stimuli_path_format"
S3_STIMULI_PATH_TO_LOCAL = "s3_stimuli_paths_to_local_name"
MANIFEST = "manifest.json"

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
    "--base_experiment_config",
    default=os.path.join(DEFAULT_EXPORT_DIR, DEFAULT_BASE_CONFIG),
    help="Base experimental config to populate with experiment-specific data.",
)
parser.add_argument(
    "--curriculum",
    required=True,
    help="Name of the curriculum file. Must be in the curriculum export dir.",
)
parser.add_argument(
    "--skip_upload",
    action="store_true",
    help="Whether to skip data upload and only generate a config.",
)


def get_stim_paths_from_curriculum(args):
    curriculum_path = os.path.join(args.curriculum_export_dir, args.curriculum)
    with open(curriculum_path) as f:
        curriculum = json.load(f)

    all_stimuli_paths = []
    for split in SPLITS:
        if split in curriculum:
            for condition in curriculum[split]:
                for curriculum_block in curriculum[split][condition]:
                    stimuli_file_paths = curriculum[split][condition][curriculum_block]
                    all_stimuli_paths += [
                        os.path.join(args.stimuli_export_dir, stimuli_file_path)
                        for stimuli_file_path in stimuli_file_paths
                    ]
    for stimuli_file_path in all_stimuli_paths:
        assert os.path.exists(stimuli_file_path)
    print(f"Found {len(all_stimuli_paths)} stimuli paths to upload....")
    return curriculum, sorted(all_stimuli_paths)


def cleaned_name(name):
    # Cleans characters for S3.
    name = name.lower()
    for escaped_character in ["_", ","]:
        name = name.replace(escaped_character, "-")
    return name


def get_bucket_name(args, curriculum):
    cleaned_curriculum_name = cleaned_name(
        curriculum[CURRICULUM_METADATA][CURRICULUM_NAME]
    )
    return f"{EXPERIMENT_NAME}-{DOMAIN_NAME}-{cleaned_curriculum_name}"


def get_stimuli_name(args, curriculum, index_number):
    padded_index = str.zfill(str(index_number), 3)
    cleaned_curriculum_name = cleaned_name(
        curriculum[CURRICULUM_METADATA][CURRICULUM_NAME]
    )
    return (
        f"{EXPERIMENT_NAME}-{DOMAIN_NAME}-{cleaned_curriculum_name}-{padded_index}.png"
    )


def connect_to_s3_and_create_bucket(bucket_name):
    # Establish connection to S3
    s3 = boto3.resource("s3")
    try:
        b = s3.create_bucket(Bucket=bucket_name)
    except:
        print(f"Found existing S3 bucket: {bucket_name}")
        b = s3.Bucket(Bucket=bucket_name)
    b.Acl().put(ACL="public-read")
    return s3, b


def upload_stimuli_and_manifest_to_s3(args, curriculum, stim_paths_to_upload):
    """Uploads stimuli following the naming convention for S3 buckets. Also uploads a manifest with details mapping the bucket stimuli paths to the originals."""
    bucket_name = get_bucket_name(args, curriculum)
    demo_stimuli_name = get_stimuli_name(args, curriculum, 0)
    input(
        f"Uploading {len(stim_paths_to_upload)} to bucket: {bucket_name} with stimuli_names: {demo_stimuli_name}? Hit any key to continue:"
    )
    s3, b = connect_to_s3_and_create_bucket(bucket_name)
    stim_in_bucket_to_local = dict()
    for stim_idx, stim_path in enumerate(stim_paths_to_upload):
        stimuli_name_in_bucket = get_stimuli_name(args, curriculum, stim_idx)
        stim_in_bucket_to_local[stimuli_name_in_bucket] = stim_path
        if not args.skip_upload:
            print(
                f"Now uploading [{stim_idx}/{len(stim_paths_to_upload)}]: {stim_path} ==> {stimuli_name_in_bucket}"
            )
            s3.Object(bucket_name, stimuli_name_in_bucket).put(
                Body=open(stim_path, "rb")
            )  # Upload stimuli
            s3.Object(bucket_name, stimuli_name_in_bucket).Acl().put(
                ACL="public-read"
            )  # Set access controls

    # Create and upload manifest.
    manifest = generate_manifest(args, curriculum, stim_in_bucket_to_local)
    s3.Object(bucket_name, MANIFEST).put(
        Body=str(json.dumps(manifest))
    )  # Upload stimuli
    s3.Object(bucket_name, MANIFEST).Acl().put(ACL="public-read")

    total_stimuli = len(stim_paths_to_upload)
    return bucket_name, demo_stimuli_name, total_stimuli


def generate_manifest(args, curriculum, stim_in_bucket_to_local):
    manifest_base = curriculum
    manifest_base[S3_STIMULI_PATH_TO_LOCAL] = stim_in_bucket_to_local
    return manifest_base


def generate_base_config(args, bucket_name, demo_stimuli_name, total_stimuli):
    """Generates a base experiment config for using the stimuli in this bucket."""
    with open(args.base_experiment_config) as f:
        base_config = json.load(f)

    base_config[CONFIG_EXP_PARAMETERS][S3_BUCKET] = bucket_name
    base_config[CONFIG_EXP_PARAMETERS][S3_STIMULI_PATH_FORMAT] = demo_stimuli_name
    base_config[CONFIG_EXP_PARAMETERS][S3_BUCKET_TOTAL_STIMULI] = total_stimuli
    base_config[CONFIG_NAME] = bucket_name

    config_name = os.path.join(DEFAULT_EXPORT_DIR, f"{bucket_name}.json")
    with open(config_name, "w") as f:
        json.dump(base_config, f)
    print(f"Wrote base experimental config for bucket to: {config_name}")


def main(args):
    curriculum, stim_paths_to_upload = get_stim_paths_from_curriculum(args)
    bucket_name, demo_stimuli_name, total_stimuli = upload_stimuli_and_manifest_to_s3(
        args, curriculum, stim_paths_to_upload
    )
    generate_base_config(args, bucket_name, demo_stimuli_name, total_stimuli)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
