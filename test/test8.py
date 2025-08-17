import sys
import os

# Use the WSL-resolved Linux path
videoAI_path = "/home/riosshin/code/videoAI"
sys.path.append(videoAI_path)


import torch
from diffusers import StableDiffusionPipeline



pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",  # You can use other models too
    torch_dtype=torch.float16,         # Use float16 to save VRAM
).to("cuda")  # Use GPU
pipe.enable_xformers_memory_efficient_attention()
# Prompt for image generation
prompts = "woman with a book"

# Generate image
image = pipe(prompts).images[0]

# Save the result
image.save("output"+".png")