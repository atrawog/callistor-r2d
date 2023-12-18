#!/bin/bash

# Check if the user can execute commands with sudo
if sudo -l &>/dev/null; then
    echo "User has sudo privileges. Proceeding with file checks."

    # Get the current user's UID and GID
    USER_UID=$(id -u)
    USER_GID=$(id -g)

    # Define the environment variables to check
    env_vars=("KVM_DEVICE" "DOCKER_SOCKET" "MAMBA_ROOT_PREFIX" "CONTAINER_WORKSPACE_FOLDER")

    # Loop over the environment variables
    for env_var in "${env_vars[@]}"; do
        # Check if the environment variable is set
        if [ -n "${!env_var}" ]; then
            echo "Checking files in ${!env_var}"

            # Loop through each file in the specified directory
            for file in ${!env_var}/*; do
                if [ -f "$file" ]; then
                    # Get file's UID and GID
                    FILE_UID=$(stat -c '%u' "$file")
                    FILE_GID=$(stat -c '%g' "$file")

                    # Compare file's UID and GID with the user's UID and GID
                    if [ "$FILE_UID" -ne "$USER_UID" ] || [ "$FILE_GID" -ne "$USER_GID" ]; then
                        echo "Changing ownership for $file"
                        sudo chown "$USER_UID":"$USER_GID" "$file" # Change file ownership to the current user
                    else
                        echo "Ownership for $file is already correct."
                    fi
                fi
            done
        else
            echo "Environment variable $env_var is not set. Skipping."
        fi
    done
else
    echo "User does not have sudo privileges. Exiting script."
fi
