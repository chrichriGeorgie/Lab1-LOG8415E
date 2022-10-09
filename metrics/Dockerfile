# syntax=docker/dockerfile:1

FROM ombu/boto3:1.8

ADD metrics.py .
ADD terraform.tfstate .

ENTRYPOINT [ "python3", "./metrics.py"]