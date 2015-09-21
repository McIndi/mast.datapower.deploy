# -*- coding: utf-8 -*-
from mast.datapower import datapower
from mast.config import get_config
from mast.logging import make_logger
from mast.timestamp import Timestamp
from mast.cli import Cli
import os
import sys

mast_home = os.environ["MAST_HOME"]

def _get_data_file(f):
    _root = os.path.dirname(__file__)
    path = os.path.join(_root, "data", f)
    with open(path, "rb") as fin:
        return fin.read()


def ensure_config_file_exists():
    config_file_default = os.path.join(
        mast_home, "etc", "default", "deploy.conf"
    )
    config_file_local = os.path.join(
        mast_home, "etc", "local", "deploy.conf"
    )
    error = False
    if not os.path.exists(config_file_default):
        # The default config doesn't exist
        with open(config_file_default, "w") as fout:
            fout.write(_get_data_file("deploy.conf"))
        logger.error(
            "default config file not found. "
            "A blank config file was placed created for you "
            "Please follow the instructions within this file "
            "to configure this script. "
            "The file can be found here: {}".format(config_file_default)
        )
        error = True
    elif not os.path.exists(config_file_local):
        # The default config exists, the user needs to configure the
        # local config
        logger.error(
            "Configuration not found please follow the instructions "
            "here {} to configure this script".format(config_file_default))
        error = True
    if error:
        print "Error: Config file does not exists, see log for details"
        sys.exit(-1)


def ensure_environment_is_configured(config, environment):
    if not config.has_section(environment):
        logger.error("environment {} is not configured in deploy.conf")
        sys.exit(-1)


def clone_repo_from_vcs(vcs_details):
    vcs_type = vcs_details[0]
    if vcs_type.lower() == "git":
        repo_path = clone_git(vcs_details)
    elif vcs_type.lower() == "svn":
        repo_path = clone_svn(vcs_details)
    elif vcs_type.lower() == "tfs":
        repo_path = clone_tfs(vcs_details)
    else:
        logger.error("Unsupported VCS type defined")
        print "Unsupported VCS type defined"
        sys.exit(-1)
    return repo_path


def create_inprogress_file(environment):
    fname = os.path.join(mast_home, "tmp", "{}.inprogress".format(environment))
    if os.path.exists(fname):
        logger.error("Deployment already in progress, aborting!")
        print "Deployment already in progress, aborting!"
        sys.exit(-1)
    else:
        with open(fname, "w") as fout:
            fout.write(Timestamp().timestamp())

def delete_inprogress_file(environment):
    fname = os.path.join(mast_home, "tmp", "{}.inprogress".format(environment))
    os.remove(fname)    

def main(credentials=[],          timeout=120,
         no_check_hostname=False, environment="",
         vcs_creds="",            vcs_uri=""):

    check_hostname = not no_check_hostname

    # Make sure deployment is not in progress
    create_inprogress_file(environment)

    ensure_config_file_exists()
    config = get_config("deploy.conf")
    ensure_environment_is_configured(config, environment)

    appliances = config.get(environment, "appliances").split()
    domain = config.get(environment, "domain").split()

    env = datapower.Environment(
        appliances, credentials, timeout, check_hostname=check_hostname)

    # Clone fresh copy of deployment from VCS
    vcs_details = [config.get("VCS", x) for x in
                        ["type", "server", "base_uri"]]
    repo_path = clone_repo_from_vcs(vcs_details)


    # Get list of files to copy to DataPower appliances

    # Get list of zip files to deploy

    for appliance in appliances:
        # optionally quiesce appliance
        
        # optionally quiesce domain
        
        # optionally quiesce service
        
        # Backup domain on DataPower
    
        # Copy all files to DataPower
    
        # Deploy deployment policy to current domain
    
        # Deploy config zip files to DataPower apply deployment policy
    
        # Save the config
        pass

    # Clean-up, check-out and exit
    delete_inprogress_file(environment)

if __name__ == "__main__":
    logger = make_logger("mast.datapower.deploy")
    try:
        cli = Cli(main=main)
        cli.run()
    except:
        logger.exception(
            "Sorry, an unhandled exception occurred during deployment")
