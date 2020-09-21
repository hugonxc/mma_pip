from .mma import *
from .MMA import *

# MMAdir and platform for package
from os import path
import platform
global MMAdir, platform_so
MMAdir = path.join(path.dirname(__file__))
platform_so = platform.system()

