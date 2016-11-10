from random import SystemRandom
from hashlib import sha224

def get_random_seed():
    """
    Returns a random 16 bit seed
    """
    return SystemRandom().getrandbits(16)

def extract(pw, seed):
    """
    Returns a deterministic random number generated from the given password and seed.
    """
    digest = sha224('%s$%s' % (pw, seed)).hexdigest()
    return long(digest, 16) % 2**16
