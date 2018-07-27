#!/bin/bash -e
ARCHS="amd64 arm32v6 arm64v8"
IMAGE="mannkind/borg-rclone-autobackup"

for docker_arch in $ARCHS; do
  case ${docker_arch} in
    amd64   ) qemu_arch="x86_64"; rclone_arch="amd64" ;;
    arm32v6 ) qemu_arch="arm"; rclone_arch="arm" ;;
    arm64v8 ) qemu_arch="aarch64"; rclone_arch="arm64" ;;    
  esac
  cp Dockerfile.cross Dockerfile.${docker_arch}
  sed -i "" "s|__BASEIMAGE_ARCH__|${docker_arch}|g" Dockerfile.${docker_arch}
  sed -i "" "s|__QEMU_ARCH__|${qemu_arch}|g" Dockerfile.${docker_arch}
  sed -i "" "s|__RCLONE_ARCH__|${rclone_arch}|g" Dockerfile.${docker_arch}
  if [ ${docker_arch} == 'amd64' ]; then
    sed -i "" "/__CROSS_/d" Dockerfile.${docker_arch}
  else
    sed -i "" "s/__CROSS_//g" Dockerfile.${docker_arch}
  fi
done


for arch in $ARCHS; do
  docker build -f Dockerfile.${arch} -t ${IMAGE}:${arch}-latest .
  docker push ${IMAGE}:${arch}-latest
done

docker manifest create ${IMAGE}:latest ${IMAGE}:amd64-latest ${IMAGE}:arm32v6-latest ${IMAGE}:arm64v8-latest
docker manifest annotate ${IMAGE}:latest ${IMAGE}:arm32v6-latest --os linux --arch arm
docker manifest annotate ${IMAGE}:latest ${IMAGE}:arm64v8-latest --os linux --arch arm64 --variant armv8
docker manifest push ${IMAGE}:latest
