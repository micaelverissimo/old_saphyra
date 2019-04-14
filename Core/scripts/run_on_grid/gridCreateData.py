#!/usr/bin/env python

import os
# This script is a simple redirection for the standalone createData.py
from RingerCore.util import include
# parseOpts using standalone
include(os.path.expandvars('$ROOTCOREBIN/user_scripts/TuningTools/standalone/createData.py'))
