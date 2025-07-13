import base64
import datetime
import random
import traceback
import requests
from requests.auth import HTTPBasicAuth
import cloudpickle as pickle
import timeit

from .blackbox import Plackbox, Blackbox


class Client:
    def __init__(self, team_name, server=None, timeout=0.1):
        self.team_name = team_name
        if server:
            self.url = "https://" + server + ".ngrok-free.app"
        else:
            self.url = None
        self.timeout = timeout

    def test(self, source_or_function, verbose=False, strict=False, allow_state=True):
        return self._submit(source_or_function, strict=strict, submit=False, allow_state=allow_state, verbose=verbose)

    def submit(self, source_or_function, allow_state=True):
        return self._submit(source_or_function, strict=False, submit=True, allow_state=allow_state, verbose=False)
        
    def _submit(self, source_or_function, strict, submit, allow_state, verbose):
        if submit and not self.url:
            print('Automatic submission not enabled. Please send an email with your snippet to the organizers.')
            return
        test_cases = [
            ((1.5, 5, 1, 10, 1.3, [1.1, 2.3]), "generic inputs", None),
            ((-1.5, 5, 1, 10, 1.3, [1.1, 2.3]), "negative reward", (False, 'It never makes sense to take a negative reward')),
            ((0, 5, 1, 10, 1.3, [1.1, 2.3]), "zero rewards", (False, "It doesn't make sense to accept a lockout in return for no reward")),
            ((1.5, 5, 1, 10, 1.3, []), "playing by yourself", None),
            ((1.5, 5, 1, 10, -1, [-1.1, 2.3]), "negative score", None),
            ((0.0001, 5, 10, 10, 1.3, [1.1, 2.3]), "no time left after this round", (True, 'There is no time left after this round, you should accept any reward you can get')),
            ((0.0001, 0, 1, 10, 1.3, [1.1, 2.3]), "no lockout", (True, 'There is no lockout, you should accept any reward you can get')),
        ]
        if isinstance(source_or_function, str):
            output = source_or_function
            foo = Blackbox(output)
        else:
            output = pickle.dumps(source_or_function)
            foo = Plackbox(output)
        outputs = dict()
        for j in range(3):
            for i, (args, err, hint) in enumerate(test_cases):
                test_str = f'Test {i} ("{err}"): f{args}'
                if j == 0 and verbose:
                    print(test_str)
                    test_str = ''
                try:
                    a = foo(*args)
                    if j == 0:
                        outputs[i] = a
                    else:
                        if a != outputs[i] and not allow_state:
                            print(test_str)
                            raise Exception(f"""You previously returned `{outputs[i]}` and are now returning `{a}`. If this is intentional, set `allow_state=True`""")
                        elif not isinstance(a, bool):
                            print(test_str)
                            raise Exception(f"""You should return `False` or `True` but you returned `{a}` of type {type(a)}""")
                        elif strict and hint is not None and a != hint[0]:
                            print(test_str)
                            raise Exception(hint[1])
                except Exception:
                    print(test_str)
                    raise
                if j == 0 and verbose:
                    print(f'\tSuccess -- returned {a}')
        tic = timeit.default_timer()
        for j in range(1_000):
            T = int(1_000_000 * random.random())
            t = int(random.random() * T)
            lockout = int(10 * random.random())
            reward = 100 * random.random()
            score = reward * T * random.random()
            scores = [reward * T * random.random() for _ in range(10)]
            args = (reward, lockout, t, T,  score, scores)
            try:
                a = foo(*args)
            except Exception:
                print(f'Random input {args}')
                raise
            else:
                if not isinstance(a, bool):
                    print(f'Random input {args}')
                    raise Exception(f"""You should return `False` or `True` but returned `{a}` of type {type(a)}""")
            toc = timeit.default_timer()
            if toc - tic > max(1, (j + 1) * self.timeout):
                raise Exception(f"""Your code is too slow. Should take {self.timeout}s per round but took {(toc - tic) / (j + 1):.3f}s""")
        if submit:
            self.fancy_submit(source_or_function)
        else:
            print("All tests passed. You're ready to call `submit`\n")

    def fancy_submit(self, output):
        if isinstance(output, str):
            submission = 's' + base64.b64encode(output.encode('utf-8')).decode('utf-8')
        else:
            submission = 'p' + base64.b64encode(pickle.dumps(output)).decode('utf-8')
        j = {"team": self.team_name, 'time': str(datetime.datetime.now()), 'submission': submission}
        response = requests.post(
            self.url + '/receive',
            json=j,
            auth=HTTPBasicAuth("colabuser", "secretcolab"),
        )
        try:
            response.raise_for_status()
        except Exception:
            raise Exception("Couldn't connect to server. Please notify an organizer.")
        else:
            print('Submission successful: ', j['team'], j['time'])
