import os
from mma import MMAdir

def copy_grooves(src):
    os.system("cp -rf "+ src + " " + MMAdir +"/lib")

def add_grooves(src):
    copy_grooves(src)
    return 2

def update_grooves(src):
    copy_grooves(src)
    return 1
