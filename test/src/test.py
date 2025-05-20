class Blackbox:
    def __init__(self, source, name):
        import io
        self.name = name
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        from IPython.terminal.interactiveshell import TerminalInteractiveShell
        self.shell = TerminalInteractiveShell()
        with redirect_stderr(self.stderr), redirect_stdout(self.stdout):
            out = self.shell.run_cell(source)
            if out.error_before_exec is not None:
                raise exec_result.error_before_exec 
            if out.error_in_exec is not None:
                raise exec_result.error_in_exec
        if not isinstance(name, str) or name not in self.shell.user_ns:
            raise Exception(f"Your source code must define a function called `{name}`, but only has `{self.shell.user_ns.keys()}`")
    def __call__(self, *args, **kwargs):
        input_variable_name = '__magic_input__'
        with redirect_stderr(self.stderr), redirect_stdout(self.stdout):
            self.shell.user_ns[input_variable_name] = args, kwargs
            out = self.shell.run_cell(f'{self.name}(*{input_variable_name}[0], **{input_variable_name}[1])')
            if out.error_before_exec is not None:
                raise exec_result.error_before_exec 
            if out.error_in_exec is not None:
                raise exec_result.error_in_exec
            return out.result

import traceback
def test(source_or_function, hints=False):
    success = True
    test_cases = [
        ((1.5, 5, 1, 10, 1.3, [1.1, 2.3]), "generic inputs", None),
        ((-1.5, 5, 1, 10, 1.3, [1.1, 2.3]), "negative reward", (False, 'It never makes sense to take a negative reward')),
        ((0, 5, 1, 10, 1.3, [1.1, 2.3]), "zero rewards", (False, "It doesn't make sense to accept a lockout in return for no reward")),
        ((1.5, 5, 1, 10, 1.3, []), "playing by yourself", None), # empty other scores -- don't fail
        ((1.5, 5, 1, 10, -1, [-1.1, 2.3]), "negative score", None), # negative myscore -- don't fail
        ((0.0001, 5, 10, 10, 1.3, [1.1, 2.3]), "no time left after this round", (True, 'There is no time left after this round, you should accept any reward you can get')),
        ((0.0001, 0, 1, 10, 1.3, [1.1, 2.3]), "no lockout", (True, 'There is no lockout, you should accept any reward you can get')),
    ]
    if isinstance(source_or_function, str):
        allow_state = True
        foo = Blackbox(source_or_function, 'play')
    else:
        allow_state = False
        foo = source_or_function
    outputs = dict()
    for j in range(2):
        for i, (args, err, hint) in enumerate(test_cases):
            try:
                a = foo(*args)
                if i not in outputs:
                    outputs[i] = a
                if a != outputs[i] and not allow_state:
                        success = False
                        print(f'Error on input {args} ("{err}")')
                        print(f'\tYou previously returned `{outputs[i]}` and are now returning `{a}`')
                        print(f"\tIf this is intentional, please submit the source code of your entire submission rather than the function object")
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
                tb = e.__traceback__.tb_next  # Skip one frame
                stack = ''.join(['\t' + x for x in traceback.format_exception(type(e), e, tb)])
                print(stack)
            
    if success:
        print("# You're good good to go\n")
        if allow_state:
            print(source_or_function)
        else:
            import inspect
            print(inspect.getsource(source_or_function))


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

test("""import random

def play(reward: float, lockout: int, t: int, T: int, your_score: float, other_scores: list[float]):
    #z = 1 / lockout
    #z = 1 / remaining_rounds
    #z = other_scores[0]
    return random.random() > 0.5
    threshold = 0.1
    if lockout <= 0:
        threshold = 0
    if t >= T:
        threshold = 0
    #return 1
    return reward > threshold
    """)


test(foo)
