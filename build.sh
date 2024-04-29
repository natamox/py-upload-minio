docker buildx build --platform linux/amd64,linux/arm64 -t natamox/py-minio-upload:$version . --load
