#!/usr/bin/python -d
# -*- coding: utf-8 -*-

# Finner ut hvilke Diana versjoner som finnes og gir brukeren mulighet til å velge
# hvilke som skal brukes til å kjøre som diana-beredt-test

# ls  -d /etc/diana/*.?? | tail -3 | cut -d '/' -f 4



from Tkinter import *
import subprocess
import re

FrameSizeX = 350
FrameSizeY = 100
FramePosX = 150
#FramePosY = 200

versions = []

def getversions():
  DianaVersions = subprocess.check_output('ls  -d /etc/diana/*.?? | tail -3 | cut -d "/" -f 4', shell=True)
  DianaVersions.rstrip()
  for ver in DianaVersions.split("\n"):
    if not re.match(r'^\s*$', ver):
#      print "<"+ver+">"
      versions.append(ver)

def center_window(w=FrameSizeX, h=FrameSizeY):
 # get screen width and height
  ws = root.winfo_screenwidth()
  hs = root.winfo_screenheight()
  # calculate position x, y
  x = (ws/2) - (w/2)    
  y = (hs/2) - (h/2)
  root.geometry('%dx%d+%d+%d' % (w, h, x - FramePosX, y))

def clicked():
  #exitstring = "/usr/bin/diana.bin-" + versions[var.get() - 1]
  exitstring = "" + versions[var.get() - 1]
  print str(exitstring)
  root.destroy()

getversions()

root = Tk()
root.wm_title("Velg Diana versjon som skal testes")
center_window()

widget1 = Label(root,textvariable="Placeholder") # Legger til et felt for å få litt mellomrom
widget1.pack()

var = IntVar()
num = 1
for ver in versions:
  Btext = "Diana versjon " + str(ver) 
  Radiobutton(root, text=Btext, variable=var, value=num, command=clicked, indicatoron=0, padx=150).pack(anchor=W)
  num+=1;


root.mainloop()
