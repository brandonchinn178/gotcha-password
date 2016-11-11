from django.utils.crypto import get_random_string, pbkdf2

from random import SystemRandom
from hashlib import sha224

ACCURACY_THRESHOLD = 2
HASH_ITERATIONS = 24000

def get_random_seed():
    """
    Returns a random 12-character string (71 bits, alphanumeric characters)
    """
    return get_random_string()

def extract(pw, seed):
    """
    Returns a deterministic random seed generated from the given password and seed.
    """
    digest = sha224('%s$%s' % (pw, seed)).hexdigest()
    return long(digest, 16) % 2**16

def hash_password(raw_password, salt, permutation, iterations=HASH_ITERATIONS):
    """
    Hash data of the form "<raw_password>$<comma sep permutations>"
    """
    password = '%s$%s' % (raw_password, ','.join(permutation))
    hashed = pbkdf2(password, salt, iterations)
    return '%s$%s' % (salt, hashed)

def list_permutations(permutation, max_val, threshold=ACCURACY_THRESHOLD):
    """
    Generate all permutations that differ from the given permutation by ACCURACY_THRESHOLD,
    where the items in the permutation can be anything in the range [0, max_val)
    """
    pass
