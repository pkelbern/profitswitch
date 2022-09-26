#!/usr/bin/env bash

FOLDER="/usr/profitswitch"
VERSION="1.0"
RELEASE_FILE="release-v${VERSION}.zip"
CRON_FILE="/etc/cron.d/profitswitch"

sudo apt-get install -y python3 unzip python3-pip nano python3-requests

if [ -d "$FOLDER" ]; then
    rm -R "$FOLDER"
fi

wget "https://github.com/pkelbern/profitswitch/raw/main/release/${RELEASE_FILE}"

unzip $RELEASE_FILE -d $FOLDER

rm -rf RELEASE_FILE

echo "0 * * * * root /usr/bin/python3 $FOLDER/profitswitch.py " > "${CRON_FILE}"

printf "..................\nThe HiveOS ProfitSwitch has been installed, but must be configured.\nPlease set the TOKEN in the file:\n ${FOLDER}\hiveosapi.txt \n\nIf you want to change the check inverval, configure the new cron\n nano ${CRON_FILE}\n\nFor more information, see https://github.com/pkelbern/profitswitch\n..................\n"