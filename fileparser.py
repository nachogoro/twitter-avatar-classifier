# Retrieves the colors defined in a file
# Throws ValueError if something goes wrong
def getColors(filename):
    colors = {}
    with open(filename, 'rb') as f:
        # Read the whole file line by line and parse it
        content = f.readlines()
        for line in content:
            words = line.split()
            if len(words) != 4:
                raise ValueError('Invalid line %s in %s' % (line, filename))
        colors[words[0]] = (int(words[1]), int(words[2]), int(words[3]))
        return colors