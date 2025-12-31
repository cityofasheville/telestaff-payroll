# Telestaff Payroll FTP
_(Note: Telestaff Import Person is a Bedrock job.)_

Exports payroll files from UKG Telestaff SaaS SFTP.

Deployed as two Lambdas: 
- Main program: telestaff-payroll (Nodejs) 
- FTP Functions: telestaff-payroll-ftp (Python)

Checks FTP site for files.
If found, Payroll csv file is downloaded from Telestaff, decrypted, and loaded into Munis, using stored procedure.
A copy of the encrypted and decrypted file is stored in S3.

### Timing 
We poll for new Payroll every 10 minutes; runs whenever they post to FTP. 
Rule: Every 10 minutes 1400 to 2300 (9 or 10 AM to 6 or 7 PM) cron(02,12,22,32,42,52 12-18 ? * MON-FRI *)

### Commands in each subdir
First run ```npm install```

```package.json``` has these scripts:
- Test Locally: 
  - ```npm start``` (or for a Python program: ```npm run startpy```)
- Deploy: 
  - ```npm run deploy```
- Destroy: (removes all objects from AWS)
  - ```npm run destroy```
- Clean: 
  - ```npm run clean``` (removes local temp files)

The Deploy/Destroy commands use the name of the active GitHub branch when creating AWS resources.
For example, if the active GitHub branch is "feature" and the name of the resource is "template", the resource is named "template_feature". For API gateway domains, it's "feature-template.ashevillenc.gov". Production (or main) branches do not get a prefix/suffix.


### Prerequisites
Nodejs
Python
AWS SAM
Docker (I use Colima)