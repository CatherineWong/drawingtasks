"""
upload_context_stimuli.py | Upload context stimuli, then upload the stimuli sets.

Usage:  
v1 experiment: 
python upload_context_stimuli.py --task_generators wheels_context_programs dials_context_programs furniture_context_programs --generate_v1_random_contexts

python upload_context_stimuli.py --task_generators wheels_context_programs dials_context_programs furniture_context_programs --generate_v2_random_contexts --skip_upload_stimuli 

Uploads to: https://lax-context-stimuli.s3.amazonaws.com/
"""
import os
import random
import numpy as np

import boto3
import argparse
import json

import tasksgenerator.furniture_context_tasks_generator
import tasksgenerator.dial_context_tasks_generator
import tasksgenerator.wheels_context_tasks_generator

from tasksgenerator.bases_parts_tasks_generator import (
    CONTEXT_DIVERSE,
    CONTEXT_LARGE_ABSTRACTIONS,
    CONTEXT_SMALL_ABSTRACTIONS,
)

TARGET_PATH = "https://lax-context-stimuli.s3.amazonaws.com/"

DEFAULT_EXPORT_DIR = "data"
DEFAULT_RENDERS_SUBDIR = "renders"

parser = argparse.ArgumentParser()

parser.add_argument(
    "--task_generators",
    nargs="+",
    help="Task generators to draw on to create contextual stimuli.",
)

parser.add_argument(
    "--context_size",
    type=int,
    default=9,
    help="Task generators to draw on to create contextual stimuli.",
)

parser.add_argument(
    "--targets_size",
    type=int,
    default=6,
    help="Task generators to draw on to create contextual stimuli.",
)

parser.add_argument(
    "--skip_upload_stimuli",
    action="store_true",
    help="Whether to skip images upload and only generate a config.",
)

parser.add_argument(
    "--generate_v1_random_contexts",
    action="store_true",
    help="v1 experiment: 3 contexts, single target.",
)

parser.add_argument(
    "--generate_v2_random_contexts",
    action="store_true",
    help="v2 experiment: 2 contexts, n targets.",
)

random.seed(0)


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
            for image_path in os.listdir(renders_path)
            if task_generator in image_path
        ]
        images_to_upload += image_paths
    images_to_upload = [os.path.join(renders_path, p) for p in images_to_upload]
    upload_images_to_s3(images_to_upload, bucket_name="lax-context-stimuli")


def generate_v1_random_contexts(args):
    # All possible images.
    renders_path = os.path.join(DEFAULT_EXPORT_DIR, DEFAULT_RENDERS_SUBDIR)
    all_context_images = []
    for task_generator in args.task_generators:
        image_paths = [
            image_path
            for image_path in os.listdir(renders_path)
            if task_generator in image_path
        ]
        all_context_images += image_paths

    context_targets = []
    for task_generator in args.task_generators:
        # Large context targets.
        large_abstractions_context = [
            p
            for p in all_context_images
            if task_generator in p and CONTEXT_LARGE_ABSTRACTIONS in p
        ]
        small_abstractions_context = [
            p
            for p in all_context_images
            if task_generator in p and CONTEXT_SMALL_ABSTRACTIONS in p
        ]
        other_subdomains_context = [
            p for p in all_context_images if task_generator not in p
        ]
        for target in large_abstractions_context:
            target_large_context = random.sample(
                [p for p in large_abstractions_context if p != target],
                args.context_size,
            )
            target_small_context = random.sample(
                [p for p in small_abstractions_context if p != target],
                args.context_size,
            )
            target_diverse_context = random.sample(
                other_subdomains_context, args.context_size,
            )
            context_targets.append(
                {
                    "target": TARGET_PATH + target,
                    "subdomain": task_generator,
                    "context_0": [TARGET_PATH + p for p in target_large_context],
                    "context_1": [TARGET_PATH + p for p in target_small_context],
                    "context_2": [TARGET_PATH + p for p in target_diverse_context],
                }
            )
    # Create the JSON.
    experiment_name = "lax-drawing-context-library-v1"
    context_json = {
        "experiment_name": experiment_name,
        "metadata": {
            "human_readable": "Context manipulation experiment. This contains the PNG names which need to be preprocessed to map them to URLs on S3, since we have a different numbering scheme.",
        },
        "stimuli": context_targets,
    }
    return experiment_name, context_json


def generate_v2_random_contexts(args):
    # All possible images.
    renders_path = os.path.join(DEFAULT_EXPORT_DIR, DEFAULT_RENDERS_SUBDIR)
    all_context_images = []
    for task_generator in args.task_generators:
        image_paths = [
            image_path
            for image_path in os.listdir(renders_path)
            if task_generator in image_path
        ]
        all_context_images += image_paths

    context_targets = []
    for task_generator in args.task_generators:
        # Large context targets.
        large_abstractions_context = [
            p
            for p in all_context_images
            if task_generator in p and CONTEXT_LARGE_ABSTRACTIONS in p
        ]
        small_abstractions_context = [
            p
            for p in all_context_images
            if task_generator in p and CONTEXT_SMALL_ABSTRACTIONS in p
        ]
        # Random shuffle.
        random.shuffle(large_abstractions_context)
        random.shuffle(small_abstractions_context)

        # Total stimuli: n_context + n_targets
        total_stimuli = args.context_size + args.targets_size
        large_abstractions_context, small_abstractions_context = (
            large_abstractions_context[:total_stimuli],
            small_abstractions_context[:total_stimuli],
        )
        # Create shifted disjoint batches to the best that we can.
        n_batches = int(np.ceil(total_stimuli / args.targets_size))
        large_wraparound, small_wraparound = (
            large_abstractions_context + large_abstractions_context,
            small_abstractions_context + small_abstractions_context,
        )
        for batch in range(n_batches):
            batch_start, batch_end = (
                batch * args.targets_size,
                (batch + 1) * args.targets_size,
            )
            large_targets = large_wraparound[batch_start:batch_end]
            small_targets = small_wraparound[batch_start:batch_end]
            large_context = [
                i for i in large_abstractions_context if i not in large_targets
            ]
            small_context = [
                i for i in small_abstractions_context if i not in small_targets
            ]

            context_targets.append(
                {
                    "target-set-id": hash(str(large_targets)),
                    "subdomain": task_generator,
                    "targets": [TARGET_PATH + t for t in large_targets],
                    "context-1-id": hash(str(large_context)),
                    "context-2-id": hash(str(small_context)),
                    "context-1": [TARGET_PATH + p for p in large_context],
                    "context-2": [TARGET_PATH + p for p in small_context],
                }
            )
    # Create the JSON.
    experiment_name = "lax-drawing-context-library-v2"
    context_json = {
        "experiment_name": experiment_name,
        "metadata": {
            "human_readable": "Context manipulation experiment v2. Fixed context, n targets",
        },
        "stimuli": context_targets,
    }
    return experiment_name, context_json


def main(args):
    if not args.skip_upload_stimuli:
        upload_image_stimuli(args)

    if args.generate_v1_random_contexts:
        experiment_name, context_generation = generate_v1_random_contexts(args)

    if args.generate_v2_random_contexts:
        experiment_name, context_generation = generate_v2_random_contexts(args)

    # Write out the stimulus file.
    with open(os.path.join(DEFAULT_EXPORT_DIR, f"{experiment_name}.json"), "w",) as f:
        json.dump(context_generation, f)

    upload_json_to_s3(
        json_object=context_generation,
        json_name=f"{experiment_name}.json",
        bucket_name="lax-context-stimuli",
    )


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
