import os
import struct
import sys
import time


def writeTo(filename, position, content):
    fh = open(filename, "r+b")
    fh.seek(position)
    fh.write(content)
    fh.close()


def main(f0, f1):
    boneNames1, SRT_1 = ReadCSV(f1)

    numBones0 = []
    boneNames0 = []
    pointerBones_0 = []
    SRT_0 = []
    pointerModel_0 = ModelPointer(f0, 0)
    numModels0 = ModelAmount(f0, pointerModel_0)
    for i in range(numModels0):
        numBones0.append(inModelReader(f0, pointerModel_0, i)[0])
        pointerBones_0.append(inModelReader(f0, pointerModel_0, i)[1])
        boneNames0.append(boneRead(f0, pointerBones_0[i], numBones0[i],
                                   boneNames0))
        SRT_0.append([SRTRead(f0, pointerBones_0[i], numBones0[i])])

    print(boneNames0)
    print()
    print("Do you want to select individual skeletons to read data from?"
          " (y/n)")
    yn = input()

    if(yn == "y"):
        print("Copy over this skeleton (bone collection)? (y/n)")
        yn0 = input()
        if(yn0 == "y"):
            print("Do you want to select individual bones?")
            print("This can be tedious. (y/n)")
            yn1 = input()
            skeletonSelection(numModels0, boneNames0, boneNames1, SRT_1,
                              pointerModel_0, f0, yn1)
    elif(yn == "n"):
        skeletonSelection(numModels0, boneNames0, boneNames1, SRT_1,
                          pointerModel_0, f0, "n")
    print("Done! Maybe it even worked.")


def skeletonSelection(numModels0, boneNames0, boneNames1, SRT_1,
                      pointerModel_0, f0, yn1):
    for m in range(len(boneNames1)):
        boneSelection(m, numModels0, boneNames0, boneNames1, SRT_1,
                      pointerModel_0, f0, yn1)


def boneSelection(m, numModels0, boneNames0, boneNames1, SRT_1, pointerModel_0,
                  f0, yn1):
    for s in range(numModels0):
        if(boneNames1[m] in boneNames0[s]):
            if(yn1 == "y"):
                print("Match this bone? -> " + boneNames1[m] + " (y/n)")
                yn2 = input()
                if(yn2 == "y"):
                    boneSelection1(m, s, numModels0, boneNames0, boneNames1,
                                   SRT_1, pointerModel_0, f0)
                elif(yn2 == "n"):
                    print("Skipped.")
                else:
                    print("Invalid response!")
                    break
            elif(yn1 == "n"):
                boneSelection1(m, s, numModels0, boneNames0, boneNames1, SRT_1,
                               pointerModel_0, f0)
            else:
                print("Invalid response!")
                break


def boneSelection1(m, s, numModels0, boneNames0, boneNames1, SRT_1, pointerModel_0, f0):
    with open(f0, 'rb') as f:
        p = boneNames0[s].index(boneNames1[m])
        for q in range(10):
            mPos = 0
            bone = float(SRT_1[m][q])
            content = struct.pack(">f", bone)
            mPos = SRTpointer(f0, inModelReader(f0, pointerModel_0, s)[1]) + ((p+1) * 16) + 8 + 12
            f.seek(mPos)
            mPos = f.tell() + struct.unpack(">l", f.read(4))[0] + 20 + q * 4
            writeTo(f0, mPos, content)
    print("Matched " + boneNames1[m] + ".")


def boneRead(filename, tempPos, number_of_bones, bone_names):
    with open(filename, 'rb') as f:
        bone_names = []
        for j in range(1, number_of_bones + 1):
            mPos = 0
            mPos = tempPos + 8
            f.seek(mPos)
            ofsBoneDict = struct.unpack(">l", f.read(4))[0]
            mPos += ofsBoneDict + (j * 16) + 16
            f.seek(mPos)
            ofsKey = struct.unpack(">l", f.read(4))[0]
            mPos += ofsKey - 4
            f.seek(mPos)
            lenName = int(struct.unpack(">l", f.read(4))[0])
            name = ""
            for k in range(1, lenName+1):
                name += str(struct.unpack(">s", f.read(1))[0])
                name = name.replace("b", "", 1).replace("'", "")
            bone_names.append(name)
        return bone_names


def SRTRead(filename, tempPos, number_of_bones):
    with open(filename, 'rb') as f:
        SRT = []
        for j in range(number_of_bones):
            mPos = SRTpointer(filename, tempPos)
            mPos += (j * 64) + 20
            f.seek(mPos)
            Sx = struct.unpack(">f", f.read(4))[0]
            Sy = struct.unpack(">f", f.read(4))[0]
            Sz = struct.unpack(">f", f.read(4))[0]
            Rx = struct.unpack(">f", f.read(4))[0]
            Ry = struct.unpack(">f", f.read(4))[0]
            Rz = struct.unpack(">f", f.read(4))[0]
            Rw = struct.unpack(">f", f.read(4))[0]
            Tx = struct.unpack(">f", f.read(4))[0]
            Ty = struct.unpack(">f", f.read(4))[0]
            Tz = struct.unpack(">f", f.read(4))[0]
            SRT.append([Sx, Sy, Sz, Rx, Ry, Rz, Rw, Tx, Ty, Tz])
        return SRT


def SRTpointer(filename, tempPos):
    with open(filename, 'rb') as f:
        mPos = 0
        mPos = tempPos + 8
        f.seek(mPos)
        ofsBoneDict = struct.unpack(">l", f.read(4))[0]
        mPos += ofsBoneDict
        return mPos


def ModelPointer(filename, nameSRTpack, content=0, r=0):
    with open(filename, 'rb') as f:
        f.seek(32)
        ofsModelDict = struct.unpack(">l", f.read(4))[0]
        pointer = 32 + ofsModelDict
        f.seek(pointer)
        modelSize = struct.unpack(">l", f.read(4))[0]
        pointer += 4
        return pointer


def ModelAmount(filename, pointer):
    with open(filename, 'rb') as f:
        f.seek(pointer)
        number_Models = struct.unpack(">l", f.read(4))[0]
        return number_Models


def inModelReader(filename, pointer, i):
    with open(filename, 'rb') as f:
        pointer += 4
        Mpointer = 0
        Mpointer = pointer + ((i+1) * 16) + 12
        f.seek(Mpointer)
        ofsData = struct.unpack(">l", f.read(4))[0]
        Mpointer += ofsData + 12
        f.seek(Mpointer)
        ofsSkeleton = struct.unpack(">l", f.read(4))[0]
        Mpointer += ofsSkeleton + 8
        f.seek(Mpointer)
        numBone = struct.unpack(">h", f.read(2))[0]
    return numBone, Mpointer


def ReadCSV(filename):
    boneNames = []
    SRT = []
    Type = 0
    SubType = 0
    Temp = []
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("Bones Geometry"):
                Type = 1
                SubType = 0
            else:
                line = line.replace("\n", "").replace("\r", "").split(",")
                if Type == 1:
                    if SubType == 0:
                        boneNames.extend(line)
                        SubType += 1
                    elif SubType < 4:
                        Temp.extend((float(x) for x in line))
                        SubType += 1
                        if SubType == 4:
                            SRT.append(Temp)
                            SubType = 0
                            Temp = []

    return boneNames, SRT


if __name__ == "__main__":
    print("")
    print("")
    print("Bone Matching Program by Mystixor, much credits to zephenryus for"
          " excellent explanations!")
    if len(sys.argv) < 3:
        print('Insufficient arguments. Please supply a bfres file and a csv'
              ' file when using this tool.')
        exit()
    if len(sys.argv) > 3:
        print('Insufficient arguments. Please supply a bfres file and a csv'
              ' file when using this tool.')
        exit()
    else:
        filenames = []
        file = sys.argv[1]
        filenames.append(file)
        with open(file, 'rb') as f:
            p1 = struct.unpack(">s", f.read(1))[0]
            p2 = struct.unpack(">s", f.read(1))[0]
            p3 = struct.unpack(">s", f.read(1))[0]
            p4 = struct.unpack(">s", f.read(1))[0]
            word = str(p1+p2+p3+p4)
            word = word.replace("b", "").replace("'", "")
            if word == "Yaz0":
                print("Error 1: Encoded File Detected")
                print("File Name: {}".format(sys.argv[i].rsplit("\\", 2)[-1]))
                print("This file has not been decoded yet. Please use"
                      " BOTW-Yaz0 or Yaz0dec before using this tool.")
                print("Continuing in 5 seconds...")
                time.sleep(5)
            elif word != "FRES":
                print("Error 2: Unusual Filetype detected")
                print("File Name: {}".format(sys.argv[i].rsplit("\\", 2)[-1]))
                print('File is the wrong format. Format Given : ' + str(word))
                print("Continuing in 5 seconds...")
                time.sleep(5)
            else:
                print("Put Bones into: {}".format(file.rsplit("\\", 2)[-1]))
        file = sys.argv[2]
        filenames.append(file)
        if file.lower().find('csv') == -1:
            print("Error: Unusual Filetype detected")
            print("File Name: {}".format(file))
            print("File is in the wrong format, should be .csv")
            print("Continuing in 5 seconds...")
            time.sleep(5)
        else:
            print("Load Bones from: {}".format(file.rsplit("\\", 2)[-1]))
    print("Files accepted! The following can take a while due to Bone"
          "matching.")
    main(filenames[0], filenames[1])
