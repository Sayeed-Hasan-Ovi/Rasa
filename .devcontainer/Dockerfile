FROM python:3.10-slim

# Install necessary packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set the default user
USER $USERNAME

# Ensure pip is updated
RUN pip install --upgrade pip

# Set working directory
WORKDIR /workspace

# Set environment variables to ensure Python outputs everything immediately
ENV PYTHONUNBUFFERED=1