from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup

def launchpad_username_exists(username):
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