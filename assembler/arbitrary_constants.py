# This value will eventually be a part of the assembly language itself and not a constant here

current_mode = 128

print("Assembling for mode:", current_mode)

# These numbers don't change behavior much and aren't specified yet, but there being a number is required

max_immediate_value_size = current_mode * 16
immediate_bit_size = math.ceil(math.log2(max_immediate_value_size))

print("Bits required to specify immediate references' size or an index into it:", immediate_bit_size)

num_general_registers = 16
num_segment_registers = 8

num_special_registers = 4 + 2 + 6 + 3
# MR,PR,FR,OFR + RS,RW + O{IP,PR}{H,E,DE} + IP,SP,BP

num_registers = num_general_registers + num_segment_registers + num_special_registers
bits_for_register_selection = math.ceil(math.log2(num_registers))

print("Number of different registers (total):", num_registers)
print("Bits required to specify which register to use:", bits_for_register_selection)



bits_for_current_mode = math.log2(current_mode)
if bits_for_current_mode//1 != bits_for_current_mode:
	print("¦|") # this isn't a valid mode for HaxCPU
	os._exit(1)

bits_for_each_mode_value = math.ceil(math.log2(bits_for_current_mode))

print("Bits required for showing each power of 2 value <= current mode:", bits_for_each_mode_value)

parameter_data_bits = bits_for_each_mode_value + max(immediate_bit_size, bits_for_register_selection) + bits_for_each_mode_value

print("Bits available for a parameter's data:", parameter_data_bits)

num_param_types = 5
bits_for_parameter_type = math.ceil(math.log2(num_param_types))

print("Bits taken to state which parameter type this is:", bits_for_parameter_type)

bits_per_parameter = parameter_data_bits + bits_for_parameter_type

print("Bits per parameter:", bits_per_parameter)

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

print("Max parameters any instruction will take:", max_parameters_per_instruction)

max_instruction_queue_size = (max_types_per_queue * (opcode_bit_size + num_instructions_bit_size + (bits_per_parameter * max_parameters_per_instruction * max_instructions_per_type)))

print("Max size of the instruction part of the queue:", max_instruction_queue_size)

size_instruction_queue_bits = math.ceil(math.log2(max_instruction_queue_size))

print("Bits taken to state instruction queue size:", size_instruction_queue_bits)

# Can be lower, but makes no sense to go over
# Currently not actually used other than for instruction queue size bc I haven't written it into the assembly syntax yet
# Will have to do that to make it very useful... but just to get it working first
max_flag_save_definitions = max_types_per_queue * max_instructions_per_type

bits_for_flag_save_definition_size = math.ceil(math.log2(max_flag_save_definitions))
