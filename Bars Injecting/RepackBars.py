# Aaaboy97 2018


import os
import shutil
import sys

if len(sys.argv) != 4:
    print('Incorrect arguments for running')
    print('Usage: bars_repack.py <bars file> <original folder> <new folder>')
    exit()

shutil.copy2(sys.argv[1], 'output.bars')
new = open('output.bars', 'r+b')
full = new.read()

for file in os.listdir(sys.argv[2]):
    sound = open(sys.argv[2] + '\\' + file, 'rb')
    orig = sound.read()
    sound.close()

    try:
        sound2 = open(sys.argv[3] + '\\' + file, 'rb')
        repl = sound2.read()
        sound2.close()
    except:
        print('No new file for ' + file + ', skipping...')
        continue

    if len(orig) > len(repl):
        repl = repl + b'\x00'*(len(orig) - len(repl))
    elif len(orig) < len(repl):
        print('New file ' + file + ' larger than original, skipping...')
        continue

    offset = full.find(orig)
    if offset != -1:
        new.seek(full.find(orig))
        new.write(repl)
        print(file + ' was succesfully written')
    else:
        print(file + ' was not found in original bars, skipping...')

new.close()
print('Succesfully written to output.bars')
