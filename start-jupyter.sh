#!/bin/bash

# Check if JUPYTERHUB_SERVICE_URL is set
if [ -z "$JUPYTERHUB_SERVICE_URL" ]; then
    # If not set, start Jupyter Notebook
    echo "Starting Jupyter Notebook..."
    exec jupyter notebook --ip='0.0.0.0' --port=8888 --no-browser --allow-root
else
    # If set, start JupyterHub Single-User server
    echo "Starting JupyterHub Single-User Server..."
    exec jupyterhub-singleuser --ip='0.0.0.0' --port=8888
fi
