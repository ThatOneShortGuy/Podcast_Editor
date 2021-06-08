# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 14:19:59 2021

@author: braxt
"""

from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import DoubleVar, Frame, Tk, ttk, StringVar, IntVar
from Sound_Edit import main, compile_func, proccess, save, compile_gpu_func
from win32com.client import GetObject
import tkinter as tk
from os import cpu_count
import nvidia_smi as nv


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """

    def __init__(self, widget, text='widget info'):
        self.waittime = 500  # miliseconds
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = ttk.Label(self.tw, text=self.text, justify='left',
                          background="#ffffff", relief='solid', borderwidth=1,
                          wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


def get_file():
    file.set(askopenfilename())
    name = file.get()
    saveFile.set(name[:-4]+'_new'+name[-4:])


def save_file():
    filetypes = (("WAV file", "*.wav"), ("All Files", "*.*"), ('M4A file', "*.m4a"))
    saveFile.set(asksaveasfilename(defaultextension='.wav', filetypes=filetypes))


def remove_cores(x):
    if int(x.split(' : ')[0]) >= ccount:
        cpuCount.grid_remove()
        cpuC.grid_remove()
        display_cpu.grid_remove()
    else:
        cpuCount.grid(row=10, column=0)
        cpuC.grid(row=10, column=1)
        display_cpu.grid(row=10, column=2)


def presets():
    n = var.get()
    if n == 0:
        threshold.set(1)
        seconds.set(.5)
    elif n == 1:
        threshold.set(1)
        seconds.set(.14)
    elif n == 2:
        threshold.set(1)
        seconds.set(.05)


def roundvar(var):
    var.set(round(var.get(), 2))


def edit_file_name(filename):
    filename = filename.split('/')
    for i in range(len(filename)):
        if ' ' in filename[i]:
            filename[i] = f'"{filename[i]}"'
    return '/'.join(filename)


def send_params():
    in_file = file.get()
    out_file = saveFile.get()
    thres = str(threshold.get())
    secs = str(seconds.get())
    CPU = str(cpu.get())
    device = gpu.get()[0]
    text = [in_file, '-fileName', out_file, '-s', secs, '-t', thres, '-c', CPU, '-gpu', device]
    args = main(text)
    root.destroy()
    if args.gpu:
        func = compile_gpu_func()
    else:
        func = compile_func(args)
    arr, rate = proccess(args, func)
    save(out_file, arr, rate)


def get_cpu_type():
    root_winmgmts = GetObject("winmgmts:root\cimv2")
    cpus = root_winmgmts.ExecQuery("Select * from Win32_Processor")
    return (len(cpus), [i.Name for i in cpus])


ccount, gpus = get_cpu_type()
gpus = [f'{i} : {e}' for i, e in enumerate(gpus)]
root = Tk()
file = StringVar()
saveFile = StringVar()
var = IntVar()
threshold = DoubleVar(value=1)
seconds = DoubleVar(value=.5)
gpu = StringVar(value=gpus[0])
cpu = IntVar(value=cpu_count())

root.geometry('1280x720')
root.title('Audio Edit')

container = Frame(root)
container.pack(pady=25)
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

label1 = ttk.Label(container, text='Audio file to edit')
label1.grid(row=0, column=0)

button1 = ttk.Button(container, text='Browse', command=get_file)
button1.grid(row=0, column=2)

display_file = ttk.Entry(container, textvariable=file, width=69)
display_file.grid(row=0, column=1)

label2 = ttk.Label(container, text='Output File')
label2.grid(row=1, column=0, pady=20)

display_save_file = ttk.Entry(container, textvariable=saveFile, width=69)
display_save_file.grid(row=1, column=1)

button2 = ttk.Button(container, text='Browse', command=save_file)
button2.grid(row=1, column=2)

label3 = ttk.Label(container, text='Settings')
label3.grid(row=2, column=0)

r = []
for i, ty in zip(range(4), ('Custom ', 'Fast        ', 'Medium', 'Slow      ')):
    r.append(ttk.Radiobutton(container, text=ty, variable=var, value=-i+3, command=presets))
    r[i].grid(column=1, row=-i+5)

label4 = ttk.Label(container, text='Volume cut off level (0,255]:')
label4.grid(row=6, column=0, pady=20)

thresh_slider = ttk.Scale(container, variable=threshold, to=15,
                          length=420, command=lambda x: roundvar(threshold))
thresh_slider.grid(row=6, column=1)

display_thres = ttk.Entry(container, textvariable=threshold, width=8)
display_thres.grid(row=6, column=2)

label5 = ttk.Label(container, text='Seconds before cut off: ')
label5.grid(row=7, column=0)

sec_slider = ttk.Scale(container, variable=seconds, to=2, length=420,
                       command=lambda x: roundvar(seconds))
sec_slider.grid(row=7, column=1)

display_secs = ttk.Entry(container, textvariable=seconds, width=8)
display_secs.grid(row=7, column=2)

gpu_label = ttk.Label(container, text='Use Device: ')
gpu_label.grid(row=8, column=0)
cpuToolTip = CreateToolTip(gpu_label,
                           'Gpu is significantly faster.')

nv.nvmlInit()
gpu_count = nv.nvmlDeviceGetCount()
gpus += [f'{i+ccount} : '+nv.nvmlDeviceGetName(nv.nvmlDeviceGetHandleByIndex(i)).decode()
         for i in range(gpu_count)]

gpu_check = ttk.OptionMenu(container, gpu, False, *gpus, command=remove_cores)
gpu_check.grid(row=8, column=1)
cpuToolTip = CreateToolTip(gpu_check,
                           'Gpu is significantly faster.')


cpuCount = ttk.Label(container, text='# of proccessing cores\n      (only for cpu)')
cpuCount.grid(row=10, column=0)
corestt = CreateToolTip(cpuCount, 'Only for cpus')


cpuC = ttk.Scale(container, variable=cpu, length=420, from_=1,
                 to=cpu_count(), command=lambda x: roundvar(cpu))
cpuC.grid(row=10, column=1)
corestt = CreateToolTip(cpuC, 'Only for cpus')

display_cpu = ttk.Entry(container, textvariable=cpu, width=8)
display_cpu.grid(row=10, column=2)

go_button = ttk.Button(container, text='Run', command=send_params)
go_button.grid(row=69, column=1, sticky='s')

root.mainloop()
