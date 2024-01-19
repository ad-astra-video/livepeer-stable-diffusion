#!/bin/bash
echo "starting sd-video-api"

#set options
export RUN_FRONTEND=no
export RUN_PROCESSING=yes

#set the env variables
#front end setup
export SVD_HOST=localhost
export SVD_PORT=9000
#backend processing setup
#run check_cuda_devices.py to see ordering of GPUs
export SVD_GPU="cuda:0"
export GO_LIVEPEER_URL="https://127.0.0.1:9935"
export GO_LIVEPEER_SECRET="verybigsecret"
export LIVEPEER_JOB_CAPABILITY="stable-video-diffusion"
export LIVEPEER_JOB_CAPABILITY_DESCRIPTION="generate videos using stable-video-diffusion"
#capability_url is url that is reachable by go-livepeer orchestrator. localhost would mean processing backend is ran on same machine as orchestrator
export LIVEPEER_JOB_CAPABILITY_URL="http://127.0.0.1:9000/process"
export LIVEPEER_JOB_CAPABILITY_CAPACITY=1
export LIVEPEER_JOB_CAPABILITY_PRICE="100/1"

# not implemented yet (cached in .cache folder in home dir) MODEL_PATH = os.getenv("MODEL_PATH", "./models/stable-video-diffusion-img2vid-xt")
export DATA_PATH="data"
export DECODE_SIZE=1

#run the web server
pipenv run python sd-video-api.py


