FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-devel

WORKDIR /app
RUN set -xe \
    && apt-get update \
    && apt-get install python3-pip -y

RUN python3 -m pip install gradio
RUN python3 -m pip install opencv-python
RUN python3 -m pip install omegaconf
RUN python3 -m pip install iopath
RUN python3 -m pip install timm
RUN python3 -m pip install webdataset
RUN python3 -m pip install decord
RUN python3 -m pip install sentencepiece
RUN python3 -m pip install fschat
RUN python3 -m pip install accelerate
RUN python3 -m pip install bitsandbytes
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install --upgrade wheel
RUN python3 -m pip install --upgrade torch torchvision torchaudio -f https://download.pytorch.org/whl/nightly/cu121/torch_nightly.html
RUN apt-get install libgl1-mesa-glx -y

CMD ["python3", "demo.py", "--cfg-path", "eval_configs/minigpt4_eval.yaml"]