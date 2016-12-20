#!/usr/bin/env python3
import sys

'''bytecode compiler'''

if len(sys.argv)>1:
	source=sys.argv[1]
else:
	source='source.zsc'
try:
	ifp=open(source, 'r')
except FileNotFoundError:
	print(source, 'file not found')
	sys.exit()
print('opened source file:', source)

if len(sys.argv)>2:
	bytecode=sys.argv[2]
else:
	bytecode='out.zbc'
ofp=open(bytecode, 'wb')
print('opened bytecode file:', bytecode)

# fields size specs
address_bytes_count=1
instruction_bytes_count=2
field_sizes = {0:address_bytes_count, 1:address_bytes_count, 2:instruction_bytes_count, 3:instruction_bytes_count}

# mapping
def max_value_bits(bytes_count):
	return 2**(bytes_count*8)
address_max_value=max_value_bits(address_bytes_count)-1
instruction_max_value=max_value_bits(instruction_bytes_count)-1
mapping={'PATHSEL':address_max_value, 'ZERO':0, 'ONE':1, 'IN':address_max_value-1, 'OUT':address_max_value-1, 'EXIT': instruction_max_value}

'''
read from ORIGIN: PATHSEL(255), ZERO(0), ONE(1), IN(254), memory(rest...)
read-not from: OUT(254)
write to DESTINATION: PATHSEL(255), OUT(254), memory(rest...)
write-not to: ZERO(0), ONE(1), IN(254)
'''

#FIELD0 IS DESTINATION
field0_ok=['PATHSEL', 'OUT']
field0_not_ok=['ZERO', 'ONE', 'IN']

#FIELD1 IS ORIGIN
field1_ok=['PATHSEL', 'ZERO', 'ONE', 'IN']
field1_not_ok=['OUT']

#############

ofp.write(bytes(field_sizes.values()))

for line in ifp:
	line=line.rstrip("\n")
	line=line.split("#")[0]
	fields=line.split(',')
	fields = [field.strip(' \t\n\r') for field in fields]
	
	error = lambda why: print("wrong fields:",why, repr(fields))
	if(['']==fields): continue
	if(len(fields)!=4):
		error('not 4')
		continue
	try:
		def convert(i, field):
			if('-'==field[0]):
				field=field.lstrip('-')
				
				if i==0: #field0
					if field in field0_ok and field not in field0_not_ok:
						pass
					else:
						error("field0 not ok")
						
				elif i==1: #field1
					if field in field1_ok and field not in field1_not_ok:
						pass
					else:
						error("field1 not ok")
						
				elif i in [2,3]:
					pass
					
				else:
					error("field index not valid")
					
				try:					
					field=mapping[field]
					
				except KeyError:
					error("field not mapped")
			else:
				field=int(field)
				if(i in (0,1)):
					field+=2
					assert(field<=address_max_value)
				
			return field
			
		print('repr(fields)    ', repr(fields))
		fields=[convert(i,field) for i,field in enumerate(fields)]
		
		
	except ValueError:
		error('not int')
		continue
	
	print('fields          ', fields)
	for i,field in enumerate(fields):
		ofp.write(field.to_bytes(field_sizes[i], byteorder='big'))
	
print("end of file scanning")
