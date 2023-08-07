import pasta_sos.config_handler as config
import pasta_sos.uvt_kvm_handler as uvt
import pasta_sos.launchpad_handler as lp

class UvtNotInstalled(Exception):
    pass

def promt_for_Launchpad_username():
    #see: https://docs.python.org/dev/library/functions.html#input
    return input("Please enter a Launchpad username: ")

if __name__ == "__main__":
    if not uvt.is_installed():
        raise UvtNotInstalled("Please install 'uvtool': `sudo apt -y install uvtool`")
    
    if not config.exists():
        lp_username = promt_for_Launchpad_username()

        if not lp.username_exists(lp_username):
            raise lp.LaunchpadUserNotExist(lp_username)
        
        config.add_LaunchPad_username(lp_username)
        config.add_public_key(lp.get_public_key(lp_username))