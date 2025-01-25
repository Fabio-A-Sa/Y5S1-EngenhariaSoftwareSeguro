from time import time
from random import SystemRandom

r = SystemRandom()

def create_nonce():
    seconds_section = str(int(time()))
    random_section = r.randrange(0, 1000)
    return f"{seconds_section}{random_section:03}"
