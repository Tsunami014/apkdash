LOGS = []

def log(*args):
    LOGS.append("".join(str(i) for i in args))
def good(*args):
    LOGS.append("\020+"+"".join(str(i) for i in args))
def info(*args):
    LOGS.append("\020~"+"".join(str(i) for i in args))
def warn(*args):
    LOGS.append("\020*"+"".join(str(i) for i in args))
def error(*args):
    LOGS.append("\020-"+"".join(str(i) for i in args))

