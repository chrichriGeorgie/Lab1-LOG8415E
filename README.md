# Lab1-LOG8415E
Github repository for the first assignment of the LOG8415E class. Made by: Jimmy Bell, Jérôme Cléris, Louis-Alexandre Hébert and Christophe St-Georges

# Run the code
Before executing the startu.sh script, verify that you have the lastest version of the AWS CLI on your machine. Terraform 1.3.1, Docker and Python 3 must also be installed.

Make sure to give the rights permission to the start up script. It can be done with the "chmod +x ./scripts/startup.sh" command.

Then, you can run the "./scripts/startup.sh" command.

The command will ask for the three following AWS credentials: AWS Access Key ID, AWS Secret Access Key and the AWS Session Token. Be sure to have them near!

This command will deploy the nine machines. Then it will run a benchmark test. Finally, it will collect and print metrics. Those metrics will evaluate the performances of the two clusters.


