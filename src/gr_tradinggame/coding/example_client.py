from gr_tradinggame.coding.client import Client

server = '52bc-34-16-234-11'


client = Client('Team A', server=server)


def foo(reward: float, lockout: int, t: int, T: int, your_score: float, other_scores: list[float]):
    #z = 1 / lockout
    #z = 1 / remaining_rounds
    #z = other_scores[0]
    #return random.random() > 0.5
    threshold = 0.1
    if lockout <= 0:
        threshold = 0
    if t >= T:
        threshold = 0
    #return 1
    return reward > threshold
client.submit(foo)


client = Client('Team B', threshold=0.1, server=server)

def foo(reward: float, lockout: int, t: int, T: int, your_score: float, other_scores: list[float]):
    #z = 1 / lockout
    #z = 1 / remaining_rounds
    #z = other_scores[0]
    #return random.random() > 0.5
    threshold = 100
    if lockout <= 0:
        threshold = 0
    if t >= T:
        threshold = 0
    #return 1
    return reward > threshold

client.submit(foo)
