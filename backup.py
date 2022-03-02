#!/usr/bin/python3
import os, logging, subprocess, ast, smtplib
from time import strftime, localtime
from socket import gaierror

BACKUP_NAME=os.environ.get("BACKUP_NAME")
BACKUP_ENCRYPTION_KEY=os.environ.get("BACKUP_ENCRYPTION_KEY")
BACKUP_SCHEDULE=os.environ.get("BACKUP_SCHEDULE")
BACKUP_LOCATION=os.environ.get("BACKUP_LOCATION")
BACKUP_PRUNE=os.environ.get("BACKUP_PRUNE")
BACKUP_NOW=os.environ.get("BACKUP_NOW")
BACKUP_VERBOSE=os.environ.get("BACKUP_VERBOSE")
BORG_CUSTOM_ARGS=ast.literal_eval(os.environ.get("BORG_CUSTOM_ARGS"))
EMAIL_HOST=os.environ.get("EMAIL_HOST")
EMAIL_USER=os.environ.get("EMAIL_USER")
EMAIL_PASS=os.environ.get("EMAIL_PASS")
EMAIL_USE_TLS=bool(os.environ.get("EMAIL_USE_TLS"))
EMAIL_PORT=os.environ.get("EMAIL_PORT")
EMAIL_FROM=os.environ.get("EMAIL_FROM")
EMAIL_TO=os.environ.get("EMAIL_TO")
EMAIL_TEST=bool(os.environ.get("EMAIL_TEST"))
EMAIL_ENABLED=bool(os.environ.get("EMAIL_ENABLED"))
B2_ID=os.environ.get("B2_ID")
B2_KEY=os.environ.get("B2_KEY")
BORG_REPO="/backups/"+BACKUP_NAME


def sendEmail(message=str,subject_tag="success"):
    email = f"Subject: Backup alerts - {subject_tag}\n\n{message}"

    try:
        #send your message with credentials specified above

        if EMAIL_USE_TLS:
            logging.debug("Using SMTP-TLS")
            server = smtplib.SMTP(EMAIL_HOST,int(EMAIL_PORT))
            server.starttls()
            server.ehlo()
        else:
            logging.debug("Using SMTP-SSL")
            server = smtplib.SMTP_SSL(EMAIL_HOST,int(EMAIL_PORT))
            

        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, email)
        server.close()

        logging.debug("Email sent successfully")
    except (gaierror, ConnectionRefusedError):
        logging.error('Error while sending email: the SMTP server refused the connection')
    except smtplib.SMTPServerDisconnected:
        logging.error('Error while sending email, check login credentials')
    except smtplib.SMTPException as e:
        logging.error('Error whiel sending email:  General SMTP error: ' + str(e))




os.environ["BORG_PASSPHRASE"]=BACKUP_ENCRYPTION_KEY
os.environ["BORG_HOST_ID"]=BACKUP_NAME
os.environ["BORG_REPO"]=BORG_REPO

if BACKUP_VERBOSE:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

if EMAIL_TEST:
    logging.info("Sending test email")
    sendEmail("Test email",subject_tag="TEST")
    exit(0)


logging.debug("Starting Borg Backup")

if not os.path.isdir(BORG_REPO):
    logging.debug("Starting Repository Initialization")
    os.mkdir(BORG_REPO)

    command = ['borg', 'init', '--encryption=repokey']
    logging.debug("Executing command: " + str(command))
    try:
        output = subprocess.run(command, shell=False,capture_output=True, check=True)
    except subprocess.CalledProcessError as error:
        logging.fatal("There was a problem initializing the repository")
        sendEmail("Error during repository initialization, borg said: " + error.stderr, subject_tag="ERROR_BORG")
        raise Exception("Error running command: " + error.stderr)
    logging.debug("Ending Repository Initialization")


borg_pid = subprocess.run(['pidof','borg'],shell=False,capture_output=True)
if not borg_pid.stdout:
    logging.debug("Clearing Locks; Borg Not Running")
    subprocess.run(['borg','break-lock'],shell=False,check=True)


logging.debug("Starting Daily Archive")
timestamp = strftime("%Y-%m-%d-%s", localtime())
command = ['borg','create','::'+timestamp,'/data']
if BORG_CUSTOM_ARGS:
    command[2:0] = BORG_CUSTOM_ARGS

logging.debug("Executing command: " + str(command))
try:
    output = subprocess.run(command,shell=False,check=True,capture_output=True)
except subprocess.CalledProcessError as error:
    logging.fatal("There was a problem creating the daily archive")
    sendEmail("Error during archive creation, borg said: " + error.stderr, subject_tag="ERROR_BORG")
    raise Exception("Error running command: " + error.stderr)


if BACKUP_PRUNE:
    logging.debug("Starting Prune")
    BACKUP_PRUNE=BACKUP_PRUNE.split()
    command = ['borg','prune']
    command+=BACKUP_PRUNE
    try:
        output = subprocess.run(command,shell=False,check=True,capture_output=True)
    except subprocess.CalledProcessError as error:
      logging.warning("There was a problem pruning the daily archive")
      sendEmail("Error during archive prune: " + error.stderr, subject_tag="ERROR_PRUNE")
      raise Exception("Error running command: " + error.stderr)
    logging.debug("Ending Prune")


logging.debug("Ending Daily Archive")
logging.debug("Ending Borg Backup")
logging.debug("Starting Rclone")

command = ['rclone','sync','--transfers','16',BORG_REPO,BACKUP_LOCATION]
logging.debug("Executing command: " + str(command))
try:
    output = subprocess.run(command,shell=False,capture_output=True,check=True)
except subprocess.CalledProcessError as error:
      logging.fatal("There was a problem syncing the backup")
      sendEmail("Error during rclone sync, rclone said: " + error.stderr, subject_tag="ERROR_RCLONE")
      raise Exception("Error running command: " + error.stderr)
logging.debug("Ending Rclone")
logging.debug("Ending Backup")
if EMAIL_ENABLED:
    sendEmail("Backup was successful")

