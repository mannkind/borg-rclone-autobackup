#!/bin/bash
echo "Starting Backup"
export BORG_PASSPHRASE="$BACKUP_ENCRYPTION_KEY"

echo "  Starting Variable Setup"
export BORG_REPO="/backups/$BACKUP_NAME"
echo "  Ending Variable Setup"

echo "  Starting Borg Backup"
if [[ ! -d "$BORG_REPO" ]]; then
    echo "    Initializing Repoistory"
    mkdir -p "$BORG_REPO"
    borg init --encryption=repokey
fi

echo "    Creating Daily Archive"
borg create ::$(date +%Y-%m-%d-%s) /data

if [[ $BACKUP_PRUNE ]]; then
    echo "    Pruning Daily Archive"
    borg prune $BACKUP_PRUNE
fi

echo "  Ending Borg Backup"

echo "  Starting Rclone"
rclone sync --transfers 16 "$BORG_REPO" "$BACKUP_LOCATION"
echo "  Ending Rclone"

echo "Ending Backup"
