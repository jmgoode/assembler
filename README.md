About
-----
This program was written in Python 3.
It takes in assembly language (.asm) and outputs corresponding binary machine code (.hack)

To Run Program:
---------------

./assembler.py [filepath.asm]

Notes
-----
- assembler.py should be permissioned to run as an executable. Just in case it doesn't work, run <chmod u+x assembler.py>
- You must specify a valid .asm file paths as the first argument; otherwise the program will not run
- The program will output results to a .hack file with the same name as the .asm, located the same directory
- I tested by comparing my program's .hack output to the official Hack Assembler Output for a given .asm
- I imported parser.py as a module to my main program since I had already made it a few weeks ago
- Code has been tested on Linux and OSX without error
