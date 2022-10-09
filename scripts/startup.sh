#!/bin/bash
#setting working directory
cd "$(dirname "$0")"

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
echo Retrieving load balancer url :
urlString=$( python3 url_retriever.py)
echo $urlString

#We then create the container and run it with $urlString as an argument
sudo docker build --tag query_maker .
sudo docker run -it query_maker $urlString

#Display metrics
cd ../metrics
cp ../terraform-aws-flask/terraform.tfstate ./terraform.tfstate
sudo docker build --tag metrics .
sudo docker run -it -e AWS_DEFAULT_REGION=us-east-1 \
-e AWS_ACCESS_KEY_ID=$aws_access_key_id \
-e AWS_SECRET_ACCESS_KEY=$aws_secret_access_key \
 -e AWS_SESSION_TOKEN=$aws_session_token \
 metrics

 #Clean up instances
cd ../terraform-aws-flask
echo Cleaning instances...
rm -f destroy.txt
terraform destroy -auto-approve > destroy.txt
echo Done!
cd ..