#!/usr/bin/env python3

import json
import subprocess
import os
import sys

def preprocess_json(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    processed_lines = []
    for line in lines:
        if '//' in line:
            # Split the line at the first occurrence of '//' and keep only the first part
            line = line.split('//', 1)[0]
        processed_lines.append(line)

    return ''.join(processed_lines)

def read_devcontainer_config(file_path):
    json_content = preprocess_json(file_path)
    return json.loads(json_content)

def build_docker_image_with_buildx(config_file_path, config, image_name):
    build_config = config.get('build', {})
    build_context = build_config.get('context', '.')
    dockerfile = build_config.get('dockerfile', 'Dockerfile')
    build_args = build_config.get('args', {})
    cache_from = build_config.get('cacheFrom', [])

    # Prepare build arguments for buildx
    args_str = ' '.join([f"--build-arg {key}={value}" for key, value in build_args.items()])
    cache_from_str = ' '.join([f"--cache-from={item}" for item in cache_from])

    # Change to the directory where devcontainer.json is located
    os.chdir(os.path.dirname(config_file_path))

    # Ensure docker buildx is available and set up
    subprocess.run("docker buildx use default", shell=True, check=True)

    # Build the image using buildx
    buildx_command = f"DOCKER_BUILDKIT=1 BUILDKIT_INLINE_CACHE=1 docker buildx build -f {dockerfile} {args_str} {cache_from_str} {build_context} -t {image_name} --load"
    print("Running",buildx_command)
    subprocess.run(buildx_command, shell=True, check=True)

if __name__ == "__main__":
    config_file_path = '.devcontainer/devcontainer.json'
    config = read_devcontainer_config(config_file_path)
    
    # Set the default image name or use the one provided as an argument
    image_name = sys.argv[1] if len(sys.argv) > 1 else 'atrawog/callisto-minimal'
    build_docker_image_with_buildx(config_file_path, config, image_name)
