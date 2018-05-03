FROM alpine:3.7

ENV BACKUP_SCHEDULE='5 2 * * *' \
    BACKUP_NAME='Default' \
    BACKUP_LOCATION='' \
    BACKUP_ENCRYPTION_KEY='' \
    BACKUP_PRUNE='' \
    BACKUP_NOW='' \
    B2_ID='' \
    B2_KEY='' \
    RCLONE_VERSION=v1.40 \
    ARCH=amd64

RUN apk --no-cache add ca-certificates bash wget borgbackup && \
    wget http://downloads.rclone.org/${RCLONE_VERSION}/rclone-${RCLONE_VERSION}-linux-${ARCH}.zip && \
    unzip rclone-${RCLONE_VERSION}-linux-${ARCH}.zip && \
    mv rclone-*-linux-${ARCH}/rclone /usr/bin && \
    rm -r rclone* && \
    apk del wget && \
    mkdir -p p /app

WORKDIR /app
ADD *.sh ./
RUN chmod +x *.sh

VOLUME ["/data", "/backups"]
ENTRYPOINT ["/app/entrypoint.sh"]
