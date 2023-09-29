# Imports from the python standard library:
import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import font
from tkinter import filedialog
from tkinter import tix

# Third party imports, installable via pip:
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tifffile import imread, imwrite

# Our code, one .py file per module, copy files to your local directory:
import sols_microscope as sols          # github.com/amsikking/sols_microscope
import tkinter_compound_widgets as tkcw # github.com/amsikking/tkinter

class GuiMicroscope:
    def __init__(self, init_microscope=True): # set False for GUI design...
        self.init_microscope = init_microscope 
        self.root = tix.Tk()
        self.root.title('SOLS Microscope GUI')
        # adjust font size and delay:
        size = 10 # default = 9
        font.nametofont("TkDefaultFont").configure(size=size)
        font.nametofont("TkFixedFont").configure(size=size)
        font.nametofont("TkTextFont").configure(size=size)
        self.gui_delay_ms = int(1e3 * 1 / 30) # 30fps/video rate target
        # load hardware GUI's:
        self.init_transmitted_light()
        self.init_laser_box()
        self.init_dichroic_mirror()
        self.init_filter_wheel()
        self.init_camera()
        self.init_galvo()
        self.init_focus_piezo()
        self.init_XY_stage()
        # load microscope GUI's and quit:
        self.init_grid_navigator()  # navigates an XY grid of points
        self.init_tile_navigator()  # generates and navigates XY tiles
        self.init_settings()        # collects settings from GUI
        self.init_settings_output() # shows output from settings
        self.init_position_list()   # navigates position lists
        self.init_acquire()         # microscope methods
        self.init_quit()
        # optionally initialize microscope:
        if init_microscope:
            self.max_allocated_bytes = 100e9
            self.scope = sols.Microscope(
                max_allocated_bytes=self.max_allocated_bytes, ao_rate=1e4)
            # configure any hardware preferences:
            self.scope.XY_stage.set_velocity(5, 5)
            # make mandatory call to 'apply_settings':
            self.scope.apply_settings(
                channels_per_slice   = ('LED',),
                power_per_channel    = (self.power_tl.value.get(),),
                emission_filter      = self.emission_filter.get(),
                illumination_time_us = self.illumination_time_us.value.get(),
                height_px            = self.height_px.value.get(),
                width_px             = self.width_px.value.get(),
                voxel_aspect_ratio   = self.voxel_aspect_ratio.value.get(),
                scan_range_um        = self.scan_range_um.value.get(),
                volumes_per_buffer   = self.volumes_per_buffer.value.get(),
                focus_piezo_z_um     = (0, 'relative'),
                XY_stage_position_mm = (0, 0, 'relative')).join() # finish
            # get XYZ direct from hardware and update gui to aviod motion:
            self.focus_piezo_z_um.update_and_validate(
                int(round(self.scope.focus_piezo.z)))
            self._update_XY_stage_position(
                [self.scope.XY_stage.x, self.scope.XY_stage.y])
            # check microscope periodically:
            def run_check_microscope():
                self.scope.apply_settings().join() # update attributes
                self.volumes_per_s.set(self.scope.volumes_per_s)
                self.total_bytes.set(self.scope.total_bytes)
                self.data_bytes.set(self.scope.bytes_per_data_buffer)
                self.preview_bytes.set(self.scope.bytes_per_preview_buffer)
                self.buffer_time_s.set(self.scope.buffer_time_s)
                self._check_joystick()
                self.root.after(self.gui_delay_ms, run_check_microscope)
                return None
            run_check_microscope()
            # run snoutfocus periodically:
            def run_snoutfocus():
                if not self.running_acquire.get():
                    self.scope.snoutfocus(settle_vibrations=False)
                wait_ms = int(round(5 * 60 * 1e3))
                self.root.after(wait_ms, run_snoutfocus)
                return None
            run_snoutfocus()
            # make session folder:
            dt = datetime.strftime(datetime.now(),'%Y-%m-%d_%H-%M-%S_')
            self.session_folder = dt + 'sols_gui_session\\'
            os.makedirs(self.session_folder)
            # snap a volume:
            self.last_acquire_task = self.scope.acquire()
        # start event loop:
        self.root.mainloop() # blocks here until 'QUIT'
        self.root.destroy()

    def _get_folder_name(self):
        dt = datetime.strftime(datetime.now(),'%Y-%m-%d_%H-%M-%S_')
        folder_index = 0
        folder_name = (
            self.session_folder + dt +
            '%03i_'%folder_index + self.label_textbox.text)
        while os.path.exists(folder_name): # check before overwriting
            folder_index +=1
            folder_name = (
                self.session_folder + dt +
                '%03i_'%folder_index + self.label_textbox.text)
        return folder_name

    def _set_running_mode(self, mode, enable=False): # enable=True for 'Buttons'
        # define mode dictionary:
        mode_to_variable = {
            'grid_preview':self.running_grid_preview,
            'tile_preview':self.running_tile_preview,
            'live':self.running_live_mode,
            'scout':self.running_scout_mode,
            'acquire':self.running_acquire
            }
        variable = mode_to_variable[mode]
        # turn everything off except current mode:
        for v in mode_to_variable.values():
            if v != variable:
                v.set(0)
        # optionally enable the mode if not done by 'CheckButton':
        if enable:
            variable.set(1)
        return None

    def _snap_and_display(self):
        if self.volumes_per_buffer.value.get() != 1:
            self.volumes_per_buffer.update_and_validate(1)
        self.last_acquire_task.join()# don't accumulate
        self.last_acquire_task = self.scope.acquire()
        return None

    def init_transmitted_light(self):
        frame = tk.LabelFrame(self.root, text='TRANSMITTED LIGHT', bd=6)
        frame.grid(row=1, column=0, padx=10, pady=10, sticky='n')
        frame_tip = tix.Balloon(frame)
        frame_tip.bind_widget(
            frame,
            balloonmsg=(
                "The 'TRANSMITTED LIGHT' illuminates the sample from above.\n" +
                "NOTE: either the 'TRANSMITTED LIGHT' or at least 1 \n " +
                "'LASER' must be selected."))
        self.power_tl = tkcw.CheckboxSliderSpinbox(
            frame,
            label='470-850nm (%)',
            checkbox_default=True,
            slider_length=200,
            default_value=25,
            width=5)
        self.power_tl.checkbox_value.trace_add(
            'write', self._apply_channel_settings)        
        self.power_tl.value.trace_add(
            'write', self._apply_channel_settings)
        return None

    def init_laser_box(self):
        frame = tk.LabelFrame(self.root, text='LASER BOX', bd=6)
        frame.grid(row=2, column=0, padx=10, pady=10, sticky='n')
        frame_tip = tix.Balloon(frame)
        frame_tip.bind_widget(
            frame,
            balloonmsg=(
                "The 'LASER' illuminates the sample with a 'light-sheet'.\n" +
                "NOTE: either the 'TRANSMITTED LIGHT' or at least 1 \n " +
                "'LASER' must be selected."))
        # 405:
        self.power_405 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='405nm (%)',
            color='magenta',
            slider_length=200,
            default_value=5,
            width=5)
        self.power_405.checkbox_value.trace_add(
            'write', self._apply_channel_settings)        
        self.power_405.value.trace_add(
            'write', self._apply_channel_settings)
        # 488:
        self.power_488 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='488nm (%)',
            color='blue',
            slider_length=200,
            default_value=5,
            row=1,
            width=5)
        self.power_488.checkbox_value.trace_add(
            'write', self._apply_channel_settings)        
        self.power_488.value.trace_add(
            'write', self._apply_channel_settings)
        # 561:
        self.power_561 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='561nm (%)',
            color='green',
            slider_length=200,
            default_value=5,
            row=2,
            width=5)
        self.power_561.checkbox_value.trace_add(
            'write', self._apply_channel_settings)        
        self.power_561.value.trace_add(
            'write', self._apply_channel_settings)
        # 640:
        self.power_640 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='640nm (%)',
            color='red',
            slider_length=200,
            default_value=5,
            row=3,
            width=5)
        self.power_640.checkbox_value.trace_add(
            'write', self._apply_channel_settings)        
        self.power_640.value.trace_add(
            'write', self._apply_channel_settings)
        return None

    def _apply_channel_settings(self, var, index, mode):
        # var, index, mode are passed from .trace_add but not used
        channels_per_slice, power_per_channel = [], []
        if self.power_tl.checkbox_value.get():
            channels_per_slice.append('LED')
            power_per_channel.append(self.power_tl.value.get())
        if self.power_405.checkbox_value.get():
            channels_per_slice.append('405')
            power_per_channel.append(self.power_405.value.get())
        if self.power_488.checkbox_value.get():
            channels_per_slice.append('488')
            power_per_channel.append(self.power_488.value.get())
        if self.power_561.checkbox_value.get():
            channels_per_slice.append('561')
            power_per_channel.append(self.power_561.value.get())
        if self.power_640.checkbox_value.get():
            channels_per_slice.append('640')
            power_per_channel.append(self.power_640.value.get())
        if len(channels_per_slice) > 0: # at least 1 channel selected
            self.scope.apply_settings(channels_per_slice=channels_per_slice,
                                      power_per_channel=power_per_channel)
        return None

    def init_dichroic_mirror(self):
        frame = tk.LabelFrame(self.root, text='DICHROIC MIRROR', bd=6)
        frame.grid(row=3, column=0, padx=10, pady=10, sticky='n')
        frame_tip = tix.Balloon(frame)
        frame_tip.bind_widget(
            frame,
            balloonmsg=(
                "The 'DICHROIC MIRROR' couples the LASER light into the \n" +
                "microscope (and blocks some of the emission light).\n" +
                "Search the part number to see the specification."))
        inner_frame = tk.LabelFrame(frame, text='fixed')
        inner_frame.grid(row=0, column=0, padx=10, pady=10)
        dichroic_mirror_options = ( # copy paste from sols_microscope
            'ZT405/488/561/640rpc',)
        dichroic_mirror = tk.StringVar()
        dichroic_mirror.set('ZT405/488/561/640rpc') # set default
        option_menu = tk.OptionMenu(
            inner_frame,
            dichroic_mirror,
            *dichroic_mirror_options)
        option_menu.config(width=46, height=2) # match to TL and lasers
        option_menu.grid(row=0, column=0, padx=10, pady=10)
        return None

    def init_filter_wheel(self):
        frame = tk.LabelFrame(self.root, text='FILTER WHEEL', bd=6)
        frame.grid(row=4, column=0, padx=10, pady=10, sticky='n')
        frame_tip = tix.Balloon(frame)
        frame_tip.bind_widget(
            frame,
            balloonmsg=(
                "The 'FILTER WHEEL' has a choice of 'emission filters' \n" +
                "(typically used to stop LASER light reaching the camera).\n" +
                "Search the part numbers to see the specifications."))
        inner_frame = tk.LabelFrame(frame, text='choice')
        inner_frame.grid(row=0, column=0, padx=10, pady=10)
        emission_filter_options = ( # copy paste from sols_microscope
            'Shutter',
            'Open',
            'ET450/50M',
            'ET525/50M',
            'ET600/50M',
            'ET690/50M',
            'ZET405/488/561/640m',
            'LP02-488RU',
            'LP02-561RU',
            '(unused)')
        self.emission_filter = tk.StringVar()
        self.emission_filter.set('ZET405/488/561/640m') # set default
        option_menu = tk.OptionMenu(
            inner_frame,
            self.emission_filter,
            *emission_filter_options)
        option_menu.config(width=46, height=2) # match to TL and lasers
        option_menu.grid(row=0, column=0, padx=10, pady=10)
        self.emission_filter.trace_add(
            'write',
            lambda var, index, mode: self.scope.apply_settings(
                emission_filter=self.emission_filter.get()))
        return None

    def init_camera(self):
        frame = tk.LabelFrame(self.root, text='CAMERA', bd=6)
        frame.grid(row=1, column=1, rowspan=2, padx=10, pady=10, sticky='n')
        # illumination_time_us:
        self.illumination_time_us = tkcw.CheckboxSliderSpinbox(
            frame,
            label='illumination time (us)',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=100,
            max_value=1000000,
            default_value=1000,
            columnspan=2,
            row=0,
            width=10,
            sticky='w')
        self.illumination_time_us.value.trace_add(
            'write',
            lambda var, index, mode: self.scope.apply_settings(
                illumination_time_us=self.illumination_time_us.value.get()))
        illumination_time_us_tip = tix.Balloon(self.illumination_time_us)
        illumination_time_us_tip.bind_widget(
            self.illumination_time_us,
            balloonmsg=(
                "The 'illumination time (us)' determines how long the \n" +
                "sample will be exposed to light (i.e. the camera will \n" +
                "collect the emmitted light during this time).\n" +
                "NOTE: the range in the GUI is 100us to 1000000us (1s)."))
        # height_px:
        self.height_px = tkcw.CheckboxSliderSpinbox(
            frame,
            label='height pixels',
            orient='vertical',
            checkbox_enabled=False,
            slider_length=200,
            tickinterval=3,
            slider_flipped=True,
            min_value=12,
            max_value=500,
            default_value=250,
            row=1,
            width=5)
        self.height_px.value.trace_add(
            'write',
            lambda var, index, mode: self.scope.apply_settings(
                height_px=self.height_px.value.get()))
        height_px_tip = tix.Balloon(self.height_px)
        height_px_tip.bind_widget(
            self.height_px,
            balloonmsg=(
                "The 'height pixels' determines how many vertical pixels \n" +
                "are used by the camera. Less pixels is a smaller field \n" +
                "of view (FOV) and less data.\n" +
                "NOTE: less vertical pixels speeds up the acquisition!"))
        # width_px:
        self.width_px = tkcw.CheckboxSliderSpinbox(
            frame,
            label='width pixels',
            checkbox_enabled=False,
            slider_length=240,
            tickinterval=4,
            min_value=60,
            max_value=1000,
            default_value=1000,
            row=2,
            column=1,
            sticky='s',
            width=5)
        self.width_px.value.trace_add(
            'write',
            lambda var, index, mode: self.scope.apply_settings(
                width_px=self.width_px.value.get()))
        width_px_tip = tix.Balloon(self.width_px)
        width_px_tip.bind_widget(
            self.width_px,
            balloonmsg=(
                "The 'width pixels' determines how many horizontal pixels \n" +
                "are used by the camera. Less pixels is a smaller field \n" +
                "of view (FOV) and less data.\n"))
        # ROI display:
        tkcw.CanvasRectangleSliderTrace2D(
            frame,
            self.width_px,
            self.height_px,
            row=1,
            column=1,
            fill='yellow')
        return None

    def init_galvo(self):
        frame = tk.LabelFrame(self.root, text='GALVO', bd=6)
        frame.grid(row=3, column=1, rowspan=2, padx=10, pady=10, sticky='n')
        slider_length = 365 # match to camera
        button_width, button_height = 10, 2
        # scan slider:
        scan_range_um_min, scan_range_um_max = 1, 100
        scan_range_um_center = int(round((
            scan_range_um_max - scan_range_um_min) / 2))
        self.scan_range_um = tkcw.CheckboxSliderSpinbox(
            frame,
            label='~scan range (um)',
            checkbox_enabled=False,
            slider_length=slider_length,
            tickinterval=10,
            min_value=scan_range_um_min,
            max_value=scan_range_um_max,
            default_value=scan_range_um_center,
            row=0,
            width=5)
        self.scan_range_um.value.trace_add(
            'write',
            lambda var, index, mode: self.scope.apply_settings(
                scan_range_um=self.scan_range_um.value.get()))        
        scan_range_um_tip = tix.Balloon(self.scan_range_um)
        scan_range_um_tip.bind_widget(
            self.scan_range_um,
            balloonmsg=(
                "The '~scan range (um)' setting requests that the \n" +
                "microscope use the chosen scan range when acquiring a \n" +
                "volume.\n" +
                "NOTE: the actual scan range is optimized by the \n" +
                "microscope and may differ from the requested value."))
        # scan min button:
        button_scan_range_um_min = tk.Button(
            frame,
            text="min",
            command=lambda: self.scan_range_um.update_and_validate(
                scan_range_um_min),
            width=button_width,
            height=button_height)
        button_scan_range_um_min.grid(
            row=1, column=0, padx=10, pady=10, sticky='w')
        # scan center button:
        button_scan_range_um_center = tk.Button(
            frame,
            text="center",
            command=lambda: self.scan_range_um.update_and_validate(
                scan_range_um_center),
            width=button_width,
            height=button_height)
        button_scan_range_um_center.grid(
            row=1, column=0, padx=5, pady=5)
        # scan max button:
        button_scan_range_um_max = tk.Button(
            frame,
            text="max",
            command=lambda: self.scan_range_um.update_and_validate(
                scan_range_um_max),
            width=button_width,
            height=button_height)
        button_scan_range_um_max.grid(
            row=1, column=0, padx=10, pady=10, sticky='e')
        # voxel slider:
        voxel_aspect_ratio_min, voxel_aspect_ratio_max = 2, 32
        voxel_aspect_ratio_center = int(round((
            voxel_aspect_ratio_max - voxel_aspect_ratio_min) / 2))
        self.voxel_aspect_ratio = tkcw.CheckboxSliderSpinbox(
            frame,
            label='~voxel aspect ratio',
            checkbox_enabled=False,
            slider_length=slider_length,
            tickinterval=10,
            min_value=voxel_aspect_ratio_min,
            max_value=voxel_aspect_ratio_max,
            default_value=voxel_aspect_ratio_max,
            row=2,
            width=5)
        self.voxel_aspect_ratio.value.trace_add(
            'write',
            lambda var, index, mode: self.scope.apply_settings(
                voxel_aspect_ratio=self.voxel_aspect_ratio.value.get()))        
        voxel_aspect_ratio_tip = tix.Balloon(self.voxel_aspect_ratio)
        voxel_aspect_ratio_tip.bind_widget(
            self.voxel_aspect_ratio,
            balloonmsg=(
                "The short answer: this determines how finely \n" +
                "(or coarsely) the acquired volume is sampled.\n" +
                "The real answer: the '~voxel aspect ratio' setting \n" +
                "requests that the microscope acquires a volume with \n" +
                "'cuboid' pixels (i.e. voxels) that have the chosen \n" +
                "aspect ratio. For example, a ratio of 2 gives voxels \n" +
                "that are twice as long as they are wide.\n" +
                "NOTE: the actual voxel aspect ratio is optimized by the \n" +
                "microscope and may differ from the requested value."))
        # voxel min button:
        button_voxel_aspect_ratio_min = tk.Button(
            frame,
            text="min",
            command=lambda: self.voxel_aspect_ratio.update_and_validate(
                voxel_aspect_ratio_min),
            width=button_width,
            height=button_height)
        button_voxel_aspect_ratio_min.grid(
            row=3, column=0, padx=10, pady=10, sticky='w')
        # voxel center button:
        button_voxel_aspect_ratio_center = tk.Button(
            frame,
            text="center",
            command=lambda: self.voxel_aspect_ratio.update_and_validate(
                voxel_aspect_ratio_center),
            width=button_width,
            height=button_height)
        button_voxel_aspect_ratio_center.grid(
            row=3, column=0, padx=5, pady=5)
        # voxel max button:
        button_voxel_aspect_ratio_max = tk.Button(
            frame,
            text="max",
            command=lambda: self.voxel_aspect_ratio.update_and_validate(
                voxel_aspect_ratio_max),
            width=button_width,
            height=button_height)
        button_voxel_aspect_ratio_max.grid(
            row=3, column=0, padx=10, pady=10, sticky='e')
        return None

    def init_focus_piezo(self):
        frame = tk.LabelFrame(self.root, text='FOCUS PIEZO (Scout mode)', bd=6)
        frame.grid(row=1, column=2, rowspan=2, padx=10, pady=10, sticky='n')
        frame_tip = tix.Balloon(frame)
        frame_tip.bind_widget(
            frame,
            balloonmsg=(
                "The 'FOCUS PIEZO' is a (fast) fine focus device for \n" +
                "precisley adjusting the focus of the primary objective \n" +
                "over a short range.\n" +
                "NOTE: this is only active in 'Scout mode'"))
        min_um, max_um = 0, 100
        small_move_um, large_move_um = 1, 5
        center_um = int(round((max_um - min_um) / 2))
        # slider:
        self.focus_piezo_z_um = tkcw.CheckboxSliderSpinbox(
            frame,
            label='position (um)',
            orient='vertical',
            checkbox_enabled=False,
            slider_fast_update=True,
            slider_length=460, # match to camera
            tickinterval=10,
            min_value=min_um,
            max_value=max_um,
            rowspan=5,
            width=5)
        def move():
            self.scope.apply_settings(
                focus_piezo_z_um=(self.focus_piezo_z_um.value.get(),
                                  'absolute'))
            if self.running_scout_mode.get():
                self._snap_and_display()
            return None
        self.focus_piezo_z_um.value.trace_add(
            'write',
            lambda var, index, mode: move())
        def update_position(how):
            # check current position:
            z_um = self.focus_piezo_z_um.value.get()
            # check which direction:
            if how == 'large_up':     z_um -= large_move_um
            if how == 'small_up':     z_um -= small_move_um
            if how == 'center':       z_um  = center_um
            if how == 'small_down':   z_um += small_move_um
            if how == 'large_down':   z_um += large_move_um
            # update:
            self.focus_piezo_z_um.update_and_validate(z_um)
            return None
        button_width, button_height = 10, 2
        # large up button:
        button_large_move_up = tk.Button(
            frame,
            text="up %ium"%large_move_um,
            command=lambda d='large_up': update_position(d),
            width=button_width,
            height=button_height)
        button_large_move_up.grid(row=0, column=1, padx=10, pady=10)
        # small up button:
        button_small_move_up = tk.Button(
            frame,
            text="up %ium"%small_move_um,
            command=lambda d='small_up': update_position(d),
            width=button_width,
            height=button_height)
        button_small_move_up.grid(row=1, column=1, sticky='s')
        # center button:
        button_center_move = tk.Button(
            frame,
            text="center",
            command=lambda d='center': update_position(d),
            width=button_width,
            height=button_height)
        button_center_move.grid(row=2, column=1, padx=5, pady=5)
        # small down button:
        button_small_move_down = tk.Button(
            frame,
            text="down %ium"%small_move_um,
            command=lambda d='small_down': update_position(d),
            width=button_width,
            height=button_height)
        button_small_move_down.grid(row=3, column=1, sticky='n')
        # large down button:
        button_large_move_down = tk.Button(
            frame,
            text="down %ium"%large_move_um,
            command=lambda d='large_down': update_position(d),
            width=button_width,
            height=button_height)
        button_large_move_down.grid(row=4, column=1, padx=10, pady=10)
        return None

    def init_XY_stage(self):
        frame = tk.LabelFrame(self.root, text='XY STAGE (Scout mode)', bd=6)
        frame.grid(row=3, column=2, rowspan=2, columnspan=2,
                   padx=10, pady=10, sticky='n')
        frame_tip = tix.Balloon(frame)
        frame_tip.bind_widget(
            frame,
            balloonmsg=(
                "The 'XY STAGE' moves the sample in XY with a high \n" +
                "degree of accuracy (assuming the sample does not move).\n"
                "To help with XY navigation this panels shows:\n"
                "- The direction of the 'last move'.\n" +
                "- The absolute '[X, Y] position (mm)'.\n" +
                "- Move buttons for 'left', 'right', 'up' and 'down'.\n" +
                "- A slider bar for the 'step size (% of FOV)', which \n" +
                "determines how much the move buttons will move as a % \n" +
                "of the current field of view (FOV).\n"
                "NOTE: this is only active in 'Scout mode'"))
        # position:
        self.XY_stage_position_mm = tk.StringVar()
        def move():
            self.scope.apply_settings(
                XY_stage_position_mm=(self.X_stage_position_mm,
                                      self.Y_stage_position_mm,
                                      'absolute'))
            return None
        self.XY_stage_position_mm.trace_add(
            'write',
            lambda var, index, mode: self.scope.apply_settings(
                XY_stage_position_mm=(self.X_stage_position_mm,
                                      self.Y_stage_position_mm,
                                      'absolute')))
        # position textbox:
        self.XY_stage_position_textbox = tkcw.Textbox(
            frame,
            label='[X, Y] position (mm)',
            row=1,
            column=1,
            height=1,
            width=20)
        # last move textbox:
        self.last_move = tk.StringVar()
        last_move_textbox = tkcw.Textbox(
            frame,
            label='last move',
            default_text='None',
            height=1,
            width=10)
        def update_last_move():
            last_move_textbox.textbox.delete('1.0', '10.0')
            last_move_textbox.textbox.insert('1.0', self.last_move.get())
            return None
        self.last_move.trace_add(
            'write',
            lambda var, index, mode: update_last_move())
        def update_position(how):
            # calculate move size:
            move_factor = move_pct.value.get() / 100
            ud_move_mm = 1e-3 * self.scan_range_um.value.get() * move_factor
            scan_width_um = self.width_px.value.get() * sols.sample_px_um
            lr_move_mm = 1e-3 * scan_width_um * move_factor
            # check which direction:
            if how == 'up (+Y)':       move_mm = (0,  ud_move_mm)
            if how == 'down (-Y)':     move_mm = (0, -ud_move_mm)
            if how == 'left (-X)':     move_mm = (-lr_move_mm, 0)
            if how == 'right (+X)':    move_mm = (lr_move_mm, 0)
            # update:
            self.last_move.set(how)
            self._update_XY_stage_position(
                [self.X_stage_position_mm + move_mm[0],
                 self.Y_stage_position_mm + move_mm[1]])
            if self.running_scout_mode.get():
                self._snap_and_display()
            return None
        # move size:
        move_pct = tkcw.CheckboxSliderSpinbox(
            frame,
            label='step size (% of FOV)',
            checkbox_enabled=False,
            slider_length=250,
            tickinterval=6,
            min_value=1,
            max_value=100,
            default_value=100,
            row=4,
            columnspan=3,
            width=5)
        button_width, button_height = 10, 2
        # up button:
        button_up = tk.Button(
            frame,
            text="up",
            command=lambda d='up (+Y)': update_position(d),
            width=button_width,
            height=button_height)
        button_up.grid(row=0, column=1, padx=10, pady=10)
        # down button:
        button_down = tk.Button(
            frame,
            text="down",
            command=lambda d='down (-Y)': update_position(d),
            width=button_width,
            height=button_height)
        button_down.grid(row=2, column=1, padx=10, pady=10)
        # left button:
        button_left = tk.Button(
            frame,
            text="left",
            command=lambda d='left (-X)': update_position(d),
            width=button_width,
            height=button_height)
        button_left.grid(row=1, column=0, padx=10, pady=10)
        # right button:
        button_right = tk.Button(
            frame,
            text="right",
            command=lambda d='right (+X)': update_position(d),
            width=button_width,
            height=button_height)
        button_right.grid(row=1, column=2, padx=10, pady=10)
        return None

    def _update_XY_stage_position(self, XY_stage_position_mm):
        X, Y = XY_stage_position_mm[0], XY_stage_position_mm[1]
        XY_string = '[%0.3f, %0.3f]'%(X, Y)
        # textbox:
        self.XY_stage_position_textbox.textbox.delete('1.0', '10.0')
        self.XY_stage_position_textbox.textbox.insert('1.0', XY_string)
        # attributes
        self.X_stage_position_mm, self.Y_stage_position_mm = X, Y
        self.XY_stage_position_mm.set(XY_string)
        return None

    def _check_joystick(self):
        XY_mm = list(self.scope.XY_stage_position_mm)
        joystick_active = False
        if   XY_mm[0] == self.scope.XY_stage.x_min:
            joystick_active = True
            self.last_move.set('left (-X)')
        elif XY_mm[0] == self.scope.XY_stage.x_max:
            joystick_active = True
            self.last_move.set('right (+X)')
        elif XY_mm[1] == self.scope.XY_stage.y_min:
            joystick_active = True
            self.last_move.set('down (-Y)')
        elif XY_mm[1] == self.scope.XY_stage.y_max:
            joystick_active = True
            self.last_move.set('up (+Y)')
        if (joystick_active and self.running_scout_mode.get()):
            self._snap_and_display()
        if (not joystick_active and (
            XY_mm[0] != self.X_stage_position_mm or
            XY_mm[1] != self.Y_stage_position_mm)):
            self._update_XY_stage_position(XY_mm)
        return None

    def init_grid_navigator(self):
        grid_frame = tk.LabelFrame(
            self.root, text='GRID NAVIGATOR', bd=6)
        grid_frame.grid(
            row=1, column=4, rowspan=2, padx=10, pady=10, sticky='n')
        button_width, button_height = 25, 2
        spinbox_width = 20
        # set grid defaults:
        self.grid_rows = 2
        self.grid_cols = 4
        self.grid_spacing_um = 1000
        # load from file:
        def load_grid_from_file():
            # get file from user:
            file_path = tk.filedialog.askopenfilename(
                parent=self.root,
                initialdir=os.getcwd(),
                title='Please choose a previous "grid" file (.txt)')        
            with open(file_path, 'r') as file:
                grid_data = file.read().splitlines()
            # parse and update attributes:
            self.grid_rows = int(grid_data[0].split(':')[1])
            self.grid_cols = int(grid_data[1].split(':')[1])
            self.grid_spacing_um = int(grid_data[2].split(':')[1])
            # show user:
            create_grid()
            # reset state of grid buttons:
            self.set_grid_location_button.config(state='normal')
            self.move_to_grid_location_button.config(state='disabled')
            self.start_grid_preview_button.config(state='disabled')
            return None
        load_grid_from_file_button = tk.Button(
            grid_frame,
            text="Load from file",
            command=load_grid_from_file,
            font=('Segoe UI', '10', 'underline'),
            width=button_width,
            height=button_height)
        load_grid_from_file_button.grid(row=0, column=0, padx=10, pady=10)
        load_grid_from_file_tip = tix.Balloon(load_grid_from_file_button)
        load_grid_from_file_tip.bind_widget(
            load_grid_from_file_button,
            balloonmsg=(
                "Use the 'Load from file' button to select a \n" + 
                "'grid_navigator_parameters.txt' file from a previous \n" +
                "'sols_gui_session' folder and load these settings into \n" +
                "the GUI.\n"
                "NOTE: this will overwrite any existing grid parameters"))
        # create grid:
        def create_grid():
            def create():
                # tidy up any previous display:
                if hasattr(self, 'create_grid_buttons_frame'):
                    self.create_grid_buttons_frame.destroy()
                # update attributes:
                self.grid_rows = self.grid_rows_spinbox.value.get()
                self.grid_cols = self.grid_cols_spinbox.value.get()
                self.grid_spacing_um = self.grid_spacing_spinbox.value.get()
                # show grid buttons:
                self.create_grid_buttons_frame = tk.LabelFrame(
                    create_grid_popup, text='XY GRID', bd=6)
                self.create_grid_buttons_frame.grid(
                    row=0, column=1, rowspan=5, padx=10, pady=10)
                grid_button_array = [[None for c in range(
                    self.grid_cols)] for r in range(self.grid_rows)]
                for r in range(self.grid_rows):
                    for c in range(self.grid_cols):
                        name = '%s%i'%(chr(ord('@')+r + 1), c + 1)
                        grid_button_array[r][c] = tk.Button(
                            self.create_grid_buttons_frame,
                            text=name,
                            width=5,
                            height=2)
                        grid_button_array[r][c].grid(
                            row=r, column=c, padx=10, pady=10)
                        grid_button_array[r][c].config(state='disabled')
                # set button status:
                self.set_grid_location_button.config(state='normal')
                self.move_to_grid_location_button.config(state='disabled')
                self.start_grid_preview_button.config(state='disabled')
                # overwrite grid file:
                with open(self.session_folder +
                          "grid_navigator_parameters.txt", "w") as file:
                    file.write('rows:%i'%self.grid_rows + '\n')
                    file.write('columns:%i'%self.grid_cols + '\n')
                    file.write('spacing_um:%i'%self.grid_spacing_um + '\n')
                return None
            # popup:
            create_grid_popup = tk.Toplevel()
            create_grid_popup.title('Create grid')
            create_grid_popup.grab_set() # force user to interact
            x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
            create_grid_popup.geometry("+%d+%d" % (x + 800, y + 400))
            spinbox_width = 20
            # user input:
            self.grid_rows_spinbox = tkcw.CheckboxSliderSpinbox(
                create_grid_popup,
                label='How many rows? (1-16)',
                checkbox_enabled=False,
                slider_enabled=False,
                min_value=1,
                max_value=16,
                default_value=self.grid_rows,
                row=0,
                width=spinbox_width,
                sticky='n')
            self.grid_cols_spinbox = tkcw.CheckboxSliderSpinbox(
                create_grid_popup,
                label='How many columns? (1-24)',
                checkbox_enabled=False,
                slider_enabled=False,
                min_value=1,
                max_value=24,
                default_value=self.grid_cols,
                row=1,
                width=spinbox_width,
                sticky='n')
            self.grid_spacing_spinbox = tkcw.CheckboxSliderSpinbox(
                create_grid_popup,
                label='What is the spacing (um)?',
                checkbox_enabled=False,
                slider_enabled=False,
                min_value=1,
                max_value=20000,
                default_value=self.grid_spacing_um,
                row=2,
                width=spinbox_width,
                sticky='n')
            # create button:
            create_button = tk.Button(
                create_grid_popup, text="Create",
                command=create,
                height=button_height, width=button_width)
            create_button.grid(row=3, column=0, padx=10, pady=10, sticky='n')
            # exit button:
            exit_button = tk.Button(
                create_grid_popup, text="Exit",
                command=create_grid_popup.destroy,
                height=button_height, width=button_width)
            exit_button.grid(row=4, column=0, padx=10, pady=10, sticky='n')
            create()
            return None
        create_grid_button = tk.Button(
            grid_frame,
            text="Create grid",
            command=create_grid,
            width=button_width,
            height=button_height)
        create_grid_button.grid(row=1, column=0, padx=10, pady=10)
        create_grid_tip = tix.Balloon(create_grid_button)
        create_grid_tip.bind_widget(
            create_grid_button,
            balloonmsg=(
                "Use the 'Create grid' button to create a new grid \n" +
                "of points you want to navigate (by specifying the rows, \n" +
                "columns and spacing). For example, this tool can be used \n" +
                "to move around multiwell plates (or any grid like sample).\n" +
                "NOTE: this will overwrite any existing grid parameters"))
        # set location:
        def set_grid_location():
            def _set(r, c):
                # update grid:
                self.grid_location_rc = [r, c]
                update_grid_location()
                # get current position and spacing:
                spacing_mm = self.grid_spacing_um / 1000
                # set home position:
                self.grid_home_mm = [
                    self.X_stage_position_mm + c * spacing_mm,
                    self.Y_stage_position_mm - r * spacing_mm]
                # make grid of positions:
                self.grid_positions_mm = [
                    [None for c in range(
                        self.grid_cols)] for j in range(self.grid_rows)]
                for rows in range(self.grid_rows):
                    for cols in range(self.grid_cols):
                        self.grid_positions_mm[rows][cols] = [
                            self.grid_home_mm[0] - (cols * spacing_mm),
                            self.grid_home_mm[1] + (rows * spacing_mm)]
                # allow moves:
                self.move_to_grid_location_button.config(state='normal')
                self.start_grid_preview_button.config(state='disabled')
                if self.grid_location_rc == [0, 0]:
                    self.start_grid_preview_button.config(state='normal')
                # exit:
                set_grid_location_popup.destroy()                
                return None
            set_grid_location_popup = tk.Toplevel()
            set_grid_location_popup.title('Set current location')
            set_grid_location_popup.grab_set() # force user to interact
            x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
            set_grid_location_popup.geometry("+%d+%d" % (x + 800, y + 400))
            # show grid buttons:
            set_grid_location_buttons_frame = tk.LabelFrame(
                set_grid_location_popup, text='XY GRID', bd=6)
            set_grid_location_buttons_frame.grid(
                row=0, column=1, rowspan=5, padx=10, pady=10)
            grid_button_array = [[None for c in range(
                self.grid_cols)] for r in range(self.grid_rows)]
            for r in range(self.grid_rows):
                for c in range(self.grid_cols):
                    name = '%s%i'%(chr(ord('@')+r + 1), c + 1)
                    grid_button_array[r][c] = tk.Button(
                        set_grid_location_buttons_frame,
                        text=name,
                        command=lambda rows=r, cols=c: _set(rows, cols),
                        width=5,
                        height=2)
                    grid_button_array[r][c].grid(
                        row=r, column=c, padx=10, pady=10)
        self.set_grid_location_button = tk.Button(
            grid_frame,
            text="Set grid location",
            command=set_grid_location,
            width=button_width,
            height=button_height)
        self.set_grid_location_button.grid(row=2, column=0, padx=10, pady=10)
        self.set_grid_location_button.config(state='disabled')
        set_grid_location_tip = tix.Balloon(self.set_grid_location_button)
        set_grid_location_tip.bind_widget(
            self.set_grid_location_button,
            balloonmsg=(
                "Use the 'Set grid location' button to specify where you \n" +
                "are currently located in the grid. \n" +
                "NOTE: all other grid points will then be referenced by \n" +
                "this operation (i.e. this operation 'homes' the grid). \n" +
                "To change the grid origin simply update with this button"))
        # current location:
        def update_grid_location():
            name = '%s%i'%(chr(ord('@')+ self.grid_location_rc[0] + 1),
                           self.grid_location_rc[1] + 1)
            self.grid_location_textbox.textbox.delete('1.0', '10.0')
            self.grid_location_textbox.textbox.insert('1.0', name)
            return None
        self.grid_location_textbox = tkcw.Textbox(
            grid_frame,
            label='Grid location',
            default_text='None',
            height=1,
            width=20)
        self.grid_location_textbox.grid(
            row=3, column=0, padx=10, pady=10)
        grid_location_tip = tix.Balloon(self.grid_location_textbox)
        grid_location_tip.bind_widget(
            self.grid_location_textbox,
            balloonmsg=(
                "The 'Current grid location' displays the last grid \n" +
                "location that was moved to (or set) with the \n" +
                "'GRID NAVIGATOR' panel.\n" +
                "NOTE: it does not display the current position and is not \n" +
                "aware of XY moves made elsewhere (e.g. with the joystick \n" +
                "or 'XY STAGE' panel)."))
        # move to location:
        def move_to_grid_location():
            def move(r, c):
                # update gui, apply and display:
                XY_stage_position_mm = self.grid_positions_mm[r][c]
                self._update_XY_stage_position(XY_stage_position_mm)
                self._snap_and_display()
                # update attributes and buttons:
                self.grid_location_rc = [r, c]
                update_grid_location()
                self.start_grid_preview_button.config(state='disabled')
                if [r, c] == [0, 0]:
                    self.start_grid_preview_button.config(state='normal')
                # exit:
                move_to_grid_location_popup.destroy()
                return None
            move_to_grid_location_popup = tk.Toplevel()
            move_to_grid_location_popup.title('Move to location')
            move_to_grid_location_popup.grab_set() # force user to interact
            x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
            move_to_grid_location_popup.geometry("+%d+%d" % (x + 800, y + 400))
            # show grid buttons:
            move_to_grid_location_buttons_frame = tk.LabelFrame(
                move_to_grid_location_popup, text='XY GRID', bd=6)
            move_to_grid_location_buttons_frame.grid(
                row=0, column=1, rowspan=5, padx=10, pady=10)
            grid_button_array = [[None for c in range(
                self.grid_cols)] for r in range(self.grid_rows)]
            for r in range(self.grid_rows):
                for c in range(self.grid_cols):
                    name = '%s%i'%(chr(ord('@')+r + 1), c + 1)
                    grid_button_array[r][c] = tk.Button(
                        move_to_grid_location_buttons_frame,
                        text=name,
                        command=lambda rows=r, cols=c: move(rows, cols),
                        width=5,
                        height=2)
                    grid_button_array[r][c].grid(
                        row=r, column=c, padx=10, pady=10)
            # disable current location button:
            r, c = self.grid_location_rc
            grid_button_array[r][c].config(state='disabled')
            # cancel button:
            cancel_button = tk.Button(
                move_to_grid_location_popup, text="Cancel",
                command=move_to_grid_location_popup.destroy,
                height=button_height, width=button_width)
            cancel_button.grid(row=1, column=0, padx=10, pady=10, sticky='n')
            return None
        self.move_to_grid_location_button = tk.Button(
            grid_frame,
            text="Move to grid location",
            command=move_to_grid_location,
            width=button_width,
            height=button_height)
        self.move_to_grid_location_button.grid(
            row=4, column=0, padx=10, pady=10)
        self.move_to_grid_location_button.config(state='disabled')
        move_to_grid_location_tip = tix.Balloon(
            self.move_to_grid_location_button)
        move_to_grid_location_tip.bind_widget(
            self.move_to_grid_location_button,
            balloonmsg=(
                "The 'Move to grid location' button moves to the chosen \n" +
                "grid location based on the absolute XY grid positions \n" +
                "that have been loaded or created. The grid origin is \n" +
                "set by the 'Set grid location' button.\n"))
        # save data and position:
        self.save_grid_data_and_position = tk.BooleanVar()
        save_grid_data_and_position_button = tk.Checkbutton(
            grid_frame,
            text='Save data and position',
            variable=self.save_grid_data_and_position)
        save_grid_data_and_position_button.grid(
            row=5, column=0, padx=10, pady=10, sticky='w')
        save_grid_data_and_position_tip = tix.Balloon(
            save_grid_data_and_position_button)
        save_grid_data_and_position_tip.bind_widget(
            save_grid_data_and_position_button,
            balloonmsg=(
                "If 'Save data and position' is enabled then the \n" +
                "'Start grid preview (from A1)' button will save the \n" +
                "full data set (in addition to the preview data) and \n" +
                "populate the 'POSITION LIST'."))
        # tile the grid:
        self.tile_the_grid = tk.BooleanVar()
        tile_the_grid_button = tk.Checkbutton(
            grid_frame,
            text='Tile the grid',
            variable=self.tile_the_grid)
        tile_the_grid_button.grid(
            row=6, column=0, padx=10, pady=10, sticky='w')
        tile_the_grid_tip = tix.Balloon(tile_the_grid_button)
        tile_the_grid_tip.bind_widget(
            tile_the_grid_button,
            balloonmsg=(
                "If 'Tile the grid' is enabled then the 'Start grid \n" +
                "preview (from A1)' button will tile the grid locations \n" +
                "with the number of tiles set by the 'TILE NAVIGATOR'."))
        # start grid preview:
        def start_grid_preview():
            print('\nGrid preview -> started')
            self._set_running_mode('grid_preview', enable=True)
            if self.volumes_per_buffer.value.get() != 1:
                self.volumes_per_buffer.update_and_validate(1)
            folder_name = self._get_folder_name() + '_grid'
            if self.tile_the_grid.get():
                folder_name = self._get_folder_name() + '_grid_tile'
                # get tile parameters:
                self.tile_rows = self.tile_array_width.value.get()
                self.tile_cols = self.tile_rows
                # calculate move size:
                self.tile_X_mm = (
                    1e-3 * self.width_px.value.get() * sols.sample_px_um)
                self.tile_Y_mm = 1e-3 * self.scan_range_um.value.get()
            # generate rows/cols list:
            self.XY_grid_rc_list = []
            for r in range(self.grid_rows):
                for c in range(self.grid_cols):
                    if self.tile_the_grid.get():
                        for tile_r in range(self.tile_rows):
                            for tile_c in range(self.tile_cols):
                                self.XY_grid_rc_list.append(
                                    [r, c, tile_r, tile_c])
                    else:
                        self.XY_grid_rc_list.append([r, c])
            self.current_grid_image = 0
            def run_grid_preview():
                if self.tile_the_grid.get():
                    r, c, tile_r, tile_c = self.XY_grid_rc_list[
                        self.current_grid_image]
                    name = '%s%i_r%ic%i'%(
                        chr(ord('@')+r + 1), c + 1, tile_r, tile_c)
                    XY_stage_position_mm = [
                        self.grid_positions_mm[r][c][0] - (
                            tile_c * self.tile_X_mm),
                        self.grid_positions_mm[r][c][1] + (
                            tile_r * self.tile_Y_mm)]
                    self._update_XY_stage_position(XY_stage_position_mm)
                else:
                    r, c = self.XY_grid_rc_list[self.current_grid_image]
                    name = '%s%i'%(chr(ord('@')+r + 1), c + 1)
                    self._update_XY_stage_position(self.grid_positions_mm[r][c])
                filename = name + '.tif'
                # update gui and move stage:
                self.grid_location_rc = [r, c]
                update_grid_location()
                # check mode:
                preview_only = True
                if self.save_grid_data_and_position.get():
                    preview_only = False
                    self._update_position_list()
                # get image:
                self.scope.acquire(
                    filename=filename,
                    folder_name=folder_name,
                    description=self.description_textbox.text,
                    preview_only=preview_only).join()
                grid_preview_filename = (folder_name + '\preview\\' + filename)
                while not os.path.isfile(grid_preview_filename):
                    self.root.after(self.gui_delay_ms)
                grid_image = imread(grid_preview_filename)
                shape = grid_image.shape
                # add reference:
                grid_image = Image.fromarray(grid_image) # convert to ImageDraw
                XY = (int(0.1 * min(shape)), shape[0] - int(0.15 * min(shape)))
                font_size = int(0.1 * min(shape))
                font = ImageFont.truetype('arial.ttf', font_size)
                ImageDraw.Draw(grid_image).text(XY, name, fill=0, font=font)
                # make grid image:
                if self.tile_the_grid.get():
                    if (r, c, tile_r, tile_c) == (0, 0, 0, 0):
                        self.grid_preview = np.zeros(
                            (self.grid_rows * shape[0] * self.tile_rows,
                             self.grid_cols * shape[1] * self.tile_cols),
                            'uint16')
                    self.grid_preview[
                        (r * self.tile_rows + tile_r) * shape[0]:
                        (r * self.tile_rows + tile_r + 1) * shape[0],
                        (c * self.tile_cols + tile_c) * shape[1]:
                        (c * self.tile_cols + tile_c + 1) * shape[1]
                        ] = grid_image
                else:
                    if (r, c) == (0, 0):
                        self.grid_preview = np.zeros(
                            (self.grid_rows * shape[0],
                             self.grid_cols * shape[1]), 'uint16')
                    self.grid_preview[
                        r * shape[0]:(r + 1) * shape[0],
                        c * shape[1]:(c + 1) * shape[1]
                        ] = grid_image
                # display:
                self.scope.display.show_grid_preview(self.grid_preview)
                # check before re-run:
                if (self.running_grid_preview.get() and
                    self.current_grid_image < len(self.XY_grid_rc_list) - 1):
                    self.current_grid_image += 1
                    self.root.after(self.gui_delay_ms, run_grid_preview)
                else:
                    print('Grid preview -> finished\n')
                return None
            run_grid_preview()
            return None
        self.running_grid_preview = tk.BooleanVar()
        self.start_grid_preview_button = tk.Button(
            grid_frame,
            text="Start grid preview (from A1)",
            command=start_grid_preview,
            font=('Segoe UI', '10', 'italic'),
            width=button_width,
            height=button_height)
        self.start_grid_preview_button.grid(row=7, column=0, padx=10, pady=10)
        self.start_grid_preview_button.config(state='disabled')
        start_grid_preview_tip = tix.Balloon(self.start_grid_preview_button)
        start_grid_preview_tip.bind_widget(
            self.start_grid_preview_button,
            balloonmsg=(
                "The 'Start grid preview (from A1)' button will start to \n" +
                "generate previews for the whole grid of points (starting \n" +
                "at A1). Consider using 'Save data and position' and 'Tile \n" +
                "the grid' for extra functionality."))
        # cancel grid preview:
        def cancel_grid_preview():
            self.running_grid_preview.set(0)
            print('\n ***Grid preview -> canceled*** \n')
            return None
        cancel_grid_preview_button = tk.Button(
            grid_frame,
            text="Cancel grid preview",
            command=cancel_grid_preview,
            width=button_width,
            height=button_height)
        cancel_grid_preview_button.grid(row=8, column=0, padx=10, pady=10)
        cancel_grid_preview_tip = tix.Balloon(cancel_grid_preview_button)
        cancel_grid_preview_tip.bind_widget(
            cancel_grid_preview_button,
            balloonmsg=(
                "The 'Cancel grid preview' button will cancel any ongoing \n" +
                "grid preview generation.\n" +
                "NOTE: this is not immediate since some processes must \n" +
                "finish once launched."))
        return None

    def init_tile_navigator(self):
        frame = tk.LabelFrame(self.root, text='TILE NAVIGATOR', bd=6)
        frame.grid(row=3, column=4, rowspan=2, padx=10, pady=10, sticky='n')
        button_width, button_height = 25, 2
        spinbox_width = 20
        # tile array width:
        self.tile_array_width = tkcw.CheckboxSliderSpinbox(
            frame,
            label='Array height and width (tiles)',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=2,
            max_value=9,
            default_value=2,
            row=0,
            width=spinbox_width)
        tile_array_width_tip = tix.Balloon(self.tile_array_width)
        tile_array_width_tip.bind_widget(
            self.tile_array_width,
            balloonmsg=(
                "The 'Array height and width (tiles)' determines how many \n" +
                "tiles the 'Start tile' button will generate. For example, \n" +
                "2 gives a 2x2 array of tiles, 3 a 3x3 array, etc."))
        # save data and position:
        self.save_tile_data_and_position = tk.BooleanVar()
        save_tile_data_and_position_button = tk.Checkbutton(
            frame,
            text='Save data and position',
            variable=self.save_tile_data_and_position)
        save_tile_data_and_position_button.grid(
            row=1, column=0, padx=10, pady=10)
        save_tile_data_and_position_tip = tix.Balloon(
            save_tile_data_and_position_button)
        save_tile_data_and_position_tip.bind_widget(
            save_tile_data_and_position_button,
            balloonmsg=(
                "If 'Save data and position' is enabled then the \n" +
                "'Start tile' button will save the full data set \n" +
                "(in addition to the preview data) and populate the \n" +
                "'POSITION LIST'."))
        # start tile preview:
        def start_tile_preview():
            print('\nTile preview -> started')
            self._set_running_mode('tile_preview', enable=True)
            if self.volumes_per_buffer.value.get() != 1:
                self.volumes_per_buffer.update_and_validate(1)
            folder_name = self._get_folder_name() + '_tile'
            # get tile parameters:
            self.tile_rows = self.tile_array_width.value.get()
            self.tile_cols = self.tile_rows
            # calculate move size:
            X_move_mm = 1e-3 * self.width_px.value.get() * sols.sample_px_um
            Y_move_mm = 1e-3 * self.scan_range_um.value.get()
            # generate tile list:
            self.tile_list = []
            for r in range(self.tile_rows):
                for c in range(self.tile_cols):
                    p_mm = (self.X_stage_position_mm - c * X_move_mm,
                            self.Y_stage_position_mm + r * Y_move_mm)
                    self.tile_list.append((r, c, p_mm))
            self.current_tile = 0
            def run_tile_preview():
                # update position:
                r, c, p_mm = self.tile_list[self.current_tile]
                self._update_XY_stage_position(p_mm)
                # get tile:
                name = "r%ic%i"%(r, c)
                filename = name + '.tif'
                preview_only = True
                if self.save_tile_data_and_position.get():
                    preview_only = False
                    self._update_position_list()
                self.scope.acquire(
                    filename=filename,
                    folder_name=folder_name,
                    description=self.description_textbox.text,
                    preview_only=preview_only).join()
                tile_filename = (folder_name + '\preview\\' + filename)
                while not os.path.isfile(tile_filename):
                    self.root.after(self.gui_delay_ms)
                tile = imread(tile_filename)
                shape = tile.shape
                # add reference:
                tile = Image.fromarray(tile) # convert to PIL for ImageDraw
                XY = (int(0.1 * min(shape)), shape[0] - int(0.15 * min(shape)))
                font_size = int(0.1 * min(shape))
                font = ImageFont.truetype('arial.ttf', font_size)
                ImageDraw.Draw(tile).text(XY, name, fill=0, font=font)
                # make base image:
                if self.current_tile == 0:
                    self.tile_preview = np.zeros(
                        (self.tile_rows * shape[0],
                         self.tile_cols * shape[1]), 'uint16')
                # add current tile:
                self.tile_preview[r * shape[0]:(r + 1) * shape[0],
                                  c * shape[1]:(c + 1) * shape[1]] = tile
                # display:
                self.scope.display.show_tile_preview(self.tile_preview)
                if (self.running_tile_preview.get() and
                    self.current_tile < len(self.tile_list) - 1): 
                    self.current_tile += 1
                    self.root.after(self.gui_delay_ms, run_tile_preview)
                else:
                    self.running_tile_preview.set(0)
                    self.move_to_tile_button.config(state='normal')
                    print('Tile preview -> finished\n')
                return None
            run_tile_preview()
            return None
        self.running_tile_preview = tk.BooleanVar()
        start_tile_preview_button = tk.Button(
            frame,
            text="Start tile",
            command=start_tile_preview,
            font=('Segoe UI', '10', 'italic'),
            width=button_width,
            height=button_height)
        start_tile_preview_button.grid(row=2, column=0, padx=10, pady=10)
        start_tile_tip = tix.Balloon(start_tile_preview_button)
        start_tile_tip.bind_widget(
            start_tile_preview_button,
            balloonmsg=(
                "The 'Start tile' button will start to generate previews \n" +
                "for the tile array using the current XY position as the \n" +
                "first tile (the top left position r0c0). Consider using \n" +
                "'Save data and position' for extra functionality."))
        # cancel tile preview:
        def cancel_tile_preview():
            self.running_tile_preview.set(0)
            print('\n ***Tile preview -> canceled*** \n')
            return None
        cancel_tile_preview_button = tk.Button(
            frame,
            text="Cancel tile",
            command=cancel_tile_preview,
            width=button_width,
            height=button_height)
        cancel_tile_preview_button.grid(row=3, column=0, padx=10, pady=10)
        cancel_tile_preview_tip = tix.Balloon(cancel_tile_preview_button)
        cancel_tile_preview_tip.bind_widget(
            cancel_tile_preview_button,
            balloonmsg=(
                "The 'Cancel tile' button will cancel any ongoing tile\n" +
                "preview generation.\n" +
                "NOTE: this is not immediate since some processes must \n" +
                "finish once launched."))        
        # move to tile:
        def move_to_tile():
            move_to_tile_popup = tk.Toplevel()
            move_to_tile_popup.title('Move to tile')
            move_to_tile_popup.grab_set() # force user to interact
            x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
            move_to_tile_popup.geometry("+%d+%d" % (x + 800, y + 400))
            # cancel button:
            cancel_button = tk.Button(
                move_to_tile_popup, text="Cancel",
                command=move_to_tile_popup.destroy,
                height=button_height, width=button_width)
            cancel_button.grid(row=1, column=0, padx=10, pady=10, sticky='n')
            # make buttons:
            tile_buttons_frame = tk.LabelFrame(
                move_to_tile_popup, text='XY TILES', bd=6)
            tile_buttons_frame.grid(
                row=0, column=1, rowspan=5, padx=10, pady=10)
            def move(tile):
                self._update_XY_stage_position(self.tile_list[tile][2])
                self._snap_and_display()
                self.current_tile = tile
                move_to_tile_popup.destroy()
                return None
            for t in range(len(self.tile_list)):
                r, c, p_mm = self.tile_list[t]
                tile_button = tk.Button(
                    tile_buttons_frame,
                    text='r%ic%i'%(r, c),
                    command=lambda tile=t: move(tile),
                    width=5,
                    height=2)
                tile_button.grid(row=r, column=c, padx=10, pady=10)
                if t == self.current_tile:
                    tile_button.config(state='disabled')
            return None
        self.move_to_tile_button = tk.Button(
            frame,
            text="Move to tile",
            command=move_to_tile,
            width=button_width,
            height=button_height)
        self.move_to_tile_button.grid(row=4, column=0, padx=10, pady=10)
        self.move_to_tile_button.config(state='disabled')
        move_to_tile_tip = tix.Balloon(self.move_to_tile_button)
        move_to_tile_tip.bind_widget(
            self.move_to_tile_button,
            balloonmsg=(
                "The 'Move to tile' button moves to the chosen tile \n" +
                "location based on the absolute XY tile positions \n" +
                "from the last tile routine."))
        return None

    def init_settings(self):
        self.settings_frame = tk.LabelFrame(
            self.root, text='SETTINGS (misc)', bd=6)
        self.settings_frame.grid(
            row=1, column=5, rowspan=2, padx=10, pady=10, sticky='n')
        button_width, button_height = 25, 2
        spinbox_width = 20
        # load from file:
        def load_settings_from_file():
            # get file from user:
            file_path = tk.filedialog.askopenfilename(
                parent=self.root,
                initialdir=os.getcwd(),
                title='Please choose a previous "metadata" file (.txt)')        
            with open(file_path, 'r') as file:
                metadata = file.read().splitlines()
            # format into settings and values:
            file_settings = {}
            for data in metadata:
                file_settings[data.split(':')[0]] = (
                    data.split(':')[1:][0].lstrip())
            # re-format strings from file settings for gui:
            channels = file_settings[
                'channels_per_slice'].strip('(').strip(')').split(',')
            powers   = file_settings[
                'power_per_channel'].strip('(').strip(')').split(',')
            channels_per_slice, power_per_channel = [], []
            for i, c in enumerate(channels):
                if c == '': break # avoid bug from tuple with single entry
                channels_per_slice.append(c.split("'")[1])
                power_per_channel.append(int(powers[i]))
            # turn off all illumination:
            self.power_tl.checkbox_value.set(0)
            self.power_405.checkbox_value.set(0)
            self.power_488.checkbox_value.set(0)
            self.power_561.checkbox_value.set(0)
            self.power_640.checkbox_value.set(0)
            # apply file settings to gui:
            for i, channel in enumerate(channels_per_slice):
                if channel == 'LED':
                    self.power_tl.checkbox_value.set(1)
                    self.power_tl.update_and_validate(power_per_channel[i])
                if channel == '405':
                    self.power_405.checkbox_value.set(1)
                    self.power_405.update_and_validate(power_per_channel[i])
                if channel == '488':
                    self.power_488.checkbox_value.set(1)
                    self.power_488.update_and_validate(power_per_channel[i])
                if channel == '561':
                    self.power_561.checkbox_value.set(1)
                    self.power_561.update_and_validate(power_per_channel[i])
                if channel == '640':
                    self.power_640.checkbox_value.set(1)
                    self.power_640.update_and_validate(power_per_channel[i])
            self.emission_filter.set(file_settings['emission_filter'])
            self.illumination_time_us.update_and_validate(
                int(file_settings['illumination_time_us']))
            self.height_px.update_and_validate(int(file_settings['height_px']))
            self.width_px.update_and_validate(
                int(file_settings['width_px']))
            self.voxel_aspect_ratio.update_and_validate(
                int(round(float(file_settings['voxel_aspect_ratio']))))
            self.scan_range_um.update_and_validate(
                int(round(float(file_settings['scan_range_um']))))
            self.volumes_per_buffer.update_and_validate(
                int(file_settings['volumes_per_buffer']))
            return None
        load_from_file_button = tk.Button(
            self.settings_frame,
            text="Load from file",
            command=load_settings_from_file,
            font=('Segoe UI', '10', 'underline'),
            width=button_width,
            height=button_height)
        load_from_file_button.grid(row=0, column=0, padx=10, pady=10)
        load_from_file_tip = tix.Balloon(load_from_file_button)
        load_from_file_tip.bind_widget(
            load_from_file_button,
            balloonmsg=(
                "Use the 'Load from file' button to select a '.txt' file \n" + 
                "from the 'metadata' folder of a previous acquisition and \n" +
                "load these settings into the GUI. The loaded settings are:\n" +
                "- 'TRANSMITTED LIGHT'.\n" +
                "- 'LASER BOX'.\n" +
                "- 'DICHROIC MIRROR'.\n" +
                "- 'FILTER WHEEL'.\n" +
                "- 'CAMERA'.\n" +
                "- 'GALVO'.\n" +
                "- 'Volumes per acquire'.\n" +
                "NOTE: 'FOCUS PIEZO', 'XY STAGE', 'Foder label' and \n" +
                "'Description' are not loaded. To load previous XYZ \n" +
                "positions use the 'POSITION LIST' panel."))
        # label textbox:
        self.label_textbox = tkcw.Textbox(
            self.settings_frame,
            label='Folder label',
            default_text='sols',
            row=1,
            width=spinbox_width,
            height=1)
        label_textbox_tip = tix.Balloon(self.label_textbox)
        label_textbox_tip.bind_widget(
            self.label_textbox,
            balloonmsg=(
                "The label that will be used for the data folder (after \n" +
                "the date and time stamp). Edit to preference"))
        # description textbox:
        self.description_textbox = tkcw.Textbox(
            self.settings_frame,
            label='Description',
            default_text='what are you doing?',
            row=2,
            width=spinbox_width,
            height=3)
        description_textbox_tip = tix.Balloon(self.description_textbox)
        description_textbox_tip.bind_widget(
            self.description_textbox,
            balloonmsg=(
                "The text that will be recorded in the metadata '.txt'\n" +
                "file (along with the microscope settings for that \n" +
                "acquisition). Describe what you are doing here."))        
        # volumes spinbox:
        self.volumes_per_buffer = tkcw.CheckboxSliderSpinbox(
            self.settings_frame,
            label='Volumes per acquire',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=1e3,
            default_value=1,
            row=3,
            width=spinbox_width)
        self.volumes_per_buffer.value.trace_add(
            'write',
            lambda var, index, mode: self.scope.apply_settings(
                volumes_per_buffer=self.volumes_per_buffer.value.get()))
        volumes_per_buffer_tip = tix.Balloon(self.volumes_per_buffer)
        volumes_per_buffer_tip.bind_widget(
            self.volumes_per_buffer,
            balloonmsg=(
                "In short: How many back to back (as fast as possible) \n" +
                "volumes did you want for a given acquisition?\n" +
                "(If you are not sure or don't care then leave this as 1!)\n" +
                "In detail: increasing this number (above 1 volume) \n" +
                "pre-loads more acquisitions onto the analogue out (AO) \n" +
                "card. This has pro's and con's.\n" +
                "Pros:\n" +
                "- It allows successive volumes to be taken with minimal \n" +
                "latency.\n" +
                "- The timing for successive volumes can be 'us' precise.\n" +
                "Cons:\n" +
                "- It takes time to 'load' and 'play' a volume. More \n" +
                "volumes takes more time, and once requested this \n"
                "operation cannot be cancelled.\n" +
                "- The data from a single 'play' of the AO card is \n" +
                "recording into a single file. More volumes is more data \n" +
                "and a bigger file. It's easy to end up with a huge file \n" +
                "that is not a 'legal' .tiff (<~4GB) and is tricky to \n" +
                "manipulate."))
        # loop over positions:
        self.loop_over_position_list = tk.BooleanVar()
        loop_over_position_list_button = tk.Checkbutton(
            self.settings_frame,
            text='Loop over position list',
            variable=self.loop_over_position_list)
        loop_over_position_list_button.grid(
            row=4, column=0, padx=10, pady=10, sticky='w')
        loop_over_position_list_tip = tix.Balloon(
            loop_over_position_list_button)
        loop_over_position_list_tip.bind_widget(
            loop_over_position_list_button,
            balloonmsg=(
                "If checked, the 'Run acquire' button will loop over the \n" +
                "XYZ positions stored in the 'POSITION LIST'.\n" +
                "NOTE: it can take a significant amount of time to image \n" +
                "many positions so this should be taken into consideration \n" +
                "(especially for a time series)."))
        # acquire number spinbox:
        self.acquire_number_spinbox = tkcw.CheckboxSliderSpinbox(
            self.settings_frame,
            label='Acquire number',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=1e6,
            default_value=1,
            row=5,
            width=spinbox_width)
        acquire_number_spinbox_tip = tix.Balloon(self.acquire_number_spinbox)
        acquire_number_spinbox_tip.bind_widget(
            self.acquire_number_spinbox,
            balloonmsg=(
                "How many acquisitions did you want when you press the \n" +
                "'Run acquire' button?\n" +
                "NOTE: there is no immediate limit here, but data \n"
                "accumulation and thermal drift can limit in practice."))
        # delay spinbox:
        self.delay_spinbox = tkcw.CheckboxSliderSpinbox(
            self.settings_frame,
            label='Inter-acquire delay (s) >=',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=0,
            max_value=3600,
            default_value=0,
            row=6,
            width=spinbox_width)
        delay_spinbox_tip = tix.Balloon(self.delay_spinbox)
        delay_spinbox_tip.bind_widget(
            self.delay_spinbox,
            balloonmsg=(
                "How long do you want to wait between acquisitions?\n" +
                "NOTE: the GUI will attempt to achieve the requested \n" +
                "interval. However, if the acquisition (which may \n" +
                "include multiple colors/volumes/positions) takes \n" +
                "longer than the requested delay then it will simply \n" +
                "run as fast as it can."))        
        return None

    def init_settings_output(self):
        self.output_frame = tk.LabelFrame(
            self.root, text='SETTINGS OUTPUT', bd=6)
        self.output_frame.grid(
            row=3, column=5, rowspan=2, padx=10, pady=10, sticky='n')
        button_width, button_height = 25, 2
        spinbox_width = 20
        # volumes per second textbox:
        self.volumes_per_s = tk.IntVar()
        volumes_per_s_textbox = tkcw.Textbox(
            self.output_frame,
            label='Volumes per second',
            default_text='None',
            row=0,
            width=spinbox_width,
            height=1)
        def update_volumes_per_s():            
            text = '%0.3f'%self.volumes_per_s.get()
            volumes_per_s_textbox.textbox.delete('1.0', '10.0')
            volumes_per_s_textbox.textbox.insert('1.0', text)
            return None
        self.volumes_per_s.trace_add(
            'write',
            lambda var, index, mode: update_volumes_per_s())
        volumes_per_s_textbox_tip = tix.Balloon(volumes_per_s_textbox)
        volumes_per_s_textbox_tip.bind_widget(
            volumes_per_s_textbox,
            balloonmsg=(
                "Shows the 'Volumes per second' (Vps) based on the \n" +
                "settings that were last applied to the microscope.\n" +
                "NOTE: this is the volumetric rate for the acquisition \n" +
                "(i.e. during the analogue out 'play') and does reflect \n" +
                "any delays or latency between acquisitions."))
        # total memory textbox:
        self.total_bytes = tk.IntVar()
        total_memory_textbox = tkcw.Textbox(
            self.output_frame,
            label='Total memory (GB)',
            default_text='None',
            row=1,
            width=spinbox_width,
            height=1)
        def update_total_memory():
            total_memory_gb = 1e-9 * self.total_bytes.get()
            max_memory_gb = 1e-9 * self.max_allocated_bytes
            memory_pct = 100 * total_memory_gb / max_memory_gb
            text = '%0.3f (%0.2f%% of max)'%(total_memory_gb, memory_pct)
            total_memory_textbox.textbox.delete('1.0', '10.0')
            total_memory_textbox.textbox.insert('1.0', text)
            return None
        self.total_bytes.trace_add(
            'write',
            lambda var, index, mode: update_total_memory())
        total_memory_textbox_tip = tix.Balloon(total_memory_textbox)
        total_memory_textbox_tip.bind_widget(
            total_memory_textbox,
            balloonmsg=(
                "Shows the 'Total memory (GB)' that the microscope will \n" +
                "need to run the settings that were last applied.\n" +
                "NOTE: this can be useful for montoring resources and \n" +
                "avoiding memory limits."))
        # total storage textbox:
        self.data_bytes = tk.IntVar()
        self.preview_bytes = tk.IntVar()
        total_storage_textbox = tkcw.Textbox(
            self.output_frame,
            label='Total storage (GB)',
            default_text='None',
            row=2,
            width=spinbox_width,
            height=1)
        def update_total_storage():
            positions = 1
            if self.loop_over_position_list.get():
                positions = max(len(self.XY_stage_position_list), 1)
            acquires = self.acquire_number_spinbox.value.get()
            data_gb = 1e-9 * self.data_bytes.get()
            preview_gb = 1e-9 * self.preview_bytes.get()
            total_storage_gb = (data_gb + preview_gb) * positions * acquires
            text = '%0.3f'%total_storage_gb
            total_storage_textbox.textbox.delete('1.0', '10.0')
            total_storage_textbox.textbox.insert('1.0', text)
            return None
        self.data_bytes.trace_add(
            'write',
            lambda var, index, mode: update_total_storage())
        total_storage_textbox_tip = tix.Balloon(total_storage_textbox)
        total_storage_textbox_tip.bind_widget(
            total_storage_textbox,
            balloonmsg=(
                "Shows the 'Total storage (GB)' that the microscope will \n" +
                "need to save the data if 'Run acquire' is pressed (based \n" +
                "on the settings that were last applied).\n" +
                "NOTE: this can be useful for montoring resources and \n" +
                "avoiding storage limits."))
        # min time textbox:
        self.buffer_time_s = tk.DoubleVar()
        min_time_textbox = tkcw.Textbox(
            self.output_frame,
            label='Minimum acquire time (s)',
            default_text='None',
            row=3,
            width=spinbox_width,
            height=1)
        def update_min_time():
            positions = 1
            if self.loop_over_position_list.get():
                positions = max(len(self.XY_stage_position_list), 1)
            acquires = self.acquire_number_spinbox.value.get()
            min_acquire_time_s = self.buffer_time_s.get() * positions
            min_total_time_s = min_acquire_time_s * acquires
            if self.delay_spinbox.value.get() > min_acquire_time_s:
                min_total_time_s = (self.delay_spinbox.value.get() * (
                    acquires - 1) + min_acquire_time_s)
            text = '%0.6f (%0.0f min)'%(
                min_total_time_s, (min_total_time_s / 60))
            min_time_textbox.textbox.delete('1.0', '10.0')
            min_time_textbox.textbox.insert('1.0', text)
            return None
        self.buffer_time_s.trace_add(
            'write',
            lambda var, index, mode: update_min_time())
        min_time_textbox_tip = tix.Balloon(min_time_textbox)
        min_time_textbox_tip.bind_widget(
            min_time_textbox,
            balloonmsg=(
                "Shows the 'Minimum acquire time (s)' that the microscope \n" +
                "will need if 'Run acquire' is pressed (based on the \n" +
                "settings that were last applied).\n" +
                "NOTE: this value does not take into account the \n" +
                "'move time' when using the 'Loop over position list' \n" +
                "option (so the actual time will be significantly more)."))
        return None

    def init_position_list(self):
        positions_frame = tk.LabelFrame(
            self.root, text='POSITION LIST (Scout mode)', bd=6)
        positions_frame.grid(
            row=1, column=6, rowspan=2, padx=10, pady=10, sticky='n')
        button_width, button_height = 25, 2
        spinbox_width = 20
        # set list defaults:
        self.focus_piezo_position_list = []
        self.XY_stage_position_list = []
        def make_empty_position_list():
            self.focus_piezo_position_list = []
            self.XY_stage_position_list = []
            with open(self.session_folder +
                      "focus_piezo_position_list.txt", "w") as file:
                file.write(self.session_folder + '\n')
            with open(self.session_folder +
                  "XY_stage_position_list.txt", "w") as file:
                file.write(self.session_folder + '\n')
            return None
        # load from folder:
        def load_positions_from_folder():
            # get folder from user:
            folder_path = tk.filedialog.askdirectory(
                parent=self.root,
                initialdir=os.getcwd(),
                title='Please choose a previous "gui session" folder')
            # read files, parse into lists and update attributes:
            focus_piezo_file_path = (
                folder_path + '\\focus_piezo_position_list.txt')
            XY_stage_file_path = (
                folder_path + '\\XY_stage_position_list.txt')
            with open(focus_piezo_file_path, 'r') as file:
                focus_piezo_position_list = file.read().splitlines()
            with open(XY_stage_file_path, 'r') as file:
                XY_stage_position_list = file.read().splitlines()
            for i, element in enumerate(focus_piezo_position_list):
                focus_piezo_z_um = int(element.strip(','))
                focus_piezo_position_list[i] = focus_piezo_z_um
                self.focus_piezo_position_list.append(focus_piezo_z_um)
            for i, element in enumerate(XY_stage_position_list):
                XY_stage_position_mm = [
                    float(element.strip('[').strip(']').split(',')[0]),
                    float(element.strip('[').split(',')[1].strip(']').lstrip())]
                XY_stage_position_list[i] = XY_stage_position_mm
                self.XY_stage_position_list.append(XY_stage_position_mm)
            # append positions to files:
            with open(self.session_folder +
                      "focus_piezo_position_list.txt", "a") as file:
                for i in range(len(focus_piezo_position_list)):
                    file.write(str(focus_piezo_position_list[i]) + ',\n')
            with open(self.session_folder +
                      "XY_stage_position_list.txt", "a") as file:
                for i in range(len(XY_stage_position_list)):
                    file.write(str(XY_stage_position_list[i]) + ',\n')
            # update gui:
            total_positions = len(self.focus_piezo_position_list)
            self.total_positions_spinbox.update_and_validate(total_positions)
            return None
        load_from_folder_button = tk.Button(
            positions_frame,
            text="Load from folder",
            command=load_positions_from_folder,
            font=('Segoe UI', '10', 'underline'),
            width=button_width,
            height=button_height)
        load_from_folder_button.grid(row=0, column=0, padx=10, pady=10)
        load_from_folder_tip = tix.Balloon(load_from_folder_button)
        load_from_folder_tip.bind_widget(
            load_from_folder_button,
            balloonmsg=(
                "Use the 'Load from folder' button to select a previous \n" + 
                "'sols_gui_session' folder and load the associated \n" +
                "position list into the GUI.\n" +
                "NOTE: this will overwrite any existing position list"))
        # delete all:
        def delete_all_positions():
            make_empty_position_list()
            self.total_positions_spinbox.update_and_validate(0)
            self.current_position_spinbox.update_and_validate(0)
            return None        
        delete_all_positions_button = tk.Button(
            positions_frame,
            text="Delete all positions",
            command=delete_all_positions,
            width=button_width,
            height=button_height)
        delete_all_positions_button.grid(row=1, column=0, padx=10, pady=10)
        delete_all_positions_tip = tix.Balloon(delete_all_positions_button)
        delete_all_positions_tip.bind_widget(
            delete_all_positions_button,
            balloonmsg=(
                "The 'Delete all positions' button clears the current \n" + 
                "position list in the GUI and updates the associated \n" +
                ".txt files in the 'sols_gui_session' folder.\n" +
                "NOTE: this operation cannot be reversed."))
        # delete current:
        def delete_current_position():
            if self.total_positions_spinbox.value.get() == 0:
                return
            i = self.current_position_spinbox.value.get() - 1
            self.focus_piezo_position_list.pop(i)
            self.XY_stage_position_list.pop(i)
            # overwrite files:
            with open(self.session_folder +
                      "focus_piezo_position_list.txt", "w") as file:
                file.write(self.session_folder + '\n')
            with open(self.session_folder +
                      "XY_stage_position_list.txt", "w") as file:
                file.write(self.session_folder + '\n')
            # update files:
            with open(self.session_folder +
                      "focus_piezo_position_list.txt", "a") as file:
                for i in range(len(self.focus_piezo_position_list)):
                    file.write(str(self.focus_piezo_position_list[i]) + ',\n')
            with open(self.session_folder +
                      "XY_stage_position_list.txt", "a") as file:
                for i in range(len(self.XY_stage_position_list)):
                    file.write(str(self.XY_stage_position_list[i]) + ',\n')
            # update gui:
            total_positions = len(self.focus_piezo_position_list)
            self.total_positions_spinbox.update_and_validate(total_positions)
            self.current_position_spinbox.update_and_validate(i)
            return None
        delete_current_position_button = tk.Button(
            positions_frame,
            text="Delete current position",
            command=delete_current_position,
            width=button_width,
            height=button_height)
        delete_current_position_button.grid(row=2, column=0, padx=10, pady=10)
        delete_current_position_tip = tix.Balloon(
            delete_current_position_button)
        delete_current_position_tip.bind_widget(
            delete_current_position_button,
            balloonmsg=(
                "The 'Delete current position' button clears the current \n" + 
                "position from the position list in the GUI and updates \n" +
                "the associated .txt files in the 'sols_gui_session' \n" +
                "folder.\n" +
                "NOTE: this operation cannot be reversed."))
        # total positions:
        self.total_positions_spinbox = tkcw.CheckboxSliderSpinbox(
            positions_frame,
            label='Total positions',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=0,
            max_value=1e6,
            default_value=0,
            row=3,
            width=spinbox_width)
        self.total_positions_spinbox.spinbox.config(state='disabled')
        total_positions_spinbox_tip = tix.Balloon(
            self.total_positions_spinbox)
        total_positions_spinbox_tip.bind_widget(
            self.total_positions_spinbox,
            balloonmsg=(
                "The 'Total positions' displays the total number of \n" + 
                "positions currently stored in the position list (both in \n" +
                "the GUI and the associated .txt files in the\n" +
                "'sols_gui_session' folder."))
        # utility function:
        def update_position(position):
            if self.total_positions_spinbox.value.get() != 0:
                self.focus_piezo_z_um.update_and_validate(
                    self.focus_piezo_position_list[position - 1])
                self._update_XY_stage_position(
                    self.XY_stage_position_list[position - 1])
                self.current_position_spinbox.update_and_validate(position)
                if not self.running_scout_mode.get():
                    self._snap_and_display()
            return None
        # move to start:
        def move_to_start():
            update_position(1)
            return None
        move_to_start_button = tk.Button(
            positions_frame,
            text="Move to start",
            command=move_to_start,
            width=button_width,
            height=button_height)
        move_to_start_button.grid(row=4, column=0, padx=10, pady=10)
        move_to_start_button_tip = tix.Balloon(move_to_start_button)
        move_to_start_button_tip.bind_widget(
            move_to_start_button,
            balloonmsg=(
                "The 'Move to start' button will move the 'FOCUS PIEZO' \n" + 
                "and 'XY STAGE' to the first position in the position list.\n" +
                "NOTE: this is only active in 'Scout mode' and if the \n" +
                "position is not already at the start of the position list."))
        # move back:
        def move_back():
            new_position = self.current_position_spinbox.value.get() - 1
            if new_position < 1:
                new_position = 1
            update_position(new_position)
            return None
        move_back_button = tk.Button(
            positions_frame,
            text="Move back (-1)",
            command=move_back,
            width=button_width,
            height=button_height)
        move_back_button.grid(row=5, column=0, padx=10, pady=10)
        move_back_button_tip = tix.Balloon(move_back_button)
        move_back_button_tip.bind_widget(
            move_back_button,
            balloonmsg=(
                "The 'Move back (-1)' button will move the 'FOCUS PIEZO' \n" + 
                "and 'XY STAGE' to the previous (n - 1) position in the \n" +
                "position list.\n" +
                "NOTE: this is only active in 'Scout mode' and if the \n" +
                "position is not already at the start of the position list."))
        # current position:
        self.current_position_spinbox = tkcw.CheckboxSliderSpinbox(
            positions_frame,
            label='Current position',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=0,
            max_value=1e6,
            default_value=0,
            row=6,
            width=spinbox_width)
        self.current_position_spinbox.spinbox.config(state='disabled')
        current_position_spinbox_tip = tix.Balloon(
            self.current_position_spinbox)
        current_position_spinbox_tip.bind_widget(
            self.current_position_spinbox,
            balloonmsg=(
                "The 'Current position' displays the current position in \n" + 
                "the position list based on the last update to the \n" +
                "position list or move request in the 'POSITION LIST' \n" +
                "panel.\n" +
                "NOTE: is not aware of XY moves made elsewhere (e.g. with \n" +
                "the joystick or 'XY STAGE' panel). Use one of the 'move' \n" +
                "buttons to update if needed."))
        # go forwards:
        def move_forward():
            new_position = self.current_position_spinbox.value.get() + 1
            if new_position > self.total_positions_spinbox.value.get():
                new_position = self.total_positions_spinbox.value.get()
            update_position(new_position)
            return None
        move_forward_button = tk.Button(
            positions_frame,
            text="Move forward (+1)",
            command=move_forward,
            width=button_width,
            height=button_height)
        move_forward_button.grid(row=7, column=0, padx=10, pady=10)
        move_forward_button_tip = tix.Balloon(move_forward_button)
        move_forward_button_tip.bind_widget(
            move_forward_button,
            balloonmsg=(
                "The 'Move forward (+1)' button will move the 'FOCUS \n" + 
                "PIEZO' and 'XY STAGE' to the next (n + 1) position in \n" +
                "the position list.\n" +
                "NOTE: this is only active in 'Scout mode' and if the \n" +
                "position is not already at the end of the position list."))
        # move to end:
        def move_to_end():
            update_position(self.total_positions_spinbox.value.get())
            return None
        move_to_end_button = tk.Button(
            positions_frame,
            text="Move to end",
            command=move_to_end,
            width=button_width,
            height=button_height)
        move_to_end_button.grid(row=8, column=0, padx=10, pady=10)
        move_to_end_button_tip = tix.Balloon(move_to_end_button)
        move_to_end_button_tip.bind_widget(
            move_to_end_button,
            balloonmsg=(
                "The 'Move to end' button will move the 'FOCUS PIEZO' \n" + 
                "and 'XY STAGE' to the last position in the position list.\n" +
                "NOTE: this is only active in 'Scout mode' and if the \n" +
                "position is not already at the end of the position list."))        
        return None

    def _update_position_list(self):
        # update list:
        self.focus_piezo_position_list.append(self.focus_piezo_z_um.value.get())
        self.XY_stage_position_list.append([self.X_stage_position_mm,
                                            self.Y_stage_position_mm])
        # update gui:
        positions = len(self.focus_piezo_position_list)
        self.total_positions_spinbox.update_and_validate(positions)
        self.current_position_spinbox.update_and_validate(positions)
        # write to file:
        with open(self.session_folder +
                  "focus_piezo_position_list.txt", "a") as file:
            file.write(str(self.focus_piezo_position_list[-1]) + ',\n')
        with open(self.session_folder +
                  "XY_stage_position_list.txt", "a") as file:
            file.write(str(self.XY_stage_position_list[-1]) + ',\n')
        return None

    def init_acquire(self):
        self.acquire_frame = tk.LabelFrame(
            self.root, text='ACQUIRE', font=('Segoe UI', '10', 'bold'), bd=6)
        self.acquire_frame.grid(
            row=3, column=6, rowspan=2, padx=10, pady=10, sticky='n')
        button_width, button_height = 25, 2
        bold_width_adjust = -3
        spinbox_width = 20
        # snap volume:
        snap_volume_button = tk.Button(
            self.acquire_frame,
            text="Snap volume",
            command=self._snap_and_display,
            font=('Segoe UI', '10', 'bold'),
            width=button_width + bold_width_adjust,
            height=button_height)
        snap_volume_button.grid(row=0, column=0, padx=10, pady=10)
        snap_volume_button_tip = tix.Balloon(snap_volume_button)
        snap_volume_button_tip.bind_widget(
            snap_volume_button,
            balloonmsg=(
                "The 'Snap volume' button will apply the lastest \n" + 
                "microscope settings and acquire a volume. This is \n" +
                "useful for refreshing the display.\n" +
                "NOTE: this does not save any data or position information."))
        # live mode:
        def live_mode():
            self._set_running_mode('live')
            def run_live_mode():
                if self.running_live_mode.get():
                    self._snap_and_display()
                    self.root.after(self.gui_delay_ms, run_live_mode)
                return None
            run_live_mode()
            return None
        self.running_live_mode = tk.BooleanVar()
        live_mode_button = tk.Checkbutton(
            self.acquire_frame,
            text='Live mode (On/Off)',
            variable=self.running_live_mode,
            command=live_mode,
            indicatoron=0,
            font=('Segoe UI', '10', 'italic'),
            width=button_width,
            height=button_height)
        live_mode_button.grid(row=1, column=0, padx=10, pady=10)
        live_mode_button_tip = tix.Balloon(live_mode_button)
        live_mode_button_tip.bind_widget(
            live_mode_button,
            balloonmsg=(
                "The 'Live mode (On/Off)' button will enable/disable 'Live \n" + 
                "mode'. 'Live mode' will continously apply the lastest \n" +
                "microscope settings and acquire a volume.\n" +
                "NOTE: this continously exposes the sample to light which \n" +
                "may cause photobleaching/phototoxicity. To reduce this \n" +
                "effect use 'Scout mode'.")) 
        # scout mode:
        def scout_mode():
            self._set_running_mode('scout')
            if self.running_scout_mode.get():
                self._snap_and_display()
            return None
        self.running_scout_mode = tk.BooleanVar()
        scout_mode_button = tk.Checkbutton(
            self.acquire_frame,
            text='Scout mode (On/Off)',
            variable=self.running_scout_mode,
            command=scout_mode,
            indicatoron=0,
            font=('Segoe UI', '10', 'bold', 'italic'),
            fg='green',
            width=button_width + bold_width_adjust,
            height=button_height)
        scout_mode_button.grid(row=2, column=0, padx=10, pady=10)
        scout_mode_button_tip = tix.Balloon(scout_mode_button)
        scout_mode_button_tip.bind_widget(
            scout_mode_button,
            balloonmsg=(
                "The 'Scout mode (On/Off)' button will enable/disable \n" + 
                "'Scout mode'. 'Scout mode' will only acquire a volume\n" +
                "if XYZ motion is detected. This helps to reduce \n" +
                "photobleaching/phototoxicity.\n" +
                "NOTE: to reduce latency the microscope settings are only \n" +
                "updated when a button from the 'ACQUIRE' panel is pressed \n" +
                "(excluding 'Cancel acquire'). For example, you can use \n" +
                "'Snap volume' to refresh the display with the latest \n" +
                "settings."))
        # save volume and position:
        def save_volume_and_position():
            if self.volumes_per_buffer.value.get() != 1:
                self.volumes_per_buffer.update_and_validate(1)
            self._update_position_list()
            folder_name = self._get_folder_name() + '_snap'
            self.last_acquire_task.join() # don't accumulate acquires
            self.scope.acquire(filename='snap.tif',
                               folder_name=folder_name,
                               description=self.description_textbox.text)
            return None
        save_volume_and_position_button = tk.Button(
            self.acquire_frame,
            text="Save volume and position",
            command=save_volume_and_position,
            font=('Segoe UI', '10', 'bold'),
            fg='blue',
            width=button_width + bold_width_adjust,
            height=button_height)
        save_volume_and_position_button.grid(row=3, column=0, padx=10, pady=10)
        save_volume_and_position_tip = tix.Balloon(
            save_volume_and_position_button)
        save_volume_and_position_tip.bind_widget(
            save_volume_and_position_button,
            balloonmsg=(
                "The 'Save volume and position' button will apply the \n" + 
                "latest microscope settings, save a volume and add the \n" +
                "current position to the position list."))
        # run acquire:
        def acquire():
            print('\nAcquire -> started')
            self._set_running_mode('acquire', enable=True)
            self.folder_name = self._get_folder_name() + '_acquire'
            self.description = self.description_textbox.text
            self.acquire_count = 0
            self.saved_delay_s = False
            self.current_position = 0
            self.total_positions = 0
            if self.loop_over_position_list.get():
                self.total_positions = len(self.XY_stage_position_list)
            def run_acquire():
                if not self.running_acquire.get(): # check for cancel
                    return None
                # don't launch all tasks: either wait 1 buffer time or delay:
                wait_ms = int(round(1e3 * self.scope.buffer_time_s))
                # check mode -> either single position or loop over positions:
                if self.loop_over_position_list.get():
                    if self.current_position == 0:
                        self.loop_t0_s = time.perf_counter()
                    self.focus_piezo_z_um.update_and_validate(
                        self.focus_piezo_position_list[self.current_position])
                    self._update_XY_stage_position(
                        self.XY_stage_position_list[self.current_position])
                    self.current_position_spinbox.update_and_validate(
                        self.current_position + 1)
                    self.scope.acquire(filename='%06i_p%06i.tif'%(
                        self.acquire_count, self.current_position),
                                       folder_name=self.folder_name,
                                       description=self.description)
                    if self.current_position < (self.total_positions - 1):
                        self.current_position +=1
                    else:
                        self.current_position = 0
                        self.acquire_count += 1
                        loop_time_s = time.perf_counter() - self.loop_t0_s
                        if self.delay_spinbox.value.get() > loop_time_s:
                            wait_ms = int(round(1e3 * (
                                self.delay_spinbox.value.get() - loop_time_s)))                   
                else:
                    self.scope.acquire(filename='%06i.tif'%self.acquire_count,
                                       folder_name=self.folder_name,
                                       description=self.description)
                    self.acquire_count += 1
                    if self.delay_spinbox.value.get() > self.scope.buffer_time_s:
                        wait_ms = int(round(1e3 * self.delay_spinbox.value.get()))
                # record gui delay:
                if (not self.saved_delay_s and os.path.exists(
                    self.folder_name)):
                    with open(self.folder_name + '\\'  "gui_delay_s.txt",
                              "w") as file:
                        file.write(self.folder_name + '\n')
                        file.write(
                            'gui_delay_s: %i'%self.delay_spinbox.value.get() + '\n')
                        self.saved_delay_s = True
                # check acquire count before re-run:
                if self.acquire_count < self.acquire_number_spinbox.value.get():
                    self.root.after(wait_ms, run_acquire)
                else:
                    self.scope.finish_all_tasks()
                    self.running_acquire.set(0)
                    print('Acquire -> finished\n')
                return None
            run_acquire()
            return None
        self.running_acquire = tk.BooleanVar()
        run_acquire_button = tk.Button(
            self.acquire_frame,
            text="Run acquire",
            command=acquire,
            font=('Segoe UI', '10', 'bold'),
            fg='red',
            width=button_width + bold_width_adjust,
            height=button_height)
        run_acquire_button.grid(row=4, column=0, padx=10, pady=10)
        run_acquire_button_tip = tix.Balloon(run_acquire_button)
        run_acquire_button_tip.bind_widget(
            run_acquire_button,
            balloonmsg=(
                "The 'Run acquire' button will run a full acquisition \n" + 
                "and may include: \n" +
                "- multiple colors (enable with the 'TRANSMITTED LIGHT' \n" +
                "and 'LASER BOX' panels).\n"
                "- multiple positions (populate the 'POSITION LIST' and \n" +
                "enable 'Loop over position list').\n"
                "- multiple fast volumes per position (set 'Volumes per \n" +
                "acquire' > 1).\n"
                "- multiple iterations of the above (set 'Acquire number' \n" +
                "> 1).\n"
                "- a time delay between successive iterations of the above \n" +
                "(set 'Inter-acquire delay (s)' > the time per iteration)"))
        # cancel acquire:
        def cancel_acquire():
            self.running_acquire.set(0)
            print('\n ***Acquire -> canceled*** \n')
            return None
        cancel_acquire_button = tk.Button(
            self.acquire_frame,
            text="Cancel acquire",
            command=cancel_acquire,
            width=button_width,
            height=button_height)
        cancel_acquire_button.grid(row=5, column=0, padx=10, pady=10)
        cancel_acquire_button_tip = tix.Balloon(cancel_acquire_button)
        cancel_acquire_button_tip.bind_widget(
            cancel_acquire_button,
            balloonmsg=(
                "The 'Cancel acquire' button will cancel any ongoing \n" +
                "acquisition.\n" +
                "NOTE: this is not immediate since some processes must \n" +
                "finish once launched."))
        return None

    def init_quit(self):
        quit_frame = tk.LabelFrame(
            self.root, text='QUIT', font=('Segoe UI', '10', 'bold'), bd=6)
        quit_frame.grid(row=5, column=6, padx=10, pady=10, sticky='n')
        def close():
            if self.init_microscope: self.scope.close()
            self.root.quit()
            return None
        quit_gui_button = tk.Button(
            quit_frame,
            text="EXIT GUI",
            command=close,
            height=2,
            width=25)
        quit_gui_button.grid(row=0, column=0, padx=10, pady=10, sticky='n')
        quit_gui_button_tip = tix.Balloon(quit_gui_button)
        quit_gui_button_tip.bind_widget(
            quit_gui_button,
            balloonmsg=(
                "The 'EXIT GUI' button will close down the microscope \n" +
                "without errors. It's the right way the end the GUI session."))
        return None

if __name__ == '__main__':
    gui_microscope = GuiMicroscope(init_microscope=True)
