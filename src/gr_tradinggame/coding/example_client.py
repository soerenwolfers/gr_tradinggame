from gr_tradinggame.coding.client import Client

server = '28ca-45-80-244-212'

client = Client('Team A', server=server)

import random
def foo(reward: float, lockout: int, t: int, T: int, your_score: float, other_scores: list[float]):
    return random.random() > 0.5
client.test(foo)
client.test(foo, allow_state=True)

client.submit(foo, allow_state=True)

client = Client('Team B', server=server)

def foo(reward: float, lockout: int, t: int, T: int, your_score: float, other_scores: list[float]):
    threshold = -0.1
    if lockout <= 0:
        threshold = 0
    if t >= T:
        threshold = 0
    return reward > threshold
client.test(foo)
client.test(foo, strict=True)

def foo(reward: float, lockout: int, t: int, T: int, your_score: float, other_scores: list[float]):
    threshold = 0.1
    if lockout <= 0:
        threshold = 0
    if t >= T:
        threshold = 0
    return reward > threshold
client.test(foo, strict=True)

client.submit(foo)

client = Client('Team C', server=server)

client.submit('''
import time; 
def play(*args): time.sleep(0.1); return True
''', allow_state=True)

client.submit('''def play(*args): return True''', allow_state=True)

client = Client('Team D', server=server)

client.submit(foo)

def foo(reward: float, lockout: int, t: int, T: int, your_score: float, other_scores: list[float]):
    threshold = 0.2
    if lockout <= 0:
        threshold = 0
    if t >= T:
        threshold = 0
    return reward > threshold
client.submit(foo)
