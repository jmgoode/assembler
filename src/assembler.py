#!/usr/bin/env python3

"""
MPCS52011 Project 6: Assembler
Author: Jason Goode
"""

import sys
import os
import parser as p

# ACCEPT INPUT FILE (.asm)
try:
    in_file = sys.argv[1] # assign value to arg_one. if not entered, except block is triggered
    if os.path.exists(in_file): # if sys.argv[1] entered, check to see if filepath exists
        if not in_file.endswith('.asm'): # check the file extension
            print('Parser only accepts .asm files. Please try again')
            sys.exit()
    else: # invalid filepath
        print('Invalid filename. Please try again')
        sys.exit()

except IndexError: # throws error if no input specified
    print('Error: please specify input file as the first argument')
    sys.exit()

p.strip(in_file) # strip whitespace and comments
clean_file = in_file.split('.asm')[0] + '_clean.asm' # produce temporary "clean" file

class Instruction:
    """Instruction class"""
    # takes in line of assembly and it's associated assembler
    def __init__(self, line, assembler):
        self.assembler = assembler # assembler
        self.assembly = line # clean line of assembly
        self.instruction_type = self.get_instruction_type() # A or C instruction
        self.comp = None # comp binary
        self.dest = None # dest binary
        self.jump = None # jump binary
        self.binary = self.get_binary() # get full binary

    def get_instruction_type(self):
        """get assembly's instruction type"""
        if self.assembly.startswith('@'):
            instr_type = 'A'
        else:
            instr_type = 'C'
        return instr_type

    def parse_a_instruction(self):
        """Parses an A instruction"""
        assembly = self.assembly[1:] # remove leading @ symbol
        try: # see if it's an integer
            val = int(assembly) # cast into an integer
            binary = bin(val)[2:].zfill(16) # generate the binary and fill to 16 digits

        except ValueError: # otherwise its a symbol, e.g. @sum
            # if it's not already in the symbol table, add an entry
            if assembly not in self.assembler.symbol_table.keys():
                current = self.assembler.current_address
                binary = bin(current)[2:].zfill(16)
                self.assembler.symbol_table[assembly] = current
                self.assembler.current_address += 1 # increment next address to be stored
            else: # otherwise just access the existing value and generate the binaryß
                val = self.assembler.symbol_table[assembly]
                binary = bin(val)[2:].zfill(16)

        return binary

    def parse_c_instruction(self):
        """Parses a C instruction"""
        line = self.assembly
        if '=' in line and ';' in line: #dest=comp;jump
            dest, temp = line.split('=') # split on = to get dest and comp/jump
            comp, jump = temp.split(';') # split on ; to get comp and jump
            # set dest, comp, jump
            self.dest = self.assembler.dest_table[dest]
            self.comp = self.assembler.comp_table[comp]
            self.jump = self.assembler.jump_table[jump]
        elif '=' in line and ';' not in line: # dest=comp
            dest, comp = line.split('=')
            # set dest, comp, jump
            self.dest = self.assembler.dest_table[dest]
            self.comp = self.assembler.comp_table[comp]
            self.jump = self.assembler.jump_table['null']
        elif '=' not in line and ';' in line: # comp;jump
            comp, jump = line.split(';')
            # set dest, comp, jump
            self.dest = self.assembler.dest_table['null']
            self.comp = self.assembler.comp_table[comp]
            self.jump = self.assembler.jump_table[jump]
        else: #otherwise it is a standalone comp
            comp = line
            # set dest, comp, jump
            self.dest = self.assembler.dest_table['null']
            self.comp = self.assembler.comp_table[comp]
            self.jump = self.assembler.jump_table['null']

        return '111' + self.comp + self.dest + self.jump

    def get_binary(self):
        """Parses assembly and returns machine binary"""
        if self.instruction_type == 'A':
            binary = self.parse_a_instruction()
        elif self.instruction_type == 'C':
            binary = self.parse_c_instruction()
        return binary

class Assembler:
    """Assembler class"""
    def __init__(self, in_file): # takes the cleaned file as an arg
        self.in_file = in_file # stores in_file filepath
        self.lines = self.get_lines() # strips out newline, stores in list
        self.clean = [] # for removing labels

        # store symbol table
        self.symbol_table = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
                             'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5,
                             'R6': 6, 'R7': 7, 'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11,
                             'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15, 'SCREEN': 16384,
                             'KBD': 24576}

        # store dest, comp, jump binary
        self.comp_table = {'0':'0101010', '1':'0111111', '-1':'0111010', 'D': '0001100',
                           'A':'0110000', '!D':'0001101', '!A': '0110001', '-D':'0001111',
                           '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
                           'A-1':'0110010', 'D+A': '0000010', 'D-A': '0010011', 'A-D': '0000111',
                           'D&A': '0000000', 'D|A': '0010101', 'M': '1110000', '!M': '1110001',
                           '-M': '1110011', 'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010',
                           'D-M': '1010011', 'M-D': '1000111', 'D&M': '1000000', 'D|M': '1010101'}

        self.dest_table = {'null':'000', 'M':'001', 'D':'010', 'MD':'011',
                           'A':'100', 'AM':'101', 'AD':'110','AMD':'111'}

        self.jump_table = {'null':'000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
                           'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}

        self.current_line = 0 # keep track of program line
        self.current_address = 16 # keep track of next available memory address
        self.final_output = {} # dictionary storing output {program_line : binary}
        self.first_pass() # take first pass to remove labels

    def get_lines(self):
        """Strip out newline from cleaned file, put lines in list"""
        with open(self.in_file) as f:
            clean = f.read().splitlines() # strips out newline character
        return clean

    def first_pass(self):
        """Remove any (label) references"""
        line_count = 0 # keep track of line
        for line in self.lines:
            # if a line is a (label), store it's position in the symbol table
            if line.startswith('(') and line.endswith(')'):
                self.symbol_table[line[1:-1]] = line_count
            else: # otherwise just add the line into the "clean" set of lines for 2nd pass
                self.clean.append(line)
                line_count += 1 # increment line count if it's not a label

    def generate_output(self):
        """Write .hack file with machine language"""
        # name output file <program>.hack and open file
        out_file = self.in_file.replace('_clean', '')
        out_file = out_file.replace('.asm', '.hack')
        out = open(out_file, 'w')

        # write each line of machine language
        for line in self.final_output.values():
            out.write(line+'\n') # add a newline back since we stripped out

def main():
    """Generate the .hack file"""
    assembler = Assembler(clean_file) # initialize an Assembler object

    # for each line of assembly, get the binary, store in {line:binary} dictionary
    for line in assembler.clean:
        instruction = Instruction(line, assembler) # create Instruction object
        assembler.final_output[assembler.current_line] = instruction.binary # set {line:binary}
        assembler.current_line += 1 # increment current program line

    # write results to .hack file
    assembler.generate_output()

if __name__ == '__main__':
    main()
