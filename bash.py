#!/usr/bin/env python3
import subprocess
import re

def get_latest_image_tag():
    # Get the list of Docker images sorted by creation date
    result = subprocess.run(['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}', '--no-trunc'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to get Docker images list")

    # Extract image tags
    image_tags = result.stdout.strip().split('\n')

    # Filter tags for a specific repository if necessary
    filtered_tags = [tag for tag in image_tags if tag.startswith('atrawog/callisto-r2d:')]

    if not filtered_tags:
        return None

    # Return the latest tag
    return filtered_tags[0]

def run_bash_in_latest_image(image_tag):
    print(f"Running Bash in Docker image: {image_tag}")
    run_command = f"docker run -it --rm {image_tag} /bin/bash"
    subprocess.run(run_command, shell=True)

if __name__ == "__main__":
    image_tag = get_latest_image_tag()
    if image_tag:
        run_bash_in_latest_image(image_tag)
    else:
        print("No suitable Docker images found to run.")
