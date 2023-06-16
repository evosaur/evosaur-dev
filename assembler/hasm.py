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

def my_int(size):
	base = 10
	if size[:2] == "0x":
		base = 16 # int() will remove the 0x
	elif size[:-1] == "h":
		if size[:2].lower() == "0x": # We don't want int() to silently remove this
			raise Exception("Error at line "+str(linenum)+": Parameter size is not a valid number: "+input.split("\n")[instruction["linenum"]])
		base = 16
	elif size[:2] == "0b":
		base = 2 # As with 0x, int() will remove this

	return int(size, base)

instructions = {}

num_instructions = 0
for file in paths:
	if os.path.isfile(file) and not os.path.basename(file).endswith("notes.txt"):
		name = os.path.splitext(os.path.basename(file))[0]

		if name in instructions:
			raise Exception("Instruction name conflict")

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

registers = ["MR", "PR", "FR", "OFR", "RS", "RW", "OIPH", "OIPE", "OIPDE", "OPRH", "OPRE", "OPRDE", "IP", "SP", "BP"]
i=0
while i < num_general_registers:
	registers.append("R"+str(i))
	i += 1
i=0
while i < num_segment_registers:
	registers.append("SS"+str(i))
	i += 1

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

labels = {}

# first pass: validate instructions, validate syntax (mostly), evaluate what labels exist and their default sizes, split up input to the relevant data
lines = [] # For the next pass

in_queue = False
linenum = 0
for line in input.split("\n"):
	linenum += 1
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

	command = line[:i]

	i += 1

	param_start = i

	params = []

	num_parameters = 0
	was_space = True
	escaped = False
	in_singlequote = False
	in_doublequote = False
	in_backtick = False
	last_space = i-1
	while i < len(line):
		if line[i] == "'":
			raise Exception("Error at line "+str(linenum)+": ' has no defined meaning in this syntax yet!")
		elif line[i] == '"':
			if in_doublequote and not escaped:
				in_doublequote = False
			elif not in_doublequote:
				in_doublequote = True
		elif line[i] == "`":
			if in_backtick and not escaped:
				in_backtick = False
			elif not in_backtick:
				in_backtick = True
		elif line[i] == ";" and was_space:
			break # rest is a comment

		if line[i] == " " or line[i] == "	":
			old_was_space = was_space
			was_space = (not in_singlequote and not in_doublequote and not in_backtick)
			if was_space and not old_was_space:
				num_parameters = num_parameters + 1
				if line[i-1] == ",":
					params.append(line[last_space+1:i-1])
				else:
					params.append(line[last_space+1:i])

			last_space = i
		else:
			was_space = False

		i += 1


	if i == len(line):
		num_parameters += 1
		params.append(line[last_space+1:i])

	if command in instructions:
		if num_parameters != instructions[command]['params']:
			raise Exception("Error at line "+str(linenum)+": Wrong number of parameters given for this instruction: "+line)
		# Not actually doing anything with this on this pass
	elif command == "declare":
		if in_queue:
			raise Exception("Error at line "+str(linenum)+": Cannot declare data inside an instruction queue: "+line)

		pass # Again nothing to do on this pass, but important to have these here so they won't be seen as unknown instructions
	elif command == "{":
		if num_parameters != 0:
			raise Exception("Error at line "+str(linenum)+": { does not take any parameters!")

		if in_queue:
			raise Exception("Error at line "+str(linenum)+": Instruction queues cannot be nested!")
		in_queue = True
	elif command == "}":
		if num_parameters != 0:
			raise Exception("Error at line "+str(linenum)+": } does not take any parameters!")

		if not in_queue:
			raise Exception("Error at line "+str(linenum)+": Found } but no matching { before it!")
		in_queue = False
	elif command[-1] == ":":
		if in_queue:
			raise Exception("Error at line "+str(linenum)+": Cannot declare a label inside an instruction queue: "+line)

		if num_parameters != 0:
			raise Exception("Error at line "+str(linenum)+": Labels do not take any parameters!")

		label = command[:-1]

		size = current_mode
		if len(label) > 0 and label[0] == "{":
			i = 1
			size = ""
			while i < len(label):
				if label[i] == "}":
					break

				size += label[i]

				i += 1
			if i == len(label):
				raise Exception("Error at line "+str(linenum)+": Label starts with { but doesn't contain a }: "+line)

			label = label[i+1:]

			try:
				size = my_int(size)
			except ValueError:
				raise Exception("Error at line "+str(linenum)+": Label size is not a valid number: "+line)

		if label in labels:
			raise Exception("Error at line "+str(linenum)+": Label already declared at line "+str(labels[label]["linenum"])+": "+line)

		labels[label] = {"linenum": linenum, "bits": size}
	else:
		raise Exception("Unknown instruction at line "+str(linenum)+": "+command)

	lines.append({"command": command, "params": params, "linenum": linenum})

if in_queue:
	raise Exception("Unterminated instruction queue found at <EOF>!")

print("First pass results: labels =", labels, ", lines =", lines)

# second pass: calculate all sizes, calculate label addresses
def get_size(queue):
	size = 0

	size += size_instruction_queue_bits
	last_opcode = None
	current_opcodes = None
	for instruction in queue:
		if instruction["command"] != last_opcode:
			if max_instructions_per_type != 1: # < 1 makes no sense so I don't care about handling it
				last_opcode = instruction["command"]
				current_opcodes = 1

			size += opcode_bit_size
			size += num_instructions_bit_size
		else:
			current_opcodes += 1
			if current_opcodes == max_instructions_per_type:
				last_opcode = None
		size += bits_per_parameter * instructions[instruction["command"]]["params"]

	size += immediate_bit_size

	for instruction in queue:
		for parameter in instruction["params"]:
			if parameter[-1] == "]":
				tmp = parameter.split("[", maxsplit=1)
				if len(tmp) != 2:
					raise Exception("Error at line "+str(linenum)+": Parameter ends with ] but no matching [ was found: "+input.split("\n")[instruction["linenum"]])
				parameter = tmp[1][:-1]
				if len(parameter) == 0:
					raise Exception("Error at line "+str(linenum)+": Invalid parameter: "+input.split("\n")[instruction["linenum"]])

			this_size = current_mode
			if parameter[0] == "{":
				i = 1
				this_size = ""
				while i < len(parameter):
					if parameter[i] == "}":
						break

					this_size += parameter[i]

					i += 1
				if i == len(parameter):
					raise Exception("Error at line "+str(linenum)+": Parameter starts with { but doesn't contain a }: "+input.split("\n")[instruction["linenum"]])

				parameter = parameter[i+1:]

				try:
					this_size = my_int(this_size)
				except ValueError:
					raise Exception("Error at line "+str(linenum)+": Parameter size is not a valid number: "+input.split("\n")[instruction["linenum"]])
			elif parameter[-1] == ":":
				this_size = labels[parameter[:-1]]["bits"]

			if this_size <= parameter_data_bits:
				continue # So you can actually use the 9th or whatever bit even if it doesn't support a full 16
				# For other things, it'll have to be rounded up

			this_size = 2**math.ceil(math.log2(this_size))

			if parameter[-1] == ":": # Will stuff this into immediate references, unless the size is declared to be <= max allowed directly in param
						 # Could get away with it if the higher bits would have been 0 anyways, but not going to bother with that yet
				size += this_size
			elif parameter.upper() in registers:
				continue
			else:
				try:
					my_int(parameter)
					size += this_size
				except ValueError:
					raise Exception("Error at line "+str(linenum)+": Unknown parameter: `"+parameter+"': "+input.split("\n")[instruction["linenum"]])

	size += bits_for_flag_save_definition_size

	return size

address = 0

current_queue = []
in_queue = False

for line in lines:
	if line["command"] in instructions:
		if in_queue:
			current_queue.append(line)
		else:
			address += get_size([line])
	elif line["command"] == "{":
		in_queue = True
	elif line["command"] == "}":
		address += get_size(current_queue)

		current_queue = []
		in_queue = False
	elif line["command"] == "declare":
		pass # TODO: Declare
	elif line["command"][:-1] == ":":
		pass # TODO: Labels

# third pass: calculate parameter values, calculate immediate reference values, create binary output
