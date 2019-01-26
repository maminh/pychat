import random
from string import ascii_letters, digits


def random_name(size=32):
    chars = ascii_letters + digits
    return ''.join(random.choice(chars) for _ in range(size))
