#!/usr/bin/env python3
import subprocess
import re
import datetime

def get_latest_image_tag():
    # Define the base pattern for the image tag
    base_tag_pattern = r"atrawog/callisto-r2d:\d{4}\.\d{2}\."

    # Get the list of Docker images
    result = subprocess.run(['docker', 'images', '--format', '{{.CreatedAt}}\t{{.Repository}}:{{.Tag}}', '--no-trunc'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to get Docker images list")

    # Extract image creation time and tag
    latest_image = None
    latest_time = None
    for line in result.stdout.strip().split('\n'):
        match = re.match(r"(.+)\t(" + base_tag_pattern + r"\d{4})", line)
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
