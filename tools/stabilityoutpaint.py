import requests
import os
from io import BytesIO
from PIL import Image
from tools import BaseTool
import time

class StabilityOutpaintTool(BaseTool):
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = config.get('api_key') or os.getenv('STABILITY_API_KEY')
        self.output_format = config.get('output_format', 'webp')
    
    def _get_api_key(self):
        import os
        key = os.getenv('STABILITY_API_KEY')
        if not key:
            raise ValueError("API key not found in config or environment variables")
        return key

    def load_model(self):
        pass

    def process(self, image: Image.Image, **kwargs) -> Image.Image:
        if not self.api_key:
            raise ValueError("Missing Stability API key")

        img_bytes = self._pil_to_bytes(image)
        start_time = time.time()
        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/edit/outpaint",
            headers={
                "authorization": f"Bearer {self.api_key}",
                "accept": "image/*"
            },
            files={
                "image": ("input.png", img_bytes, "image/png")
            },
            data={
                "left": kwargs.get('left', 250),
                "right": kwargs.get('right', 250),
                "up": kwargs.get('up', 250),
                "down": kwargs.get('down', 250),
                "output_format": self.output_format
            },
            timeout=30
        )

        end_time = time.time() 
        execution_time = end_time - start_time  
        if response.status_code == 200:
            output_image = Image.open(BytesIO(response.content))
            return {
                "image": output_image,
                "execution_time": execution_time
            }
        
        raise Exception(f"API Error {response.status_code}: {response.text}")

    def _pil_to_bytes(self, image: Image.Image) -> bytes:
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()