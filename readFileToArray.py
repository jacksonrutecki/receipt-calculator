def readFileToArray(filename):
    stringArray = []
    with open(filename) as f:
        for line in f.readlines():
            stringArray.append(line.replace("\n", ""))
    return stringArray