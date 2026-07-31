#!/bin/bash

TARGET="$1"
TOKEN="$2"
ENDPOINT="$3"

echo "[*] Scanning ${TARGET}${ENDPOINT}"
echo "[*] Testing IDs 1-50"

for id in $(seq 1 50); do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "${TARGET}${ENDPOINT}/${id}")

    if [ "$STATUS" != "404" ]; then
        echo "[+] ID $id -> HTTP $STATUS"
    fi
done
