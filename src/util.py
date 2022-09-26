import json
from os.path import exists, splitext

def readFile(filepath, default = None):
	if exists(filepath):
		file_name, file_extension = splitext(filepath)
		with open(filepath, mode='r') as ff:
			if file_extension == '.json':
				cnt = json.loads(ff.read())
				ff.close()
				return cnt
			elif file_extension == '.txt' or file_extension == '.conf':
				cnt = ff.read()
				ff.close()
				return cnt

	return default