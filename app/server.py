import boto3
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import supabase_py as supabase
import re
import os
import sys

import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AWS Textract client
session = boto3.Session(
    aws_access_key_id='AKIAYS2NTWQ3OACHFCD6',
    aws_secret_access_key='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',
    region_name='ap-south-1'
)
textract = session.client('textract')

# Initialize Supabase client
supabase_url = 'https://jriiagfvufqqsxdtqtom.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpyaWlhZ2Z2dWZxcXN4ZHRxdG9tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDUyMjM5MTgsImV4cCI6MjAyMDc5OTkxOH0.UpGcu9vmNU0kZVFKFYlIIENaXLL5PHTgjaxupG_Gn-k'
supabase_client = supabase.create_client(supabase_url, supabase_key)
table_name = 'products'

# Function to check if an item contains more than 3 digits
def has_more_than_three_digits(item):
    return len(re.findall(r'\d', item)) > 3


@app.post('/extract-text')
async def extract_text(request: Request):
    data = await request.json()
    image_url = data.get('image_url')
    
    if not image_url:
        return {"error": "No image URL provided"}
    
    # Download the image
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_bytes = BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
    # Call AWS Textract
    try:
        response = textract.detect_document_text(Document={'Bytes': image_bytes.getvalue()})
    except Exception as e:
        return {"error": str(e)}
    
    # Extract text blocks
    text_blocks = [item["Text"] for item in response.get('Blocks', []) if item['BlockType'] == 'LINE'] 
    
    # Filter out items that are purely digits or contain more than 3 digits
    clean_text_blocks = [
    item for item in text_blocks
    if not item.isdigit() and not has_more_than_three_digits(item)
]

# Clean the items and include only the first five characters
    clean_text_blocks = [
    item.replace('\\', '').replace('[', '').replace(']', '')
    for item in clean_text_blocks
]

# Print the result
    print(clean_text_blocks)
    
    #clean_text_blocks = [item for item in text_blocks if not item.isdigit()]
    #clean_text_blocks = [item.replace('\\', '').replace('[', '').replace(']', '') for item in clean_text_blocks]
    #print(clean_text_blocks)
    print('That was clean_text_blocks\n')
    data = supabase_client.table(table_name).select('*').in_('Item', clean_text_blocks).execute()
    
    print(data, "  This was data")
    return data


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), log_level="info")
