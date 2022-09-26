import json
import requests
import re
from util import readFile


RIG_FILE= '/hive-config/rig.conf'

#GPU_STATS_JSON="/run/hive/gpu-stats.json"
#curl https://raw.githubusercontent.com/cryptopoo/hiveos_gddr6x_temps/main/quick-install-unstable.sh | bash
#https://app.swaggerhub.com/apis/HiveOS/public/2.1-beta



def _getKey(cfile, key):
	match = re.search(f'{key}=([\"\S])', cfile)
	if match:
	   return match.groups(1)
	return None

class HiveOS():

	OS = 'HIVEOS'
	
	_farm = None
	_rig = None
	_apitoken = None
	_rigfile = None

	BaseUrl= "https://api2.hiveos.farm/api/v2"

	def __init__(self, apitoken, jsonConfig = None, rigfile = RIG_FILE):
		self._apitoken = apitoken
		self._rigfile = rigfile
	   
		if jsonConfig and 'farmid' in jsonConfig:
			self._farm = jsonConfig['farmid']
			
		if jsonConfig and 'rigid' in jsonConfig:
			self._rig = jsonConfig['rigid']
		
		if not self._farm or not self._rig:
			cp = readFile(rigfile)
			if cp: 
			  self._farm = self._farm if self._farm else _getKey(cp, "FARM_ID")
			  self._rig = self._rig if self._rig else  _getKey(cp,"RIG_ID")
			else:
				print('RIG configuration file not found')

	def _getURL(self, url, info = ''):
		headers = { 'Authorization': 'Bearer ' + self._apitoken }
		response = requests.get(self.BaseUrl + url, headers=headers)
		ret = json.loads(json.dumps(response.json()))
		return ret["data"] if "data" in ret else ret

	def _patchURL(self, url, payload  ):
		headers = { 
			'Authorization': 'Bearer ' + self._apitoken,
			'content-type': 'application/json'	}
		response = requests.patch(self.BaseUrl + url, data=json.dumps(payload), headers=headers)
		ret = json.loads(json.dumps(response.json()))
		return ret

	def _postURL(self, url, payload  ):
		headers = { 
			'Authorization': 'Bearer ' + self._apitoken,
			'content-type': 'application/json'	}
		response = requests.post(self.BaseUrl + url, data=json.dumps(payload), headers=headers)
		ret = json.loads(json.dumps(response.json()))
		return ret

	def getFarmId (self):
		if self._farm:
			return self._farm
		
		f = self.farms()
		if 'message' in f:
			print(f'ERROR: An error ocurred during the conection: {f["message"]}')
			return None
			
		self._farm = f[0]['id']
		return self._farm

	def getWorkerId (self):
		if self._rig:
			return self._rig
		
		f = self.farm_workers(self.getFarmId())
		
		if 'message' in f:
			print(f'ERROR: An error ocurred during the conection: {f["message"]}')
			return None
			
		self._rig = f[0]['id']
		return self._rig
		
	def farms(self):
		return self._getURL('/farms/', 'Farms')

	def farm (self, farmId):
		return self._getURL('/farms/' + str(farmId), 'Farm ' + str(farmId))

	def farm_workers (self,farmId):
		return self._getURL('/farms/' + str(farmId) + '/workers', 'Workers ' + str(farmId))
		
	def farm_gpus (self,farmId):
		return self._getURL('/farms/' + str(farmId) + '/workers/gpus', 'Workers GPUS' + str(farmId))

	def worker (self,farmId = None, workerId = None):
		
		if farmId and workerId:
			return self._getURL('/farms/' + str(farmId) + '/workers/'+ str(workerId), 'Worker ' + str(farmId) + ',' + str(workerId))

		return self.worker(farmId if farmId else self.getFarmId(), workerId if workerId else self.getWorkerId())
			
	def worker_metric (self, farmId, workerId):
		return self._getURL('/farms/' + str(farmId) + '/workers/'+ str(workerId) + '/metrics', 'Worker Metrics' + str(farmId) + ',' + str(workerId))

	def flight_sheets(self, farmId):
		return self._getURL('/farms/' + str(farmId) + '/fs')

	def set_farm_flight_sheets(self, farmId, fs):
		workers = self.farm_workers(farmId)
		
		print(fs['name'])
		for worker in workers:
			#worker["flight_sheet"] = fs
			self._patchURL('/farms/' + str(farmId) + '/workers/' + str(worker['id']),  { "fs_id": fs['id'] } )

	def set_worker_flight_sheets(self, farmId, workerId, fsId):
		self._patchURL('/farms/' + str(farmId) + '/workers/' + str(workerId),  { "fs_id": fsId } )

	def get_worker_overclock(self, farmId, workerId):
		return self.worker(farmId, workerId)['overclock']
	
	def set_worker_overclock(self, farmId, workerId, gpu_index, is_nvidia, core=None, mem_clock=None, fan_speed = None, power_limit= None):
		#https://app.swaggerhub.com/apis/HiveOS/public/2.1-beta#/workers/post_farms__farmId__workers_overclock

		#"core_clock": 0,
		#				"mem_clock": 0,
		#				"fan_speed": 0,
		#				"power_limit": 0
						
		oc = {
				"workerId": workerId,
				"gpu_data": [
					{
						"amd" : { "tref_timing" : ""},
						"gpus": [
							{
							"worker_id": workerId,
							"gpu_index": str(gpu_index)
							}
						],					
						"nvidia": {
							"reduce_power": True,
						}
					}				
				],
				"common_data": [
					{
						"worker_ids": [
						workerId
						],
						"amd": {},
						"nvidia": {
							"reduce_power": True,
						}
					}
				]
			}

		if not core == None:
			oc["gpu_data"][0]["nvidia"]['core_clock'] = core
			
		if not mem_clock == None:
			oc["gpu_data"][0]["nvidia"]['mem_clock'] = mem_clock
			
		if not fan_speed == None:
			oc["gpu_data"][0]["nvidia"]['fan_speed'] = fan_speed
			
		if not power_limit == None:
			oc["gpu_data"][0]["nvidia"]['power_limit'] = power_limit
			
		self._postURL('/farms/' + str(farmId) + '/workers/overclock',  oc )


