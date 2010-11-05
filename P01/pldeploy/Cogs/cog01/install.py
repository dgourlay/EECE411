#! /usr/bin/env python
import os

bp = "~/deploy/java/bash_profile"

# setup dloads directory JRE
os.system("mkdir ~/downloads")
os.chdir("~/downloads")
#download and extract jre tarball
os.system("wget -N http://www.ece.ubc.ca/~samera/TA/411/project/jre.tar.gz" )
os.system("tar xvzf jre.tar.gz")       
os.system("mkdir ~/Programs/")
os.system("mv jre1.6.0_16/ ~/Programs/")
os.chdir("~/")

#setup .bash_profile to have the correct path
os.system("mv "+bp+" ~/.bash_profile")

