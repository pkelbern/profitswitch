
from os.path import dirname, join
from hiveos import HiveOS
import whattomine 
from util import readFile

BASE_DIR = dirname(__file__)

WHATTOMINE_FILE = join(BASE_DIR, 'whattomine.txt')
HIVEOS_API_FILE = join(BASE_DIR,'hiveosapi.txt')
CONFIG_FILE = join(BASE_DIR,'config.json')
FS_FILE = join(BASE_DIR,'flightsheets.json')


api = readFile(HIVEOS_API_FILE)

if not api:
	print('ERROR: Invalid TOKEN for HiveOS')
	print('Access the link for HiveOS: ')
	print('https://id.hiveon.com/auth/realms/id/account/sessions')
	print(f'Generate a Personal Token, copy it and put into hiveosapi.txt')
	quit(100)

config = readFile(CONFIG_FILE, {})

hiveOS = HiveOS(api, config)

farmId = hiveOS.getFarmId()
if not farmId:
	print('ERROR: Invalid FARM ID for the TOKEN')
	quit(101)

workerId = hiveOS.getWorkerId()
if not workerId:
	print(f'ERROR: Invalid WORKER ID for the FarmId {farmId}')
	quit(102)
	
worker = hiveOS.worker()
if not worker:
	print(f'ERROR: Invalid WORKER ({workerId}) for the FarmId {farmId}')
	quit(103)

wurl = readFile(WHATTOMINE_FILE)
if not wurl:
	cost = float(config['cost']) if 'cost' in config else None
	if not cost:		
		cost = 0.1		
		farm = hiveOS.farm(farmId)	
		if farm['power_price']:	   
			if not farm["power_price_currency"] == "$" and not farm["power_price_currency"] == "USD":
				print(f'Power price currency in HiveOS must be in USD, using default price: {cost} USD/kWh')	
				print(f'You can set the kWh cost in HiveOS with USD currency:')
				print(f'https://the.hiveos.farm/farms/{farmId}/settings')
			else:
				cost = float(farm['power_price'])
		else:
			print(f'Power price configuration is not set in HIVEOS, using default price: {cost} USD/kWh')
			print(f'You can set the kWh cost in HiveOS with USD currency:')
			print(f'https://the.hiveos.farm/farms/{farmId}/settings')
	wurl = whattomine.createWhattoMineURL(worker['gpu_summary']['gpus'], cost)
else:
	print('Using the WhatToMine URL configured in the file: whattomine.txt')

coinlist = whattomine.calculate(wurl, config)

currentCoin = ''
fsName = ''
if 'flight_sheet' in worker:
	currentFS = worker['flight_sheet']
	fsName = currentFS['name']
	currentCoin = currentFS['items'][0]['coin']
	print(f"Current flight sheet ({fsName}): coin {currentCoin}")

if not coinlist[0]['tag'] == currentCoin:
	print(f'Looking for an optimal mining setting')

	listFs = sorted(hiveOS.flight_sheets(farmId), key= lambda fs: (fs['is_favorite'] == True, fs['id']), reverse=True)
	fsConfig = readFile(FS_FILE, {})
	
	sheet = None
	for coin in coinlist:
		coinTag = coin['tag']
		if coinTag in fsConfig:
			# search for the fs with the name for the coin
			name = fsConfig[coinTag]			
			if name == '' or name == False:
				#Set to not mine this coin
				print(f"{coinTag} was set to IGNORE in {flightsheets.json}")
				continue
				
			print(f"{coinTag} was configured in {flightsheets.json}")
			sheet = next((fs for fs in listFs if fs['name'] == name), None)
			if sheet:				
				break;
			else:
				print(f'Flight sheet ({name}) not found')
		
		sheet = next((fs for fs in listFs if fs['items'][0]['coin'] == coinTag), None)
		if sheet:
			break;
	
	
	if sheet and not sheet['name'] == fsName:
		if not 'switch' in config or not config['switch'] == False:		
			print(f"Setting new flight sheet for {worker['name']} to: {sheet['name']}")
			hiveOS.set_worker_flight_sheets(farmId, workerId, sheet['id'])
		else:
			print(f"You should set the HiveOs flight sheet for {worker['name']} to: {sheet['name']}")
	else:
		print(f"Nothing to do")

print(f'All done. Good mining')
		#email?



