import requests
from os.path import dirname, join
import json
import re
from urllib.parse import urlencode
from util import readFile

BASE_DIR = dirname(__file__)


WCOINMAP_FILE = join(BASE_DIR,'algomap.json')
WGPUMAP_FILE = join(BASE_DIR,'gpumap.json')

FACTOR_URL = "https://whattomine.com/gpus/factors.json"
COIN_URL = "https://whattomine.com/coins.json?"
REVENUE_KEY='btc_revenue24'
ORDER_KEY='profit'



BTC_API = "https://api.coinbase.com/v2/prices/spot?currency=USD"
#{"data":{"base":"BTC","currency":"USD","amount":"19282.22"}}


def createWhattoMineURL(gpus, cost):
		
	response = requests.get(FACTOR_URL)
	ret = json.loads(json.dumps(response.json()))
	factors = ret

	wgpu = readFile(WGPUMAP_FILE, {})

	dicAlgo = {}
	for hiveGpu in gpus:
		name = hiveGpu['name']
		if not name in wgpu:
			print(f"Not found {name} for Whattomine " )
			continue

		gpu = wgpu[name]
		qnt = hiveGpu['amount']
		#fator (HR e P) por GPU para cada moeda
		if gpu in factors:
			factorGpu = factors[gpu]
			for factor in factorGpu.keys():
				# factor vai ser ou XXX?_hr hashrate ou XXX?_p power
				fac = factor.split('_')
				algo = fac[0]
				obj = {}
				if algo in dicAlgo:
					obj = dicAlgo[algo]
				else:
					dicAlgo[algo] = obj
				
				if not factor in obj:			
					obj[factor] = 0
				
				obj[factor] = round(obj[factor] + factorGpu[factor] * qnt, 1)
		else:
			print(f"Not found GPU {name}" )
		
	wtmParams = {
		"commit": "Calculate",
		"dataset": "Main",
		"revenue": "current",
		"sort": "Profit",
		"volume": 0,
		"factor[cost_currency]": "USD",
		"factor[cost]": round(cost,2)
	}	
	
	if len(dicAlgo.keys()) > 0:
		#https://whattomine.com/coins.json?... eth=true&factor[eth_hr]=10000.0&factor[eth_p]=640.0
		for algoKey in dicAlgo.keys():
			info = dicAlgo[algoKey]
			wtmParams[algoKey] = 'true'
			for factorKey in info.keys():
				wtmParams[f"factor[{factorKey}]"]=info[factorKey]
	
	return COIN_URL + urlencode(wtmParams)

def calculate(urlwatttomine, jsonConfig):
			
	response = requests.get(urlwatttomine)
	ret = json.loads(json.dumps(response.json()))
	
	responseBTC = requests.get(BTC_API)
	retBTC = json.loads(json.dumps(responseBTC.json()))
	btcValor = float(retBTC['data']['amount'])
	
	cost = 0
	match = re.search('factor(\[|%5B)cost(\]|%5D)=([\d\.]+)',urlwatttomine, flags=re.IGNORECASE)
	if match:
		cost = float(match.group(3))
	
	print(f'BTC value: {btcValor}' )
	print(f'Cost value: {cost}' )
	
	walgotag = readFile(WCOINMAP_FILE, {})
	
	revenueKey = jsonConfig['revenuekey'] if 'revenuekey' in jsonConfig and jsonConfig['revenuekey'] else REVENUE_KEY
	keyOrder = jsonConfig['orderkey'] if 'orderkey' in jsonConfig and jsonConfig['orderkey'] else ORDER_KEY
	
	coins = []	
	for coinName, coin in ret["coins"].items():

		# nicehast is not a coin		
		if coin['tag'] == 'NICEHASH':
			continue
		
		algorithm = coin['algorithm']
		
		if not algorithm in walgotag:
			print(f'Algorithm mapping not found for {coin["tag"]}:{algorithm}')
			continue

		pw = 0
		pwKey = walgotag[algorithm] + "_p"
		match = re.search('factor(\[|%5B)' + pwKey + '(\]|%5D)=([\d\.]+)',urlwatttomine, flags=re.IGNORECASE)
		if match:
			pw = float(match.group(3))
		else:
			print(f'Power values not found for {coin["tag"]}:{algorithm}')

		coin['power'] = pw
		coin['cost'] = pw * float(cost) * 24 /1000
		coin['usd_revenue'] = float(coin[revenueKey]) * btcValor
		coin['profit'] = float(coin['usd_revenue'] - coin['cost'])
		
		coins.append(coin)
	  
	listCoins = sorted(coins, key=lambda d: d[keyOrder], reverse=True)
	
	if 'verbose' in jsonConfig and jsonConfig['verbose']:
		if len(listCoins) > 0:
			best = listCoins[0]
			for idx, l in enumerate(listCoins):
				perc = (float(l[keyOrder]) / float(best[keyOrder] ) -1 ) * 100
				print (str(idx + 1) + ". " + l["tag"] + " -> " + str(l[keyOrder])  +  ( '' if idx == 0 else " (" + str(round(perc,2)) + " %)" ))

	return listCoins
