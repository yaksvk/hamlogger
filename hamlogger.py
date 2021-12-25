#!/usr/bin/env python

license = """
Copyright 2014-2021, Jakub Ondrusek, OM1WS (yak@gmx.co.uk)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# global libs
import os
import sys
import signal
import pathlib

# application libs
from lib import config as cfg
from lib import app
from lib import commandline

# init application
absolute_script_path = pathlib.Path(__file__).parent.resolve()
config = cfg.PersistentConfig(source_path=absolute_script_path)
application = app.HamLogger(config)

# process command line arguments (can perfectly end here)
commandline.process(application, license)

# catch sigint, run GUI, exit cleanly
signal.signal(signal.SIGINT, signal.SIG_DFL)
status = application.run(sys.argv)
sys.exit(status)
