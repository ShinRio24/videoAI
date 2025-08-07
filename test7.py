import torch
from diffusers import StableDiffusionPipeline

# Load model
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",  # You can use other models too
    torch_dtype=torch.float16,         # Use float16 to save VRAM
    revision="fp16"
).to("cuda")  # Use GPU

# Prompt for image generation
prompt = "a futuristic city at sunset, cyberpunk, highly detailed"

# Generate image
image = pipe(prompt).images[0]

# Save the result
image.save("output.png")
