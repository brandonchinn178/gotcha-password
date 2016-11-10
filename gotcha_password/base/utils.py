from django.utils.crypto import get_random_string

from random import SystemRandom
from hashlib import sha224

ACCURACY_THRESHOLD = 2
HASH_ITERATIONS = 24000

def get_random_seed():
    """
    Returns a random 71 bit seed (string with 12 alphanumeric characters)
    """
    return get_random_string()

def extract(pw, seed):
    """
    Returns a deterministic random seed generated from the given password and seed.
    """
    digest = sha224('%s$%s' % (pw, seed)).hexdigest()
    return long(digest, 16) % 2**16

def list_permutations(permutation, max_val):
    """
    Generate all permutations that differ from the given permutation by ACCURACY_THRESHOLD,
    where the items in the permutation can be anything in the range [0, max_val)
    """
    pass
