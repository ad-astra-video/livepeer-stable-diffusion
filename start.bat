@ECHO OFF
REM change to this directory
cd %~dp0
echo starting sd-video-api

REM setup variables
SET HOST=localhost
SET PORT=9000
SET GO_LIVEPEER_URL=https://svd.ad-astra.video:9935
SET GO_LIVEPEER_SECRET = os.getenv("GO_LIVEPEER_SECRET", "verybigsecret")

SET GPU=cuda:0
SET LIVEPEER_JOB_CAPABILITY=stable-video-diffusion
SET LIVEPEER_JOB_URL=http://127.0.0.1:9000/process
SET LIVEPEER_JOB_CAPABILITY_DESCRIPTION=generate videos using stable-video-diffusion
SET LIVEPEER_JOB_CAPABILITY_CAPACITY=1
REM tried to set price = one 2s video = one ticket at 50gwei
SET LIVEPEER_JOB_CAPABILITY_PRICE=1695421/1000

REM not implemented yet (cached in .cache folder in home dir) MODEL_PATH = os.getenv("MODEL_PATH", "./models/stable-video-diffusion-img2vid-xt")
SET DATA_PATH=data
SET DECODE_SIZE=1

REM run the web server
pipenv run python sd-video-api.py

pause