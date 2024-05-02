#!/bin/bash

VERSION='1.4.2'

version_main=$(echo $VERSION | cut -d. -f-2)

version_minor=$(echo $VERSION | cut -d. -f3)

if [ $version_main = '1.4' ]; then
  ((version_minor++))
fi

NEW_VERSION="${version_main}.${version_minor}"

IMAGE_TAG="natamox/py-minio-upload:${NEW_VERSION}"

echo "Final tag is: $IMAGE_TAG"

docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_TAG . --load
