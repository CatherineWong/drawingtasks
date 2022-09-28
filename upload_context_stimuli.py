"""
upload_context_stimuli.py | Upload context stimuli, then upload the stimuli sets.

Usage:  python upload_context_stimuli.py --task_generators wheels_context_programs dials_context_programs furniture_context_programs
"""
import os
import boto3
import argparse
import json

import tasksgenerator.furniture_context_tasks_generator
import tasksgenerator.dial_context_tasks_generator
import tasksgenerator.wheels_context_tasks_generator

DEFAULT_EXPORT_DIR = "data"
DEFAULT_RENDERS_SUBDIR = "renders"

parser = argparse.ArgumentParser()

parser.add_argument(
    "--task_generators",
    action="store_true",
    nargs="+",
    help="Whether to skip data upload and only generate a config.",
)

parser.add_argument(
    "--skip_upload",
    action="store_true",
    help="Whether to skip data upload and only generate a config.",
)


def connect_to_s3_and_create_bucket(bucket_name="lax-context-stimuli"):
    # Establish connection to S3
    s3 = boto3.resource("s3")
    try:
        b = s3.create_bucket(Bucket=bucket_name)
    except:
        print(f"Found existing S3 bucket: {bucket_name}")
        b = s3.Bucket(Bucket=bucket_name)
    b.Acl().put(ACL="public-read")
    return s3, b


def upload_images_to_s3(stim_paths_to_upload, bucket_name="lax-context-stimuli"):
    s3, b = connect_to_s3_and_create_bucket(bucket_name)
    for stim_idx, stim_path in enumerate(stim_paths_to_upload):
        stimuli_name_in_bucket = os.path.basename(stim_path)
        if not args.skip_upload_stimuli:
            print(
                f"Now uploading [{stim_idx}/{len(stim_paths_to_upload)}]: {stim_path} ==> {stimuli_name_in_bucket}"
            )
            s3.Object(bucket_name, stimuli_name_in_bucket).put(
                Body=open(stim_path, "rb")
            )  # Upload stimuli
            s3.Object(bucket_name, stimuli_name_in_bucket).Acl().put(
                ACL="public-read"
            )  # Set access controls


def upload_json_to_s3(json_object, json_name, bucket_name="lax-context-stimuli"):
    s3, b = connect_to_s3_and_create_bucket(bucket_name)
    s3.Object(bucket_name, json_name).put(
        Body=str(json.dumps(json_object))
    )  # Upload stimuli
    s3.Object(bucket_name, json_name).Acl().put(ACL="public-read")


def upload_image_stimuli(args):
    # Get images to upload.
    renders_path = os.path.join(DEFAULT_EXPORT_DIR, DEFAULT_RENDERS_SUBDIR)

    images_to_upload = []
    for task_generator in args.task_generators:
        # Check for any images that have that name.
        image_paths = [
            image_path
            for image_path in os.path.list(renders_path)
            if task_generator in image_path
        ]
        images_to_upload += image_paths
    print(image_paths)


def main(args):
    upload_image_stimuli(args)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
