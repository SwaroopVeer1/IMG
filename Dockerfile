FROM python:3.10-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    git \
    wget \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /ComfyUI
WORKDIR /ComfyUI
RUN pip install -r requirements.txt

# Back to app
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY handler.py .

EXPOSE 8000 8188

CMD python /ComfyUI/main.py --listen 0.0.0.0 & \
    uvicorn handler:app --host 0.0.0.0 --port 8000
