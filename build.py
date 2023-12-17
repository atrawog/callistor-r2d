#!/usr/bin/env python3
import subprocess
import datetime
import re

def get_next_build_number():
    # Define the base of the image tag (without the build number)
    base_tag = datetime.datetime.now().strftime("atrawog/callisto-r2d:%Y.%m.")

    print(f"Pulling tags from the Docker registry for base tag: {base_tag}")

    # Pull tags from the Docker registry
    result = subprocess.run(['docker', 'pull', '--all-tags', 'atrawog/callisto-r2d'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to pull tags from Docker registry")

    # Initialize the highest build number found
    highest_build_number = 0

    # Regex to find matching tags
    tag_regex = re.compile(rf'^{re.escape(base_tag)}(\d{{2}})$')

    # Check each tag to find the highest build number
    for line in result.stdout.strip().split('\n'):
        match = tag_regex.search(line)
        if match:
            build_number = int(match.group(1))
            if build_number > highest_build_number:
                highest_build_number = build_number

    # Return the next build number
    return highest_build_number + 1

def build_and_tag_docker_image(build_number):
    # Define the image tag with month as two digits and build number as two digits
    image_tag = datetime.datetime.now().strftime(f"atrawog/callisto-r2d:%Y.%m.{build_number:02d}")

    print(f"Building Docker image with tag: {image_tag}")

    # Build the Docker image from Dockerfile.tpl and tag it
    build_command = f"docker build -f Dockerfile.tpl -t {image_tag} ."
    subprocess.run(build_command, shell=True, check=True)

    # Generate a new Dockerfile with the latest image as the base
    with open("Dockerfile", "w") as file:
        file.write(f"FROM {image_tag}\n")

    print(f"Docker image built and tagged as {image_tag}")
    print("New Dockerfile generated with the base image.")

if __name__ == "__main__":
    build_number = get_next_build_number()
    build_and_tag_docker_image(build_number)
