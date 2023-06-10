#!/usr/bin/env python3

import os
import sys
import glob

datadir = os.path.abspath(os.path.dirname(__file__)+"/../cpu")

paths = glob.glob(datadir+"/instructions/*/*")

paths.sort()

instructions = {}

num_instructions = 0
for file in paths:
	if os.path.isfile(file) and not os.path.basename(file).endswith("notes.txt"):
		name = os.path.splitext(os.path.basename(file))[0]
		try:
			_ = instructions[name]
			raise Exception("Instruction name conflict")
		except KeyError:
			pass
		instructions[name] = {"path": file, "id": num_instructions}
		num_instructions += 1

for ins in instructions:
	info = instructions[ins]
	f = open(info["path"], "r")
	line = f.readline()
	f.close()

	header, num = line.rsplit(maxsplit=1)
	if header != "Number of parameters:":
		print("Unable to read file "+info["path"]+": does not look like an instruction. ignoring...")

	if type(int(num)) != int:
		raise Exception("Invalid number: "+num)

	info["params"] = int(num)

print(instructions)
print(num_instructions)
