import os
import psutil

class SSHAgentNotReady(Exception):
    def __init__(self):
        m = "The process `ssh-agent` does not seem to be running or setup correctly."
        m += "\n"
        m += "Please run: 'eval `ssh-agent`' to launch."
        m += "\n"
        m += "https://manpages.ubuntu.com/manpages/ssh-agent.1.html"
        
        super().__init__(m)

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
