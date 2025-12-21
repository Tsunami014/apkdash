import shutil

def printScreen():
    size = shutil.get_terminal_size()
    print("╭"+"─"*(size.columns-2)+"╮")
    for i in range(size.lines-2):
        print("│"+" "*(size.columns-2)+"│")
    print("╰"+"─"*(size.columns-2)+"╯", end="\033[0;0H", flush=True)

