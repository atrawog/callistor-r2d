#!/usr/bin/env python3
import subprocess
import re
import datetime

def get_latest_image_tag():
    base_tag_pattern = r"atrawog/callisto-r2d:\d{4}\.\d{2}\."

    print("Checking local Docker images to find the latest image...")

    # Get the list of Docker images
    result = subprocess.run(['docker', 'images', '--format', '{{.CreatedAt}}\t{{.Repository}}:{{.Tag}}', '--no-trunc'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to get Docker images list")

    # Extract image creation time and tag
    image_tags = []
    for line in result.stdout.strip().split('\n'):
        match = re.match(r"(.+)\t(" + base_tag_pattern + r"\d{2})", line)
        if match:
            image_time, image_tag = match.groups()
            try:
                image_time = datetime.datetime.strptime(image_time.split('+')[0].strip(), "%Y-%m-%d %H:%M:%S")
                image_tags.append((image_time, image_tag))
            except ValueError as e:
                print(f"Error parsing date: {e}")

    if not image_tags:
        return None

    # Sort the tags by creation time and build number, and return the latest
    latest_image_tag = sorted(image_tags, key=lambda x: (x[0], int(x[1].split('.')[-1])), reverse=True)[0][1]
    return latest_image_tag

def push_docker_image_to_hub(image_tag):
    print(f"Pushing Docker image to Docker Hub: {image_tag}")
    push_command = f"docker push {image_tag}"
    subprocess.run(push_command, shell=True, check=True)
    print(f"Docker image {image_tag} pushed to Docker Hub.")

if __name__ == "__main__":
    image_tag = get_latest_image_tag()
    if image_tag:
        push_docker_image_to_hub(image_tag)
    else:
        print("No Docker images found.")
