# ProfitSwitch for HiveOS

This project focus to set the currency mined on HiveOS for the one with the highest profitability according to the Whattomine website (https://whattomine.com/).

From the Rig available in HiveOS, it gets the referring values for hashrate and power consumption according to the cards found in HiveOS using the default Whattomine values. If you want to change this values, you can configure.

It requires python version 3.8 or higher installed.

## Installation

You can either install on the HiveOS RIG, extracting the files into a folder and run from time to time as configured in crontab, or running the script for installation.

```
wget -O - https://raw.githubusercontent.com/pkelbern/profitswitch/main/install.sh | bash
```

When running the installation script, a file will be created to run the scan every 1 hour. If you want to change or delete the file, it can be found in `/etc/cron.d/profitswitch`. 

To test the installation, run the command:
```
/usr/bin/python3 /usr/profitswitch/profitswitch.py
```

## Available settings:

### hiveosapi.txt
File with the HiveOS API Access Personal Token. Available at url:
```
https://id.hiveon.com/auth/realms/id/account/sessions
```

### whattomine.txt (optional)
If you want the whattomine data not to be automatically mounted for your rig, you can put in this file the whattomine url. To generate the url, configure whattomine and click the JSON button. Then copy the generated URL to that file.

### config.json (optional)
The config.json file can be configured as below.

| Key | Type | Value Description |
| --- | --- | --- |
| farmid | optional | Looks for the FARM ID in HiveOS, if it is not configured, it will look for the configured one in the `/hive-config/rig.conf` file. If both do not exist, search for the first available FARM |
| rigid | optional | Looks for the RIG ID in HiveOS, if it is not configured, it will look for the configured one in the `/hive-config/rig.conf` file. If both do not exist, search for the first RIG from the first available FARM |
| cost | optional | Cost in USD/kWh, default value of `0.1`. It can also be configured on HiveOS in the Farm |
| switch | optional | If it is `false`, the flight sheet will not be changed |
| verbose | optional | Displays on screen the coin values ​​according to the Whattomine website |

### flightsheets.json (optional)
The flightsheets.json file can be configured with the currencies to perform the flight sheets exchange in HiveOS.

| Key | Type | Value Description |
| --- | --- | --- |
| "coin" | optional | It informs that for the "coin", which flight sheet should be used, if it is `false`, ignore any flight sheet for this coin|

### algomap.json
Json with algorithm-to-coin mapping in Whattomine.

### gpumap.json
Json with GPU Mapping on HiveOS with Whattomine.
