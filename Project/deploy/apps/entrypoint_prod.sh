#!/bin/sh

gunicorn \
    -w 4 \
    -b "0.0.0.0:${APP_PORT}" \
    -k "secure_endpoints.worker.ClientCertificateSyncWorker" \
    --certfile "${DATA_DIR}/own_dns_certificate/certificate.pem" \
    --keyfile "${DATA_DIR}/own_dns_certificate/key.pem" \
    --cert-reqs 1 \
    --ca-certs "${DATA_DIR}/communications_ca/certificate.pem" \
    --do-handshake-on-connect \
    --access-logfile=- \
    "${APP_NAME}:app"
