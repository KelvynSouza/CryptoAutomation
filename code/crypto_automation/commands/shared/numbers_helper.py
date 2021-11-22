import random


def random_waitable_number(config):
    return random.uniform(config['COMMON'].getfloat('random_waits_from'), config['COMMON'].getfloat('random_waits_to'))


def random_number_between(min, max):
    return random.uniform(min, max)