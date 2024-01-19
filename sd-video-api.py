#!/usr/bin/env python3
import sys, getopt, os, json, random
from pathlib import Path

#webapi imports
from typing import Union, Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, HTMLResponse
import httpx, uvicorn

#stable video diffusion imports
import torch, PIL
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video

RUN_PROCESSING = os.getenv("RUN_PROCESSING", "yes")
GO_LIVEPEER_URL = os.getenv("GO_LIVEPEER_URL","https://127.0.0.1:8935")
GO_LIVEPEER_SECRET = os.getenv("GO_LIVEPEER_SECRET", "verybigsecret")


HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 9000))
GPU = os.getenv("GPU","cuda:0")
CAPABILITY = os.getenv("LIVEPEER_JOB_CAPABILITY", "stable-video-diffusion")
CAPABILITY_URL = os.getenv("LIVEPEER_JOB_URL","http://"+HOST+":"+str(PORT)+"/process")
CAPABILITY_DESC = os.getenv("LIVEPEER_JOB_CAPABILITY_DESCRIPTION", "generate videos using stable-video-diffusion")
CAPABILITY_CAPACITY = int(os.getenv("LIVEPEER_JOB_CAPABILITY_CAPACITY", 1))
CAPABILITY_PRICE = os.getenv("LIVEPEER_JOB_CAPABILITY_PRICE", "1695421/1000")
# not implemented yet (cached in .cache folder in home dir) MODEL_PATH = os.getenv("MODEL_PATH", "./models/stable-video-diffusion-img2vid-xt")
DATA_PATH = os.getenv("DATA_PATH", "data")
DECODE_SIZE = os.getenv("DECODE_SIZE", 1)
CHUNK_SIZE = 1024*1024

#register capabilities available with this api
process_status = {}

models = {}

@asynccontextmanager
async def startup(app: FastAPI):
    #make sure DATA_PATH exists
    os.makedirs(DATA_PATH, exist_ok=True)
    if RUN_PROCESSING == "yes":
        print("loading models")
        #setup stable video diffusion pipeline
        pipe = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt", torch_dtype=torch.float16, variant="fp16"
        )
        pipe = pipe.to(GPU)
        #pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
        pipe.enable_model_cpu_offload()
        pipe.unet.enable_forward_chunking()
        
        models[CAPABILITY] = pipe
        
        print("registering capability with go-livepeer")
        #register capabilities available with this api
        try:
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
        except httpx.ConnectError:
            print("failed to register capability, orchestrator not available")
            return
    
    yield
    
#start api
app = FastAPI(lifespan=startup)
#add static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

############################
##########FRONTEND##########
############################
@app.get("/svd", response_class=HTMLResponse)
async def svd(request: Request):
    return templates.TemplateResponse(
        request=request, name="job.html", context={"id": ""}
    )

@app.get("/outputs")
async def outputs():
    paths = sorted(Path(dirpath).iterdir(), key=os.path.getmtime)
    filenames = [p.name for p in paths]
    return {"outputs": ','.join(filenames)}
    
@app.get("/play/{filename}")
async def play(request: Request, filename: str, range: Annotated[str | None, Header()] = None):
    if len(filename) == 0:
        return Response({"error": "no filename provided"}, status_code=400)
    
    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE
    with open(DATA_PATH+"/"+filename, "rb") as video:
        video.seek(start)
        data = video.read(end - start)
        filesize = str(video_path.stat().st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes'
        }
        return Response(data, status_code=206, headers=headers, media_type="video/mp4")
    

@app.get("/download/{filename}")
async def download(request: Request, filename: str):
    return FileResponse(path=DATA_PATH+"/"+filename, filename=filename, media_type="video/mp4")
    
@app.get("/status/{prompt_id")
async def video_status():
    pass

###########################
###GO-LIVEPEER ENDPOINTS###
###########################
@app.get("/ok")
async def ok():
    return {"status":"ok"}
    
@app.post("/process")
async def generate_video(request_data: UploadFile | None = None, livepeer_job: Annotated[str | None, Header()] = None):
    pipe = models[CAPABILITY]
    decode_chunk_size = DECODE_SIZE
    
    #setup process
    try:
        job = json.loads(livepeer_job)
        print("processing "+job["id"])
        
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
        
        output_file = DATA_PATH+"/"+job["id"]+".mp4"
        print("saving output to: "+output_file)
        export_to_video(frames, output_file, fps=fps)
        
        #https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse
        return FileResponse(path=output_file, filename=job["id"]+".mp4", headers={"id":job["id"]})


#run the app
if __name__ == "__main__":
    uvicorn.run("sd-video-api:app", host="0.0.0.0", port=PORT, log_level="debug")