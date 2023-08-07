import pasta_sos.config_handler as config
import pasta_sos.uvt_kvm_handler as uvt
import pasta_sos.launchpad_handler as lp
from paramiko.agent import Agent
import pasta_sos.ssh_handler as ssh

from paramiko.pkey import PKey

from pathlib import Path

def prompt_for_Launchpad_username():
    #see: https://docs.python.org/dev/library/functions.html#input
    return input("Please enter a Launchpad username: ")

if __name__ == "__main__":
    if not uvt.is_installed():
        raise uvt.UvtNotInstalled()

    if not config.exists():
        lp_username = prompt_for_Launchpad_username()

        if not lp.username_exists(lp_username):
            raise lp.LaunchpadUserNotExist(lp_username)
        
        lp_key = lp.get_public_key(lp_username)
        
        if not ssh.is_key_on_system(lp_key):
            m = "A Launchpad public key must be on the system to ssh into instances."
            m += "\n"
            m += "The Launchpad public key coudl not be found on the system."
            m += "\n"
            m += "Please add the public/private key-pair associated with Launchpad "
            m += "to the system to continue."
            m += "\n"
            m += "see: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#adding-your-ssh-key-to-the-ssh-agent"

            raise ssh.KeyIsNotOnSystem(m)

        config.add_LaunchPad_username(lp_username)
        config.add_public_key(lp_key)

    #a = Agent()
    #print(a.get_keys())
    #PKey.from_path('/home/peter/.ssh/id_rsa.pub')
    '''
    _lp_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDGzoNuHNpJvOkzi3V9fSYbnkLhv8gRonW+N67ohZ1lRc17LPvcgVvonJp/Xo1sX0pxIUrsQsUBhnOPGg/DDrIUmZsEDvTEsAwXbuEXmGgceWDH1bVECbzspsMPGyC4DrHNGY6C59pmh+beKepZwlNUuYWMLiJCPgwhtPRqOM1T9rGEC3z/c1Y2V2naOgezD3jWRe9aqSmIarsAzog0Evobt624+jotwVnhEg6cZWRi2OySiNm2YwarTfEa+GapV97bcP+kH48j8efeHJnwQ9JIllNf5wPuoWS0uMtheF5DVe3juAMKEj/X4Qi3WNXOZ47J7Giyb737YnaO9H02gblY9zEsbbSMDx1NMdAYJgRt3gHZoM7+QhWbW/HEJ6yGXAMmdhWDddMc6GbZwhlD6Pu0zLi29kTtx48TwlDFvkyuit4SdPiFM+k197kXZitZa3roOfGzVxzqy+UeuZn7cARZ2/RnkuviY5fx04i2FDn9uoqSBKzL3hWnT5TTaVP0Dus= peter@pwn-j00'
    print( Path('/home/peter/.ssh/id_rsa.pub').read_text() )
    print(_lp_key)
    print(_lp_key.strip() == Path('/home/peter/.ssh/id_rsa.pub').read_text().strip())
    '''