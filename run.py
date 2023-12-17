#!/usr/bin/env python3
import subprocess
import re
import datetime

def get_latest_image_tag():
    base_tag_pattern = r"atrawog/callisto-r2d:\d{4}\.\d{2}\."

    # Get the list of Docker images
    result = subprocess.run(['docker', 'images', '--format', '{{.CreatedAt}}\t{{.Repository}}:{{.Tag}}', '--no-trunc'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to get Docker images list")

    # Extract image creation time and tag
    image_tags = []
    for line in result.stdout.strip().split('\n'):
        match = re.match(r"(.+)\t(" + base_tag_pattern + r"\d{4})", line)
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

def run_latest_image(image_tag):
    run_command = f"docker run -p 8888:8888 {image_tag}"
    subprocess.run(run_command, shell=True, check=True)
    print(f"Running Docker image: {image_tag}")

if __name__ == "__main__":
    image_tag = get_latest_image_tag()
    if image_tag:
        run_latest_image(image_tag)
    else:
        print("No Docker images found.")
