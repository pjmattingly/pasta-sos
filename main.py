import pasta_sos.util as util
import pasta_sos.config_handler as config
import pasta_sos.uvt_kvm_handler as uvt

class UvtNotInstalled(Exception):
    pass

class LaunchpadUsernameNotExist(Exception):
    pass

def promt_for_Launchpad_username():
    #see: https://docs.python.org/dev/library/functions.html#input
    return input("Please enter a Launchpad username: ")

if __name__ == "__main__":
    if not uvt.is_installed():
        raise UvtNotInstalled("Please install 'uvtool': `sudo apt -y install uvtool`")
    
    if not config.exists():
        lp_username = promt_for_Launchpad_username()

        if not util.launchpad_username_exists(lp_username):
            #see: https://stackoverflow.com/questions/10660435/how-do-i-split-the-definition-of-a-long-string-over-multiple-lines
            m = f"Could not find an active launchpad username: {lp_username}. "
            m += f"Please check that 'https://launchpad.net/~{lp_username}' "
            m+= "exists and is responding."
            raise LaunchpadUsernameNotExist(m)
        
        config.add_LaunchPad_username(lp_username)