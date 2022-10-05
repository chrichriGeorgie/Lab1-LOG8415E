#!/bin/bash
# Base configuration of instances, e.g. installing docker
#                                       pulling code from git
#                                       starting container

# Installing Docker from repository (see Docker's official docs : https://docs.docker.com/engine/install/ubuntu/)
sudo apt-get update -y
sudo apt-get install ca-certificates curl gnupg lsb-release -y
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# Pulling the code from the git repository
git clone https://github.com/chrichriGeorgie/Lab1-LOG8415E.git
cd ./Lab1-LOG8415E/web-app/

# Starting the docker container
