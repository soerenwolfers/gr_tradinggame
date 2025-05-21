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
    def __init__(self, team_name, server=None, threshold=0.1):
        self.team_name = team_name
        self.url = "https://" + server + ".ngrok-free.app"
        self.threshold = threshold

    def test(self, source_or_function, verbose=False, hints=False, allow_state=False):
        return self._submit(source_or_function, hints=hints, submit=False, allow_state=allow_state, verbose=verbose)

    def submit(self, source_or_function, allow_state=False):
        return self._submit(source_or_function, hints=False, submit=True, allow_state=allow_state, verbose=False)
        
    def _submit(self, source_or_function, hints, submit, allow_state, verbose):
        if submit and not self.url:
           print('Automatic submission not enabled. Please send an email with your snippet to the organizers.')
           return
        success = True
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
        for i, (args, err, hint) in enumerate(test_cases):
            try:
                a = foo(*args)
                if i not in outputs:
                    outputs[i] = a
                if i == 0 and verbose:
                    print(f'Output on input {args} ("{err}"): {a}')
                if a != outputs[i] and not allow_state:
                        success = False
                        print(f'Error on input {args} ("{err}")')
                        print(f'\tYou previously returned `{outputs[i]}` and are now returning `{a}`')
                        print(f"\tIf this is intentional, set `allow_state=True`")
                elif not isinstance(a, bool):
                    success = False
                    print(f'Error on input {args} ("{err}")')
                    print(f'\tYou should return `False` or `True` but you returned `{a}` of type {type(a)}')
                elif hints and hint is not None and a != hint[0]:
                    success = False
                    print(f'Warning on input {args} ("{err}")')
                    print(f'\t{hint[1]}')
                
            except Exception as e:
                success = False
                print(f'Error on input {args} ("{err}")')
                tb = e.__traceback__.tb_next
                stack = ''.join(['\t' + x for x in traceback.format_exception(type(e), e, tb)])
                print(stack)
        if not success:
            return
        tic = timeit.default_timer()
        for j in range(1_000):
            T = int(1_000_000 * random.random())
            t = int(random.random() * T)
            cooldown = int(10 * random.random())
            reward = 100 * random.random()
            score = reward * T * random.random()
            scores = [reward * T * random.random() for _ in range(10)]
            args = (reward, cooldown, t, T,  score, scores)
            try:
                a = foo(*args)
            except Exception as e:
                success = False
                print(f'Error on input {args}')
                tb = e.__traceback__.tb_next
                stack = ''.join(['\t' + x for x in traceback.format_exception(type(e), e, tb)])
                print(stack)
            else:
                if not isinstance(a, bool):
                    success = False
                    print(f'Error on input {args}')
                    print(f'\tYou should return `False` or `True` but returned `{a}` of type {type(a)}')
            if not success:
                return    
        toc = timeit.default_timer()
        if toc - tic > self.threshold:
            print(f'Error: Your code is too slow. Should finish in {self.threshold}s but took {toc - tic:.2f}s')
            return
        if success:
            if submit:
                self.fancy_submit(source_or_function)
            else:
                print("All tests passed. You're ready to call `submit`\n")

    def fancy_submit(self, output):
        if isinstance(output, str):
          submission = 's' + output
        else:
          submission = 'p' + base64.b64encode(pickle.dumps(output)).decode('utf-8')
        j = {"team": self.team_name, 'time': str(datetime.datetime.now()), 'submission': submission}
        response = requests.post(
            self.url + '/receive',
            json=j,
            auth=HTTPBasicAuth("colabuser", "secretcolab"),
        )
        response.raise_for_status()
        print('Submission successful: ', j['team'], j['time'])
