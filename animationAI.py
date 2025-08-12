#this one doesnt really work well because stable diffusion is ass LMAO



import torch
from diffusers import StableDiffusionPipeline
from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker


from llmPrompt import extract_json_between_markers
from llmPrompt import prompt

def dummy_checker(images, **kwargs):
    return images, [False] * len(images)  # Make it a list of bools



def genChar():
    title='The largest drug cartel in mexico'
    character = 'Nmesio Oseguera Cervantes'

    getDetails = f"""I am creating a short form film titled: {title}
    For this film, its going to be about {character}, and his life, how they got to where they are, etc.
    Generate a detailed description of the character, which can be used to generate images that resemble them. Make sure to be as detailed as possible, but keep in mind the image will be animated.


    The output should be in the following JSON format:
    {{
    "background": "the description of the character"}}
        ONLY RETURN THE RAW JSON FILE, DO NOT REUTURN ANYTHING ELSE"""

    background = prompt(getDetails)
    background = extract_json_between_markers(background)['background']

    print(background)

    charDetail = f"""Generate a detailed and consistent character prompt suitable for use across multiple image generations. The goal is to ensure the same animated character is clearly and consistently reproduced, even when the surrounding scene or setting changes. The character should be described thoroughly — including physical appearance, clothing, personality, and any unique visual traits — in a way that makes them visually distinct and memorable. The style should be animated or anime-like. I will provide the character description next.
    Keep the summarization to under 50 characters

    here is the character:
    name: {character}
    details: {background}

    The output should be in the following JSON format:
    {{
    "description": "the description of the character"}}
    """

    description = prompt(charDetail)
    description = extract_json_between_markers(description)['description']

    print(description)

    temp=["standing solemnly at a grave under pouring rain, holding a black umbrella, cemetery in the background"," walking through a sun-scorched desert battlefield, dust swirling around his boots, intense glare","standing in a luxurious ballroom lit by chandeliers, surrounded by well-dressed guests"]

    pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",  # You can use other models too
    torch_dtype=torch.float16,         # Use float16 to save VRAM
    ).to("cuda")  # Use GPU
    pipe.enable_xformers_memory_efficient_attention()
    pipe.safety_checker = dummy_checker

    for i in range(len(temp)):
        temp[i]=description+ '  '+temp[i]

        # Load model
        

        # Prompt for image generation
        prompts = temp[i]

        # Generate image
        image = pipe(prompts).images[0]

        # Save the result
        image.save("media/diffusion/"+"output"+str(i)+".png")


if __name__ == '__main__':
    genChar()