import time
import os
import numpy as np
from datetime import datetime
from tifffile import imread, imwrite

import sols_microscope as sols

if __name__ == '__main__': # required block for sols_microscope
    # Create scope:
    scope = sols.Microscope(max_allocated_bytes=100e9, ao_rate=1e4)
    dataz = sols.DataZ() # create postprocessor for software autofocus

    # Apply settings at least once: (required)
    scope.apply_settings(
        channels_per_slice=("LED",),# ('LED','405','488','561','640')
        power_per_channel=(10,),    # match channels 0-100% i.e. (5,0,20,30,100)
        emission_filter='Shutter',  # reset later, options are:
        # 'Shutter', 'Open'
        # 'ET450/50M', 'ET525/50M', 'ET600/50M', 'ET690/50M'
        # 'ZET405/488/561/640m', 'LP02-488RU', 'LP02-561RU', '(unused)'
        illumination_time_us=1*1e3, # reset later
        height_px=500,                          # 12 -> 500  (typical range)
        width_px=1020,                          # 60 -> 1020 (typical range)
        voxel_aspect_ratio=2,                   # 2  -> 10   (typical range)
        scan_range_um=100,                      # 10 -> 100  (typical range)
        volumes_per_buffer=1,                   # usually 1, can be more...
        focus_piezo_z_um=(0,'relative'),        # = don't move
        XY_stage_position_mm=(0,0,'relative'),  # = don't move
        ).get_result()
    
    # Get current XY position for moving back at the end of the script:
    x_mm_0, y_mm_0 = scope.XY_stage_position_mm
    
    # Setup minimal positions for no moving (current FOV only):
    XY_stage_positions      = ((0, 0, 'relative'),)
    focus_piezo_positions   = [[0,'relative'],]

    # Optional XYZ moves from position lists collected by GUI:
    # -> uncomment and copy paste lists to use...
    # ***CAUTION WHEN MOVING XY STAGE -> DOUBLE CHECK POSITIONS***
##    XY_stage_positions      = [ # copy past lists in here:
##        # e.g. here's 2 XY positions:
##        [-0.412, -4.9643],
##        [-0.528025, -4.9643],
##        ]
##    focus_piezo_positions   = [ # copy past lists in here:
##        # e.g. here's 2 focus positions:
##        48,
##        48,
##        ]
##    # convert to correct format for .apply_settings():
##    for xy in XY_stage_positions:
##        xy.append('absolute')
##    for i, z in enumerate(focus_piezo_positions):
##            focus_piezo_positions[i] = [z, 'absolute']

    # Get number of positions:
    assert len(focus_piezo_positions) == len(XY_stage_positions)
    positions = len(XY_stage_positions)

    # Make folder name for data:
    folder_label = 'sols_acquisition_template'  # edit name to preference
    dt = datetime.strftime(datetime.now(),'%Y-%m-%d_%H-%M-%S_000_')
    folder_name = dt + folder_label

    # Decide parameters for acquisition:
    time_points = 2     # how many time points for full acquisition?
    time_delay_s = None # delay between full acquisitions in seconds (or None)
    # -> should run autofocus every few minutes to keep focus (< ~300s/5min?)
    # autofocus every acquisition? or run autofocus at a higher rate?
    autofocus_rate = 1  # 1 = once per acquire, 2 = twice per acquire, 3 =...
    # -> can be used to keep focus but reduce data size/photodose

    # Run acquisition: (tzcyx)
    if time_delay_s is not None:
        time_delay_s = time_delay_s / autofocus_rate
    iterations = time_points * autofocus_rate
    current_time_point = 0
    current_autofocus_point = 1
    for i in range(iterations):
        print('\nRunning iteration %i:'%i)
        # check if full acquisition or software autofocus:
        full_acquire = False
        if not i%autofocus_rate:
            full_acquire = True
        # start timer:
        t0 = time.perf_counter()
        scope.snoutfocus() # apply thermal stabilization routine
        for p in range(positions):
            # Move to XYZ position:
            # -> also applies 'z_change_um' for software autofocus (if active)
            scope.apply_settings(focus_piezo_z_um=focus_piezo_positions[p],
                                 XY_stage_position_mm=XY_stage_positions[p])
            if full_acquire: # set setting and acquire:
                print('-> full acquisition %i (position:%i)'%(
                    current_time_point, p))
                # 488 example:
                filename488 = '488_%06i_%06i.tif'%(current_time_point, p)
                scope.apply_settings(
                    channels_per_slice=('488',),
                    power_per_channel=(5,),
                    emission_filter='LP02-488RU',
                    illumination_time_us=1*1e3,
                    voxel_aspect_ratio=2,
                    scan_range_um=100,
                    volumes_per_buffer=1,
                    )
                scope.acquire(filename=filename488,
                              folder_name=folder_name,
                              description='488 something...',
                              preview_only=False)
                # 561 example:
                filename561 = '561_%06i_%06i.tif'%(current_time_point, p)
                scope.apply_settings(
                    channels_per_slice=('561',),
                    power_per_channel=(5,),
                    emission_filter='LP02-561RU',
                    illumination_time_us=1*1e3,
                    voxel_aspect_ratio=2,
                    scan_range_um=100,
                    volumes_per_buffer=1,
                    )
                scope.acquire(filename=filename561,
                              folder_name=folder_name,
                              description='561 something...',
                              preview_only=False)
            # Software autofocus (optional):
            else:
                print('-> autofocus acquisition (position:%i)'%p)
                # 488 autofocus example:
                filename488 = 'af488_%06i_%06i_%06i.tif'%(
                    (current_time_point - 1), p, current_autofocus_point)
                # trim down settings for increased speed/reduced photodose:
                scope.apply_settings(
                    channels_per_slice=('488',),
                    power_per_channel=(1,),
                    emission_filter='LP02-488RU',
                    illumination_time_us=1*1e3,
                    voxel_aspect_ratio=10,
                    scan_range_um=100,
                    volumes_per_buffer=1,
                    )
                scope.acquire(filename=filename488,
                              folder_name=folder_name,
                              description='488 autofocus',
                              preview_only=True)
            # run autofocus routine:
            scope.finish_all_tasks() # must finish before looking at preview!
            autofocus_filename = filename488 # which filename for autofocus?
            preview = imread( # 1 2D image from preview! (1 vol, 1 ch)
                folder_name + '\preview\\' + autofocus_filename)
            z_um = dataz.estimate(preview, # parameters must match preview file!
                                  scope.height_px,
                                  scope.width_px,
                                  scope.preview_line_px,
                                  scope.preview_crop_px,
                                  scope.timestamp_mode)
            if i == 0: # get set point for z from first preview (set by user)
                z_um_0 = z_um
            z_change_um = z_um - z_um_0
            print('Sample z-axis change um: %0.3f\n'%z_change_um)
            # update focus piezo positions with measured drift:
            focus_piezo_positions[p] = [scope.focus_piezo_z_um + z_change_um,
                                        'absolute']
        # finish timing and increment time point if applicable:
        loop_time_s = time.perf_counter() - t0
        if full_acquire:
            current_time_point += 1
            current_autofocus_point = 1
            if current_time_point == time_points:
                break # avoid last delay/autofocus routine
        else:
            current_autofocus_point += 1
        # Apply time delay if applicable:
        if time_delay_s is not None:
            if time_delay_s > loop_time_s:
                print('\nApplying time_delay_s: %0.2f'%time_delay_s)
                time.sleep(time_delay_s - loop_time_s)
            else:
                print('\n***WARNING***')
                print('time_delay_s not applied (loop_time_s > time_delay_s)')

    # return to 'zero' starting position for user convenience
    scope.apply_settings(focus_piezo_z_um=focus_piezo_positions[0],
                         XY_stage_position_mm=(x_mm_0, y_mm_0, 'absolute'))
    scope.close()
