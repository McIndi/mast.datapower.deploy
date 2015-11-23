# -*- coding: utf-8 -*-
import os
import re
import sys
import subprocess
from mast.cli import Cli
import dulwich.porcelain as git
from mast.config import get_config
from mast.datapower import datapower
from mast.logging import make_logger
from mast.timestamp import Timestamp
from contextlib import contextmanager

mast_home = os.environ["MAST_HOME"]


@contextmanager
def cd(path):
    curdir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(curdir)


def system_call(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False):
    """
    # system_call

    helper function to shell out commands. This should be platform
    agnostic.
    """
    stderr = subprocess.STDOUT
    pipe = subprocess.Popen(
        command,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        shell=shell)
    stdout, stderr = pipe.communicate()
    return stdout, stderr


def _get_data_file(f):
    _root = os.path.dirname(__file__)
    path = os.path.join(_root, "data", f)
    with open(path, "rb") as fin:
        return fin.read()


def ensure_config_file_exists():
    logger = make_logger("mast.datapower.deploy")
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
        msg = " ".join((
            "default config file not found.",
            "A blank config file was placed created for you",
            "Please follow the instructions within this file",
            "to configure this script.",
            "The file can be found here: {}".format(config_file_default)
        ))
        logger.error(msg)
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
    logger = make_logger("mast.datapower.deploy")
    if not config.has_section(environment):
        logger.error("environment {} is not configured in deploy.conf")
        sys.exit(-1)


def clone_svn(server, base_uri, vcs_creds, vcs_uri, export_dir):
    logger = make_logger("mast.datapower.deploy")
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    url = "'https://{}{}{}'".format(
        server,
        base_uri,
        vcs_uri).replace("//", "/")
    username, password = vcs_creds.split(":")
    command = [
        "svn",
        "export",
        url,
        "--force",
        "--no-auth-cache",
        "--non-interactive",
        "--username",
        "'{}'".format(username),
        "--password",
        "'{}'".format(re.escape(password))
    ]
    with cd(export_dir):
        out, err = system_call(command)
    if err:
        logger.err("Error received from svn: {}".format(err))
        print "Error received from svn: {}".format(err)
        sys.exit(-1)
    return export_dir


def clone_git(server, base_uri, vcs_creds, vcs_uri, export_dir):
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    with cd(export_dir):
        url = "https://{}@{}{}{}".format(vcs_creds, server, base_uri, vcs_uri)
        repo = git.clone(url)
        path = os.path.abspath(repo.path)
    return path


def clone_tfs(server, base_uri, vcs_creds, vcs_uri, export_dir):
    raise NotImplementedError


def clone_repo_from_vcs(vcs_details):
    logger = make_logger("mast.datapower.deploy")
    vcs_type = vcs_details[0]
    if vcs_type.lower() == "git":
        repo_path = clone_git(*vcs_details[1:])
    elif vcs_type.lower() == "svn":
        repo_path = clone_svn(*vcs_details[1:])
    elif vcs_type.lower() == "tfs":
        repo_path = clone_tfs(*vcs_details[1:])
    else:
        logger.error("Unsupported VCS type defined")
        print "Unsupported VCS type defined"
        sys.exit(-1)
    return repo_path


def create_inprogress_file(environment):
    logger = make_logger("mast.datapower.deploy")
    fname = os.path.join(mast_home, "tmp", "{}.inprogress".format(environment))
    if os.path.exists(fname):
        logger.error("Deployment already in progress, aborting!")
        print "Deployment already in progress, aborting!"
        sys.exit(-1)
    else:
        with open(fname, "w") as fout:
            fout.write(Timestamp().timestamp)


def delete_inprogress_file(environment):
    fname = os.path.join(mast_home, "tmp", "{}.inprogress".format(environment))
    os.remove(fname)


def main(credentials=[],          timeout=120,
         no_check_hostname=False, environment="",
         vcs_creds="",            vcs_uri="",
         vcs_dir="tmp",           quiesce_appliance=False,
         quiesce_domain=False,    no_quiesce_service=False,
         backup_dir="tmp"):

    logger = make_logger("mast.datapower.deploy")
    check_hostname = not no_check_hostname
    quiesce_service = not no_quiesce_service

    # Make sure deployment is not in progress
    create_inprogress_file(environment)

    ensure_config_file_exists()
    config = get_config("deploy.conf")
    ensure_environment_is_configured(config, environment)

    appliances = config.get(environment, "appliances").split()
    domain = config.get(environment, "domain").strip()

    env = datapower.Environment(
        appliances, credentials, timeout, check_hostname=check_hostname)

    # Clone fresh copy of deployment from VCS
    vcs_details = [config.get("VCS", x) for x in
                   ["type", "server", "base_uri"]]
    export_dir = os.path.abspath(vcs_dir)
    vcs_details.extend([vcs_creds, vcs_uri, export_dir])
    repo_path = clone_repo_from_vcs(vcs_details)

    cwd = os.getcwd()
    os.chdir(repo_path)


    # Get list of files to copy to DataPower appliances

    # gather anything below ./local/.

    # gather anything below ./$environment/local/.



    # Get list of zip files to deploy

    # get a list of any xml or zip files under ./config/.


    # Get deployment policy from ./$environment/deploymentPolicy/.


    for appliance in env.appliances:
        # optionally quiesce appliance

        # optionally quiesce domain

        # optionally quiesce service

        # Backup domain on DataPower
        backup = appliance.get_normal_backup(
            domain=domain,
            format="ZIP",
            comment="deployment")
        filename = os.path.join(backup_dir, "{}.zip".format(appliance.hostname))

        # Copy all files to DataPower

        # Deploy deployment policy to current domain

        # Deploy config zip files to DataPower apply deployment policy

        # Save the config
        pass

    # Clean-up, check-out and exit
    delete_inprogress_file(environment)
    os.chdir(cwd)
    os.rmdir(repo_path)

if __name__ == "__main__":
    try:
        cli = Cli(main=main)
        cli.run()
    except:
        logger = make_logger("mast.datapower.deploy")
        logger.exception(
            "Sorry, an unhandled exception occurred during deployment")
