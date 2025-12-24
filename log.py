LOGS = []

def log(*args):
    LOGS.append("".join(str(i) for i in args))

