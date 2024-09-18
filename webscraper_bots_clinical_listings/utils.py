def normalise_space(s):
    return ' '.join(filter(None, map(str.strip, s.split(' '))))


def _try(to, on_exc, exc):
    """
    Helper for persistently retrying an action.
    Only supports one exception handler for all exceptions.
    """

    while True:
        try:
            return to()
        except exc:
            on_exc()

def progressbar(iteration, total, prefix='', suffix='',
                length=100, fill='█', printEnd="\r"):
    """Print a progress bar.

    Call from within a loop to draw a progress bar in the console.

    Parameters
        iteration   - current iteration (int)
        total       - total iterations (int)
        prefix      - prefix string (str)
        suffix      - suffix string (str)
        length      - character length of bar (int)
        fill        - character to fill bar (str)
        printEnd    - end character, eg "\r", "\r\n" (str)
    """
    filledLength = length * iteration // total
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {suffix}', end=printEnd)

