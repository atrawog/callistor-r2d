#!/usr/bin/env python3
import subprocess
import re
import datetime

def get_latest_image_tag():
    base_tag_pattern = r"atrawog/callisto-r2d:\d{4}\.\d{2}\."

    print("Checking local Docker images to find the latest image to run...")

    # Get the list of Docker images
    result = subprocess.run(['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}', '--no-trunc'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to get Docker images list")

    # Extract image tag
    image_tags = []
    for line in result.stdout.strip().split('\n'):
        match = re.match(base_tag_pattern + r"\d{2}", line)
        if match:
            image_tags.append(line)

    if not image_tags:
        return None

    # Sort the tags by build number, and return the latest
    latest_image_tag = sorted(image_tags, key=lambda x: int(x.split('.')[-1]), reverse=True)[0]
    return latest_image_tag

def run_latest_image(image_tag):
    print(f"Running Docker image: {image_tag} with port 8888:8888 mapping")
    run_command = f"docker run -p 8888:8888 {image_tag}"
    subprocess.run(run_command, shell=True, check=True)

if __name__ == "__main__":
    image_tag = get_latest_image_tag()
    if image_tag:
        run_latest_image(image_tag)
    else:
        print("No suitable Docker images found to run.")
