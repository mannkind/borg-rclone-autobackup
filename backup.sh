#!/bin/bash

whisper() {
    msg=$1
    if [[ "$BACKUP_VERBOSE" = "true" ]]; then
        echo $msg
    fi
}

whisper "Starting Backup"

whisper "  Starting Variable Setup"
export BORG_PASSPHRASE="$BACKUP_ENCRYPTION_KEY"
export BORG_HOST_ID=$BACKUP_NAME
export BORG_REPO="/backups/$BACKUP_NAME"
whisper "  Ending Variable Setup"

whisper "  Starting Borg Backup"
if [[ ! -d "$BORG_REPO" ]]; then
    whisper "    Starting Repository Initialization"
    mkdir -p "$BORG_REPO"
    borg init --encryption=repokey

    if [[ $? -ne 0 ]]; then
        echo "FATAL - There was a problem initializing the repository"
        exit 1
    fi

    whisper "    Ending Repository Initialization"
fi

if [[ $(pidof borg) = "" ]]; then
    whisper "    Clearing Locks; Borg Not Running"
    borg break-lock
fi

whisper "    Starting Daily Archive"
borg create ::$(date +%Y-%m-%d-%s) /data
if [[ $? -ne 0 ]]; then
    echo "FATAL - There was a problem creating the daily archive"
    exit 1
fi

if [[ $BACKUP_PRUNE ]]; then
    whisper "    Starting Prune"
    
    borg prune $BACKUP_PRUNE
    if [[ $? -ne 0 ]]; then
        echo "WARNING - There was a problem pruning the daily archive"
        exit 1
    fi

    whisper "    Ending Prune"
fi

whisper "    Ending Daily Archive"

whisper "  Ending Borg Backup"

whisper "  Starting Rclone"
rclone sync --transfers 16 "$BORG_REPO" "$BACKUP_LOCATION"
if [[ $? -ne 0 ]]; then
    echo "FATAL - There was a problem syncing the backup"
    exit 1
fi

whisper "  Ending Rclone"

whisper "Ending Backup"
