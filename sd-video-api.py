#!/usr/bin/env python3

#requirements
#pip install diffusers transformers accelerate python-multipart
#pip install httpx
#pip install fastapi, uvicorn[standard]

import sys, getopt, os, json, random

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


go_livepeer_url = os.getenv("GO_LIVEPEER_URL","http://127.0.0.1:8935")
go_livepeer_secret = os.getenv("GO_LIVEPEER_SECRET", "verybigsecret")
capability_url = os.getenv("LIVEPEER_JOB_URL","http://127.0.0.1:9595/process")
capability = os.getenv("LIVEPEER_JOB_CAPABILITY", "stable-video-diffusion")
capability_desc = os.getenv("LIVEPEER_JOB_CAPABILITY_DESCRIPTION", "generate videos using stable-video-diffusion")
capability_capacity = os.getenv("LIVEPEER_JOB_CAPABILITY_CAPACITY", 1)
capability_price = os.getenv("LIVEPEER_JOB_CAPABILITY_PRICE", "100/1")
model_path = os.getenv("MODEL_PATH", "models/stable-video-diffusion-img2vid-xt")
tmp_file_path = os.getenv("TMP_FILE_PATH", "~/svd")

#start api
app = FastAPI()

#register capabilities available with this api
in_process = {}

@asynccontextmanager
async def startup(app: FastAPI):
    #make sure tmp_file_path exists
    os.makedirs(tmp_file_path, exit_ok=True)

    #register capabilities available with this api
    async with httpx.AsyncClient() as client:
        cap_hdr = {
                   "name":capability, 
                   "description":capability_desc,
                   "url":capability_url,
                   "capacity": capability_capacity,
                   "price": capability_price
                  }
        client.headers.update({"Livepeer-Job-Register-Capabilities":json.dumps(cap_hdr)})
        resp = await client.post(go_livepeer_url+"/registercapability")
        if resp.status_code == 200:
           print("capability registered with go-livepeer")
        else:
           print("error: capability not registered "+str(resp.status_code))

@app.post("/process")
async def generate_video(livepeer_job: Annotated[str | None, Header()] = None, request_data: UploadFile | None = None):
    #setup stable video diffusion pipeline
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        "stabilityai/stable-video-diffusion-img2vid-xt", torch_dtype=torch.float16, variant="fp16"
    )
    pipe.enable_model_cpu_offload()

    #setup process
    try:
        job = json.loads(livepeer_job)
        if "request" in job:
            if job["request"] != "img2vid":
                raise HTTPException(status_code=400, detail="invalid job request, job type not supported")
    except:
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
        
        output_file = tmp_file_path+"/"+job["id"]+".mp4"
        export_to_video(frames, output_file, fps=fps)
        
        #https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse
        return FileResponse(path=output_file, headers={"jobId":job["id"]})


@app.get("/status/{prompt_id")
async def video_status():
    pass
