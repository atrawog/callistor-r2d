#!/usr/bin/env python3
import requests
import datetime
import re
import subprocess

# Define the base of the image tag (without the build number)
current_year_month = datetime.datetime.now().strftime("%Y.%m.")

def get_next_build_number():
    base_tag = f"atrawog/callisto-r2d:{current_year_month}"

    print("Fetching tags from Docker registry...")

    # Fetch tags from the Docker registry
    response = requests.get('https://registry.hub.docker.com/v2/repositories/atrawog/callisto-r2d/tags')
    if response.status_code != 200:
        raise RuntimeError("Failed to fetch tags from Docker registry")

    tags = response.json().get('results', [])
    build_numbers = []

    # Regex to find matching tags
    tag_regex = re.compile(rf'^{re.escape(current_year_month)}(\d{{2}})$')

    for tag in tags:
        tag_name = tag.get('name')
        match = tag_regex.match(tag_name)
        if match:
            build_number = int(match.group(1))  # Convert to integer to handle leading zeros
            build_numbers.append(build_number)

    # Determine the next build number
    next_build_number = max(build_numbers) + 1 if build_numbers else 1

    return next_build_number

def build_and_tag_docker_image(build_number):
    image_tag = f"atrawog/callisto-r2d:{current_year_month}{build_number:02d}"

    print(f"Next build number calculated: {build_number:02d}")
    print(f"Building Docker image with tag: {image_tag}")

    # Build the Docker image from Dockerfile.tpl and tag it
    build_command = f"docker build -f Dockerfile.tpl -t {image_tag} ."
    subprocess.run(build_command, shell=True, check=True)

    # Generate a new Dockerfile with the latest image as the base
    with open("Dockerfile", "w") as file:
        file.write(f"FROM {image_tag}\n")

    print(f"Docker image built and tagged as {image_tag}")

if __name__ == "__main__":
    build_number = get_next_build_number()
    build_and_tag_docker_image(build_number)
