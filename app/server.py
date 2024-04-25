import os
import sys
import aiohttp
import asyncio
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

import json
import textract as txrct
import tempfile
from base64 import b64decode
from io import BytesIO
from PIL import Image
import requests
app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])

@app.route('/textract', methods=['POST'])
async def textract(request):      
    data = await request.body()
    data_json = json.loads(data)
    image_url = data_json['image_url']

    # Download the image from the provided URL
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))

    # Convert the image to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', buffering=0) as t:
        image.save(t.name)

        # Extract text from the image
        text = txrct.process(t.name)

    resp = {'text': text.decode('utf-8')}
    return JSONResponse(resp)

@app.route('/status', methods=['GET'])
def status(request):
    res = {'status': 'OK'}
    return JSONResponse(res)

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), log_level="info")