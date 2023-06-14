#!/usr/bin/env python3

# Usage of Exception() is to give an easy traceback, not to actually be used as an exception

import math
import glob
import os
import sys

thisdir = os.path.abspath(os.path.dirname(__file__))

datadir = os.path.abspath(thisdir+"/../cpu")

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

print("Opcodes:", instructions)
print("Opcode count:", num_instructions)
opcode_bit_size = math.ceil(math.log2(num_instructions)) + 1 # + 1 for is_conditional
print("Bits per opcode:", opcode_bit_size)

# do this after reading the config
f = open(thisdir+"/arbitrary_constants.py");
exec(f.read())
f.close()

argc = len(sys.argv)
print("Number of args given:", argc)

if argc < 2 or argc > 3:
	raise Exception("Too few arguments given! Syntax: "+sys.argv[0]+" <input> [<output>]")

if argc >= 3:
	output = open(sys.argv[2], "wb")
else:
	output = open("/dev/stdout", "wb") # not going to fiddle with using fd 1 from python

print("Using output file", output)

try:
	inputf = open(sys.argv[1], "r")
except Exception:
	print("Unable to open file `"+sys.argv[1]+"'! Exiting...")
	os._exit(1)

input = inputf.read()
inputf.close()

print(input)

# first pass: evaluate instructions, calculate sizes, validate syntax, evaluate label addresses
linenum = 0
in_queue = False
last_queue_opcode = None
for line in input.split('\n'):
	linenum+=1
	line = line.strip()

	if line == "" or line[0] == ";":
		continue

	i=0
	while i < len(line):
		if line[i] == " " or line[i] == "	":
			break
		elif line[i] == "'" or line[i] == "\"" or line == "`":
			raise Exception("Invalid instruction at line "+str(linenum)+": "+line)
		i+=1

	print(line[0:i])

# second pass: evaluate parameter values, create binary output
