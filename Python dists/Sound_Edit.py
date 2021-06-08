# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 20:45:32 2021

@author: Braxton Brown

Librosa - ISC License
Copyright (c) 2013--2017, librosa development team.
https://github.com/librosa/librosa/blob/main/LICENSE.md

Numpy - Copyright (c) 2005-2020, NumPy Developers.
All rights reserved.
https://numpy.org/doc/stable/license.html

Numba - numba/numba is licensed under the BSD 2-Clause "Simplified" License
Copyright (c) 2012, Anaconda, Inc.
All rights reserved.
https://github.com/numba/numba/blob/master/LICENSE

Soundfile - bastibe/python-soundfile is licensed under the BSD 3-Clause "New" or "Revised" License
Copyright (c) 2013, Bastian Bechtold
All rights reserved.
https://github.com/bastibe/python-soundfile/blob/master/LICENSE


"""

from librosa import get_samplerate, stream
from numpy import array, abs
from numba import njit, cuda
from soundfile import write
from argparse import ArgumentParser
from time import time
from sys import argv, exit
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from subprocess import Popen, PIPE


def compile_gpu_func():
    @cuda.jit
    def kernel(d_arr, to_remove, on):
        # Thread ID
        tx = cuda.threadIdx.x
        # Block ID
        bx = cuda.blockIdx.x
        # Threads per block (block width)
        bw = cuda.blockDim.x

        # get position
        pos = bx * bw + tx
        # check if in array boundaries
        if pos+on < d_arr.size:
            for i in range(on):
                if (-to_remove <= d_arr[pos+i] <= to_remove):
                    continue
                else:
                    return
            d_arr[pos] = 1000
    return kernel


def compile_func(parsed):
    print("Compiling for parallel execution")

    @njit(["f8[:](f4[:], f8, f8, i4)"], nogil=True)
    def remove_prev(li, to_remove, on, index):
        return array([li[i] for i in range(li.shape[0])
                      if not (abs(li[i: i + on]) <= to_remove).all()]+[index])

    return remove_prev


def format_seconds(secs):
    return f"{int((secs//3600))}:{str(int((secs//60)%60)).zfill(2)}:{str(int(secs%60)).zfill(2)}"


def proccess(parsed_args, method):
    file = parsed_args.file
    try:
        rate = get_samplerate(file)
        frame_rate = (2048 * rate) // 22050
        hop_length = (512 * rate) // 22050
        print("loading...")
        streams = list(stream(file, 2**20, frame_rate, hop_length))[0] * 255
    except Exception:
        try:
            nfile = file[: -4] + ".wav"
            Popen(f'ffmpeg -i "{file}" "{nfile}" -y', stdout=PIPE, stdin=PIPE, stderr=PIPE).wait()
            parsed_args.file = nfile
            parsed_args.dele = nfile
            return proccess(parsed_args, method)
        except Exception as e:
            print(e)
            print(f'\nCould not convert "{file}" to .wav')
            exit()

    if os.path.exists(parsed_args.dele):
        os.remove(parsed_args.dele)
    remove_after = parsed_args.s
    threshold = parsed_args.t

    print("editing...")
    if parsed_args.gpu:
        cuda.select_device(parsed_args.gpu-1)
        threadsperblock = 1024
        blocks = (streams.size + threadsperblock - 1) // threadsperblock
        gpu_streams = cuda.to_device(streams)
        method[blocks, threadsperblock](gpu_streams, threshold, int(remove_after*rate))
        streams = gpu_streams.copy_to_host()
        cuda.close()
        streams = streams[streams != 1000]
        new = streams
    else:
        new = []
        storage = [None for _ in range(int(streams.shape[0] / rate + 0.5))]
        time_elapsed = time()
        time_per_epoch = parsed_args.s * .09546 + .00545
        with ThreadPoolExecutor(parsed_args.c) as ex:
            print('Intializing Threads', end='\r')
            threads = [ex.submit(method, streams[i * rate: i * rate + rate], threshold,
                                 rate * remove_after, i)
                       for i in range(int(streams.shape[0] / rate + 0.5))]
            print('\rCompleted Initalizing Threads')
            print('Proccessing Data')
            for i, future in enumerate(as_completed(threads)):
                res = future.result()
                storage[int(res[-1])] = res[: -1]
                time_left = round(time_per_epoch * (streams.shape[0] / rate - i))
                print(
                    f"\r{str(round((i+1)/int(streams.shape[0]/rate+.5)*100,2)).ljust(5)}% Complete | Time Remaining: {format_seconds(time_left)} | Elasped Time: {format_seconds(time()-time_elapsed)}",
                    end="\r")
            print('\nCompleted Proccessing')
            print('Storing Data', end='\r')
            for i in storage:
                new.extend(i)
            print('\rStored Data\t')
    return array(new), rate


def save(file_name, arr, bit_rate):
    print("Saving...")
    write(file_name[:-4] + ".wav", arr / 255, bit_rate)
    if not file_name[-4:] == ".wav":
        Popen(f'ffmpeg -i "{file_name[:-4] + ".wav"}" "{file_name}" -y',
              stdout=PIPE, stdin=PIPE, stderr=PIPE).wait()
        os.remove(file_name[:-4] + ".wav")
    print("done!")


def main(to_parse):
    parser = ArgumentParser(description="Remove silence in audio files")
    parser.add_argument("file",
                        type=str,
                        help="The location of the file to edit.")
    parser.add_argument("-fileName",
                        type=str,
                        help="The name of the new file.",
                        default="_new")
    parser.add_argument(
        "-t",
        metavar="threshold",
        type=float,
        help="The threshold of quietness to cut off silence ~ [0,255]",
        default=1)
    parser.add_argument("-s",
                        metavar="seconds",
                        type=float,
                        help="Number of seconds of silence before removal",
                        default=0.14)
    parser.add_argument('-c', metavar='cores', type=int,
                        help='Number of cores to use for computation', default=1)
    parser.add_argument('-gpu', metavar='gpu', type=int, help='What device to use', default=0)

    if isinstance(to_parse, str):
        parsed = parser.parse_args(to_parse.split(" "))
    else:
        parsed = parser.parse_args(to_parse)

    parsed.dele = "NoneFile.txt"
    return parsed


if __name__ == "__main__":
    args = main(argv[1:])  # parses inputs
    if args.gpu:
        try:
            func = compile_gpu_func()
        except Exception:
            print('Failed to compile for GPU, resorting to CPU')
            func = compile_func()
    else:
        func = compile_func(args)
    arr, rate = proccess(args, func)  # proccesses the
    if args.fileName != "_new":
        file_name = args.fileName
    else:
        file_name = args.file[:-4] + args.fileName + args.file[-4:]
    save(file_name, arr, rate)
