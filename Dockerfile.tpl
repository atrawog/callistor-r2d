# syntax=docker/dockerfile:1.2

ARG BASE_IMAGE=debian:bookworm-slim
FROM --platform=$BUILDPLATFORM $BASE_IMAGE AS fetch
ARG VERSION=1.5.3

ENV DEBIAN_FRONTEND=noninteractive

RUN rm -f /etc/apt/apt.conf.d/docker-*
RUN --mount=type=cache,target=/var/cache/apt,id=apt-deb12 apt-get update && apt-get install -y --no-install-recommends bzip2 ca-certificates curl

RUN if [ "$BUILDPLATFORM" = 'linux/arm64' ]; then \
    export ARCH='aarch64'; \
  else \
    export ARCH='64'; \
  fi; \
  curl -L "https://micro.mamba.pm/api/micromamba/linux-${ARCH}/${VERSION}" | \
  tar -xj -C "/tmp" "bin/micromamba"


FROM --platform=$BUILDPLATFORM $BASE_IMAGE as micromamba

ARG MAMBA_ROOT_PREFIX="/opt/conda"
ARG MAMBA_EXE="/bin/micromamba"

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV MAMBA_ROOT_PREFIX=$MAMBA_ROOT_PREFIX
ENV MAMBA_EXE=$MAMBA_EXE
ENV PATH="${PATH}:${MAMBA_ROOT_PREFIX}/bin"

COPY --from=fetch /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=fetch /tmp/bin/micromamba "$MAMBA_EXE"

ARG MAMBA_USER=jovian
ARG MAMBA_USER_ID=1000
ARG MAMBA_USER_GID=1000

ENV MAMBA_USER=$MAMBA_USER
ENV MAMBA_USER_ID=$MAMBA_USER_ID
ENV MAMBA_USER_GID=$MAMBA_USER_GID

RUN groupadd -g "${MAMBA_USER_GID}" "${MAMBA_USER}" && \
    useradd -m -u "${MAMBA_USER_ID}" -g "${MAMBA_USER_GID}" -s /bin/bash "${MAMBA_USER}"
RUN mkdir -p "${MAMBA_ROOT_PREFIX}/environments" && \
    chown "${MAMBA_USER}:${MAMBA_USER}" "${MAMBA_ROOT_PREFIX}"

ARG CONTAINER_WORKSPACE_FOLDER=/workspace
RUN mkdir -p "${CONTAINER_WORKSPACE_FOLDER}"
WORKDIR "${CONTAINER_WORKSPACE_FOLDER}"

USER $MAMBA_USER
RUN micromamba shell init --shell bash --prefix=$MAMBA_ROOT_PREFIX
SHELL ["/bin/bash", "--rcfile", "/$MAMBA_USER/.bashrc", "-c"]
USER root

# Set up user
ARG NB_USER=$MAMBA_USER
ARG NB_UID=$MAMBA_USER_ID
ENV USER=${NB_USER} \
    HOME=/home/${NB_USER}

RUN if ! getent group ${NB_UID} >/dev/null; then \
        groupadd --gid ${NB_UID} ${NB_USER}; \
    fi && \
    if ! getent passwd ${NB_UID} >/dev/null; then \
        useradd \
            --comment "Default user" \
            --create-home \
            --gid ${NB_UID} \
            --no-log-init \
            --shell /bin/bash \
            --uid ${NB_UID} \
            ${NB_USER}; \
    fi


# Environment variables required for build
ENV APP_BASE=/srv
# ENV CONDA_DIR=${APP_BASE}/conda
ENV NB_PYTHON_PREFIX=${CONDA_DIR}/envs/notebook
ENV NPM_DIR=${APP_BASE}/npm
ENV NPM_CONFIG_GLOBALCONFIG=${NPM_DIR}/npmrc
# ENV NB_ENVIRONMENT_FILE=/tmp/env/environment.lock
# ENV MAMBA_ROOT_PREFIX=${CONDA_DIR}
# ENV MAMBA_EXE=${CONDA_DIR}/bin/mamba
# ENV CONDA_PLATFORM=linux-64
ENV KERNEL_PYTHON_PREFIX=${NB_PYTHON_PREFIX}
# Special case PATH
# ENV PATH=${NB_PYTHON_PREFIX}/bin:${CONDA_DIR}/bin:${NPM_DIR}/bin:${PATH}
# If scripts required during build are present, copy them

# COPY --chown=${NB_UID}:${NB_UID} activate-conda.sh /etc/profile.d/activate-conda.sh
# COPY --chown=${NB_UID}:${NB_UID} environment.lock /tmp/env/environment.lock


RUN mkdir -p ${NPM_DIR} && \
chown -R ${NB_USER}:${NB_USER} ${NPM_DIR}

# ensure root user after build scripts
USER root

# Allow target path repo is cloned to be configurable
ARG REPO_DIR=${HOME}
ENV REPO_DIR=${REPO_DIR}
# Create a folder and grant the user permissions if it doesn't exist
RUN if [ ! -d "${REPO_DIR}" ]; then \
        /usr/bin/install -o ${NB_USER} -g ${NB_USER} -d "${REPO_DIR}"; \
    fi

WORKDIR ${REPO_DIR}
RUN chown ${NB_USER}:${NB_USER} ${REPO_DIR}

# We want to allow two things:
#   1. If there's a .local/bin directory in the repo, things there
#      should automatically be in path
#   2. postBuild and users should be able to install things into ~/.local/bin
#      and have them be automatically in path
#
# The XDG standard suggests ~/.local/bin as the path for local user-specific
# installs. See https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
# ENV PATH=${HOME}/.local/bin:${REPO_DIR}/.local/bin:${PATH}

# The rest of the environment
ENV CONDA_DEFAULT_ENV=${KERNEL_PYTHON_PREFIX}
# Run pre-assemble scripts! These are instructions that depend on the content
# of the repository but don't access any files in the repository. By executing
# them before copying the repository itself we can cache these steps. For
# example installing APT packages.
# If scripts required during build are present, copy them

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /opt/conda/environments/environment.yml
RUN --mount=type=cache,target=$MAMBA_ROOT_PREFIX/pkgs,id=mamba-pkgs micromamba install -y -f /opt/conda/environments/environment.yml


# ensure root user after preassemble scripts
USER root

# Copy stuff.
# COPY --chown=${NB_UID}:${NB_UID} src/ ${REPO_DIR}/

# Run assemble scripts! These will actually turn the specification
# in the repository into an image.


# Container image Labels!
# Put these at the end, since we don't want to rebuild everything
# when these change! Did I mention I hate Dockerfile cache semantics?

# LABEL repo2docker.ref="None"
# LABEL repo2docker.repo="local"
# LABEL repo2docker.version="2023.06.0"

# We always want containers to run as non-root
USER ${NB_USER}

# Add start script
# Add entrypoint
# ENV PYTHONUNBUFFERED=1
# COPY python3-login /usr/local/bin/python3-login
# COPY repo2docker-entrypoint /usr/local/bin/repo2docker-entrypoint
# ENTRYPOINT ["/usr/local/bin/repo2docker-entrypoint"]

# Specify the default command to run
CMD ["jupyter", "notebook", "--ip", "0.0.0.0"]