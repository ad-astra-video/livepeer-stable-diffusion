#!/bin/bash

#set the env variables
export GO_LIVEPEER_URL="https://svd.ad-astra.video:9935"
# not implemented yet GO_LIVEPEER_SECRET = os.getenv("GO_LIVEPEER_SECRET", "verybigsecret")

export GPU="cuda:0"
export LIVEPEER_JOB_CAPABILITY="stable-video-diffusion"
export LIVEPEER_JOB_URL="http://127.0.0.1:9000/process"
export LIVEPEER_JOB_CAPABILITY_DESCRIPTION="generate videos using stable-video-diffusion"
export LIVEPEER_JOB_CAPABILITY_CAPACITY=1
# tried to set price = one 2s video = one ticket at 50gwei
export LIVEPEER_JOB_CAPABILITY_PRICE="1695421/1000"

# not implemented yet (cached in .cache folder in home dir) MODEL_PATH = os.getenv("MODEL_PATH", "./models/stable-video-diffusion-img2vid-xt")
export DATA_PATH="./data"
export DECODE_SIZE=2

#run the web server
source venv/bin/activate
uvicorn sd-video-api:app --host 0.0.0.0 --port 9000 --reload --log-level=debug
