import requests
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

COMFY_API = "http://127.0.0.1:8188"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    text: str

def build_workflow(prompt_text: str):
    return {
        "3": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sdxl_base_1.0.safetensors"}
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt_text, "clip": ["3", 1]}
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "seed": int(time.time()),
                "steps": 30,
                "cfg": 7.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["3", 0],
                "positive": ["4", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0]
            }
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["6", 0], "vae": ["3", 2]}
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {"images": ["7", 0], "filename_prefix": "txt2img"}
        }
    }

@app.post("/generate")
def generate(req: PromptRequest):
    workflow = build_workflow(req.text)

    r = requests.post(
        f"{COMFY_API}/prompt",
        json={"prompt": workflow}
    )
    prompt_id = r.json()["prompt_id"]

    for _ in range(40):
        time.sleep(1)
        history = requests.get(f"{COMFY_API}/history/{prompt_id}").json()
        if prompt_id in history:
            images = history[prompt_id]["outputs"]["8"]["images"]
            image = images[0]

            image_url = (
                f"/image?"
                f"filename={image['filename']}"
                f"&subfolder={image['subfolder']}"
            )

            return {"image_url": image_url}

    return {"error": "Timeout"}

@app.get("/image")
def proxy_image(filename: str, subfolder: str = ""):
    return requests.get(
        f"{COMFY_API}/view",
        params={
            "filename": filename,
            "subfolder": subfolder,
            "type": "output"
        },
        stream=True
    ).raw
