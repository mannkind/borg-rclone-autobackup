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
BACKUP_EXCLUDES=os.environ.get("BACKUP_EXCLUDES")
BACKUP_VERBOSE=os.environ.get("BACKUP_VERBOSE")
BORG_CUSTOM_COMMANDS=ast.literal_eval(os.environ.get("BORG_CUSTOM_COMMANDS"))
EMAIL_HOST=os.environ.get("EMAIL_HOST")
EMAIL_USER=os.environ.get("EMAIL_USER")
EMAIL_PASS=os.environ.get("EMAIL_PASS")
EMAIL_USE_TLS=bool(os.environ.get("EMAIL_USE_TLS"))
EMAIL_PORT=os.environ.get("EMAIL_PORT")
EMAIL_FROM=os.environ.get("EMAIL_FROM")
EMAIL_TO=os.environ.get("EMAIL_TO")
B2_ID=os.environ.get("B2_ID")
B2_KEY=os.environ.get("B2_KEY")

BORG_PASSPHRASE=BACKUP_ENCRYPTION_KEY
BORG_HOST_ID=BACKUP_NAME
BORG_REPO="/backups/"+BACKUP_NAME


if BACKUP_VERBOSE:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


def sendEmail(message=str,subject_tag="success"):
    email = f"""\
    Subject: Backup alerts - {subject_tag}
    To: {EMAIL_TO}
    From: {EMAIL_FROM}
        
    {message}"""

    try:
        #send your message with credentials specified above
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, email)

        logging.debug("Email sent successfully")
    except (gaierror, ConnectionRefusedError):
        logging.error('Error while sending email: the SMTP server refused the connection')
    except smtplib.SMTPServerDisconnected:
        logging.error('Error while sending email, check login credentials')
    except smtplib.SMTPException as e:
        logging.error('Error whiel sending email:  General SMTP error: ' + str(e))


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
if BORG_CUSTOM_COMMANDS:
    command[2:0] = BORG_CUSTOM_COMMANDS

logging.debug("Executing command: " + str(command))
try:
    output = subprocess.run(command,shell=False,check=True,capture_output=True)
except subprocess.CalledProcessError as error:
    logging.fatal("There was a problem creating the daily archive")
    sendEmail("Error during archive creation, borg said: " + error.stderr, subject_tag="ERROR_BORG")
    raise Exception("Error running command: " + error.stderr)


if BACKUP_PRUNE:
    logging.debug("Starting Prune")
    command = ['borg','prune',BACKUP_PRUNE]
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
sendEmail("Backup was successful")

