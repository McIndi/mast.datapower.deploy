from mast.logging import make_logger
from mast.cli import Cli
from deploy import main

try:
    cli = Cli(main=main)
    cli.run()
except:
    make_logger("mast.deploy").exception("An unhandled exception occurred")
    print "An unhandled exception occurred, see log for details"
    raise
