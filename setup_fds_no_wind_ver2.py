import os
import errno

# import numpy as np
# from typing import List, Any, Union
from typing import List, Any, Union

i_list: List[Union[int, Any]] = [1, 2, 1, 4, 5, 1, 4, 5, 2, 5, 5]
j_list: List[Union[int, Any]] = [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 4]
k_list: List[Union[int, Any]] = [1, 1, 3, 1, 1, 6, 1, 1, 6, 3, 1]


#   import shutil

# Definitions of number of grids


# Global definitions
# grids = [1, 2, 4, 8]  # cell sizes in mm


def read_file_as_lines(fn):
    f_handle = open(fn)
    data_line = f_handle.readlines()
    f_handle.close()
    return data_line


def read_file_as_single_text(fn):
    f_handle = open(fn, 'r')
    single_text = f_handle.read()  # type: str
    f_handle.close()
    return single_text


def replace_grid_info(mesh_line1_local, mesh_line2_local):
    # Read default fds file as individual lines
    fds_file_data_line = read_file_as_lines('case10_no_wind.fds')

    h = open('temp_output.fds', "w+")
    first_time = True
    for line in fds_file_data_line:
        #               remove leading spaces
        line_left = line.lstrip()
        keyword = line_left[:max(line_left.find(' '), 0) or None]
        if keyword != '&MESH':
            h.write(line)
        elif first_time:
            first_time = False
            h.write(mesh_line1_local)
            h.write(mesh_line2_local)
    h.seek(0)  # Move to the beginning of the temporary file
    fds_file_data_local = h.read()
    h.close()
    return fds_file_data_local


def change_fds_run_file(input_data, par_type_local, num_core, dir_name):  # Changes the run_fds.sh file, rep
    number_of_processors = int(((num_core - 0.1) // 20) + 1)
    time = '15:00:00'
    #           for testing: time = '000:29:00'
    if par_type_local == 'mpi':
        task_per_node = num_core
        cpus_per_task = 1
    elif par_type == 'openmp':
        task_per_node = 1
        cpus_per_task = int(num_core)
    else:
        task_per_node = num_core
        cpus_per_task = int(20 // num_core)
    new_file_data = input_data.replace('#SBATCH --tasks-per-node=1',
                                       '#SBATCH --tasks-per-node=' + str(task_per_node))
    new_file_data = new_file_data.replace('#SBATCH -N 1', '#SBATCH -N ' + str(number_of_processors))
    new_file_data = new_file_data.replace('#SBATCH -t 10:00:00', '#SBATCH -t ' + time)
    new_file_data = new_file_data.replace('#SBATCH --cpus-per-task=1', '#SBATCH --cpus-per-task=' + str(cpus_per_task))

    # Write the file run file to the directory
    f_run_fds6 = open(dir_name + '/run_fds6.sh', 'w')
    f_run_fds6.write(new_file_data)
    f_run_fds6.close()
    return


def write_to_shell_script(par_type_local, fn, fn_ext):
    # Write a line to the command file for aurora
    shell_file_data.write('cd ' + directory + '\n')
    shell_file_data.write('sbatch -J ' + par_type_local + '_wind_' + fn + ' run_fds6.sh ' + fn_ext + '\n')
    shell_file_data.write('cd ../.. \n \n')
    return


def write_fds_file(par_type_local, fds_file_data_new, number_of_grids_local):
    directory_local = './' + par_type_local + '/' + str(number_of_grids_local)
    try:
        os.makedirs(directory_local)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        else:
            print("\nBE CAREFUL! Directory %s already exists." % directory_local)

    # Write the fds file out again
    fds_filename = 'case10_no_wind_' + str(number_of_grids_local)
    fds_filename_ext_local = fds_filename + '.fds'
    fds_file_data_new = fds_file_data_new.replace('case10_no_wind', fds_filename)
    # writing of the actual fds file
    f = open(directory_local + '/' + fds_filename_ext_local, 'w')
    f.write(fds_file_data_new)
    f.close()
    return directory_local, fds_filename_ext_local


def change_data_fds_input_file(grid_local_index: int):  # do changes to mesh and velocity tolerance
    i_divider = i_list[grid_local_index]
    j_divider = j_list[grid_local_index]
    k_divider = k_list[grid_local_index]

    i_cells = int(100 / i_divider)
    j_cells = int(100 / j_divider)
    k_cells = int(100 / k_divider)
    x_max = -10 + 20 / i_divider
    y_max = -10 + 20 / j_divider
    z_max = 12 / k_divider
    DX = 20 / i_divider
    DY = 20 / j_divider
    DZ = 12 / k_divider

    mesh_line1 = "&MESH IJK = " + str(i_cells) + ", " + str(j_cells) + ", " + str(k_cells) + ", " + \
                 "XB = -10.0, " + str(x_max) + ", -10.0, " + str(y_max) + ", 0.0, " + str(z_max) + \
                 ", MULT_ID = 'MESH_MULT' / " + '\n'
    mesh_line2 = "&MULT ID = 'MESH_MULT'" + \
                 ", DX = " + str(DX) + \
                 ", DY = " + str(DY) + \
                 ", DZ = " + str(DZ) + \
                 ", I_UPPER = " + str(i_divider - 1) + \
                 ", J_UPPER = " + str(j_divider - 1) + \
                 ", K_UPPER = " + str(k_divider - 1) + " /" + '\n'

    fds_input = replace_grid_info(mesh_line1, mesh_line2)  # replace geometry information of grid

    return fds_input


# main program
parallel_type = ['mpi', 'openmp', 'hybrid']

run_file_data = read_file_as_single_text('run_fds6.sh')  # Read in the default run file as a single text document

# Open shell file for setting up run of cases for write
# This file is first closed at the end
shell_file_data = open('run_all.sh', 'w')

for par_type in parallel_type:
    # go through all different grid combinations
    grid_index: int
    for grid_index, item in enumerate(i_list):
        number_of_grids = i_list[grid_index] * j_list[grid_index] * k_list[grid_index]  # calculate number of grids
        fl_name = str(number_of_grids)
        if par_type == 'hybrid' and (grid_index == 0 or grid_index > 7):
            continue
        if par_type == 'openmp':
            fds_file_data = change_data_fds_input_file(0)  # only have single grid, index=0
        else:
            fds_file_data = change_data_fds_input_file(grid_index)  # Change grid and return fds_file_data
        directory, fds_filename_ext = write_fds_file(par_type, fds_file_data, number_of_grids)
        change_fds_run_file(run_file_data, par_type, number_of_grids, directory)  # change fds run file
        write_to_shell_script(par_type, fl_name, fds_filename_ext)  # Write to shell script

shell_file_data.close()  # Close the shell file

# Allow execute of shell batch file on linux systems
os.chmod('run_all.sh', 0o744)

# remove temp file
if os.path.exists("temp_output.fds"):
    os.remove("temp_output.fds")

print("\nScript ran successfully")
