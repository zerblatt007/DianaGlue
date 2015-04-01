#!/usr/bin/python -d
# -*- coding: utf-8 -*-

# DianaSaveFelt.py
# Starter Diana og lytter på STDOUT for å finne valgte felter, som brukeren så kan kopiere over til en valgt katalog
#
# 20140107 Roger Storvik 

# regex: ".* INFO .*Source:(?P<SourceFile>.*) : .*$"
# r"""(?m).* INFO .*Source:(?P<SourceFile>\S*)"""

import subprocess
import re
import os

from Tkinter import *
import tkMessageBox
import ttk
import Tkinter, tkFileDialog, tkMessageBox
from ScrolledText import ScrolledText
import shutil

class CoreGUI(object):
  def __init__(self,parent):
    self.parent = parent
    self.InitUI()
    self.progress = ttk.Progressbar(self.parent, orient = 'horizontal', length = 800, mode = 'determinate')
    self.progress.grid(column=0, row=3, columnspan=8)
    dianabutton = Button(self.parent, text="Start Diana", command=self.main)
    dianabutton.grid(column=0, row=1, columnspan=2)
    self.sizetext=StringVar()
    self.sizetext.set("")
    self.sizebox = Label(self.parent, textvariable=self.sizetext, height=2)
    self.sizebox.grid(column=2, row=1, columnspan=1)
    self.pathbox = Entry(self.parent, bd =2, width=50)
    self.pathbox.grid(column=3, row=1, columnspan=3)
    self.pathbox.bind('<Return>', self.catchEnter)
    pathbutton = Button(self.parent, text="Velg Katalog", command=self.askdirectory)
    pathbutton.grid(column=6, row=1, columnspan=1)
    self.copybutton = Button(self.parent, text="Kopier filer", command=self.copytodir)
    self.copybutton.grid(column=7, row=1, columnspan=1)
    self.copybutton.config(state='disabled')
    self.copyDir = os.path.expanduser("~")
    self.pathbox.insert(0,self.copyDir)
    self.sizetext.set("Ledig: " + GetHumanReadable(dirfree(self.copyDir)))

  def main(self):

    self.progress["value"] = 0
    embedded_rawstr = r"""(?m).* INFO .*Source:(?P<SourceFile>\S*)"""
    self.sourceFiles = set() 

    cmd = subprocess.Popen('diana', shell=True, stdout=subprocess.PIPE)
    while True:
      line = cmd.stdout.readline()
      if not line:
	  # Diana er avsluttet, da kan vi fylle tekstboks hvis noen felter ble valgt
        self.text_box.delete("1.0",END)
        if (self.sourceFiles):
          self.progress["maximum"] = len(self.sourceFiles)
          self.copybutton.config(state='normal')
          self.totalFsize = 0
          for lines in self.sourceFiles:
            fileSize = os.path.getsize(lines)
            self.text_box.insert(END, GetHumanReadable(fileSize).rjust(14) + " - " + lines + "\n")
            self.totalFsize += fileSize
          self.text_box.insert(END, "\n" + GetHumanReadable(self.totalFsize).rjust(14) + " Totalt\n")
        else:
          self.copybutton.config(state='disabled')
          self.text_box.insert(END, "\n\nIngen Felter ble valgt\n") 
          self.text_box.insert(END, "\n\nBruk \"Start Diana\" på nytt og velg noen felter for å kunne kopiere..\n") 

        break
      match_obj = re.search(embedded_rawstr, line)
      if match_obj:
        SourceFile = match_obj.group('SourceFile')
        print "<" + SourceFile + ">"
        self.sourceFiles.add(SourceFile)

  def InitUI(self):
    self.text_box = ScrolledText(self.parent, wrap='word', height = 15, width=100)
    self.text_box.grid(column=0, row=0, columnspan = 8, sticky='NSWE', padx=5, pady=5)
    self.text_box.insert(END, "\nKopiering av feltfiler valgt i Diana:\n\n")
    self.text_box.insert(END, "Klikk på \"Start Diana\"\n")
    self.text_box.insert(END, "Gå til Felt menyen i Diana og velg modell\n")
    self.text_box.insert(END, "Velg de feltene du er ute etter og klikk Utfør etc\n")
    self.text_box.insert(END, "Når du er ferdig, avslutt Diana og de feltene som ble valgt listes opp her.\n")
    self.text_box.insert(END, "Velg hvor de skal kopieres med \"Velg Katalog\" og klikk deretter \"Kopier Filer\"\n")
    self.text_box.insert(END, "\nOBS: GigaByte filer tar stor plass og tar også lang tid å kopiere\n")

  def askdirectory(self):
    okorcancel = tkFileDialog.askdirectory(initialdir=self.pathbox.get(), parent=root, mustexist=True)
    if (okorcancel):
      self.copyDir = okorcancel
      self.sizetext.set("Ledig: " + GetHumanReadable(dirfree(self.copyDir)))
    else:
      self.copyDir = self.pathbox.get()
    
    self.pathbox.delete(0,END)
    self.pathbox.insert(0,self.copyDir)

  def copytodir(self):
    if (not os.path.isdir(self.pathbox.get())):
      tkMessageBox.showerror("Katalog finnes ikke!", "\"" + self.pathbox.get() + "\" er ikke tilgjengelig")
      self.pathbox.delete(0,END)
      self.pathbox.insert(0,self.copyDir)
    else:
      self.copyDir=self.pathbox.get()
      print "Target: " + self.copyDir
      targetDisk = os.statvfs(self.copyDir)
      targetFree = targetDisk.f_frsize * targetDisk.f_bavail
      if (not os.access(self.copyDir, os.W_OK)):
        tkMessageBox.showerror("Ikke skrivetilgang!","Du har ikke skrivetilgang på \n \"" + self.copyDir + "\".\nVelg en annen i stedet.")
      elif (self.totalFsize > targetFree):
        tkMessageBox.showerror("For lite ledig plass", "Det er " + GetHumanReadable(targetFree) + " ledig på katalogen \"" + self.copyDir + "\" og du trenger " + GetHumanReadable(self.totalFsize))
      else:
        self.filecnt = 1
        self.progress["value"] = 0
        self.sourcelines = list(self.sourceFiles)
        self.copyfiles()


  def copyfiles(self):
    self.progress["value"] = self.filecnt
    print "copy #" + str(self.filecnt) + " av " + str(len(self.sourcelines))  + ":" + self.sourcelines[self.filecnt -1] + " to " + self.copyDir
    errmsg = ""
    try:
      shutil.copy(self.sourcelines[self.filecnt -1], self.copyDir)
    except shutil.Error as e:
      errmsg = 'Error: %s' % e
      tkMessageBox.showerror("shutil - Feil på kopiering","Problem med å kopiere \"" + self.sourcelines[self.filecnt -1] + "\" til " + self.copyDir + "\" katalogen - " + errmsg)
      print errmsg
    except IOError as e:
      errmsg = 'Error: %s' % e.strerror
      tkMessageBox.showerror("IOError: Feil på kopiering","Problem med å kopiere \"" + self.sourcelines[self.filecnt -1] + "\" til " + self.copyDir + "\" katalogen - " + errmsg)
      print errmsg
    self.filecnt += 1
    if (self.filecnt <= len(self.sourcelines)):
      root.after(10, self.copyfiles) # Kaller seg selv etter 10ms for å oppdatere progressbar
    if (self.filecnt > len(self.sourcelines)):
      if (not errmsg):
        tkMessageBox.showinfo("DianaSaveFelt","Kopiering fullført!")
      else:
        tkMessageBox.showerror("DianaSaveFelt","Kopiering feilet!")

  # Trigger på enter i pathboksen
  def catchEnter(self,event):
    if (not os.path.isdir(self.pathbox.get())):
      tkMessageBox.showerror("Katalog finnes ikke!", "\"" + self.pathbox.get() + "\" er ikke tilgjengelig")
      self.pathbox.delete(0,END)
      self.pathbox.insert(0,self.copyDir)
    else:
      self.sizetext.set("Ledig: " + GetHumanReadable(dirfree(self.pathbox.get())))


def GetHumanReadable(size):
  suffixes=['B','KB','MB','GB','TB']
  suffixIndex = 0
  while size > 1024:
    suffixIndex += 1 #increment the index of the suffix
    size = size/1024.0 #apply the division
  return "%.2f %s"%(size,suffixes[suffixIndex])

def dirfree(path):
  targetDisk = os.statvfs(path)
  return targetDisk.f_frsize * targetDisk.f_bavail


root = Tk()
root.wm_title("Diana feltfilkopiering")
gui = CoreGUI(root)
root.mainloop()
