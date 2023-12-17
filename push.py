#!/usr/bin/env python3
import subprocess
import re
import datetime

def get_latest_image_tag():
    # Get the list of Docker images sorted by creation time
    result = subprocess.run(['docker', 'images', '--format', '{{.CreatedAt}}\t{{.Repository}}:{{.Tag}}', '--no-trunc'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to get Docker images list")

    # Extract image creation time and tag
    lines = result.stdout.strip().split('\n')
    latest_image = None
    latest_time = None
    for line in lines:
        match = re.match(r"(.+)\t(.+)", line)
        if match:
            image_time, image_tag = match.groups()
            try:
                # Adjust the datetime format to exclude the timezone
                image_time = datetime.datetime.strptime(image_time.split('+')[0].strip(), "%Y-%m-%d %H:%M:%S")
                if latest_time is None or image_time > latest_time:
                    latest_time = image_time
                    latest_image = image_tag
            except ValueError as e:
                print(f"Error parsing date: {e}")

    return latest_image

def push_docker_image_to_hub(image_tag):
    # Push the Docker image to Docker Hub
    push_command = f"docker push {image_tag}"
    subprocess.run(push_command, shell=True, check=True)

    print(f"Docker image {image_tag} pushed to Docker Hub.")

if __name__ == "__main__":
    image_tag = get_latest_image_tag()
    if image_tag:
        push_docker_image_to_hub(image_tag)
    else:
        print("No Docker images found.")
