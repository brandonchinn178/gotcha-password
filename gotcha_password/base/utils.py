from django.utils.crypto import get_random_string, pbkdf2

import random, base64
from os import urandom
from hashlib import sha224

ACCURACY_THRESHOLD = 2
HASH_ITERATIONS = 24000
SVG_WIDTH = 300
SVG_HEIGHT = 300

def get_random_seed():
    """
    Returns a random 12-character string (71 bits, alphanumeric characters)
    """
    return get_random_string()

def hash_password(raw_password, salt, permutation, iterations=HASH_ITERATIONS):
    """
    Hash data of the form "<raw_password>$<comma sep permutations>"
    """
    password = '%s$%s' % (raw_password, ','.join(map(str, permutation)))
    hashed = pbkdf2(password, salt, iterations)
    hashed = base64.b64encode(hashed).decode('ascii').strip()
    return '%s$%s' % (salt, hashed)

def list_permutations(permutation, max_val, threshold=ACCURACY_THRESHOLD):
    """
    Generate all permutations that differ from the given permutation by ACCURACY_THRESHOLD,
    where the items in the permutation can be anything in the range [0, max_val)
    """
    pass

def extract(pw, seed):
    """
    Returns a deterministic random seed generated from the given password and seed.
    """
    digest = sha224('%s$%s' % (pw, seed)).hexdigest()
    return long(digest, 16) % 2**16

def generate_images(num_images, seed):
    """
    Return a list of dictionaries containing the data for each ellipse
    """
    images = []
    random.seed(seed)

    for _ in range(num_images):
        image = []
        random_ellipses(image, 65, 30, 30)
        random_ellipses(image, 25, 15, 15)
        random_ellipses(image, 65, 30, 15)
        images.append(image)

    # re-randomize seed
    random.seed(urandom(20))

    return images

def random_ellipses(image, n, width, height):
    """
    Add n ellipses to the given image of the specified width and height, randomizing
    the coordinates, color, and rotation.
    """
    is_rotate = width != height
    data = {
        'width': width/2,
        'height': height/2,
        'is_rotate': is_rotate,
    }

    for _ in range(n):
        data1 = data.copy()
        data1['x'] = random.random() * SVG_WIDTH/2
        data1['y'] = random.random() * SVG_HEIGHT
        data1['color'] = '#%06x' % random.randint(0, 0xFFFFFF)

        # mirrored ellipse
        data2 = data1.copy()
        data2['x'] = SVG_WIDTH - data2['x']

        if is_rotate:
            data1['rotation'] = random.random() * 180
            data2['rotation'] = -data1['rotation']

        image.extend([data1, data2])
