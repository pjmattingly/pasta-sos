import os
import psutil

def _agent_running():
    '''
    To check that public keys are on the system, we need `ssh-agent` running and
    correctly configured
    To correctly configure `ssh-agent` is sets two environment variables 
    ("SSH_AGENT_PID" and "SSH_AUTH_SOCK")
    and "SSH_AGENT_PID" contains its PID
    and so checking if its PID is present shows if the process is running
        see:
        https://manpages.ubuntu.com/manpages/jammy/man1/ssh-agent.1.html
    '''
    if ("SSH_AGENT_PID" in os.environ and "SSH_AUTH_SOCK" in os.environ):
        return psutil.pid_exists(os.environ["SSH_AGENT_PID"])

def ready():
    return _agent_running()
