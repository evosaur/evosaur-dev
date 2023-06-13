# These numbers don't change behavior much and aren't specified yet, but there being a number is required

max_immediate_value_size = 64
immediate_bit_size = math.ceil(math.log2(max_immediate_value_size))

num_registers = 16

# Likely won't be limited quite like this, but this still works
max_types_per_queue = 16
max_instructions_per_type = 16

num_instructions_bit_size = math.ceil(math.log2(max_instructions_per_type))

print("Bits to declare instruction count per opcode:", num_instructions_bit_size)

max_parameters_per_instruction = 0
for name in instructions:
	if instructions[name]['params'] > max_parameters_per_instruction:
		max_parameters_per_instruction = instructions[name]['params']

max_parameters_per_instruction += 2 # conditional

