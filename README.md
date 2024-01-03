# Telestaff Payroll FTP
_(Telestaff Import Person has been moved to Bedrock.)_

Exports payroll files from Kronos Telestaff SFTP.
Deployed as an AWS Lambda.

Calls Separate Lambda ftp-jobs-py to check FTP site for new files.
If found, Payroll csv file is downloaded from Telestaff and loaded into Munis, using stored procedure.
Copy of file is stored in S3.

### Timing 
We poll for new Payroll every 15 minutes; runs whenever they post to FTP. 
JavaScript Lambda: telestaff-payroll calls Python Lambda: ftp-jobs-py
Rule: Every 10 minutes 1400 to 2300 (9 or 10 AM to 6 or 7 PM) cron(02,12,22,32,42,52 12-18 ? * MON-FRI *)


## Deploy/Test

/utils/test holds `sam local` testing files
```
cd utils/test
./runsam.sh
```
/utils/layer-deploy and /utils/deploy hold the Terraform files to deploy the Lambda and the Lambda Layer to AWS.
```
cd utils/layer-deploy
terraform init
./zip-layer-deploy.sh

cd utils/deploy
terraform init
./zipdeploy.sh
```