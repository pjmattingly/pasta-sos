from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup

class LaunchpadUserNotExist(Exception):
    #see: https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python

    def __init__(self, lp_username):
        #see: https://stackoverflow.com/questions/10660435/how-do-i-split-the-definition-of-a-long-string-over-multiple-lines
        m = f"Could not find an active launchpad username: {lp_username}. "
        m += f"Please check that 'https://launchpad.net/~{lp_username}' "
        m+= "exists and is responding."

        # Call the base class constructor with the parameters it needs
        super().__init__(m)

class LaunchpadUserHasNoKey(Exception):
    #see: https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python

    def __init__(self, lp_username):
        #see: https://stackoverflow.com/questions/10660435/how-do-i-split-the-definition-of-a-long-string-over-multiple-lines
        m = f"The Launchpad user {lp_username} has no public key. "
        m += "Please add a public key to support authentication with created instanced."

        # Call the base class constructor with the parameters it needs
        super().__init__(m)

def username_exists(username):
    return _user_exists(username)

def _user_exists(username):
    try:
        with urlopen(f"https://launchpad.net/~{username}") as response:
            soup = BeautifulSoup(response, 'html.parser')
            
            #check for unknown user, but with existing Launchpad page
            #e.g., https://launchpad.net/~test
            #see: https://en.wikipedia.org/wiki/Beautiful_Soup_(HTML_parser)
            #and: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#quick-start
            if "does not use Launchpad" in soup.get_text():
                
                return False
    except HTTPError:
        #check for unknown user (404); e.g., `some-fake-name`
        #or other errors response.status >= 400
        return False

    return True

def get_public_key(username):
    if not _user_exists(username):
        raise LaunchpadUserNotExist(username)
    
    with urlopen(f"https://launchpad.net/~{username}/+sshkeys") as response:
        soup = BeautifulSoup(response, 'html.parser')

        key = soup.get_text()

        if len(key) == 0:
            raise LaunchpadUserHasNoKey(username)
    
    return key