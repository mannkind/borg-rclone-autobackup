#!/bin/bash

# Configure RClone for B2
if [[ $B2_ID && $B2_KEY ]]; then
    echo -e "[b2]\ntype = b2\naccount = $B2_ID\nkey = $B2_KEY\nendpoint = \n" > /root/.rclone.conf
fi

# Configure RClone for GCS
if [[ $GCS_PROJECT_NUMBER ]]; then
    echo -e "[gcs]\ntype = google cloud storage\nclient_id =\nclient_secret =\nservice_account_file = /google-service-account.json\nproject_number = $GCS_PROJECT_NUMBER\nobject_acl = private\nbucket_acl = private\N" > /root/.rclone.conf
fi

# Schedule Backup
echo "$BACKUP_SCHEDULE /app/backup.sh" > /var/spool/cron/crontabs/root

# Run backup immediately
if [[ $BACKUP_NOW ]]; then
    /app/backup.sh
fi

# Start Cron
crond -l 8 -f
