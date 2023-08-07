import pasta_sos.config_handler as config
import pasta_sos.uvt_kvm_handler as uvt
import pasta_sos.launchpad_handler as lp
import pasta_sos.ssh_handler as ssh

if __name__ == "__main__":
    if not uvt.is_installed():
        raise uvt.UvtNotInstalled()

    if not config.exists():
        #see: https://docs.python.org/dev/library/functions.html#input
        lp_username = input("Please enter a Launchpad username: ")

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