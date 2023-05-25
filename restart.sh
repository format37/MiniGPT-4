# get id of running container with image name
container_id=$(sudo docker ps | grep minigpt4 | awk '{print $1}')
echo "container id: $container_id"
# get logs
sudo docker restart $container_id
# connect to container
# sudo docker exec -it $container_id /bin/bash
