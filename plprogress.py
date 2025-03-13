#Felix Bittmann, 2025
#felix.bittmann@lifbi.de

import re
import time
from os import listdir
from os.path import isfile, join


def dotcounter(filename):
	"""Counts the number of dots in a Stata logfile to count number of replications"""
	dots = 0
	fails = 0
	totalsims = 0
	startcounting = False
	with open(filename, "r") as statalog:
		for number, content in enumerate(statalog):
			if totalsims == 0 and (content.startswith("Simulation") or content.startswith("Bootstrap")):
				start = content.index("(") + 1
				end = content.index(")")
				totalsims = int(content[start:end])
			if content.startswith("----+--- 1 ---+--- 2"):
				startcounting = True
				continue
			if startcounting == True:
				dots += content.count(".")
				fails += content.count("x")
	return (dots, fails, totalsims)	



def filefinder(mypath):
	"""Checks a folder path for any parallel-logfiles currently present"""
	statalogs = []
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	for element in onlyfiles:
		if bool(re.search('_do\d+.log', element)):
			statalogs.append(element)
	return statalogs



def plprogress(mypath, threads, delay=30):
	"""Computes the progress of simulations or bootstrap resamples when
	using the Stata Ado Parallel"""
	time.sleep(1)		#Let simulations startup
	statalogs = filefinder(mypath)
	if len(statalogs) != threads:
		print("Error! Either the simulation has not started yet" \
		" or there is a mismatch between number of threads specified and" \
		" actual threads currently active! Restart the program!")
		return None
	
	sims = []
	while True:
		dots = 0
		fails = 0
		totalsims = 0
		for element in statalogs:
			res = dotcounter(join(mypath, element))
			dots += res[0]
			fails += res[1]
			totalsims += res[2]
		total = dots + fails
		sims.append(total)
		sharedone = round((total * 100) / totalsims, 3)
		print("Simulations done", total, "of", totalsims, "/", sharedone)
		print("Success rate:", round((dots * 100) / total, 2))
		
		"""Computing the ETA"""
		if len(sims) >= 7:
			diff = []
			for i in range(-7, -2):
				diff.append(sims[i+1] - sims[i])
			meanchange = sum(diff) / len(diff)
			remaining = totalsims - total
			duration = (remaining / meanchange) * delay
			print("Time remaining (sec/min/h):", round(duration), "/", round(duration / 60, 1), "/", round(duration / 3600, 1))
		print("")
		if total >= totalsims:
			print("Simulation (almost) completed!")
			return None
		time.sleep(delay)
