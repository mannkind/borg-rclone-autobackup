# Borg + RClone Autobackup

Easily automate backups using Borg + RClone.

## Usage Examples

### Docker Run

```
docker run \
    -v /home/mannkind:/data:ro \
    -e BACKUP_NAME="frodo" \
    -e BACKUP_LOCATION="b2:AllMyBorgBackups/frodo" \
    -e BACKUP_SCHEDULE="0 2 * * *" \
    -e BACKUP_ENCRYPTION_KEY="One ring to rule them all oh you know the rest" \
    -e BACKUP_PRUNE="--keep-daily=7 --keep-weekly=4" \
    -e BACKUP_NOW="true" \
    -e B2_ID="kiacup6326is" \
    -e B2_KEY="12xd5t3891tqh1qqw1qq3kmhl9hbd9lfugz2j32d" \
    --restart unless-stopped \
    mannkind/borg-rclone-autobackup
```

### Docker Compose

```
version: 3
services:
    borg-rclone-autobackup:
        image: mannkind/borg-rclone-autobackup
        restart: unless-stopped
        volumes:
            - '/home/mannkind:/data:ro'
        environment:
            - BACKUP_NAME=frodo
            - BACKUP_LOCATION='b2:AllMyBorgBackups/frodo'
            - BACKUP_SCHEDULE='0 2 * * *'
            - BACKUP_ENCRYPTION_KEY='One ring to rule them all one ring to find them one ring to bring them all and in the darkness bind them'
            - BACKUP_PRUNE='--keep-daily=7 --keep-weekly=4'
            - BACKUP_NOW='true'
            - B2_ID='kiacup6326is'
            - B2_KEY='12xd5t3891tqh1qqw1qq3kmhl9hbd9lfugz2j32d'
```

## Volumes

The following volumes can be used

  * /data - The data to backup
  * /backups - The location of the backups; backup in the container by default

## Environment Variables

The following environment variables setup Borg

  * `BACKUP_NAME`: The backup name
  * `BACKUP_ENCRYPTION_KEY`: The backup encryption key
  * `BACKUP_SCHEDULE`: Cron scheduled string
  * `BACKUP_LOCATION`: The backup location e.g. `b2:my-backup/some-host`
  * `BACKUP_PRUNE`: The backup prune string e.g. `--keep-daily=7 --keep-weekly=4`
  * `BACKUP_NOW`: Runs the backup immediately, instead of waiting for the scheduled time

The following environment variables setup B2 as the RClone target

  * `B2_ID`: The backblaze id
  * `B2_KEY`: The backblaze key
