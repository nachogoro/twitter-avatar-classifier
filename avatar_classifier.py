from PIL import Image
import clparser
import numpy.linalg
import imageprocessor
import twitteroauth
import os.path
import pickle
import sys
import time
import twitter
import urllib

DEFAULT_CRED_FILE = '.twitter-credentials.db'
DEFAULT_DIRECTORY = 'twitter-avatars'

# Generate your own APP_KEY and APP_SECRET from Twitter's developer page and 
# add them here
APP_KEY = ''
APP_SECRET = ''

# Finds how similar two colors are (see http://www.compuphase.com/cmetric.htm)
def similarity(color1, color2):
    # Mean of red
    red_mean = (color1[0] + color2[0])/2
    red = color1[0] - color2[0]
    green = color1[1] - color2[1]
    blue = color1[2] - color2[2]
    return (((512+red_mean)*red*red)/256) + 4*green*green + (((767-red_mean)*blue*blue)/256)

# Converts a string representing a color in hex triplet format ('#123456') to RGB
def hexToIntColor(color):
    if color[0] == '#':
        color = color[1:]
    assert(len(color) == 6)
    return int(color[:2], 16), int(color[2:4], 16), int(color[4:6], 16)

# Loads a serialized object from a file
def loadFromFile(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

# Dumps an object into a file
def dumpObject(filename, object):
    with open(filename, 'wb') as f:
        pickle.dump(object, f)

# Sorts a dictionary by value, in ascending order
def sortDictionary(dictionary):
    return sorted(dictionary.items(), key=lambda x:x[1])

# Prints a progress bar with a resolution of 5%
# i is the number of 5% intervals that have passed
def printProgressBar(i):
    sys.stdout.write('\r')
    # the exact output you're looking for:
    sys.stdout.write("[%-20s] %d%%" % ('='*i, 5*i))
    sys.stdout.flush()
    time.sleep(0.25)


###############################################################################

def main(argv=sys.argv):
    # Parse the command string
    param = clparser.parse(argv)

    credFile = param.get('credentials')
    directory = param.get('directory')
    color = param.get('color')
    # Whether the avatars have been provided (True) or need to be downloaded (False)
    givenAvatars = True

    if credFile is None:
        credFile = DEFAULT_CRED_FILE
    if directory is None:
        directory = DEFAULT_DIRECTORY
        givenAvatars = False

    color = hexToIntColor(color)

    # Only connect to Twitter if the avatars have not been provided
    if givenAvatars == True:
        if not (os.path.isdir(directory) and os.listdir(directory)):
            print('ERROR: Could not find avatars in %s' % directory)
            sys.exit()
    else:
        # Create directory if it does not exist
        if os.path.isdir(directory) == False:
            os.mkdir(directory)
        twitterCredentials = None

        # Load Twitter credentials. If it fails, ask user for OAuth authentication
        try:
            twitterCredentials = loadFromFile(credFile)
        except Exception:
            pass

        # If no credentials have been loaded, ask the user about them
        if twitterCredentials is None:
            twitterCredentials = twitteroauth.getAccessToken()
            # Store them for future use
            dumpObject(DEFAULT_CRED_FILE, twitterCredentials)

        api = twitter.Api(APP_KEY,
                          APP_SECRET,
                          twitterCredentials['oauth_token'],
                          twitterCredentials['oauth_token_secret'])

        thisUser = api.VerifyCredentials()
        print('Authenticated as @%s' % thisUser.screen_name)

        # Get all users one follows
        usersID = api.GetFriendIDs()

        numElems = len(usersID)
        fivePercent = int(numElems/20)+1
        # Number of seconds to wait between API calls so that the rate limit is not exceeded
        sleepingSeconds = api.GetAverageSleepTime('users/lookup')

        print('Downloading user avatars:')
        for x in range(numElems):
            userID = usersID[x]
            user = api.GetUser(userID)
            if x%fivePercent == 0:
                printProgressBar(int(x/fivePercent))
            # Parse URL
            profile_image = user.profile_image_url.rsplit('normal', 1)
            profile_image = 'bigger'.join(profile_image)
            # Download and save avatar for this user
            urllib.urlretrieve(profile_image, directory+'/'+user.screen_name+'.jpg')
            time.sleep(sleepingSeconds)
        # Print 100% (to make up for the poor approximation)
        printProgressBar(20)
        print

    # Process each image and store its distance as an entry in distance dictionary
    distance={}
    usernames = os.listdir(directory)
    numElems = len(usernames)
    fivePercent = int(numElems/20)+1
    print('Processing user avatars:')
    for x in range(numElems):
        username = usernames[x]
        if x%fivePercent == 0:
            printProgressBar(int(x/fivePercent))
        predominantColor = imageprocessor.getPredominantColor(directory+'/'+username)
        distance[username.replace('.jpg','')] = similarity(predominantColor, color)
    # Print 100% (to make up for the poor approximation)
    printProgressBar(20)

    print
    # Print to screen
    sorted_dict = sortDictionary(distance)
    # Only the first 20 users
    if numElems > 20:
        numElems = 20
    sorted_dict = sorted_dict[:numElems]
    print('Users sorted by how %s their avatar is:' % param.get('color'))
    for x in sorted_dict:
        print("@" + x[0])

if __name__ == "__main__":
    main()
