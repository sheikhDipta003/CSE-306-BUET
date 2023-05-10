import re
import pprint

serial = {'A': 'add', 'B': 'addi', 'C': 'sub', 'D': 'subi', 'E': 'and', 'F': 'andi', 'G': 'or', 'H': 'ori', 'I': 'sll', 'J': 'srl', 'K': 'nor', 'L': 'lw', 'M': 'sw', 'N': 'beq', 'O': 'bneq', 'P': 'j'}

sequence = 'HDAMGELBFPCJNIKO'
instruction = {}

for i in range(len(sequence)):
    instruction[serial[sequence[i]]] = bin(i)[2:].zfill(4)

registers = {'$zero': '0000', '$t0': '0111', '$t1': '0001', '$t2': '0010', '$t3': '0011', '$t4': '0100', '$sp': '0110'}

R_TYPE = ['add', 'sub', 'and', 'or', 'nor']
S_TYPE = ['sll', 'srl']
I_TYPE = ['addi', 'subi', 'andi', 'ori']

ALU_OP = {'add': '000', 'sub': '001', 'and': '010', 'or': '011', 'nor': '100', 'sll': '101', 'srl': '110',
          'addi':'000', 'subi':'001', 'andi':'010', 'ori':'011', 'lw':'000', 'sw':'000', 'beq':'001', 'bneq':'001',
          'j':'000'}

# reg_dst, alu_src, mem_to_reg, reg_write, mem_read, mem_write, branch, branch_neq, jump
controls = {'rtype': '100100000',
            'stype': '010100000',
            'immediate': '010100000',
            'beq': '000000100',
            'bneq': '000000010',
            'lw': '011110000',
            'sw': '011001000',
            'j': '000000001'}

def build_control_hex():
    print('Control ROM:')
    print('\t', end='')
    for i in range(len(sequence)):
        if serial[sequence[i]] in R_TYPE:       control_hex_result = controls['rtype']
        elif serial[sequence[i]] in S_TYPE:     control_hex_result = controls['stype']
        elif serial[sequence[i]] in I_TYPE:     control_hex_result = controls['immediate']
        else:  control_hex_result = controls[serial[sequence[i]]]

        control_hex_result += ALU_OP[serial[sequence[i]]]

        print(hex(int(control_hex_result, 2))[2:].zfill(3), end=' ')
# 503 501 900 640 903 902 780 500 502 008 901 506 021 505 904 011

line_no = 1
labels = {}

def generate_label_location(lines):
    changed_lines = []
    for line in lines:
        parts = [part.strip() for part in line.split(':')]

        if len(parts) == 2:                         # case label
            labels[parts[0]] = len(changed_lines)
            if parts[1] != '':                      # code without label
                changed_lines.append(parts[1])
        else:                                       # not a label
            changed_lines.append(line)
    return changed_lines

def build_instruction_binary(line_no, opcode, *args):
    bin_instruction = instruction[opcode]
    
    # add $t0, $t1, $t2 : Opcode SrcReg1($t1) SrcReg2($t2) DstReg($t0)
    if opcode in R_TYPE:
        bin_instruction += registers[args[1]] # source 1
        bin_instruction += registers[args[2]] # source 2
        bin_instruction += registers[args[0]] # destination register
    
    # sll $t0, $t1, 1 : Opcode SrcReg1($t1) DstReg($t0) unsigned-int
    elif opcode in S_TYPE:
        bin_instruction += registers[args[1]] # source register
        bin_instruction += registers[args[0]] # destination register
        bin_instruction += bin(int(args[2]))[2:].zfill(4) # shift amount
    
    # addi $t0, $t1, 1 : Opcode SrcReg1($t1) DstReg($t0) signed-int
    # beq $t0, $t1, 1 : Opcode SrcReg1($t1) SrcReg2($t0) signed-int     | if ($t1 - $t0 == 0) then goto 1
    # sw $t0, 1($t1) : Opcode SrcReg1($t1) SrcReg2($t0) signed-int      | $t0 = $t1 + 1
    # lw $t0, 1($t1) : Opcode SrcReg1($t1) DstReg($t0) signed-int       | *($t1+1) = $t0
    elif opcode in I_TYPE:
        # addi $t0, $t1, 1          | immediate position @ 3
        bin_instruction += registers[args[1]]
        bin_instruction += registers[args[0]] # destination register
        immediate = int(args[2])
        if immediate < 0:   # 16's complement if negative constant
            immediate = 2**4 + immediate
        bin_instruction += bin(immediate)[2:].zfill(4)
    elif (opcode == 'beq' or opcode == 'bneq'):
        bin_instruction += registers[args[1]]
        bin_instruction += registers[args[0]]  # destination register
        immediate = labels[args[2]] - (line_no + 1)  # PC auto-increments
        if immediate < 0:  # 16's complement if negative constant
            immediate = 2 ** 4 + immediate
        bin_instruction += bin(immediate)[2:].zfill(4)  # immediate value / address
    elif (opcode == 'lw' or opcode == 'sw'):
        bin_instruction += registers[args[2]]
        bin_instruction += registers[args[0]]  # destination register
        immediate = int(args[1])
        if immediate < 0:  # 16's complement if negative constant
            immediate = 2 ** 4 + immediate
        bin_instruction += bin(immediate)[2:].zfill(4)  # immediate value / address
    # j label1 : Opcode address (unsigned-int)
    elif opcode == 'j': # J-Type
        label_line = labels[args[0]]
        bin_instruction += bin(label_line)[2:].zfill(8) # target jump address
        bin_instruction += '0000'
    
    return bin_instruction


split_pattern = r'[ \t,\(\)]+'

def split(line):
    return re.split(split_pattern, line)

STACK_POINTER_ENABLED = True

if __name__ == '__main__':
    print('Instructions OPCODE:')
    pprint.pprint(instruction)
    print()

    build_control_hex()
    print()

    with open('C:\\Users\\hp\\Desktop\\CSE 306\\ASGN-3\\input.asm', 'r') as file:
        lines = [line.split(r'//')[0].strip() for line in file]                 # Trim Whitespaces
        lines = list(filter(lambda line : line != '', lines))   # Without Empty Lines
    
    if STACK_POINTER_ENABLED:
        push_pop_re = r'(push|pop)[ ]+(\$t[0-4])'
        original_lines = lines
        lines = ['addi $sp, $zero, 15']                         # SP initalization
        for line in original_lines:
            matched = re.search(push_pop_re, line)
            if matched is None:
                lines.append(line)
            else:
                if matched.group(1) == 'push':
                    lines.append(f'sw {matched.group(2)}, 0($sp)')        # store data in the stack top
                    lines.append('subi $sp, $sp, 1')              # allocate one variable to stack pointer
                else:
                    lines.append('addi $sp, $sp, 1')              # deallocate one variable from stack pointer
                    lines.append(f'lw {matched.group(2)}, 0($sp)')        # load data from the stack top
    
    lines = generate_label_location(lines)                      # Label Location Generated

    print('ASM Lines:')
    pprint.pprint(lines)
    
    bin_lines = []
    hex_lines = []

    for i in range(len(lines)):
        bin_line = build_instruction_binary(i, *split(lines[i]))
        bin_lines.append(bin_line)
        hex_lines.append('0x' + hex(int(bin_line, 2))[2:].zfill(4)+',')

    with open('output.bin', 'w') as bin_file:
        for i in range(len(lines)):
            bin_file.write(' '.join([bin_lines[i][j:j+4] for j in range(0, len(bin_lines[i]), 4)]) + ' : ' + lines[i] + '\n')
    
    with open('output.hex', 'w') as hex_file:
        hex_file.writelines(hex_lines)