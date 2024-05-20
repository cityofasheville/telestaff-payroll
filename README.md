# Telestaff Payroll FTP
_(Note: Telestaff Import Person is a Bedrock job.)_

Exports payroll files from Kronos Telestaff SFTP.

Deployed as two Lambdas: 
- Main program: telestaff-payroll (Nodejs) 
- FTP Functions: telestaff-payroll-ftp (Python)

Checks FTP site for files.
If found, Payroll csv file is downloaded from Telestaff and loaded into Munis, using stored procedure.
Copy of file is stored in S3.

### Timing 
We poll for new Payroll every 10 minutes; runs whenever they post to FTP. 
Rule: Every 10 minutes 1400 to 2300 (9 or 10 AM to 6 or 7 PM) cron(02,12,22,32,42,52 12-18 ? * MON-FRI *)

### Commands in each subdir
- Test Locally: npm start
- Deploy: 
  - npm run deploy prod
  - npm run deploy dev
- Destroy: (removes all objects from AWS)
  - npm run destroy prod
  - npm run destroy dev 
- Clean: npm run clean (removes local temp files)

### Prerequisites
Nodejs
Python
AWS SAM
Docker (I use Colima)
Each program needs a file .env, based on .env.example
