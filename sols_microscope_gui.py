import os
from datetime import datetime
import tkinter as tk

import sols_microscope as sols
import tkinter_compound_widgets as tki_cw

class GuiTransmittedLight:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='TRANSMITTED LIGHT', bd=6)
        frame.grid(row=0, column=0, padx=20, pady=20, sticky='n')
        self.power = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='470-850nm (%)',
            checkbox_default=True,
            slider_length=200,
            default_value=25)

class GuiLaserBox:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='LASER BOX', bd=6)
        frame.grid(row=1, column=0, padx=20, pady=20, sticky='n')
        self.power405 = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='405nm (%)',
            color='magenta',
            slider_length=200,
            default_value=5)
        self.power488 = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='488nm (%)',
            color='blue',
            slider_length=200,
            default_value=5,
            row=1)
        self.power561 = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='561nm (%)',
            color='green',
            slider_length=200,
            default_value=5,
            row=2)
        self.power640 = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='640nm (%)',
            color='red',
            slider_length=200,
            default_value=5,
            row=3)

class GuiFilterWheel:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='FILTER WHEEL', bd=6)
        frame.grid(row=0, column=1, rowspan=2, padx=20, pady=20, sticky='n')
        self.filter = tki_cw.RadioButtons(
            frame,
            label='options',
            buttons=('0: Shutter',
                     '1: Open',
                     '2: ET450/50M',
                     '3: ET525/50M',
                     '4: ET600/50M',
                     '5: ET690/50M',
                     '6: ZETquadM',
                     '7: LP02-488RU',
                     '8: LP02-561RU',
                     '9: (available)'),
            default_position=6)

class GuiGalvo:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='GALVO', bd=6)
        frame.grid(row=0, column=2, padx=20, pady=20, sticky='n')
        self.scan_range_um = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='~scan range (um)',
            checkbox_enabled=False,
            slider_length=350,
            tickinterval=10,
            min_value=1,
            max_value=100,
            default_value=50)
        self.voxel_aspect_ratio = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='~voxel aspect ratio',
            checkbox_enabled=False,
            slider_length=350,
            tickinterval=10,
            min_value=2,
            max_value=80,         
            default_value=25,
            row=1)

class GuiCamera:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='CAMERA', bd=6)
        frame.grid(row=1, column=2, padx=20, pady=20, sticky='n')
        self.illumination_time_ms = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='illumination time (ms)',
            checkbox_enabled=False,
            slider_length=350,
            tickinterval=10,
            min_value=1,
            max_value=250,
            default_value=1,
            columnspan=2)
        self.height_px = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='height pixels',
            orient='vertical',
            checkbox_enabled=False,
            slider_length=250,
            slider_flipped=True,
            min_value=12,
            max_value=500,
            default_value=250,
            row=1)
        self.width_px = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='width pixels',
            checkbox_enabled=False,
            slider_length=250,
            min_value=60,
            max_value=1000,
            default_value=1000,
            row=2,
            column=1,
            sticky='s')
        tki_cw.CanvasRectangleSliderTrace2D(
            frame, self.width_px, self.height_px, row=1, column=1)

class GuiFocusPiezo:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='FOCUS PIEZO', bd=6)
        frame.grid(row=0, column=3, rowspan=2, padx=20, pady=20, sticky='n')
        self.min_value = 0
        self.max_value = 100
        self.center_value = int(round((self.max_value - self.min_value) / 2))
        self.position_um = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='position (um)',
            orient='vertical',
            checkbox_enabled=False,
            tickinterval=10,
            min_value=self.min_value,
            max_value=self.max_value,
            default_value=gui_acquisition.focus_piezo_z_um)
        # Convenience buttons:
        self.button_width = 10
        self.button_height = 2
        self.button_up = tk.Button(frame, text="up (5um)",
                                   command=self.move_up,
                                   width=self.button_width,
                                   height=self.button_height)
        self.button_up.grid(row=0, column=1, padx=10, pady=10, sticky='n')
        self.button_center = tk.Button(frame, text="center",
                                       command=self.move_center,
                                       width=self.button_width,
                                       height=self.button_height)
        self.button_center.grid(row=0, column=1, padx=10, pady=10)
        self.button_down = tk.Button(frame, text="down (5um)",
                                     command=self.move_down,
                                     width=self.button_width,
                                     height=self.button_height)
        self.button_down.grid(row=0, column=1, padx=10, pady=10, sticky='s')

    def move_up(self):
        up_value = self.position_um.spinbox_value - 5
        if self.min_value <= up_value <= self.max_value:
            self.update_position_value(up_value)

    def move_center(self):
        self.update_position_value(self.center_value)

    def move_down(self):
        down_value = self.position_um.spinbox_value + 5
        if self.min_value <= down_value <= self.max_value:
            self.update_position_value(down_value)

    def update_position_value(self, position_um):
        self.position_um.tk_spinbox_value.set(position_um)
        self.position_um.tk_slider_value.set(position_um)
        self.position_um.spinbox_value = position_um

class GuiXYStage:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='XY STAGE', bd=6)
        frame.grid(row=1, column=3, padx=20, pady=20, sticky='s')
        self.last_move = tki_cw.Textbox(
            frame,
            label='last move',
            default_text='None',
            height=1,
            width=15)
        self.last_move.grid(row=0, column=1, padx=10, pady=10)
        self.position = tki_cw.Textbox(
            frame,
            label='position (mm)',
            height=1,
            width=20)
        self.position.grid(row=2, column=1, padx=10, pady=10)
        self.update_position(gui_acquisition.XY_stage_position_mm)
        # Convenience buttons:
        self.button_width = 10
        self.button_height = 2
        self.button_up = tk.Button(frame, text="up",
                                   command=self.move_up,
                                   width=self.button_width,
                                   height=self.button_height)
        self.button_up.grid(row=1, column=1, padx=10, pady=10)
        self.move_up = False
        self.button_down = tk.Button(frame, text="down",
                                     command=self.move_down,
                                     width=self.button_width,
                                     height=self.button_height)
        self.button_down.grid(row=3, column=1, padx=10, pady=10)
        self.move_down = False
        self.button_left = tk.Button(frame, text="left",
                                   command=self.move_left,
                                   width=self.button_width,
                                   height=self.button_height)
        self.button_left.grid(row=2, column=0, padx=10, pady=10)
        self.move_left = False
        self.button_right = tk.Button(frame, text="right",
                                     command=self.move_right,
                                     width=self.button_width,
                                     height=self.button_height)
        self.button_right.grid(row=2, column=3, padx=10, pady=10)
        self.move_right = False
        # Size of move:
        self.step_size_pct = tki_cw.CheckboxSliderSpinbox(
            frame,
            label='step size (% of FOV)',
            checkbox_enabled=False,
            slider_length=250,
            tickinterval=9,
            min_value=5,
            max_value=95,
            default_value=95,
            row=4,
            columnspan=4)

    def update_last_move(self, text):
        self.last_move.textbox.delete('1.0', '10.0')
        self.last_move.textbox.insert('1.0', text)

    def update_position(self, position_mm):
        self.position.textbox.delete('1.0', '10.0')
        self.position.textbox.insert(
                    '1.0', 'X=%0.3f, Y=%0.3f'%(position_mm[0], position_mm[1]))

    def move_up(self):
        self.move_up = True

    def move_down(self):
        self.move_down = True

    def move_left(self):
        self.move_left = True

    def move_right(self):
        self.move_right = True

class GuiAcquisition:
    def __init__(self, master):
        self.frame = tk.LabelFrame(master, text='ACQUISITION', bd=6)
        self.frame.bind('<Enter>', self.get_tkfocus)
        self.frame.grid(
            row=0, column=4, rowspan=2, padx=20, pady=20, sticky='n')
        self.spinbox_width = 20
        self.button_width = 25
        self.button_height = 2
        self.gui_delay_ms = int(1e3 * 1 / 30) # 30fps/video rate target
        # init GUI buttons:
        self.init_live_mode_button()
        self.init_scout_mode_button()
        self.init_snap_button()
        self.init_snap_and_save_button()
        self.init_volumes_spinbox()
        self.init_acquisitions_spinbox()
        self.init_delay_spinbox()
        self.init_apply_settings_and_print_button()
        self.init_label_textbox()
        self.init_description_textbox()
        self.init_run_aquisition_button()
        self.init_cancel_aquisition_button()
        # init scope:
        self.scope = sols.Microscope(max_allocated_bytes=100e9, ao_rate=1e4)
        self.scope.XY_stage.set_velocity(5, 5) # edit for taste
        # get attributes from GUI defaults:
        self.channels_per_slice, self.power_per_channel = (
            self.get_channel_settings())
        self.filter_wheel_position = gui_filter_wheel.filter.position
        self.illumination_time_us = (
            1e3 * gui_camera.illumination_time_ms.spinbox_value)
        self.height_px = gui_camera.height_px.spinbox_value
        self.width_px = gui_camera.width_px.spinbox_value
        self.voxel_aspect_ratio = gui_galvo.voxel_aspect_ratio.spinbox_value
        self.scan_range_um = gui_galvo.scan_range_um.spinbox_value
        self.volumes_per_buffer = self.volumes_spinbox.spinbox_value
        # apply GUI settings:
        self.scope.apply_settings( # Mandatory call
            channels_per_slice=self.channels_per_slice,
            power_per_channel=self.power_per_channel,
            filter_wheel_position=self.filter_wheel_position,
            illumination_time_us=self.illumination_time_us,
            height_px=self.height_px,
            width_px=self.width_px,
            voxel_aspect_ratio=self.voxel_aspect_ratio,
            scan_range_um=self.scan_range_um,
            volumes_per_buffer=self.volumes_per_buffer,
            focus_piezo_z_um=(0, 'relative'),
            XY_stage_position_mm=(0, 0, 'relative')).join()
        # update attributes from hardware: (no xyz moves from init)
        self.focus_piezo_z_um = self.scope.focus_piezo_z_um
        self.XY_stage_position_mm = self.scope.XY_stage_position_mm
        # get XY stage limits for feedback in scout mode:
        self.XY_stage_x_min = self.scope.XY_stage.x_min
        self.XY_stage_y_min = self.scope.XY_stage.y_min
        self.XY_stage_x_max = self.scope.XY_stage.x_max
        self.XY_stage_y_max = self.scope.XY_stage.y_max
        # get scope ready:
        self.loop_snoutfocus()
        self.scope.acquire()

    def get_tkfocus(self, event):   # event is not used here (.bind)
        self.frame.focus_set()      # take from other widgets to force update

    def loop_snoutfocus(self):
        if not self.running_aquisition.get(): self.scope.snoutfocus()
        wait_ms = int(round(5 * 60 * 1e3))
        self.frame.after(wait_ms, self.loop_snoutfocus)

    def init_live_mode_button(self):
        self.live_mode_enabled = tk.BooleanVar()
        live_mode_button = tk.Checkbutton(self.frame,
                                          text='Live mode (On/Off)',
                                          variable=self.live_mode_enabled,
                                          command=self.init_live_mode,
                                          indicatoron=0,
                                          width=self.button_width,
                                          height=self.button_height)
        live_mode_button.grid(row=0, column=0, padx=10, pady=10)

    def init_live_mode(self):
        self.scout_mode_enabled.set(0)
        self.run_live_mode()

    def run_live_mode(self):
        if self.live_mode_enabled.get():
            self.apply_settings(single_volume=True)
            self.scope.acquire()
            self.frame.after(self.gui_delay_ms, self.run_live_mode)

    def init_scout_mode_button(self):
        self.scout_mode_enabled = tk.BooleanVar()
        scout_mode_button = tk.Checkbutton(self.frame,
                                           text='Scout mode (On/Off)',
                                           variable=self.scout_mode_enabled,
                                           command=self.init_scout_mode,
                                           indicatoron=0,
                                           width=self.button_width,
                                           height=self.button_height)
        scout_mode_button.grid(row=1, column=0, padx=10, pady=10)

    def init_scout_mode(self):
        self.live_mode_enabled.set(0)
        self.run_scout_mode()

    def run_scout_mode(self):
        if self.scout_mode_enabled.get():
            # Check Z:
            Z_pos_um = gui_focus_piezo.position_um.spinbox_value
            if Z_pos_um != self.focus_piezo_z_um:
                self.snap_volume(_print=False)
            # Check XY:
            def snap_volume_and_update_gui(gui_text): # save lines of code
                self.snap_volume(_print=False)
                gui_xy_stage.update_last_move(gui_text)
            # -> apply GUI move requests:
            move_pct = gui_xy_stage.step_size_pct.spinbox_value / 100
            self.scope.apply_settings().join() # update attributes
            scan_width_um = self.scope.width_px * sols.sample_px_um
            ud_move_mm = 1e-3 * self.scope.scan_range_um * move_pct
            lr_move_mm = 1e-3 * scan_width_um * move_pct
            if gui_xy_stage.move_up:
                self.scope.apply_settings(
                    XY_stage_position_mm=(0, ud_move_mm, 'relative'))
                snap_volume_and_update_gui('up (+Y)')
                gui_xy_stage.move_up = False
            elif gui_xy_stage.move_down:
                self.scope.apply_settings(
                    XY_stage_position_mm=(0, -ud_move_mm, 'relative'))
                snap_volume_and_update_gui('down (-Y)')
                gui_xy_stage.move_down = False
            elif gui_xy_stage.move_left:
                self.scope.apply_settings(
                    XY_stage_position_mm=(-lr_move_mm, 0, 'relative'))
                snap_volume_and_update_gui('left (-X)')
                gui_xy_stage.move_left = False
            elif gui_xy_stage.move_right:
                self.scope.apply_settings(
                    XY_stage_position_mm=(lr_move_mm, 0, 'relative'))
                snap_volume_and_update_gui('right (+X)')
                gui_xy_stage.move_right = False
            # -> check for joystick motion:
            self.scope.apply_settings().join() # update attributes
            self.XY_stage_position_mm = self.scope.XY_stage_position_mm
            joystick_motion = False
            if self.XY_stage_position_mm[0]   == self.XY_stage_x_min: # moving
                snap_volume_and_update_gui('left (-X)')
                joystick_motion = True
            elif self.XY_stage_position_mm[0] == self.XY_stage_x_max: # moving
                snap_volume_and_update_gui('right (+X)')
                joystick_motion = True
            elif self.XY_stage_position_mm[1] == self.XY_stage_y_min: # moving
                snap_volume_and_update_gui('down (-Y)')
                joystick_motion = True
            elif self.XY_stage_position_mm[1] == self.XY_stage_y_max: # moving
                snap_volume_and_update_gui('up (+Y)')
                joystick_motion = True
            if joystick_motion: # snap again to reduce motion blur
                self.snap_volume(_print=False) # consider .after to slow more
            else: # update position in gui (avoids erroneous position updates)
                gui_xy_stage.update_position(self.XY_stage_position_mm)
            self.frame.after(self.gui_delay_ms, self.run_scout_mode)

    def init_snap_button(self):
        snap_button = tk.Button(self.frame, text="Snap volume",
                                command=self.snap_volume,
                                width=self.button_width,
                                height=self.button_height)
        snap_button.grid(row=2, column=0, padx=10, pady=10)

    def snap_volume(self, _print=True):
        self.apply_settings(single_volume=True, _print=_print)
        self.scope.acquire()

    def init_snap_and_save_button(self):
        snap_and_save_button = tk.Button(self.frame,
                                         text="Snap volume and save",
                                         command=self.snap_volume_and_save,
                                         width=self.button_width,
                                         height=self.button_height)
        snap_and_save_button.grid(row=3, column=0, padx=10, pady=10)

    def snap_volume_and_save(self):
        self.apply_settings(single_volume=True, _print=True)
        folder_name = self.get_folder_name() + '_snap'
        self.scope.acquire(filename='snap.tif',
                           folder_name=folder_name,
                           description=self.description_textbox.text)

    def init_volumes_spinbox(self):
        self.volumes_spinbox = tki_cw.CheckboxSliderSpinbox(
            self.frame,
            label='Volumes per acquisition',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=1e3,
            default_value=1,
            row=4,
            width=self.spinbox_width)

    def init_acquisitions_spinbox(self):
        self.acquisitions_spinbox = tki_cw.CheckboxSliderSpinbox(
            self.frame,
            label='Acquisition number',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=1e6,
            default_value=1,
            row=5,
            width=self.spinbox_width)

    def init_delay_spinbox(self):
        self.delay_spinbox = tki_cw.CheckboxSliderSpinbox(
            self.frame,
            label='Inter-acquisition delay (s)',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=0,
            max_value=3600,
            default_value=0,
            row=6,
            width=self.spinbox_width)

    def init_apply_settings_and_print_button(self):
        apply_settings_and_print_button = tk.Button(
            self.frame,
            text="Print memory + time",
            command=self.apply_settings_and_print,
            width=self.button_width,
            height=self.button_height)
        apply_settings_and_print_button.bind('<Enter>', self.get_tkfocus)
        apply_settings_and_print_button.grid(row=7, column=0, padx=10, pady=10)

    def apply_settings_and_print(self):
        self.apply_settings(_print=True)

    def init_label_textbox(self):
        self.label_textbox = tki_cw.Textbox(self.frame,
                                            label='Folder label',
                                            default_text='sols_gui',
                                            row=8,
                                            width=self.spinbox_width)

    def init_description_textbox(self):
        self.description_textbox = tki_cw.Textbox(
            self.frame,
            label='Description',
            default_text='what are you doing?',
            row=9,
            width=self.spinbox_width)

    def init_run_aquisition_button(self):
        self.running_aquisition = tk.BooleanVar()
        run_aquisition_button = tk.Button(self.frame, text="Run aquisition",
                                          command=self.init_acquisition,
                                          width=self.button_width,
                                          height=self.button_height)
        run_aquisition_button.bind('<Enter>', self.get_tkfocus)
        run_aquisition_button.grid(row=10, column=0, padx=10, pady=10)

    def init_acquisition(self):
        print('\nAcquisition -> started')
        if self.live_mode_enabled.get(): self.live_mode_enabled.set(0)
        if self.scout_mode_enabled.get(): self.scout_mode_enabled.set(0)
        self.cancel_aquisition.set(0)
        self.running_aquisition.set(1)
        self.apply_settings(_print=True)
        self.folder_name = self.get_folder_name()
        self.description = self.description_textbox.text
        self.delay_s = self.delay_spinbox.spinbox_value
        self.acquisitions = self.acquisitions_spinbox.spinbox_value
        self.acquisition_count = 0
        self.run_acquisition()

    def run_acquisition(self):
        delay_s = self.delay_s
        if self.acquisition_count == 0: delay_s = 0 # avoid first delay_s
        self.scope.acquire(filename='%06i.tif'%self.acquisition_count,
                           folder_name=self.folder_name,
                           description=self.description,
                           delay_s=delay_s)
        self.acquisition_count += 1
        if (self.acquisition_count < self.acquisitions
            and not self.cancel_aquisition.get()): # acquire again
                wait_ms = int(round(
                    0.99 * 1e3 * (self.scope.buffer_time_s + delay_s)))
                self.frame.after(wait_ms, self.run_acquisition) 
        else: # finish up
            self.scope.finish_all_tasks()
            self.running_aquisition.set(0)
            print('Acquisition -> finished\n')

    def init_cancel_aquisition_button(self):
        self.cancel_aquisition = tk.BooleanVar()
        cancel_aquisition_button = tk.Button(
            self.frame, text="Cancel aquisition",
            command=self.cancel_acquisition,
            width=self.button_width,
            height=self.button_height)
        cancel_aquisition_button.bind('<Enter>', self.get_tkfocus)
        cancel_aquisition_button.grid(row=11, column=0, padx=10, pady=10)

    def cancel_acquisition(self):
        self.cancel_aquisition.set(1)
        print('\n ***Acquisition -> canceled*** \n')

    def get_folder_name(self):
        dt = datetime.strftime(datetime.now(),'%Y-%m-%d_%H-%M-%S_')
        folder_index = 0
        folder_name = dt + '%03i_'%folder_index + self.label_textbox.text
        while os.path.exists(folder_name): # check before overwriting
            folder_index +=1
            folder_name = dt + '%03i_'%folder_index + self.label_textbox.text
        return folder_name

    def get_channel_settings(self):
        channels_per_slice, power_per_channel = [], []
        if gui_transmitted_light.power.checkbox_value:
            channels_per_slice.append('LED')
            power_per_channel.append(gui_transmitted_light.power.spinbox_value)
        if gui_laser_box.power405.checkbox_value:
            channels_per_slice.append('405')
            power_per_channel.append(gui_laser_box.power405.spinbox_value)
        if gui_laser_box.power488.checkbox_value:
            channels_per_slice.append('488')
            power_per_channel.append(gui_laser_box.power488.spinbox_value)
        if gui_laser_box.power561.checkbox_value:
            channels_per_slice.append('561')
            power_per_channel.append(gui_laser_box.power561.spinbox_value)
        if gui_laser_box.power640.checkbox_value:
            channels_per_slice.append('640')
            power_per_channel.append(gui_laser_box.power640.spinbox_value)
        if len(channels_per_slice) == 0: # default TL if nothing selected
            gui_transmitted_light.power.tk_checkbox_value.set(1)
            channels_per_slice = ('LED',)
            power_per_channel = (gui_transmitted_light.power.spinbox_value,)
        return channels_per_slice, power_per_channel

    def apply_settings(self, single_volume=False, _print=False):
        # get settings from GUI:
        channels_per_slice, power_per_channel = self.get_channel_settings()
        filter_wheel_position = gui_filter_wheel.filter.position
        illumination_time_us = (
            1e3 * gui_camera.illumination_time_ms.spinbox_value)
        height_px = gui_camera.height_px.spinbox_value
        width_px = gui_camera.width_px.spinbox_value
        voxel_aspect_ratio = gui_galvo.voxel_aspect_ratio.spinbox_value
        scan_range_um = gui_galvo.scan_range_um.spinbox_value
        volumes_per_buffer=self.volumes_spinbox.spinbox_value
        focus_piezo_z_um = gui_focus_piezo.position_um.spinbox_value
        if (power_per_channel != self.power_per_channel or
            channels_per_slice != self.channels_per_slice):
            self.scope.apply_settings(
                channels_per_slice=channels_per_slice,
                power_per_channel=power_per_channel)
            self.power_per_channel = power_per_channel
            self.channels_per_slice = channels_per_slice
        if filter_wheel_position != self.filter_wheel_position:
            self.scope.apply_settings(
                filter_wheel_position=filter_wheel_position)
            self.filter_wheel_position = filter_wheel_position
        if illumination_time_us != self.illumination_time_us:
            self.scope.apply_settings(
                illumination_time_us=illumination_time_us)
            self.illumination_time_us = illumination_time_us
        if height_px != self.height_px:
            self.scope.apply_settings(height_px=height_px)
            self.height_px = height_px
        if width_px != self.width_px:
            self.scope.apply_settings(width_px=width_px)
            self.width_px = width_px
        if voxel_aspect_ratio != self.voxel_aspect_ratio:
            self.scope.apply_settings(voxel_aspect_ratio=voxel_aspect_ratio)
            self.voxel_aspect_ratio = voxel_aspect_ratio
        if scan_range_um != self.scan_range_um:
            self.scope.apply_settings(scan_range_um=scan_range_um)
            self.scan_range_um = scan_range_um
        if single_volume:
            self.scope.apply_settings(volumes_per_buffer=1)
        else:
            self.scope.apply_settings(volumes_per_buffer=volumes_per_buffer)
        if focus_piezo_z_um != self.focus_piezo_z_um:
            self.scope.apply_settings(
                focus_piezo_z_um=(focus_piezo_z_um, 'absolute'))
            self.focus_piezo_z_um = focus_piezo_z_um
        self.scope.finish_all_tasks()
        if _print:
            self.print_memory_and_time()
        return None

    def print_memory_and_time(self):
        # calculate memory
        total_memory_gb = 1e-9 * self.scope.total_bytes
        max_memory_gb = 1e-9 * self.scope.max_allocated_bytes
        memory_pct = 100 * total_memory_gb / max_memory_gb
        print('Total memory needed   (GB) = %0.6f (%0.2f%% of max)'%(
            total_memory_gb, memory_pct))
        # calculate storage:
        data_gb = 1e-9 * self.scope.bytes_per_data_buffer
        preview_gb = 1e-9 * self.scope.bytes_per_preview_buffer
        total_storage_gb = (
            data_gb + preview_gb) * self.acquisitions_spinbox.spinbox_value
        print('Total storaged needed (GB) = %0.6f'%total_storage_gb)
        # calculate time:
        acquire_time_s = (
            self.scope.buffer_time_s + self.delay_spinbox.spinbox_value)
        total_time_s = (
            acquire_time_s * self.acquisitions_spinbox.spinbox_value)
        print('Total acquisition time (s) = %0.6f (%0.2f min)'%(
            total_time_s, (total_time_s / 60)))
        print('Vps ~ %0.6f'%self.scope.volumes_per_s)
        return None

    def close(self):
        self.scope.close()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('SOLS Microscope GUI')

    gui_transmitted_light = GuiTransmittedLight(root)
    gui_laser_box =         GuiLaserBox(root)
    gui_filter_wheel =      GuiFilterWheel(root)
    gui_galvo =             GuiGalvo(root)
    gui_camera =            GuiCamera(root)
    gui_acquisition =       GuiAcquisition(root)
    gui_focus_piezo =       GuiFocusPiezo(root)
    gui_xy_stage =          GuiXYStage(root)

    quit_ = tk.Button(
        root, text="QUIT GUI", command=root.quit, height=5, width=30)
    quit_.grid(row=3, column=2, padx=20, pady=20, sticky='n')

    root.mainloop()
    gui_acquisition.close()
    root.destroy()
