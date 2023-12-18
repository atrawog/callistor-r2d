#!/bin/bash

# Check if the user can execute commands with sudo
if sudo -l &>/dev/null; then
    echo "User has sudo privileges. Proceeding with file and directory checks."

    # Get the current user's UID and GID
    USER_UID=$(id -u)
    USER_GID=$(id -g)

    # Define the environment variables to check
    env_vars=("KVM_DEVICE" "DOCKER_SOCKET" "CONTAINER_WORKSPACE_FOLDER")

    # Loop over the environment variables
    for env_var in "${env_vars[@]}"; do
        # Check if the environment variable is set and points to a directory
        if [ -n "${!env_var}" ] && [ -d "${!env_var}" ]; then
            echo "Recursively checking directory and files in ${!env_var}"

            # Recursively loop through each file and directory within the specified path
            find "${!env_var}" -exec bash -c '
                for path; do
                    # Check if the path is a file or directory and update its ownership if needed
                    if [ -e "$path" ]; then
                        OWNER_UID=$(stat -c "%u" "$path")
                        OWNER_GID=$(stat -c "%g" "$path")

                        if [ "$OWNER_UID" -ne '"$USER_UID"' ] || [ "$OWNER_GID" -ne '"$USER_GID"' ]; then
                            echo "Changing ownership of $path"
                            sudo chown '"$USER_UID:$USER_GID"' "$path"
                        fi
                    fi
                done
            ' bash {} +

        else
            echo "Environment variable $env_var is not set or does not point to a valid directory. Skipping."
        fi
    done
else
    echo "User does not have sudo privileges. Exiting script."
fi
