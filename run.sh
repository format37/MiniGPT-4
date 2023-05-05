sudo docker run -it --rm --network host \
    -v $(pwd)/:/app \
    -v $(pwd)/torch_cache:/root/.cache/torch \
    --gpus '"device=0"' --name minigpt4 minigpt4