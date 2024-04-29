import paramiko
import boto3
import json
import io

WORKINGDIR = '/tmp/'
region_name = "us-east-1"

def put_ftp(sftp, ftp_path, filename):
    try:
        file_to_put = WORKINGDIR + filename

        sftp.put(file_to_put, ftp_path + filename)

        print('Uploaded To FTP: ' + filename)
    except BaseException as err:
        raise Exception("Put FTP Error: " + str(err))

def get_ftp(sftp, ftp_path, filename):
    try:
        file_to_get = WORKINGDIR + filename

        sftp.get(ftp_path + filename, file_to_get)

        print('Downloaded from FTP: ' + filename)
    except BaseException as err:
        raise Exception("Get FTP Error: " + str(err))

def list_ftp(sftp, ftp_path):
    try:
        filelist = sftp.listdir(ftp_path)

        print('File list: ', filelist)
        return filelist
    except BaseException as err:
        raise Exception("List FTP Error: " + str(err))

def del_ftp(sftp, ftp_path, filename):
    try:
        sftp.unlink(ftp_path + filename)

        print('File deleted from FTP: ' + filename)
    except BaseException as err:
        raise Exception("Del FTP Error: " + str(err))

def download_s3(s3, s3_bucket, s3_path, filename):
    try:
        downloaded_file = WORKINGDIR + filename
        s3.download_file(s3_bucket, s3_path + filename, downloaded_file)
        print("File retrieved from S3: " + filename)
    except BaseException as err:
        raise Exception("Download S3 Error: " + str(err))

def upload_s3(s3, s3_bucket, s3_path, filename):
    try:
        uploaded_file = WORKINGDIR + filename
        s3.upload_file(uploaded_file, s3_bucket, s3_path + filename)
        print ('File loaded to S3: ' + filename)
    except BaseException as err:
        raise Exception("Upload S3 Error: " + str(err))

def getConnection(secret_name):
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name,
        )
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        results = json.loads(get_secret_value_response['SecretString'])
        return results
    except BaseException as err:
        raise Exception("Connection Secret Error: " + str(err))

def connectToFTP(ftp_host, ftp_port, ftp_user, ftp_pw, ftp_keyfile):
    try:
        transport = paramiko.Transport(ftp_host, int(ftp_port))
        transport.start_client(timeout=60)
        if ftp_pw is not None:
            transport.auth_password(username = ftp_user, password = ftp_pw)
        elif ftp_keyfile is not None:
            transport.auth_publickey(username = ftp_user, key = ftp_keyfile)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp
    except BaseException as err:
        raise Exception("Connect to FTP Error: " + str(err))
        # transport.connect(username = ftp_user, password = ftp_pw)  # This is the simpler way, but you cant set timeout

        # sftp_channel = sftp.get_channel()
        # sftp_channel.settimeout(None)

        # secop = transport.get_security_options()
        # #### secop.ciphers = ("aes128-ctr",)
        # print(secop.ciphers,secop.digests,secop.key_types,secop.kex,secop.compression)

def handler(event, context):
    try:
        s3 = boto3.client('s3')
        if "s3_connection" in event.keys():
            s3_conn_name = event['s3_connection']
            s3_bucket = getConnection(s3_conn_name)["s3_bucket"]

        #  "ftp_connection" 
        ftp_conn_name = event['ftp_connection']
        ftp_conn = getConnection(ftp_conn_name)
        ftp_host = ftp_conn['host']
        ftp_port = ftp_conn['port']
        ftp_user = ftp_conn['username']
        if 'password' in ftp_conn.keys():
            ftp_pw   = ftp_conn['password']
            sftp = connectToFTP(ftp_host, ftp_port, ftp_user, ftp_pw=ftp_pw, ftp_keyfile=None)
        if 'privateKey' in ftp_conn.keys():
            ftp_keyfile = ftp_conn['privateKey']
            filelikeobj = io.StringIO(ftp_keyfile)
            pk = paramiko.RSAKey.from_private_key(filelikeobj)
            sftp = connectToFTP(ftp_host, ftp_port, ftp_user, ftp_pw=None, ftp_keyfile=pk)
       

        if event['action'] == "getall":
            filelist = list_ftp(sftp, event['ftp_path'])
            for filenm in filelist:
                get_ftp(sftp, event['ftp_path'], filenm)
                upload_s3(s3, s3_bucket, event['s3_path'], filenm)
                del_ftp(sftp, event['ftp_path'], filenm)
            retmsg = filelist
        if event['action'] == "put":
            download_s3(s3, s3_bucket, event['s3_path'], event['filename'])
            put_ftp(sftp, event['ftp_path'], event['filename'])
            retmsg = ('Uploaded to FTP: ' + event['filename'])
        if event['action'] == "get":
            get_ftp(sftp, event['ftp_path'], event['filename'])
            upload_s3(s3, s3_bucket, event['s3_path'], event['filename'])
            retmsg = ('Downloaded from FTP: ' + event['filename'])
        if event['action'] == "list":
            filelist = list_ftp(sftp, event['ftp_path'])
            retmsg = filelist
        if event['action'] == "del":
            del_ftp(sftp, event['ftp_path'], event['filename'])
            retmsg = ('File deleted from FTP: ' + event['filename'])
        
        sftp.close()
        # transport.close()

        return {
            'statusCode': 200,
            'body': retmsg
        }
    except BaseException as err:
        print(str(err))
        return {
            'statusCode': 500,
            'body': str(err)
        }

# handler({
#   "action": "list",
#   "ftp_connection": "telestaff_ftp",
#   "ftp_path": "/PROD/export/"
# },0)

# handler({
#   "action": "put",
#   "s3_connection": "s3_data_files",
#   "s3_path": "telestaff-payroll-export/",
#   "ftp_connection": "telestaff_ftp",
#   "ftp_path": "/PROD/person.errors/",
#   "filename": "PD-220218-moon.csv"
# },0)

# handler({
#   "action": "del",
#   "ftp_connection": "telestaff_ftp",
#   "ftp_path": "/PROD/person.errors/",
#   "filename": "PD-220218-moon.csvxxx"
# },0)

# handler({
#   "action": "get",
#   "s3_connection": "s3_data_files",
#   "s3_path": "telecopy/",
#   "ftp_connection": "telestaff_ftp",
#   "ftp_path": "/PROD/person.errors/",
#   "filename": "compsych_CityofAsheville_20220324.csv"
# },0)

# handler({
#   "action": "getall",
#   "s3_connection": "s3_data_files",
#   "s3_path": "telecopy/",
#   "ftp_connection": "telestaff_ftp",
#   "ftp_path": "/PROD/person.errors/"
# },0)