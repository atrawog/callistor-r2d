#!/bin/bash

has_sudo() {
    if sudo -l &>/dev/null; then
        return 0
    else
        return 1
    fi
}

fix_permissions() {
    local target_directory=$1
    local target_uid=$2
    local target_gid=$3

    if [[ -z "$target_directory" ]]; then
        echo "The target directory variable is not set. Skipping permissions change."
        return
    fi

    if [ -e "$target_directory" ]; then
        local directory_uid=$(stat -c '%u' "$target_directory")
        local directory_gid=$(stat -c '%g' "$target_directory")

        if [ "$target_uid" != "$directory_uid" ] || [ "$target_gid" != "$directory_gid" ]; then
            sudo chown -R $target_uid:$target_gid "$target_directory"
        fi
    else
        echo "Directory $target_directory does not exist."
    fi
}

if has_sudo; then
    # Fix permissions for MAMBA_ROOT_PREFIX
    fix_permissions "$MAMBA_ROOT_PREFIX" "$MAMBA_USER_ID" "$MAMBA_USER_GID"

    # Fix permissions for KVM_DEVICE
    fix_permissions "$KVM_DEVICE" "$MAMBA_USER_ID" "$MAMBA_USER_GID"

    # Fix permissions for DOCKER_SOCKET
    fix_permissions "$DOCKER_SOCKET" "$MAMBA_USER_ID" "$MAMBA_USER_GID"
else
    echo "User does not have sudo permissions. Can't set permissions."
fi
