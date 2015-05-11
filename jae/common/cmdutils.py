import subprocess

def cast(command, shell=True):
    try:
        subprocess.check_call(command, shell=shell)
    except:
        raise 


def call(command, shell=True):
    try:
        out = subprocess.check_output(command, shell=shell)
        return out
    except:
        raise

