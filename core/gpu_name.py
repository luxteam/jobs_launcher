#!/usr/bin/env python3

import sys
from ctypes import *


# -----------------------------------------------------------------------------

# returns string name for opencl device by specified device ID
def getDeviceNameByID(deviceID):
    windll.opencl.clGetDeviceInfo.resType = c_int
    windll.opencl.clGetDeviceInfo.argtypes = [c_void_p, c_uint, c_uint, c_void_p, c_void_p]
    nameLen = c_uint(0)
    CL_DEVICE_NAME = 0x102B
    status = windll.opencl.clGetDeviceInfo(deviceID, CL_DEVICE_NAME, 0, None, byref(nameLen))
    if status != 0:
        return 'N/A'
    name = (c_char * nameLen.value)(b'\0')
    status = windll.opencl.clGetDeviceInfo(deviceID, CL_DEVICE_NAME, nameLen, byref(name), None)
    if status != 0:
        return 'N/A'
    return bytearray(name).strip(b'\0').decode()


# returns concatenated all cl GPU devices on all cl platforms
# should return in a form like: "Devastator+Bonaire" or "Bonaire"
def getAllDeviceNames():
    windll.opencl.clGetPlatformIDs.resType = c_int
    windll.opencl.clGetPlatformIDs.argtypes = [c_uint, c_void_p, c_void_p]

    numPlatforms = c_uint()
    status = windll.opencl.clGetPlatformIDs(0, None, byref(numPlatforms))
    if status != 0:
        return 'N/A'
    platforms = (c_ulong * numPlatforms.value)()
    status = windll.opencl.clGetPlatformIDs(numPlatforms, byref(platforms), None)
    if status != 0:
        return 'N/A'

    allNames = list()

    for platformIndex in range(0, numPlatforms.value):

        windll.opencl.clGetDeviceIDs.resType = c_int
        windll.opencl.clGetDeviceIDs.argtypes = [c_void_p, c_ulonglong, c_uint, c_void_p, c_void_p]

        CL_DEVICE_TYPE_GPU = 4
        count = 0
        numDevices = c_uint()
        status = windll.opencl.clGetDeviceIDs(platforms[platformIndex], CL_DEVICE_TYPE_GPU, 0, None, byref(numDevices));
        if status == 0:
            devices = (c_void_p * int(numDevices.value))()

            status = windll.opencl.clGetDeviceIDs(platforms[platformIndex], CL_DEVICE_TYPE_GPU, numDevices,
                                                  byref(devices), None);
            if status == 0:
                for j in range(0, numDevices.value):
                    deviceName = getDeviceNameByID(devices[j])
                    allNames.append(deviceName)
                    count += 1

    return '+'.join(allNames), count


def main():
    allDeviceNames, count = getAllDeviceNames()
    print(allDeviceNames)
    return count


exit(main())
