FROM python:3.12-slim

WORKDIR /ouroboros

# # Copy the current directory contents into the container at WORKDIR
COPY . /ouroboros

RUN pip install  --no-cache -r requirements/dev-linux.txt

RUN apt-get update
RUN apt-get install -y --no-install-recommends azure-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN az login

