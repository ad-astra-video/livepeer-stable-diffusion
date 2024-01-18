#!/usr/bin/env python3

#requirements
#pip install diffusers transformers accelerate python-multipart
#pip install httpx
#pip install fastapi, uvicorn[standard]

import sys, getopt, os, json, random

#webapi imports
from typing import Union, Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Header
from fastapi.responses import FileResponse
import httpx

#stable video diffusion imports
import torch, PIL
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video


GO_LIVEPEER_URL = os.getenv("GO_LIVEPEER_URL","https://127.0.0.1:8935")
GO_LIVEPEER_SECRET = os.getenv("GO_LIVEPEER_SECRET", "verybigsecret")

GPU = os.getenv("USE_GPU","cuda:0")
CAPABILITY = os.getenv("LIVEPEER_JOB_CAPABILITY", "stable-video-diffusion")
CAPABILITY_URL = os.getenv("LIVEPEER_JOB_URL","http://127.0.0.1:9000/process")
CAPABILITY_DESC = os.getenv("LIVEPEER_JOB_CAPABILITY_DESCRIPTION", "generate videos using stable-video-diffusion")
CAPABILITY_CAPACITY = os.getenv("LIVEPEER_JOB_CAPABILITY_CAPACITY", 1)
CAPABILITY_PRICE = os.getenv("LIVEPEER_JOB_CAPABILITY_PRICE", "100/1")
MODEL_PATH = os.getenv("MODEL_PATH", "models/stable-video-diffusion-img2vid-xt")
TMP_FILE_PATH = os.getenv("TMP_FILE_PATH", "./data")


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
async def generate_video(request_data: UploadFile | None = None, livepeer_job: Annotated[str | None, Header()] = None):
    #setup stable video diffusion pipeline
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        "stabilityai/stable-video-diffusion-img2vid-xt", torch_dtype=torch.float16, variant="fp16"
    )
    pipe = pipe.to(GPU)
    #pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
    pipe.enable_model_cpu_offload()
    pipe.unet.enable_forward_chunking()
    decode_chunk_size = 2

    #setup process
    try:
        job = json.loads(livepeer_job)
        print(job)
        if "capability" in job:
            if job["capability"] != CAPABILITY:
                raise HTTPException(status_code=400, detail="invalid job request, job type not supported")
    except Exception as e:
       print("failed to parse job request "+str(e))
       raise HTTPException(status_code=400, detail="invalid job request json in Livepeer-Job header")
    #request_data.file

    with PIL.Image.open(request_data.file) as base:
        image = load_image(base)
        image = image.resize((1024,576))
        #set parameters
        params = json.loads(job["parameters"])
        seed = int(params.get("seed",-1))
        fps = int(params.get("fps", 25))
        motion_bucket_id = int(params.get("motion_bucket_id", 180))
        noise_aug_strength = float(params.get("noise_aug_strength", 0.1))
        duration = int(params.get("duration", 2))
        num_frames = fps * duration
        generator = torch.manual_seed(seed)

        frames = pipe(image, decode_chunk_size=decode_chunk_size, generator=generator, motion_bucket_id=motion_bucket_id, noise_aug_strength=noise_aug_strength, num_frames=num_frames).frames[0]
        
        output_file = TMP_FILE_PATH+"/"+job["id"]+".mp4"
        print("saving output to: "+output_file)
        export_to_video(frames, output_file, fps=fps)
        
        #https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse
        return FileResponse(path=output_file, filename=job["id"]+".mp4", headers={"id":job["id"]})
    
@app.get("/status/{prompt_id")
async def video_status():
    pass
