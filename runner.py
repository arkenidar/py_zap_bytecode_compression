#!/usr/bin/env python3
import sys
from bitarray import bitarray

if len(sys.argv)>1:
	bytecode_filepath=sys.argv[1]
else:
	bytecode_filepath="out.zbc"
try:
	bytecode_fp = open(bytecode_filepath, "rb")
except FileNotFoundError:
	print(bytecode_filepath, 'bytecode file not found')
	sys.exit()
print('opened bytecode file:', bytecode_filepath)

# fields size specs
fsize = [1,1,1,1]#[int(size) for size in bytecode_fp.read(4)]
tsize=sum(fsize)
print(fsize)

# instruction and address fields
assert(fsize[0]==fsize[1])
address_bytes_count=fsize[0]
assert(fsize[2]==fsize[3])
instruction_bytes_count=fsize[2]

# mapping utils from compiler.py (keep in sync or make a common module)
def max_value_bits(bytes_count):
	return 2**(bytes_count*8)
address_max_value=max_value_bits(address_bytes_count)-1
instruction_max_value=max_value_bits(instruction_bytes_count)-1
mapping={'PATHSEL':address_max_value, 'ZERO':0, 'ONE':1, 'IN':address_max_value-1, 'OUT':address_max_value-1, 'EXIT': instruction_max_value}
print('mapping', mapping)

instruction_count=instruction_max_value+1
bytecode = bytecode_fp.read(4*instruction_count)
print('bytecode', bytecode)

bit_count=address_max_value+1
ram_memory=bitarray(bit_count)#[0 for _ in range(bit_count)]

def boolean_to_bit(boolean):
	if boolean:
		return 1
	else:
		return 0

def bit_to_boolean(bit_to_convert):
	assert(bit_to_convert in (0,1))
	if bit_to_convert==0:
		return False
	elif bit_to_convert==1:
		return True

def write_bit_to_ram_memory(address, bit_to_write):
	assert(bit_to_write in (0,1))
	ram_memory[address]=bit_to_boolean(bit_to_write)

def read_bit_from_ram_memory(address):
	return boolean_to_bit(ram_memory[address])

write_bit_to_ram_memory(mapping['ZERO'], 0)
write_bit_to_ram_memory(mapping['ONE'], 1)

def read_bit(): # TODO read_bit_from_stdin()
	bit_in=None
	while bit_in not in (0,1):
		try:
			bit_in=int(input('bit?     '))
		except ValueError:
			pass
		except KeyboardInterrupt:
			print('\ninterrupted')
			sys.exit()
		if bit_in not in (0,1):
			print('invalid value')
	return bit_in

def read_memory(address):
	if address==mapping['IN']:
		value=read_bit()
	else:
		value=read_bit_from_ram_memory(address)
	return value
	
def write_memory(address, value):
	#print('write_memory', (address, value))
	if address==mapping['OUT']:
		print('out:    ', value)
	else:
		write_bit_to_ram_memory(address, value)

def get_bc_field(field_id, instruction_index):
	#print('get_bc_field', (field_id, instruction_index))
	bci=instruction_index*tsize
	field_size=fsize[field_id]
	#print('field_size', field_size)
	offset=sum([fsize[i] for i in range(field_id)])
	#print('offset', offset)
	pos=bci+offset
	value=int.from_bytes(bytecode[pos:pos+field_size], byteorder='big')
	return value

current_instruction_index=0
while True:	
	fields = [get_bc_field(field_id, current_instruction_index) for field_id in range(4)]
	#print('fields  ',fields)
	#input('pause')	
	
	#do (even last instruction in index (EXIT))
	bit_in = read_memory(get_bc_field(1, current_instruction_index))
	write_memory(get_bc_field(0, current_instruction_index), bit_in)
	
	# jump
	pathsel_bit=read_memory(mapping['PATHSEL'])
	#print('pathsel_bit', pathsel_bit)
	current_instruction_index = get_bc_field(2+pathsel_bit, current_instruction_index)
	
	#check for exit
	if current_instruction_index==mapping['EXIT']: break
	#input('pause')
	
