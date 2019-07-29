ARG REGISTRY
FROM $REGISTRY/sox/asecurityteam/sec-streamer:v2

ENTRYPOINT ["sh", "-c", "./benthos --streams"]
