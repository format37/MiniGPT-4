# FROM nvidia/cuda:11.8.0-devel-ubuntu22.04
# FROM pytorch/pytorch:latest
# FROM huggingface/transformers-pytorch-gpu
FROM huggingface/transformers-pytorch-gpu:latest
WORKDIR /app
# RUN set -xe \
#     && apt-get update \
#     && apt-get install python3-pip -y
# RUN apt-get install python3-pip -y
# COPY requirements.txt .
# RUN python3 -m pip install -r requirements.txt --no-cache-dir
RUN python3 -m pip install gradio
RUN python3 -m pip install opencv-python
RUN python3 -m pip install omegaconf
RUN python3 -m pip install iopath
RUN python3 -m pip install timm
RUN python3 -m pip install webdataset
# RUN python3 -m pip install transformers
RUN python3 -m pip install decord
RUN python3 -m pip install sentencepiece
RUN python3 -m pip install fschat
RUN python3 -m pip install accelerate
RUN python3 -m pip install bitsandbytes
# RUN python3 -m pip install 
# RUN python3 -m pip install opencv-python
# RUN python3 -m pip install onnxruntime
# RUN apt-get install libgl1-mesa-glx -y
# RUN python3 -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu117
# RUN python3 -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu118
# RUN python3 -m pip install https://download.pytorch.org/whl/cu118/torch-2.0.0%2Bcu118-cp38-cp38-linux_x86_64.whl
# COPY torch-2.0.0+cu118-cp38-cp38-linux_x86_64.whl .
# RUN python3 -m pip install torch-2.0.0+cu118-cp38-cp38-linux_x86_64.whl
# CMD ["python3", "inference_images.py", "--images-src", "/app/data/images_src/", "--images-bgr", "/app/data/images_bgr/", "--output-dir", "/app/data/images_dst/", "--model-type", "mattingbase", "--model-backbone", "resnet101", "--model-checkpoint", "/app/data/models/PyTorch/pytorch_resnet101.pth", "--output-types", "com", "pha", "fgr", "err", "--device", "cuda"]
# COPY . .
# CMD ["python3", "inference_images.py"]
# nvidia-smi
# CMD ["nvidia-smi"]
RUN python3 -m pip install --pre torch torchvision torchaudio -f https://download.pytorch.org/whl/test/cu117/torch_test.html
# infinity loop
# CMD tail -f /dev/null
RUN set -xe \
    && apt-get update \
    && apt-get upgrade -y
CMD ["python3", "demo.py", "--cfg-path", "eval_configs/minigpt4_eval.yaml"]