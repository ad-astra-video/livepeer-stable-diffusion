#!/usr/bin/env python3

#requirements
#pip install diffusers transformers accelerate python-multipart
#pip install httpx
#pip install fastapi, uvicorn[standard]

import sys, getopt, os, json, random, logging

#webapi imports
from typing import Union, Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, UploadFile, HTTPException, Header
from fastapi.responses import FileResponse
import httpx

#stable video diffusion imports
import torch
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video

logging.basicConfig(level=logging.INFO)

GO_LIVEPEER_URL = os.getenv("GO_LIVEPEER_URL","https://127.0.0.1:8935")
GO_LIVEPEER_SECRET = os.getenv("GO_LIVEPEER_SECRET", "verybigsecret")

GPU = os.getenv("USE_GPU","cuda:0")
CAPABILITY = os.getenv("LIVEPEER_JOB_CAPABILITY", "stable-video-diffusion")
CAPABILITY_URL = os.getenv("LIVEPEER_JOB_URL","http://127.0.0.1:9000/process")
CAPABILITY_DESC = os.getenv("LIVEPEER_JOB_CAPABILITY_DESCRIPTION", "generate videos using stable-video-diffusion")
CAPABILITY_CAPACITY = os.getenv("LIVEPEER_JOB_CAPABILITY_CAPACITY", 1)
CAPABILITY_PRICE = os.getenv("LIVEPEER_JOB_CAPABILITY_PRICE", "100/1")
MODEL_PATH = os.getenv("MODEL_PATH", "models/stable-video-diffusion-img2vid-xt")
TMP_FILE_PATH = os.getenv("TMP_FILE_PATH", "~/svd")


#register capabilities available with this api
in_process = {}

@asynccontextmanager
async def startup(app: FastAPI):
    #make sure tmp_file_path exists
    os.makedirs(TMP_FILE_PATH, exist_ok=True)
    
    #register capabilities available with this api
    async with httpx.AsyncClient() as client:
        client.headers.update({"Authorization": GO_LIVEPEER_SECRET})
        cap_hdr = {
                   "name": CAPABILITY, 
                   "description":CAPABILITY_DESC,
                   "url": CAPABILITY_URL,
                   "capacity": CAPABILITY_CAPACITY,
                   "price": CAPABILITY_PRICE
                  }
        client.headers.update({"Livepeer-Job-Register-Capability":json.dumps(cap_hdr)})
        resp = await client.post(GO_LIVEPEER_URL+"/registerCapability")
        if resp.status_code == 200:
           print("capability registered with go-livepeer")
        else:
           print("error: capability not registered "+str(resp.status_code))
    
    yield
    
#start api
app = FastAPI(lifespan=startup)

@app.get("/ok")
async def ok():
    return {"status":"ok"}
    
@app.post("/process")
async def generate_video(livepeer_job: Annotated[str | None, Header()] = None, request_data: UploadFile | None = None):
    print(request.headers)
    #setup stable video diffusion pipeline
    print("received request, loading model and running")
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        "stabilityai/stable-video-diffusion-img2vid-xt", torch_dtype=torch.float16, variant="fp16"
    )
    pipe = pipe.to(GPU)
    pipe.enable_model_cpu_offload()

    #setup process
    try:
        job = json.loads(livepeer_job)
        if "request" in job:
            if job["prompt"] != "stable-video-diffusion":
                raise HTTPException(status_code=400, detail="invalid job request, job type not supported")
    except Exception as e:
       print(e)
       print("failed to parse job request")
       raise HTTPException(status_code=400, detail="invalid job request json in Livepeer-Job header")
    
    with PIL.Image.open(base_image.file) as base:
        image = load_image(base)
        image = image.resize((1024,576))
        #set parameters
        seed = job["parameters"].get("seed",-1)
        fps = job["parameters"].get("fps", 25)
        motion_bucket_id = job["parameters"].get("motion_bucket_id", 180)
        noise_aug_strength = job["parameters"].get("noise_aug_strength", 0.1)
        
        generator = torch.manual_seed(seed)

        frames = pipe(image, decode_chunk_size=8, generator=generator).frames[0]
        
        output_file = TMP_FILE_PATH+"/"+job["id"]+".mp4"
        export_to_video(frames, output_file, fps=fps)
        
        #https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse
        return FileResponse(path=output_file, headers={"jobId":job["id"]})


@app.get("/status/{prompt_id")
async def video_status():
    pass
