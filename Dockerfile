FROM python:3.8-buster

RUN apt-get update && apt-get install -y 


RUN pip install  boto3 fastapi uvicorn supabase_py python-pptx   requests

WORKDIR /workdir 
COPY app /workdir/

EXPOSE $PORT

ENTRYPOINT ["python", "-u", "server.py", "serve"]
