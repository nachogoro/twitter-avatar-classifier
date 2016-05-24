import getopt
import sys


# A parser for the command line
# Parses the command line and returns a dictionary with the parameters.
def parse(args):
    parameters = {}
    name = args[0]
    del args[0]

    # Get the options and arguments
    try:
        optlist, args = getopt.getopt(args,'hd:c:l:',['credentials=','directory=','color=','help'])
    except getopt.GetoptError:
        printUsage(name)
        sys.exit(2)

    for opt,arg in optlist:
        if opt in ('-h', '--help'):
            printUsage(name)
            sys.exit()
        elif opt in ('-l', '--credentials'):
            parameters['credentials'] = arg
        elif opt in ('-d', '--directory'):
            parameters['directory'] = arg
        elif opt in ('-c', '--color'):
            parameters['color'] = arg
        else:
            # Unhandled parameter
            printUsage(name)
            sys.exit()

    if parameters.get('color') is None:
        # If there is no color specified
        printUsage(name)
        sys.exit()
    return parameters


def printUsage(name):
    print("Connects to a user's account, downloads the avatars of the people they follow to twitter-avatars directory "+
        "and classifies them according to how similar they are to a given color.")
    print("If a user authenticates to use the app, its credentials are stored in .twitter-credentials.db")
    print
    print('Usage:')
    print('\t%s [options] --color COLOR' % name)
    print
    print('Options:')
    print('-l, --credentials: a file storing the Twitter credentials for a user. If found, these are loaded automatically')
    print('\tDefault value: .twitter-credentials.db')
    print
    print('-d, --directory: a directory where all the avatars have previously been downloaded')
    print('\tIf this is set, there is no attempt to connect to Twitter, so no avatars are downloaded')
    print
    print('-c, --color: mandatory argument. It indicates the color according to which the avatars should be classified.')
    print('\tIt must be in the hex triplet format (between quotes).')
    print('\tUse online resources such as http://www.colorhexa.com/color-names to get the hex value of a color.')
    print
    print('-h, --help: prints this message')
    print
    print('Example:')
    print('\t%s -d twitter-avatars -c \'#ff55a3\'' % name)
    print('Classifies the avatars at twitter-avatars directory according to how "Bright Pink" they are')
    print
    print('Example:')
    print('\t%s -l .twitter-credentials.db -c \'#ff2800\'' % name)
    print('Uses the credentials stored at twitter-credentials.db to download the avatars which will be classified according to how "Ferrari Red" they are')