# Podcast Editor
Python program to edit podcasts. (Includes .exe version)
There is the gui program and the comand line program. The GUI program is a tkinter overlay of Sound_Edit.py and requires that program to work.
Uses ffmpeg for audio conversions to .wav files. Make sure ffmpeg is added to path and can convert the type of audio you use to .wav.

# Usage of Command line program
py Sound_edit.py file -filename -t -s -s -c -gpu

-h : show help

file : input file

-filename: output file (defaults to input file name + "_new")

-t : The threshold of quietness to cut off silence ~ [0,255] (defaults to 1)

-s : Number of seconds of silence before removal (defaults to .14)

-gpu : What gpu to use, if exists. (defaults to CPU) 

- NOTE: the device used is the device number + 1. (Device 0 is CPU, 1 is first GPU)

- REQUIRES Cuda and Cudnn. If tensorflow or pytorch works, this works.

-c : Number of cores to compute on. (only if CPU is used, defaults to 1)

# GUI usage
As simple as run the gui program and fill in the information you want.
NOTE: The GUI will close when you press the run button. The console will appear behind it providing how far along the computations are.

# Required Modules
Command Line Program:
librosa
numpy
numba
soundfile
argparse

GUI Program:
All requirements from Command Line Program plus...
tkinter
nvidia_smi
win32com

# Making .exe files
Use pyinstaller on the .spec files
pyinstaller Sound_edit.spec
pyinstaller Sound_edit_GUI.spec