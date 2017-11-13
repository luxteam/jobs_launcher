import pyopencl as cl


for cl_platform in cl.get_platforms():
    for cl_device in cl_platform.get_devices():
        print("===============================================================")
        print("Platform name:", cl_platform.name)
        print("Platform profile:", cl_platform.profile)
        print("Platform vendor:", cl_platform.vendor)
        print("Platform version:", cl_platform.version)
        print("---------------------------------------------------------------")
        print("Device name:", cl_device.name)
        print("Device type:", cl.device_type.to_string(cl_device.type))
        print("Device memory: ", cl_device.global_mem_size // 1024 // 1024, 'MB')
        print("Device max clock speed:", cl_device.max_clock_frequency, 'MHz')
        print("Device compute units:", cl_device.max_compute_units)
        print("Device max work group size:", cl_device.max_work_group_size)
        print("Device max work item sizes:", cl_device.max_work_item_sizes)




