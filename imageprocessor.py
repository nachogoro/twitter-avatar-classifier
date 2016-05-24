import struct
from PIL import Image
import scipy
import scipy.misc
import scipy.cluster

NUM_CLUSTERS = 5

def getPredominantColor(filename):
    im = Image.open(filename).convert('RGB')

    # Convert to numpy array
    ar = scipy.misc.fromimage(im)

    # Get dimensions
    shape = ar.shape

    # Convert to bidimensional array of width x height rows and 3 columns (RGB)
    ar = ar.reshape(scipy.product(shape[:2]), shape[2])

    # Find cluster centers and their distortions
    # codes contains the RGB value of the centers
    codes, dist = scipy.cluster.vq.kmeans(ar.astype(float), NUM_CLUSTERS)

    # Maps all the pixels in the image to their respective centers
    vecs, dist = scipy.cluster.vq.vq(ar, codes)

    # Counts the occurances of each color (NUM_CLUSTER different colors after the mapping)
    counts, bins = scipy.histogram(vecs, len(codes))

    # Find most frequent color
    index_max = scipy.argmax(counts)
    peak = codes[index_max]

    return peak.astype(int)