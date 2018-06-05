# Aaaboy97 2018


from sys import argv

orig = open(argv[1])
if argv[1] != 'output.csv':
    new_name = 'output.csv'
else:
    new_name = 'output2.csv'
new = open(new_name, 'w')

beg = str(input('Would you like to sort to the beginning or end? (b/e): '))
beg = beg.lower()
while beg != 'b' and beg != 'e':
    beg = str(input('Please enter either \'b\' or \'e\': '))
    beg = beg.lower()

beg = (beg == 'b')

bone = beg and 'beginning' or 'end'
bone = str(input('Enter the weight to be moved to the ' + bone +
                 ' (case sensitive): '))
bones = []
while bone != 'n':
    bones.append(bone)
    bone = str(input('Any more weights (or type \'n\' to stop)?: '))

for line in orig:
    new_line = line.replace('\n', '')
    for bone in bones:
        temp_line = new_line.replace(' ', '')
        weight_ind = temp_line.find(bone + ',')
        next_com_ind = temp_line.find(',', weight_ind + len(bone) + 2)

        if beg and weight_ind != -1 and weight_ind != 0:
            new_line = temp_line[weight_ind:next_com_ind + 1] + \
                       temp_line[:weight_ind] + \
                       temp_line[next_com_ind + 1:] + ' '
        elif (not(beg) and weight_ind != -1 and
              next_com_ind != len(temp_line) - 1):
            new_line = temp_line[:weight_ind] + \
                       temp_line[next_com_ind + 1:] + \
                       temp_line[weight_ind:next_com_ind + 1] + ' '

    new.write(new_line + '\n')

orig.close()
new.close()
print('New file was successfully saved to ' + new_name)
