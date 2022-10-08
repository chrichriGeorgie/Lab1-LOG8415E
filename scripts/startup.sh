#!/bin/bash
#AWS credentials configuration

echo AWS Access Key ID:
read aws_access_key_id

echo AWS Secret Access Key:
read aws_secret_access_key

echo AWS Session Token:
read aws_session_token

aws configure set aws_access_key_id $aws_access_key_id
aws configure set aws_secret_access_key $aws_secret_access_key
aws configure set aws_session_token $aws_session_token

#Terraform deploying AWS Infrastructure
cd ../terraform-aws-flask
terraform apply -auto-approve
cd ..

#Docker Clients startup
cd ./bonus-query-scripts

#We must first retrieve the load-balancer url to give to client container.
urlString='python3 url_retriver.py'

#We then create the container and run it with $urlString as an argument
sudo docker build --tag query_maker .
sudo dockr run query_maker $urlString



#Calls for metrics ?
