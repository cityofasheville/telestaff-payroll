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
- Deploy: npm run deploy
- Clean: npm run clean (removes local temp files)
- Destroy: npm run destroy (removes all objects from AWS)

### Prerequisites
Nodejs
Python
AWS SAM
Docker (I use Colima)
Each program needs a file .env, based on .env.example
