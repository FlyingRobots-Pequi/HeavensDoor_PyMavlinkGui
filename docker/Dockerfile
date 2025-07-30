FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    python3-tk \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxrender1 \
    libxext6 \
    libsm6 \
    libx11-dev \
    tk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir \
    pymavlink==2.4.42 \
    matplotlib \
    numpy \
    pyserial

ENV DISPLAY=:0

CMD ["python", "main.py"]
