import re
#Retrieve the URL of the load balancer to make subsequent requests
def get_lb_url():
    regex = re.compile(".+us-east-1\.elb\.amazonaws\.com\",")
    for i, line in enumerate(open('../terraform-aws-flask/terraform.tfstate')):
        for match in re.finditer(regex, line):
            address = match.group().__str__().strip()[13:-2]
    return address

if __name__ == "__main__":
    print(get_lb_url())