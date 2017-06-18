#! /usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, re, csv, os, shutil
from datetime import datetime

#
# Common
#
def get_lines(cmd):
    '''
    :param cmd: str 実行するコマンド.
    :rtype: generator
    :return: 標準出力 (行毎).
    '''
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        line = proc.stdout.readline()
        if line:
            yield line

        if not line and proc.poll() is not None:
            break
#
# Ports
#
def get_list_ports():
    output = get_lines("gphoto2 --auto-detect")
    list_ports = []
    for line in output:
        list_ports.append(line.decode('utf-8'))
    list_ports=list_ports[2:]
    list_ports = [re.split("\s\s+", port)[1] for port in list_ports]
    return list_ports

#
# Serial Numbers
#
PTN_SERIALNUM = re.compile("Current:\s+(?P<serialnum>\d+)")
def get_serialnum(port):
    output = get_lines("gphoto2 --port " + port + " --get-config eosserialnumber")
    lines = [line for line in output]
    serialnum = lines[2].decode('utf-8')
    m = PTN_SERIALNUM.match(serialnum)
    serialnum = m.group("serialnum")
    return serialnum

def get_list_serialnumber(list_ports):
    list_serialnum = []
    for port in list_ports:
        serialnum = get_serialnum(port)
        list_serialnum.append(serialnum)
    return list_serialnum

#
# 画像の取得
#
def genListCameras(list_camera_numbers, list_ports):
    list_cameras = []
    for port in list_ports:
        serialnum = get_serialnum(port)
        for cameraNum in list_camera_numbers:
            if cameraNum[1] == serialnum:
                list_cameras.append([cameraNum[0], cameraNum[1], port])
    list_cameras.sort(key=lambda x:x[0])
    return list_cameras

PTN_IMAGES_IN_CAMERA = re.compile("^#(?P<num>\d+)\s+(?P<filename>[^\s]+)\s+")
def get_list_files(port):
    list_file = []
    output = get_lines("gphoto2 --port " + port + " --list-files")
    lines = [line.decode('utf-8') for line in output]
    for line in lines:
#         print(line)
        m = PTN_IMAGES_IN_CAMERA.match(line)
        if m is not None:
            list_file.append([m.group("num"), m.group("filename")])
    return list_file

def get_all_images(list_cameras, outputPath, overwrite=False):
    cwd = os.getcwd()
    wd = os.path.normpath(os.path.join(cwd, outputPath))
    if not os.path.exists(wd):
        os.mkdir(wd)
    os.chdir(wd)
    for camera in list_cameras:
        camDirPath = os.path.join(wd,camera[0])
        if not os.path.exists(camDirPath):
            os.mkdir(camDirPath)
        else:
            shutil.rmtree(camDirPath)
            os.mkdir(camDirPath)
        print(camera)
        subprocess.run(["gphoto2", "--port", camera[2], "--get-all-files", "--filename", camera[0] +"/%04n.%C"])
    os.chdir(cwd)


#
# Set Image Formats
#
# Choice: 0 Large Fine JPEG
# Choice: 1 Large Normal JPEG
# Choice: 2 Medium Fine JPEG
# Choice: 3 Medium Normal JPEG
# Choice: 4 Small Fine JPEG
# Choice: 5 Small Normal JPEG
# Choice: 6 Smaller JPEG
# Choice: 7 Tiny JPEG
# Choice: 8 RAW + Large Fine JPEG
# Choice: 9 RAW
#
def set_imageformat(port, formatNum):
    output = get_lines("gphoto2 --port " + port + " --set-config imageformat="+str(formatNum))
    return [line for line in output]

def set_allCameras_imageformat(list_ports, formatNum):
    for port in list_ports:
        set_imageformat(port, formatNum)
    return 0


#
# format SD Cards
#
def delete_all_files(port):
    output = get_lines("gphoto2 --port " + port + " --delete-all-files --recurse")
    return [line for line in output]

def delete_all_files_inAllCameras(list_ports):
    for port in list_ports:
        delete_all_files(port)
    return 0    

#
# Sync Clocks
#
PTN_DATETIME = re.compile("^Current:\s+(?P<datetime>\d+)")
def check_clocks(list_ports):
    for port in list_ports:
        output = get_lines("gphoto2 --port " + port + " --get-config datetime")
        lines = [line for line in output]
        m = PTN_DATETIME.match(lines[2].decode("utf-8"))
        dtStr = m.group("datetime")
        dt = datetime.fromtimestamp(int(dtStr))
        print(dt.isoformat())
def set_clocks_now(list_ports):
    for port in list_ports:
        output = get_lines("gphoto2 --port " + port + " --set-config datetime=now")
        lines = [line for line in output]