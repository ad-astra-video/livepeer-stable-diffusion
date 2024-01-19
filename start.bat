@ECHO OFF
REM change to this directory
cd %~dp0
echo starting sd-video-api

REM set options
SET RUN_FRONTEND=no
SET RUN_PROCESSING=yes

REM setup environment
REM set api/frontend host/port
SET SVD_HOST=localhost
SET SVD_PORT=9000

REM backend processing setup
REM check_cuda_devices.py to see ordering of GPUs
SET SVD_GPU=cuda:0
SET GO_LIVEPEER_URL=https://127.0.0.1:9935
SET GO_LIVEPEER_SECRET = os.getenv("GO_LIVEPEER_SECRET", "verybigsecret")
SET LIVEPEER_JOB_CAPABILITY=stable-video-diffusion
SET LIVEPEER_JOB_CAPABILITY_DESCRIPTION=generate videos using stable-video-diffusion
REM capability_url is url that is reachable by go-livepeer orchestrator. localhost would mean processing backend is ran on same machine as orchestrator
SET LIVEPEER_JOB_CAPABILITY_URL=http://127.0.0.1:9000/process
SET LIVEPEER_JOB_CAPABILITY_CAPACITY=1
REM tried to set price = one 2s video = one ticket at 50gwei
SET LIVEPEER_JOB_CAPABILITY_PRICE=100/1

REM not implemented yet (cached in .cache folder in home dir) MODEL_PATH = os.getenv("MODEL_PATH", "./models/stable-video-diffusion-img2vid-xt")
SET DATA_PATH=data
SET DECODE_SIZE=1

REM run the web server
pipenv run python sd-video-api.py

pause