#!/usr/bin/env python3
import subprocess
import datetime

def build_and_tag_docker_image():
    # Format the current date and time
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M")

    # Define the image tag
    image_tag = f"atrawog/callisto-r2d:{current_time}"

    # Build the Docker image from Dockerfile.tpl and tag it
    build_command = f"docker build -f Dockerfile.tpl -t {image_tag} ."
    subprocess.run(build_command, shell=True, check=True)

    # Generate a new Dockerfile with the base image
    new_dockerfile_content = f"FROM {image_tag}\n"
    with open("Dockerfile", "w") as file:
        file.write(new_dockerfile_content)

    print(f"Docker image built and tagged as {image_tag}")
    print("New Dockerfile generated with the base image.")

if __name__ == "__main__":
    build_and_tag_docker_image()
