import os  # interface with path
import sys  # pass arguments command line
import fnmatch  # compare substring filename

# get par or rec file, returns file

defaultPath = "/mnt/Filbey/common/Studies/MJX_WF/examples/NL"


def find_par_or_rec(path):
    raw_data_list = []
    for roots, dirs, files in os.walk(path):
        for file in files:
            if fnmatch.fnmatch(file, "*.REC"):
                # print(file)
                raw_data_list.append(file)
                return raw_data_list


def find_t1(path=defaultPath):
    file_name_list = []
    for file in find_par_or_rec(path):
        if fnmatch.fnmatch(file, "*T1*"):
            file_name_list.append(file)
    return file_name_list


def find_dwi(path=defaultPath):
    dwi_list = []
    for file in find_par_or_rec(path):
        if fnmatch.fnmatch(file, "*dwi*"):
            dwi_list.append(file)
    return dwi_list


def find_fmap(path=defaultPath):
    fmap_list = []
    for file in find_par_or_rec(path):
        if fnmatch.fnmatch(file, "*topup*"):
            fmap_list.append(file)
    return fmap_list


def find_task(path=defaultPath):
    task_list = []
    for file in find_par_or_rec(path):
        if fnmatch.fnmatch(file, "*bold*"):
            if not fnmatch.fnmatch(file, "*topup*"):
                task_list.append(file)
        return task_list


print(find_t1())
print(find_dwi())
print(find_fmap())
print(find_task())
