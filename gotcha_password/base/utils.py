from django.utils.crypto import get_random_string, pbkdf2

import random, base64, os
from hashlib import sha224
from itertools import chain, combinations, product

ACCURACY_THRESHOLD = 2
HASH_ITERATIONS = 24000
SVG_WIDTH = 300
SVG_HEIGHT = 300

def get_random_seed():
    """
    Returns a random 12-character string (71 bits, alphanumeric characters)
    """
    return get_random_string()

def make_password(raw_password, labels):
    salt = get_random_seed()
    permutation = range(len(labels))
    random.SystemRandom().shuffle(permutation)

    # password = hash_password(raw_password, salt, permutation)
    password = hash_once(raw_password, salt)
    return password, salt, permutation

def hash_password(raw_password, salt, permutation, iterations=HASH_ITERATIONS):
    """
    Hash data of the form "<raw_password>$<comma sep permutations>"
    """
    permutation = ','.join(map(str, permutation))
    password = '%s$%s' % (raw_password, permutation)
    hashed = pbkdf2(password, salt, iterations)
    return base64.b64encode(hashed).decode('ascii').strip()

def hash_once(raw_password, salt):
    """
    Hash the given password once, for purposes of storing into database
    """
    hashed = pbkdf2(raw_password, salt, 1)
    return base64.b64encode(hashed).decode('ascii').strip()

def list_permutations(permutation, threshold=ACCURACY_THRESHOLD):
    """
    Generate all permutations that differ from the given permutation by ACCURACY_THRESHOLD.

    Source: http://codereview.stackexchange.com/a/88919
    """
    num_images = len(permutation)
    threshold = min(threshold, num_images)

    def _list_permutations(diff):
        # diff-length tuples representing the indices to modify
        for positions in combinations(range(num_images), diff):
            # the values to change with those positions; using all except last
            # value to only use the last value on repetitions
            for values in product(range(num_images - 1), repeat=diff):
                cousin = list(permutation)
                for i, v in zip(positions, values):
                    cousin[i] = v if cousin[i] != v else num_images - 1
                # only return if no duplicates
                if len(set(cousin)) == len(cousin):
                    yield cousin

    return chain.from_iterable(_list_permutations(i) for i in range(threshold + 1))

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
        random_ellipses(image, 30, 35, 35)
        random_ellipses(image, 20, 15, 15)
        random_ellipses(image, 30, 35, 15)
        images.append(image)

    # re-randomize seed
    random.seed(os.urandom(20))

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

def extract_labels(data):
    """
    Extract labels from the data mapping keys of the form "label-<num>" to any
    arbitrary value. Orders the resulting list on <num> and returns just the values.
    """
    labels = [
        (int(name[6:]), val)
        for name, val in data.items()
        if name.startswith('label-')
    ]
    return [val for _, val in sorted(labels, key=lambda (i, _): i)]
