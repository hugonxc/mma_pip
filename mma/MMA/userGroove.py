import os, shutil
from mma import MMAdir

def copy_grooves(src):
    # shutil.copytree(src, MMAdir+"/lib")
    os.system("cp -rf "+ src + " " + MMAdir +"/lib")

def add_grooves(src):
    copy_grooves(src)
    return 2

def update_grooves(src):
    copy_grooves(src)
    return 1
