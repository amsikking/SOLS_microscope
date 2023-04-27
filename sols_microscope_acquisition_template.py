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
        filter_wheel_position=0,    # reset later
        ## filter wheel options:        0:blocked,      1:open
        # 2:ET450/50M,  3:ET525/50M,    4:ET600/50M,    5:ET690/50M
        # 6:ZETquadM,   7:LP02-488RU    8:LP02-561RU    9:empty
        illumination_time_us=1*1e3, # reset later
        height_px=500,                          # 12 -> 500  (typical range)
        width_px=1020,                          # 60 -> 1020 (typical range)
        voxel_aspect_ratio=2,                   # 2  -> 10   (typical range)
        scan_range_um=100,                      # 10 -> 100  (typical range)
        volumes_per_buffer=1,                   # usually 1, can be more...
        focus_piezo_z_um=(0,'relative'),        # = don't move
        XY_stage_position_mm=(0,0,'relative'),  # = don't move
        ).join()

    # Make folder name for data:
    folder_label = 'sols_acquisition_template'  # edit name to preference
    dt = datetime.strftime(datetime.now(),'%Y-%m-%d_%H-%M-%S_000_')
    folder_name = dt + folder_label

    # Decide on optional XYZ moves:
    # for example options 1) to 3) -> uncomment and edit to try...   
    # start by getting current XY stage position:
    x_mm_0, y_mm_0 = scope.XY_stage_position_mm

    # option 1) no moving: (current FOV only)
    XY_stage_positions      = ((0, 0, 'relative'),)
    focus_piezo_positions   = [[0,'relative'],]

    # option 2) 'absolute' moves from metadata collected from scouting in GUI
    # for exmple here's 2 FOV's:
    # ***CAUTION WHEN MOVING XY STAGE -> DOUBLE CHECK POSITIONS FIRST***
##    XY_stage_positions      = ( # tuple for non mutable
##        (0.2421, -4.5275, 'absolute'),
##        (0.2728, -4.5275, 'absolute')) # ~1 FOV to the 'right'
##    focus_piezo_positions   = [ # list for autofocus update
##        [42.7666473,'absolute'],
##        [42.4185723,'absolute']] # some focus drift between fields
    
    # option 3) 'absolute' moves based on XY tile size from current settings:
    # for example here's some positions for a 2x2 tile:
    # ***CAUTION WHEN MOVING XY STAGE -> DOUBLE CHECK POSITIONS FIRST***
##    move_pct = 90 # how much do you want to move? 100% = 1 full FOV
##    ud_move_mm = 1e-3 * scope.scan_range_um * move_pct / 100
##    lr_move_mm = 1e-3 * scope.width_px * sols.sample_px_um * move_pct / 100
##    XY_stage_positions = ( # pick efficient order e.g. raster
##        (x_mm_0, y_mm_0, 'absolute'),                           # 'zero'
##        (x_mm_0 + lr_move_mm, y_mm_0, 'absolute'),              # 'right'
##        (x_mm_0 + lr_move_mm, y_mm_0 + ud_move_mm, 'absolute'), # 'right'+'up'
##        (x_mm_0, y_mm_0 + ud_move_mm, 'absolute'),              # 'up'
##        )
##    focus_piezo_positions   = len(XY_stage_positions) * [[0,'relative']]

    # Get number of positions:
    assert len(focus_piezo_positions) == len(XY_stage_positions)
    positions = len(XY_stage_positions)

    # Run acquisition: (tzcyx)
    iterations = 2      # how many iterations?
    time_delay_s = 0    # optional time delay
    for i in range(iterations):
        scope.snoutfocus() # apply thermal stabilization routine
        for p in range(positions):
            # Move to XYZ position:
            # -> also applies 'z_change_um' for software autofocus (if active)
            scope.apply_settings(focus_piezo_z_um=focus_piezo_positions[p],
                                 XY_stage_position_mm=XY_stage_positions[p])
            # Multi-color acquisition:
            filename488 = '488_%06i_%03i.tif'%(i, p)
            scope.apply_settings(illumination_time_us=1*1e3,
                                 channels_per_slice=('488',),
                                 power_per_channel=(5,),
                                 filter_wheel_position=7)
            scope.acquire(filename=filename488,
                          folder_name=folder_name,
                          description='488 something...',
                          preview_only=False)
            filename561 = '561_%06i_%03i.tif'%(i, p)
            scope.apply_settings(illumination_time_us=1*1e3,
                                 channels_per_slice=('561',),
                                 power_per_channel=(5,),
                                 filter_wheel_position=8)
            scope.acquire(filename=filename561,
                          folder_name=folder_name,
                          description='561 something...',
                          preview_only=False)
            # Software autofocus (optional):
            scope.finish_all_tasks() # must finish before looking at preview!
            autofocus_filename = filename488 # which filename for autofocus?
            # get parameters to estimate z: (these must match the chosen file!)
            h_px, w_px = scope.height_px, scope.width_px
            l_px, c_px = scope.preview_line_px, scope.preview_crop_px
            tsm = scope.timestamp_mode
            if i == 0: # get set point for z from first preview (set by user)
                preview_0 = imread( # 1 2D image from preview! (1 vol, 1 ch)
                    folder_name + '\preview\\' + autofocus_filename)
                z_um_0 = dataz.estimate(preview_0, h_px, w_px, l_px, c_px, tsm)
            preview_n = imread(     # 1 2D image from preview! (1 vol, 1 ch)
                folder_name + '\preview\\' + autofocus_filename)
            z_um_n = dataz.estimate(preview_n, h_px, w_px, l_px, c_px, tsm)
            z_change_um = z_um_n - z_um_0
            print('Sample z-axis change um:', z_change_um)
            # update focus piezo positions with measured drift:
            focus_piezo_positions[p] = [scope.focus_piezo_z_um + z_change_um,
                                        'absolute']
        # Apply time delay:
        if i + 1 == iterations:
            break # avoid last unecessary delay
        time.sleep(time_delay_s)
    # return to 'zero' starting position for user convenience
    scope.apply_settings(focus_piezo_z_um=focus_piezo_positions[0],
                         XY_stage_position_mm=(x_mm_0, y_mm_0, 'absolute'))
    scope.close()
