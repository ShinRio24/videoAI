from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests


# Load BLIP processor and model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Load an image from URL (or use local file path)
#img_url = "https://images.unsplash.com/photo-1512820790803-83ca734da794"
#image = Image.open(requests.get(img_url, stream=True).raw)

def describe(path):
    image = Image.open(path)

    # Prepare inputs for the model
    inputs = processor(image, return_tensors="pt")

    # Generate caption (max length 50 tokens)
    out = model.generate(**inputs, max_length=50)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

if __name__ =='__main__':
    print(describe('media/refImgs/img_5.jpeg'))