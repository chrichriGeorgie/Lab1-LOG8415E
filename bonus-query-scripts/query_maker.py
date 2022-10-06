from threading import Thread
import requests
import re

#Retrieve the URL of the load balancer to make subsequent requests
regex = re.compile(".+us-east-1\.elb\.amazonaws\.com\",")
for i, line in enumerate(open('../terraform-aws-flask/terraform.tfstate')):
    for match in re.finditer(regex, line):
        address = match.group().__str__().strip()[13:-2]


def make_1000_sequentially(cluster):
    for x in range(1000):
        print('t1 r '+x.__str__())
        requests.get('http://'+address+cluster)

def make_500_sequentially(cluster):
    for x in range(500):
        print('t2 r '+x.__str__())
        requests.get('http://'+address+cluster)

Thread(target = make_1000_sequentially('/cluster1'),).start()
Thread(target = make_500_sequentially('/cluster1'),).start()

