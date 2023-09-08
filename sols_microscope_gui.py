import os
import time
import copy
from datetime import datetime
import tkinter as tk
from tkinter import font
from tkinter import filedialog
from tkinter import tix
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import sols_microscope as sols
import tkinter_compound_widgets as tkcw
from tifffile import imread, imwrite

class GuiTransmittedLight:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='TRANSMITTED LIGHT', bd=6)
        frame.grid(row=1, column=0, padx=10, pady=10, sticky='n')
        frame_tip = tix.Balloon(frame)
        frame_tip.bind_widget(
            frame,
            balloonmsg=(
                "The 'TRANSMITTED LIGHT' illuminates the sample from above.\n" +
                "NOTE: either the 'TRANSMITTED LIGHT' or at least 1 \n " +
                "'LASER' must be selected."))
        self.power = tkcw.CheckboxSliderSpinbox(
            frame,
            label='470-850nm (%)',
            checkbox_default=True,
            slider_length=200,
            default_value=25,
            width=5)

class GuiLaserBox:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='LASER BOX', bd=6)
        frame.grid(row=2, column=0, padx=10, pady=10, sticky='n')
        frame_tip = tix.Balloon(frame)
        frame_tip.bind_widget(
            frame,
            balloonmsg=(
                "The 'LASER' illuminates the sample with a 'light-sheet'.\n" +
                "NOTE: either the 'TRANSMITTED LIGHT' or at least 1 \n " +
                "'LASER' must be selected."))
        self.power405 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='405nm (%)',
            color='magenta',
            slider_length=200,
            default_value=5,
            width=5)
        self.power488 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='488nm (%)',
            color='blue',
            slider_length=200,
            default_value=5,
            row=1,
            width=5)
        self.power561 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='561nm (%)',
            color='green',
            slider_length=200,
            default_value=5,
            row=2,
            width=5)
        self.power640 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='640nm (%)',
            color='red',
            slider_length=200,
            default_value=5,
            row=3,
            width=5)

class GuiDichroicMirror:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='DICHROIC MIRROR', bd=6)
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
        self.dichroic_mirror_options = ( # copy paste from sols_microscope
            'ZT405/488/561/640rpc',)
        self.current_dichroic_mirror = tk.StringVar()
        self.current_dichroic_mirror.set('ZT405/488/561/640rpc') # set default
        option_menu = tk.OptionMenu(
            inner_frame,
            self.current_dichroic_mirror,
            *self.dichroic_mirror_options)
        option_menu.config(width=46, height=2) # match to TL and lasers
        option_menu.grid(row=0, column=0, padx=10, pady=10)

class GuiFilterWheel:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='FILTER WHEEL', bd=6)
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
        self.emission_filter_options = ( # copy paste from sols_microscope
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
            *self.emission_filter_options)
        option_menu.config(width=46, height=2) # match to TL and lasers
        option_menu.grid(row=0, column=0, padx=10, pady=10)        

class GuiCamera:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='CAMERA', bd=6)
        frame.grid(row=1, column=1, rowspan=2, padx=10, pady=10, sticky='n')
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
        illumination_time_us_tip = tix.Balloon(self.illumination_time_us)
        illumination_time_us_tip.bind_widget(
            self.illumination_time_us,
            balloonmsg=(
                "The 'illumination time (us)' determines how long the \n" +
                "sample will be exposed to light (i.e. the camera will \n" +
                "collect the emmitted light during this time).\n" +
                "NOTE: the range in the GUI is 100us to 1000000us (1s)."))
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
        self.height_px_tip = tix.Balloon(self.height_px)
        self.height_px_tip.bind_widget(
            self.height_px,
            balloonmsg=(
                "The 'height pixels' determines how many vertical pixels \n" +
                "are used by the camera. Less pixels is a smaller field \n" +
                "of view (FOV) and less data.\n" +
                "NOTE: less vertical pixels speeds up the acquisition!"))
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
        self.width_px_tip = tix.Balloon(self.width_px)
        self.width_px_tip.bind_widget(
            self.width_px,
            balloonmsg=(
                "The 'width pixels' determines how many horizontal pixels \n" +
                "are used by the camera. Less pixels is a smaller field \n" +
                "of view (FOV) and less data.\n"))
        tkcw.CanvasRectangleSliderTrace2D(
            frame,
            self.width_px,
            self.height_px,
            row=1,
            column=1,
            fill='yellow')

class GuiGalvo:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='GALVO', bd=6)
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

class GuiFocusPiezo:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='FOCUS PIEZO (Scout mode)', bd=6)
        frame.grid(row=1, column=2, rowspan=2, padx=10, pady=10, sticky='n')
        frame_tip = tix.Balloon(frame)
        frame_tip.bind_widget(
            frame,
            balloonmsg=(
                "The 'FOCUS PIEZO' is a (fast) fine focus device for \n" +
                "precisley adjusting the focus of the primary objective \n" +
                "over a short range.\n" +
                "NOTE: this is only active in 'Scout mode'"))
        position_min, position_max = 0, 100
        position_center = int(round((position_max - position_min) / 2))
        large_move_um, small_move_um = 5, 1
        # slider:
        self.position_um = tkcw.CheckboxSliderSpinbox(
            frame,
            label='position (um)',
            orient='vertical',
            checkbox_enabled=False,
            slider_length=460, # match to camera
            tickinterval=10,
            min_value=position_min,
            max_value=position_max,
            rowspan=5,
            width=5)
        button_width, button_height = 10, 2
        # large up button:
        self.button_large_move_up = tk.Button(
            frame,
            text="up %ium"%large_move_um,
            command=lambda: self.position_um.update_and_validate(
                self.position_um.value - large_move_um),
            width=button_width,
            height=button_height)
        self.button_large_move_up.grid(row=0, column=1, padx=10, pady=10)
        # small up button:
        self.button_small_move_up = tk.Button(
            frame,
            text="up %ium"%small_move_um,
            command=lambda: self.position_um.update_and_validate(
                self.position_um.value - small_move_um),
            width=button_width,
            height=button_height)
        self.button_small_move_up.grid(row=1, column=1, sticky='s')
        # center button:
        self.button_center_move = tk.Button(
            frame,
            text="center",
            command=lambda: self.position_um.update_and_validate(
                position_center),
            width=button_width,
            height=button_height)
        self.button_center_move.grid(row=2, column=1, padx=5, pady=5)
        # small down button:
        self.button_small_move_down = tk.Button(
            frame,
            text="down %ium"%small_move_um,
            command=lambda: self.position_um.update_and_validate(
                self.position_um.value + small_move_um),
            width=button_width,
            height=button_height)
        self.button_small_move_down.grid(row=3, column=1, sticky='n')
        # large down button:
        self.button_large_move_down = tk.Button(
            frame,
            text="down %ium"%large_move_um,
            command=lambda: self.position_um.update_and_validate(
                self.position_um.value + large_move_um),
            width=button_width,
            height=button_height)
        self.button_large_move_down.grid(row=4, column=1, padx=10, pady=10)

class GuiXYStage:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='XY STAGE (Scout mode)', bd=6)
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
        button_width, button_height = 10, 2
        # up button:
        self.move_up = tk.BooleanVar()
        self.button_up = tk.Checkbutton(
            frame,
            text="up",
            variable=self.move_up,
            indicatoron=0,
            width=button_width,
            height=button_height)
        self.button_up.grid(row=0, column=1, padx=10, pady=10)
        # down button:
        self.move_down = tk.BooleanVar()
        self.button_down = tk.Checkbutton(
            frame,
            text="down",
            variable=self.move_down,
            indicatoron=0,
            width=button_width,
            height=button_height)
        self.button_down.grid(row=2, column=1, padx=10, pady=10)
        # left button:
        self.move_left = tk.BooleanVar()
        self.button_left = tk.Checkbutton(
            frame,
            text="left",
            variable=self.move_left,
            indicatoron=0,
            width=button_width,
            height=button_height)
        self.button_left.grid(row=1, column=0, padx=10, pady=10)
        # right button:
        self.move_right = tk.BooleanVar()
        self.button_right = tk.Checkbutton(
            frame,
            text="right",
            variable=self.move_right,
            indicatoron=0,
            width=button_width,
            height=button_height)
        self.button_right.grid(row=1, column=2, padx=10, pady=10)
        # last move textbox:
        self.last_move = tkcw.Textbox(
            frame,
            label='last move',
            default_text='None',
            height=1,
            width=10)
        self.last_move.grid(row=0, column=0, padx=10, pady=10)
        # position textbox:
        self.position = tkcw.Textbox(
            frame,
            label='[X, Y] position (mm)',
            height=1,
            width=20)
        self.position.grid(row=1, column=1, padx=10, pady=10)
        self.position_mm = None
        # move size:
        self.move_pct = tkcw.CheckboxSliderSpinbox(
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

    def update_last_move(self, text):
        self.last_move.textbox.delete('1.0', '10.0')
        self.last_move.textbox.insert('1.0', text)
        return None

    def update_position(self, position_mm):
        self.position.textbox.delete('1.0', '10.0')
        self.position.textbox.insert(
            '1.0', '[%0.3f, %0.3f]'%(position_mm[0], position_mm[1]))
        self.position_mm = position_mm
        return None

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
        # load nested GUI's for each element:
        self.gui_transmitted_light  = GuiTransmittedLight(self.root)
        self.gui_laser_box          = GuiLaserBox(self.root)
        self.gui_dichroic_mirror    = GuiDichroicMirror(self.root)
        self.gui_filter_wheel       = GuiFilterWheel(self.root)
        self.gui_galvo              = GuiGalvo(self.root)
        self.gui_camera             = GuiCamera(self.root)
        self.gui_focus_piezo        = GuiFocusPiezo(self.root)
        self.gui_xy_stage           = GuiXYStage(self.root)
        # load microscope GUI's and quit:
        self.init_gui_grid_navigator()  # navigates an XY grid of points
        self.init_gui_tile_navigator()  # generates and navigates XY tiles
        self.init_gui_settings()        # collects settings from GUI
        self.init_gui_settings_output() # shows output from settings
        self.init_gui_position_list()   # navigates position lists
        self.init_gui_acquire()         # microscope methods
        self.init_quit_button()
        # grey out XYZ navigation buttons if not in scout mode:
        self.enable_XYZ_navigation_buttons(False)
        # get settings from gui:
        gui_settings = self.get_gui_settings()
        if init_microscope:
            self.scope = sols.Microscope(max_allocated_bytes=100e9, ao_rate=1e4)
            # configure any hardware preferences:
            self.scope.XY_stage.set_velocity(5, 5)            
            # get XYZ direct from hardware and update gui to aviod motion:
            focus_piezo_z_um = int(round(self.scope.focus_piezo.z))
            XY_stage_position_mm = [self.scope.XY_stage.x,
                                    self.scope.XY_stage.y]
            self.gui_focus_piezo.position_um.update_and_validate(
                focus_piezo_z_um)
            self.gui_xy_stage.update_position(XY_stage_position_mm)
            self.XY_joystick_active = False
            self.XY_stage_last_move = 'None'
            # init settings attributes:
            self.applied_settings = {}
            for k in gui_settings.keys():
                self.applied_settings[k] = None
            self.apply_settings(check_XY_stage=False) # mandatory call
            # make session folder and position lists:
            dt = datetime.strftime(datetime.now(),'%Y-%m-%d_%H-%M-%S_')
            self.session_folder = dt + 'sols_gui_session\\'
            os.makedirs(self.session_folder)
            self.make_empty_position_list()
            # get scope ready:
            self.loop_snoutfocus()
            self.last_acquire_task = self.scope.acquire() # snap a volume
            self.running_scout.set(1)
            self.init_scout_mode()
        # start event loop:
        self.root.mainloop() # blocks here until 'QUIT'
        self.root.destroy()

    def loop_snoutfocus(self):
        if not self.running_acquire.get():
            self.scope.snoutfocus(settle_vibrations=False)
        wait_ms = int(round(5 * 60 * 1e3))
        self.root.after(wait_ms, self.loop_snoutfocus)
        return None

    def set_running_mode(self, mode, enable=False): # enable=True for 'Buttons'
        # define mode dictionary:
        mode_to_variable = {
            'set_grid_location':self.running_set_grid_location,
            'move_to_grid_location':self.running_move_to_grid_location,
            'grid_preview':self.running_grid_preview,
            'tile':self.running_tile,
            'move_to_tile':self.running_move_to_tile,
            'update_settings':self.running_update_settings,
            'live':self.running_live,
            'scout':self.running_scout,
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

    def get_folder_name(self):
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

    def init_gui_grid_navigator(self):
        self.grid_frame = tk.LabelFrame(
            self.root, text='GRID NAVIGATOR', bd=6)
        self.grid_frame.grid(
            row=1, column=4, rowspan=2, padx=10, pady=10, sticky='n')
        self.grid_frame.bind( # force update
            '<Enter>', lambda event: self.grid_frame.focus_set())
        button_width, button_height = 25, 2
        spinbox_width = 20
        # set grid defaults:
        self.grid_rows = 2
        self.grid_cols = 4
        self.grid_spacing_um = 1000        
        # load from file:
        load_grid_from_file_button = tk.Button(
            self.grid_frame,
            text="Load from file",
            command=self.load_grid_from_file,
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
        create_grid_button = tk.Button(
            self.grid_frame,
            text="Create grid",
            command=self.create_grid,
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
        self.running_set_grid_location = tk.BooleanVar()
        self.set_grid_location_button = tk.Button(
            self.grid_frame,
            text="Set grid location",
            command=self.set_grid_location,
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
        self.grid_location_textbox = tkcw.Textbox(
            self.grid_frame,
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
        self.running_move_to_grid_location = tk.BooleanVar()
        self.move_to_grid_location_button = tk.Button(
            self.grid_frame,
            text="Move to grid location",
            command=self.move_to_grid_location,
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
            self.grid_frame,
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
            self.grid_frame,
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
        self.running_grid_preview = tk.BooleanVar()
        self.start_grid_preview_button = tk.Button(
            self.grid_frame,
            text="Start grid preview (from A1)",
            command=self.start_grid_preview,
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
            self.grid_frame,
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

    def load_grid_from_file(self):
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
        load_grid_from_file_popup = tk.Toplevel()
        load_grid_from_file_popup.title('Grid from file')
        load_grid_from_file_popup.grab_set() # force user to interact
        x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
        load_grid_from_file_popup.geometry("+%d+%d" % (x + 800, y + 400))
        button_width, button_height = 25, 2
        # exit button:
        exit_button = tk.Button(
            load_grid_from_file_popup, text="Exit",
            command=load_grid_from_file_popup.destroy,
            height=button_height, width=button_width)
        exit_button.grid(row=1, column=0, padx=10, pady=10, sticky='n')
        self.generate_grid_buttons(
            load_grid_from_file_popup, enabled=False)
        # reset state of grid buttons:
        self.set_grid_location_button.config(state='normal')
        self.move_to_grid_location_button.config(state='disabled')
        self.start_grid_preview_button.config(state='disabled')
        return None

    def generate_grid_buttons(self, master, enabled=True):
        self.generate_grid_buttons_frame = tk.LabelFrame(
            master, text='XY GRID', bd=6)
        self.generate_grid_buttons_frame.grid(
            row=0, column=1, rowspan=5, padx=10, pady=10)
        button_width, button_height = 5, 2
        self.grid_button_array = [
            [None for c in range(self.grid_cols)] for r in range(
                self.grid_rows)]
        self.grid_button_enabled_array = [
            [None for c in range(self.grid_cols)] for r in range(
                self.grid_rows)]
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                name = '%s%i'%(chr(ord('@')+r + 1), c + 1)
                self.grid_button_enabled_array[r][c] = tk.BooleanVar()
                self.grid_button_array[r][c] = tk.Checkbutton(
                    self.generate_grid_buttons_frame,
                    text=name,
                    variable=self.grid_button_enabled_array[r][c],
                    indicatoron=0,
                    width=button_width,
                    height=button_height)
                self.grid_button_array[r][c].grid(
                    row=r, column=c, padx=10, pady=10)
                if not enabled:
                    self.grid_button_array[r][c].config(state='disabled')
        return None

    def create_grid(self):
        # popup:
        create_grid_popup = tk.Toplevel()
        create_grid_popup.title('Create grid')
        create_grid_popup.grab_set() # force user to interact
        x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
        create_grid_popup.geometry("+%d+%d" % (x + 800, y + 400))
        button_width, button_height = 25, 2
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
        def create():
            if hasattr(self, 'generate_grid_buttons_frame'):
                self.generate_grid_buttons_frame.destroy()
            # update attributes:
            self.grid_rows = self.grid_rows_spinbox.value
            self.grid_cols = self.grid_cols_spinbox.value
            self.grid_spacing_um = self.grid_spacing_spinbox.value
            # show user and reset state of grid buttons:
            self.generate_grid_buttons(create_grid_popup, enabled=False)
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
        create_button = tk.Button(
            create_grid_popup, text="Create",
            command=create,
            height=button_height, width=button_width)
        create_button.grid(row=3, column=0, padx=10, pady=10, sticky='n')
        create_button.bind( # force update
            '<Enter>', lambda event: create_grid_popup.focus_set())
        # exit button:
        exit_button = tk.Button(
            create_grid_popup, text="Exit",
            command=create_grid_popup.destroy,
            height=button_height, width=button_width)
        exit_button.grid(row=4, column=0, padx=10, pady=10, sticky='n')
        create()
        return None

    def set_grid_location(self):
        set_grid_location_popup = tk.Toplevel()
        set_grid_location_popup.title('Set current location')
        set_grid_location_popup.grab_set() # force user to interact
        x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
        set_grid_location_popup.geometry("+%d+%d" % (x + 800, y + 400))
        self.generate_grid_buttons(set_grid_location_popup)
        self.set_running_mode('set_grid_location', enable=True)
        def run_set_grid_location():
            if self.running_set_grid_location.get():
                for r in range(self.grid_rows):
                    for c in range(self.grid_cols):
                        if self.grid_button_enabled_array[r][c].get():
                            self.grid_location_rc = [r, c]
                            self.update_grid_location()
                            # get current position and spacing:
                            XY_stage_position_mm = self.check_XY_stage()
                            spacing_mm = self.grid_spacing_um / 1000
                            # set home position:
                            self.grid_home_mm = [
                                XY_stage_position_mm[0] + c * spacing_mm,
                                XY_stage_position_mm[1] - r * spacing_mm]
                            # make grid of positions:
                            self.grid_positions_mm = [[None for c in range(
                                self.grid_cols)] for j in range(self.grid_rows)]
                            for rows in range(self.grid_rows):
                                for cols in range(self.grid_cols):
                                    self.grid_positions_mm[rows][cols] = [
                                        self.grid_home_mm[0] - cols*spacing_mm,
                                        self.grid_home_mm[1] + rows*spacing_mm]
                            # allow moves:
                            self.move_to_grid_location_button.config(
                                state='normal')
                            if self.grid_location_rc == [0, 0]:
                                self.start_grid_preview_button.config(
                                    state='normal')
                            else:
                                self.start_grid_preview_button.config(
                                    state='disabled')
                            self.running_set_grid_location.set(0)
                            set_grid_location_popup.destroy()
                            return None
                self.root.after(self.gui_delay_ms, run_set_grid_location)
            return None
        run_set_grid_location()
        return None

    def update_grid_location(self):
        name = '%s%i'%(chr(ord('@')+ self.grid_location_rc[0] + 1),
                       self.grid_location_rc[1] + 1)
        self.grid_location_textbox.textbox.delete('1.0', '10.0')
        self.grid_location_textbox.textbox.insert('1.0', name)
        return None

    def move_to_grid_location(self):
        move_to_grid_location_popup = tk.Toplevel()
        move_to_grid_location_popup.title('Move to location')
        move_to_grid_location_popup.grab_set() # force user to interact
        x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
        move_to_grid_location_popup.geometry("+%d+%d" % (x + 800, y + 400))
        button_width, button_height = 25, 2
        self.generate_grid_buttons(move_to_grid_location_popup)
        r, c = self.grid_location_rc
        self.grid_button_enabled_array[r][c].set(1)
        self.grid_button_array[r][c].config(state='disabled')
        self.set_running_mode('move_to_grid_location', enable=True)
        # cancel button:
        def cancel():
            self.running_move_to_grid_location.set(0)
            move_to_grid_location_popup.destroy()
            return None
        cancel_button = tk.Button(
            move_to_grid_location_popup, text="Cancel",
            command=cancel,
            height=button_height, width=button_width)
        cancel_button.grid(row=1, column=0, padx=10, pady=10, sticky='n')        
        def run_move_to_grid_location():
            if self.running_move_to_grid_location.get():
                for r in range(self.grid_rows):
                    for c in range(self.grid_cols):
                        if (self.grid_button_enabled_array[r][c].get() and
                            [r, c] != self.grid_location_rc):
                            # update gui, apply and display:
                            XY_stage_position_mm = self.grid_positions_mm[r][c]
                            self.gui_xy_stage.update_position(
                                XY_stage_position_mm)
                            self.apply_settings(
                                single_volume=True, check_XY_stage=False)
                            self.last_acquire_task.join()# don't accumulate
                            self.last_acquire_task = self.scope.acquire()
                            # update attributes and buttons:
                            self.grid_location_rc = [r, c]
                            self.update_grid_location()
                            self.start_grid_preview_button.config(
                                state='disabled')
                            if [r, c] == [0, 0]:
                                self.start_grid_preview_button.config(
                                    state='normal')
                            cancel()
                            return None
                self.root.after(self.gui_delay_ms, run_move_to_grid_location)
            return None
        run_move_to_grid_location()
        return None

    def start_grid_preview(self):
        print('\nGrid preview -> started')
        self.set_running_mode('grid_preview', enable=True)
        self.apply_settings(single_volume=True)
        self.update_gui_settings_output()
        folder_name = self.get_folder_name() + '_grid'
        if self.tile_the_grid.get():
            folder_name = self.get_folder_name() + '_grid_tile'
            # get tile parameters:
            self.tile_rows = self.tile_array_width_spinbox.value
            self.tile_cols = self.tile_rows
            # calculate move size:
            self.tile_X_mm = 1e-3 * self.applied_settings[
                'width_px'] * sols.sample_px_um
            self.tile_Y_mm = 1e-3 * self.applied_settings['scan_range_um']            
        # generate rows/cols list:
        self.XY_grid_rc_list = []
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                if self.tile_the_grid.get():
                    for tile_r in range(self.tile_rows):
                        for tile_c in range(self.tile_cols):
                            self.XY_grid_rc_list.append([r, c, tile_r, tile_c])
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
                    self.grid_positions_mm[r][c][0] - tile_c * self.tile_X_mm,
                    self.grid_positions_mm[r][c][1] + tile_r * self.tile_Y_mm]
                self.gui_xy_stage.update_position(XY_stage_position_mm)
            else:
                r, c = self.XY_grid_rc_list[self.current_grid_image]
                name = '%s%i'%(chr(ord('@')+r + 1), c + 1)
                self.gui_xy_stage.update_position(self.grid_positions_mm[r][c])
            filename = name + '.tif'
            # update gui and move stage:
            self.apply_settings(single_volume=True, check_XY_stage=False)
            self.grid_location_rc = [r, c]
            self.update_grid_location()
            # check mode:
            preview_only = True
            if self.save_grid_data_and_position.get():
                preview_only = False
                self.update_position_list()
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

    def init_gui_tile_navigator(self):
        self.tile_frame = tk.LabelFrame(
            self.root, text='TILE NAVIGATOR', bd=6)
        self.tile_frame.grid(
            row=3, column=4, rowspan=2, padx=10, pady=10, sticky='n')
        self.grid_frame.bind( # force update
            '<Enter>', lambda event: self.grid_frame.focus_set())
        button_width, button_height = 25, 2
        spinbox_width = 20
        # tile array width:
        self.tile_array_width_spinbox = tkcw.CheckboxSliderSpinbox(
            self.tile_frame,
            label='Array height and width (tiles)',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=2,
            max_value=9,
            default_value=2,
            row=0,
            width=spinbox_width)
        tile_array_width_spinbox_tip = tix.Balloon(
            self.tile_array_width_spinbox)
        tile_array_width_spinbox_tip.bind_widget(
            self.tile_array_width_spinbox,
            balloonmsg=(
                "The 'Array height and width (tiles)' determines how many \n" +
                "tiles the 'Start tile' button will generate. For example, \n" +
                "2 gives a 2x2 array of tiles, 3 a 3x3 array, etc."))
        # save data and position:
        self.save_tile_data_and_position = tk.BooleanVar()
        save_tile_data_and_position_button = tk.Checkbutton(
            self.tile_frame,
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
        # start tile:
        self.running_tile = tk.BooleanVar()
        start_tile_button = tk.Button(
            self.tile_frame,
            text="Start tile",
            command=self.init_tile,
            font=('Segoe UI', '10', 'italic'),
            width=button_width,
            height=button_height)
        start_tile_button.grid(row=2, column=0, padx=10, pady=10)
        start_tile_tip = tix.Balloon(start_tile_button)
        start_tile_tip.bind_widget(
            start_tile_button,
            balloonmsg=(
                "The 'Start tile' button will start to generate previews \n" +
                "for the tile array using the current XY position as the \n" +
                "first tile (the top left position r0c0). Consider using \n" +
                "'Save data and position' for extra functionality."))
        # cancel tile:
        cancel_tile_button = tk.Button(
            self.tile_frame,
            text="Cancel tile",
            command=self.cancel_tile,
            width=button_width,
            height=button_height)
        cancel_tile_button.grid(row=3, column=0, padx=10, pady=10)
        cancel_tile_tip = tix.Balloon(cancel_tile_button)
        cancel_tile_tip.bind_widget(
            cancel_tile_button,
            balloonmsg=(
                "The 'Cancel tile' button will cancel any ongoing tile\n" +
                "preview generation.\n" +
                "NOTE: this is not immediate since some processes must \n" +
                "finish once launched."))        
        # move to tile:
        self.running_move_to_tile = tk.BooleanVar()
        self.move_to_tile_button = tk.Button(
            self.tile_frame,
            text="Move to tile",
            command=self.move_to_tile_popup,
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

    def init_tile(self):
        print('\nTile -> started')
        self.set_running_mode('tile', enable=True)
        self.apply_settings(single_volume=True)
        self.update_gui_settings_output()
        self.folder_name = self.get_folder_name() + '_tile'
        # get tile parameters:
        self.tile_rows = self.tile_array_width_spinbox.value
        self.tile_cols = self.tile_rows
        initial_XY_stage_position_mm = self.gui_xy_stage.position_mm
        # calculate move size:
        X_move_mm = 1e-3 * self.applied_settings['width_px'] * sols.sample_px_um
        Y_move_mm = 1e-3 * self.applied_settings['scan_range_um']
        # generate tile rows/cols and positions:
        self.XY_tile_rc_list = []
        self.XY_tile_position_list = []
        for r in range(self.tile_rows):
            for c in range(self.tile_cols):
                self.XY_tile_rc_list.append([r, c])
                XY_stage_position_mm = [
                    initial_XY_stage_position_mm[0] - c * X_move_mm,
                    initial_XY_stage_position_mm[1] + r * Y_move_mm]
                self.XY_tile_position_list.append(XY_stage_position_mm)
        self.current_tile = 0
        self.run_tile()
        return None

    def run_tile(self):           
        # update position:
        r, c = self.XY_tile_rc_list[self.current_tile]
        self.gui_xy_stage.update_position(
            self.XY_tile_position_list[self.current_tile])
        self.apply_settings(single_volume=True, check_XY_stage=False)
        # get tile:
        name = "r%ic%i"%(r, c)
        filename = name + '.tif'
        preview_only = True
        if self.save_tile_data_and_position.get():
            preview_only = False
            self.update_position_list()
        self.scope.acquire(
            filename=filename,
            folder_name=self.folder_name,
            description=self.description_textbox.text,
            preview_only=preview_only).join()
        tile_filename = (self.folder_name + '\preview\\' + filename)
        while not os.path.isfile(tile_filename):
            self.root.after(self.gui_delay_ms)
        tile = imread(tile_filename)
        shape = tile.shape
        # add reference:
        tile = Image.fromarray(tile) # convert to PIL format for ImageDraw
        XY = (int(0.1 * min(shape)), shape[0] - int(0.15 * min(shape)))
        font_size = int(0.1 * min(shape))
        font = ImageFont.truetype('arial.ttf', font_size)
        ImageDraw.Draw(tile).text(XY, name, fill=0, font=font)
        # make base image:
        if (r, c) == (0, 0):
            self.tile_preview = np.zeros(
                (self.tile_rows * shape[0],
                 self.tile_cols * shape[1]), 'uint16')
        # add current tile:
        self.tile_preview[
            r * shape[0]:(r + 1) * shape[0],
            c * shape[1]:(c + 1) * shape[1]] = tile
        # display:
        self.scope.display.show_tile_preview(self.tile_preview)
        if (self.running_tile.get() and
            self.current_tile < len(self.XY_tile_position_list) - 1): 
            self.current_tile += 1
            self.root.after(self.gui_delay_ms, self.run_tile)
        else:
            self.move_to_tile_button.config(state='normal')
            print('Tile -> finished\n')
        return None

    def cancel_tile(self):
        self.running_tile.set(0)
        print('\n ***Tile -> canceled*** \n')
        return None

    def move_to_tile_popup(self):
        self.move_to_tile_popup = tk.Toplevel()
        self.move_to_tile_popup.title('Move to tile')
        self.move_to_tile_popup.grab_set() # force user to interact
        x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
        self.move_to_tile_popup.geometry("+%d+%d" % (x + 800, y + 400))
        button_width, button_height = 25, 2
        cancel_button = tk.Button(
            self.move_to_tile_popup, text="Cancel",
            command=self.cancel_move_to_tile,
            height=button_height, width=button_width)
        cancel_button.grid(row=1, column=0, padx=10, pady=10, sticky='n')
        # make buttons:
        self.tile_buttons_frame = tk.LabelFrame(
            self.move_to_tile_popup, text='XY TILES', bd=6)
        self.tile_buttons_frame.grid(
            row=0, column=1, rowspan=5, padx=10, pady=10)
        button_width, button_height = 5, 2
        self.tile_button_array = [
            [None for c in range(self.tile_cols)] for r in range(
                self.tile_rows)]
        self.tile_button_enabled_array = [
            [None for c in range(self.tile_cols)] for r in range(
                self.tile_rows)]
        for r in range(self.tile_rows):
            for c in range(self.tile_cols):
                self.tile_button_enabled_array[r][c] = tk.BooleanVar()
                self.tile_button_array[r][c] = tk.Checkbutton(
                    self.tile_buttons_frame,
                    text='r%ic%i'%(r, c),
                    variable=self.tile_button_enabled_array[r][c],
                    indicatoron=0,
                    width=button_width,
                    height=button_height)
                self.tile_button_array[r][c].grid(
                    row=r, column=c, padx=10, pady=10)
        # set state:
        r, c = self.XY_tile_rc_list[self.current_tile]
        self.tile_button_enabled_array[r][c].set(1)
        self.tile_button_array[r][c].config(state='disabled')
        self.set_running_mode('move_to_tile', enable=True)
        self.run_move_to_tile()
        return None

    def run_move_to_tile(self):
        if self.running_move_to_tile.get():
            for r in range(self.tile_rows):
                for c in range(self.tile_cols):
                    if (self.tile_button_enabled_array[r][c].get() and
                        [r, c] != self.XY_tile_rc_list[self.current_tile]):
                        self.current_tile = self.XY_tile_rc_list.index([r, c])
                        self.gui_xy_stage.update_position(
                            self.XY_tile_position_list[self.current_tile])
                        self.apply_settings(
                            single_volume=True, check_XY_stage=False)
                        self.last_acquire_task.join()# don't accumulate acquires
                        self.last_acquire_task = self.scope.acquire()
                        self.cancel_move_to_tile()
                        return None
            self.root.after(self.gui_delay_ms, self.run_move_to_tile)
        return None

    def cancel_move_to_tile(self):
        self.running_move_to_tile.set(0)
        self.move_to_tile_popup.destroy()
        return None

    def init_gui_settings(self):
        self.settings_frame = tk.LabelFrame(
            self.root, text='SETTINGS (misc)', bd=6)
        self.settings_frame.grid(
            row=1, column=5, rowspan=2, padx=10, pady=10, sticky='n')
        self.settings_frame.bind( # force update
            '<Enter>', lambda event: self.settings_frame.focus_set())
        button_width, button_height = 25, 2
        spinbox_width = 20
        # load from file:
        load_from_file_button = tk.Button(
            self.settings_frame,
            text="Load from file",
            command=self.load_settings_from_file,
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
        self.volumes_spinbox = tkcw.CheckboxSliderSpinbox(
            self.settings_frame,
            label='Volumes per acquire',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=1e3,
            default_value=1,
            row=3,
            width=spinbox_width)
        volumes_spinbox_tip = tix.Balloon(self.volumes_spinbox)
        volumes_spinbox_tip.bind_widget(
            self.volumes_spinbox,
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

    def load_settings_from_file(self):
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
            file_settings[data.split(':')[0]] = data.split(':')[1:][0].lstrip()
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
        emission_filter = file_settings['emission_filter']
        illumination_time_us = int(file_settings['illumination_time_us'])
        height_px = int(file_settings['height_px'])
        width_px = int(file_settings['width_px'])
        voxel_aspect_ratio = int(round(float(
            file_settings['voxel_aspect_ratio'])))
        scan_range_um = int(round(float(file_settings['scan_range_um'])))        
        volumes_per_buffer = int(file_settings['volumes_per_buffer'])
        focus_piezo_z_um = float(file_settings['focus_piezo_z_um'])
        XY_mm = file_settings['XY_stage_position_mm'].strip(
            '(').strip(')').split(',')
        XY_stage_position_mm = [float(XY_mm[0]), float(XY_mm[1])]
        # turn off all illumination:
        self.gui_transmitted_light.power.checkbox_value.set(0)
        self.gui_laser_box.power405.checkbox_value.set(0)
        self.gui_laser_box.power488.checkbox_value.set(0)
        self.gui_laser_box.power561.checkbox_value.set(0)
        self.gui_laser_box.power640.checkbox_value.set(0)
        # apply file settings to gui:
        for i, channel in enumerate(channels_per_slice):
            if channel == 'LED':
                self.gui_transmitted_light.power.checkbox_value.set(1)
                self.gui_transmitted_light.power.update_and_validate(
                    power_per_channel[i])
            if channel == '405':
                self.gui_laser_box.power405.checkbox_value.set(1)
                self.gui_laser_box.power405.update_and_validate(
                    power_per_channel[i])
            if channel == '488':
                self.gui_laser_box.power488.checkbox_value.set(1)
                self.gui_laser_box.power488.update_and_validate(
                    power_per_channel[i])
            if channel == '561':
                self.gui_laser_box.power561.checkbox_value.set(1)
                self.gui_laser_box.power561.update_and_validate(
                    power_per_channel[i])
            if channel == '640':
                self.gui_laser_box.power640.checkbox_value.set(1)
                self.gui_laser_box.power640.update_and_validate(
                    power_per_channel[i])
        self.gui_filter_wheel.emission_filter.set(emission_filter)
        self.gui_camera.illumination_time_us.update_and_validate(
            illumination_time_us)
        self.gui_camera.height_px.update_and_validate(height_px)
        self.gui_camera.width_px.update_and_validate(width_px)
        self.gui_galvo.voxel_aspect_ratio.update_and_validate(
            voxel_aspect_ratio)
        self.gui_galvo.scan_range_um.update_and_validate(scan_range_um)
        self.volumes_spinbox.update_and_validate(volumes_per_buffer)
        # apply the file settings:
        self.apply_settings(check_XY_stage=False)
        return None

    def get_gui_settings(self):
        # collect settings from gui and re-format for '.scope.apply_settings'
        channels_per_slice, power_per_channel = [], []
        if self.gui_transmitted_light.power.checkbox_value.get():
            channels_per_slice.append('LED')
            power_per_channel.append(self.gui_transmitted_light.power.value)
        if self.gui_laser_box.power405.checkbox_value.get():
            channels_per_slice.append('405')
            power_per_channel.append(self.gui_laser_box.power405.value)
        if self.gui_laser_box.power488.checkbox_value.get():
            channels_per_slice.append('488')
            power_per_channel.append(self.gui_laser_box.power488.value)
        if self.gui_laser_box.power561.checkbox_value.get():
            channels_per_slice.append('561')
            power_per_channel.append(self.gui_laser_box.power561.value)
        if self.gui_laser_box.power640.checkbox_value.get():
            channels_per_slice.append('640')
            power_per_channel.append(self.gui_laser_box.power640.value)
        if len(channels_per_slice) == 0: # default TL if nothing selected
            self.gui_transmitted_light.power.checkbox_value.set(1)
            channels_per_slice = ('LED',)
            power_per_channel = (self.gui_transmitted_light.power.value,)
        emission_filter = self.gui_filter_wheel.emission_filter.get()
        illumination_time_us = self.gui_camera.illumination_time_us.value
        height_px = self.gui_camera.height_px.value
        width_px  = self.gui_camera.width_px.value
        voxel_aspect_ratio = self.gui_galvo.voxel_aspect_ratio.value
        scan_range_um = self.gui_galvo.scan_range_um.value
        volumes_per_buffer = self.volumes_spinbox.value
        focus_piezo_z_um = self.gui_focus_piezo.position_um.value
        XY_stage_position_mm = self.gui_xy_stage.position_mm
        # settings:
        gui_settings = {'channels_per_slice'    :channels_per_slice,
                        'power_per_channel'     :power_per_channel,
                        'emission_filter'       :emission_filter,
                        'illumination_time_us'  :illumination_time_us,
                        'height_px'             :height_px,
                        'width_px'              :width_px,
                        'voxel_aspect_ratio'    :voxel_aspect_ratio,
                        'scan_range_um'         :scan_range_um,
                        'volumes_per_buffer'    :volumes_per_buffer,
                        'focus_piezo_z_um'      :focus_piezo_z_um,
                        'XY_stage_position_mm'  :XY_stage_position_mm}
        return gui_settings

    def check_XY_stage(self):
        # has the position changed? is the joystick being used? 
        self.scope.apply_settings().join() # update attributes
        XY_stage_position_mm = list(self.scope.XY_stage_position_mm)
        self.XY_joystick_active = False
        if   XY_stage_position_mm[0] == self.scope.XY_stage.x_min: # moving
            self.XY_joystick_active = True
            self.XY_stage_last_move = 'left (-X)'
        elif XY_stage_position_mm[0] == self.scope.XY_stage.x_max: # moving
            self.XY_joystick_active = True
            self.XY_stage_last_move = 'right (+X)'
        elif XY_stage_position_mm[1] == self.scope.XY_stage.y_min: # moving
            self.XY_joystick_active = True
            self.XY_stage_last_move = 'down (-Y)'
        elif XY_stage_position_mm[1] == self.scope.XY_stage.y_max: # moving
            self.XY_joystick_active = True
            self.XY_stage_last_move = 'up (+Y)'
        return XY_stage_position_mm

    def apply_settings(self, single_volume=False, check_XY_stage=True):
        if check_XY_stage: # joystick used? If so update the gui:
            XY_stage_position_mm = self.check_XY_stage()
            if XY_stage_position_mm != self.gui_xy_stage.position_mm:
                self.gui_xy_stage.update_position(XY_stage_position_mm)
        gui_settings = self.get_gui_settings()
        new_settings = len(gui_settings)*[None] # pass 'None' if no change
        # check gui settings against applied settings:
        if (self.applied_settings[
            'channels_per_slice'] != gui_settings['channels_per_slice'] or
            self.applied_settings[
                'power_per_channel']  != gui_settings['power_per_channel']):
            new_settings[0] = gui_settings['channels_per_slice']
            new_settings[1] = gui_settings['power_per_channel']
        for i, k in enumerate(list(self.applied_settings.keys())[2:-2]): #-2 XYZ
            if self.applied_settings[k] != gui_settings[k]:
                new_settings[i + 2] = gui_settings[k] # + 2 started at setting 2
        if self.applied_settings[
            'focus_piezo_z_um'] != gui_settings['focus_piezo_z_um']:
            new_settings[9] = (gui_settings['focus_piezo_z_um'], 'absolute')
        if not self.XY_joystick_active:
            if self.applied_settings[
                'XY_stage_position_mm'] != gui_settings['XY_stage_position_mm']:
                new_settings[10] = (gui_settings['XY_stage_position_mm'][0],
                                    gui_settings['XY_stage_position_mm'][1],
                                    'absolute')
        # apply settings:
        if single_volume: new_settings[8] = 1
        self.scope.apply_settings(
            channels_per_slice      = new_settings[0],
            power_per_channel       = new_settings[1],
            emission_filter         = new_settings[2],
            illumination_time_us    = new_settings[3],
            height_px               = new_settings[4],
            width_px                = new_settings[5],
            voxel_aspect_ratio      = new_settings[6],
            scan_range_um           = new_settings[7],
            volumes_per_buffer      = new_settings[8],
            focus_piezo_z_um        = new_settings[9],
            XY_stage_position_mm    = new_settings[10])
        # update settings attributes:
        for k in self.applied_settings.keys(): # deepcopy to aviod circular ref
            self.applied_settings[k] = copy.deepcopy(gui_settings[k])
        if single_volume: self.applied_settings['volumes_per_buffer'] = 1
        return None

    def init_gui_settings_output(self):
        self.output_frame = tk.LabelFrame(
            self.root, text='SETTINGS OUTPUT', bd=6)
        self.output_frame.grid(
            row=3, column=5, rowspan=2, padx=10, pady=10, sticky='n')
        self.output_frame.bind( # force update
            '<Enter>', lambda event: self.output_frame.focus_set())
        button_width, button_height = 25, 2
        spinbox_width = 20
        # auto update settings button:
        self.running_update_settings = tk.BooleanVar()
        update_settings_button = tk.Checkbutton(
            self.output_frame,
            text='Auto update (On/Off)',
            variable=self.running_update_settings,
            command=self.init_update_settings,
            indicatoron=0,
            font=('Segoe UI', '10', 'italic'),
            width=button_width,
            height=button_height)
        update_settings_button.grid(row=0, column=0, padx=10, pady=10)
        update_settings_button_tip = tix.Balloon(update_settings_button)
        update_settings_button_tip.bind_widget(
            update_settings_button,
            balloonmsg=(
                "Press 'Auto update (On/Off)' to continously apply the \n" +
                "latest settings to the microscope and see how this \n" +
                "affects the 'SETTINGS OUTPUT'.\n" +
                "NOTE: selecting this mode will cancel other modes"))
        # volumes per second textbox:
        self.volumes_per_s_textbox = tkcw.Textbox(
            self.output_frame,
            label='Volumes per second',
            default_text='None',
            row=1,
            width=spinbox_width,
            height=1)
        volumes_per_s_textbox_tip = tix.Balloon(self.volumes_per_s_textbox)
        volumes_per_s_textbox_tip.bind_widget(
            self.volumes_per_s_textbox,
            balloonmsg=(
                "Shows the 'Volumes per second' (Vps) based on the \n" +
                "settings that were last applied to the microscope.\n" +
                "NOTE: this is the volumetric rate for the acquisition \n" +
                "(i.e. during the analogue out 'play') and does reflect \n" +
                "any delays or latency between acquisitions. This value \n" +
                "is only updated when 'Auto update (On/Off)' is running \n" +
                "or one of the 'ACQUIRE' buttons is pressed."))
        # total memory textbox:
        self.total_memory_textbox = tkcw.Textbox(
            self.output_frame,
            label='Total memory (GB)',
            default_text='None',
            row=2,
            width=spinbox_width,
            height=1)
        total_memory_textbox_tip = tix.Balloon(self.total_memory_textbox)
        total_memory_textbox_tip.bind_widget(
            self.total_memory_textbox,
            balloonmsg=(
                "Shows the 'Total memory (GB)' that the microscope will \n" +
                "need to run the settings that were last applied.\n" +
                "NOTE: this can be useful for montoring resources and \n" +
                "avoiding memory limits. This value is only updated when \n" +
                "'Auto update (On/Off)' is running or one of the 'ACQUIRE' \n" +
                "buttons is pressed."))
        # total storage textbox:
        self.total_storage_textbox = tkcw.Textbox(
            self.output_frame,
            label='Total storage (GB)',
            default_text='None',
            row=3,
            width=spinbox_width,
            height=1)
        total_storage_textbox_tip = tix.Balloon(self.total_storage_textbox)
        total_storage_textbox_tip.bind_widget(
            self.total_storage_textbox,
            balloonmsg=(
                "Shows the 'Total storage (GB)' that the microscope will \n" +
                "need to save the data if 'Run acquire' is pressed (based \n" +
                "on the settings that were last applied).\n" +
                "NOTE: this can be useful for montoring resources and \n" +
                "avoiding storage limits. This value is only updated when \n" +
                "'Auto update (On/Off)' is running or one of the 'ACQUIRE' \n" +
                "buttons is pressed."))
        # min time textbox:
        self.min_time_textbox = tkcw.Textbox(
            self.output_frame,
            label='Minimum acquire time (s)',
            default_text='None',
            row=4,
            width=spinbox_width,
            height=1)
        total_storage_textbox_tip = tix.Balloon(self.min_time_textbox)
        total_storage_textbox_tip.bind_widget(
            self.min_time_textbox,
            balloonmsg=(
                "Shows the 'Minimum acquire time (s)' that the microscope \n" +
                "will need if 'Run acquire' is pressed (based on the \n" +
                "settings that were last applied).\n" +
                "NOTE: this value does not take into account the \n" +
                "'move time' when using the 'Loop over position list' \n" +
                "option (so the actual time will be significantly more). \n" +
                "This value is only updated when 'Auto update (On/Off)' is \n" +
                "running or one of the 'ACQUIRE' buttons is pressed\n"))
        return None

    def init_update_settings(self):
        self.set_running_mode('update_settings')
        self.update_settings()

    def update_settings(self):
        if self.running_update_settings.get():
            self.apply_settings(check_XY_stage=False)
            self.update_gui_settings_output()
            self.root.after(self.gui_delay_ms, self.update_settings)
        return None

    def update_gui_settings_output(self):
        self.scope.apply_settings().join() # update attributes
        # volumes per second:
        text = '%0.3f'%self.scope.volumes_per_s
        self.volumes_per_s_textbox.textbox.delete('1.0', '10.0')
        self.volumes_per_s_textbox.textbox.insert('1.0', text)
        # calculate memory:
        total_memory_gb = 1e-9 * self.scope.total_bytes
        max_memory_gb = 1e-9 * self.scope.max_allocated_bytes
        memory_pct = 100 * total_memory_gb / max_memory_gb
        text = '%0.3f (%0.2f%% of max)'%(total_memory_gb, memory_pct)
        self.total_memory_textbox.textbox.delete('1.0', '10.0')
        self.total_memory_textbox.textbox.insert('1.0', text)
        # get position count:
        positions = 1
        if self.loop_over_position_list.get():
            positions = max(len(self.XY_stage_position_list), 1)
        # calculate storage:
        acquires = self.acquire_number_spinbox.value
        data_gb = 1e-9 * self.scope.bytes_per_data_buffer
        preview_gb = 1e-9 * self.scope.bytes_per_preview_buffer
        total_storage_gb = (data_gb + preview_gb) * positions * acquires
        text = '%0.3f'%total_storage_gb
        self.total_storage_textbox.textbox.delete('1.0', '10.0')
        self.total_storage_textbox.textbox.insert('1.0', text)        
        # calculate time:
        min_acquire_time_s = self.scope.buffer_time_s * positions
        min_total_time_s = min_acquire_time_s * acquires
        if self.delay_spinbox.value > min_acquire_time_s:
            min_total_time_s = (
                self.delay_spinbox.value * (acquires - 1) + min_acquire_time_s)
        text = '%0.6f (%0.0f min)'%(min_total_time_s, (min_total_time_s / 60))
        self.min_time_textbox.textbox.delete('1.0', '10.0')
        self.min_time_textbox.textbox.insert('1.0', text)
        return None

    def init_gui_position_list(self):
        self.positions_frame = tk.LabelFrame(
            self.root, text='POSITION LIST (Scout mode)', bd=6)
        self.positions_frame.grid(
            row=1, column=6, rowspan=2, padx=10, pady=10, sticky='n')
        self.positions_frame.bind( # force update
            '<Enter>', lambda event: self.positions_frame.focus_set())
        button_width, button_height = 25, 2
        spinbox_width = 20
        # load from folder:
        load_from_folder_button = tk.Button(
            self.positions_frame,
            text="Load from folder",
            command=self.load_positions_from_folder,
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
        delete_all_positions_button = tk.Button(
            self.positions_frame,
            text="Delete all positions",
            command=self.delete_all_positions,
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
        delete_current_position_button = tk.Button(
            self.positions_frame,
            text="Delete current position",
            command=self.delete_current_position,
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
            self.positions_frame,
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
        # move to start:
        self.move_to_start = tk.BooleanVar()
        self.move_to_start_button = tk.Checkbutton(
            self.positions_frame,
            text="Move to start",
            variable=self.move_to_start,
            indicatoron=0,
            width=button_width,
            height=button_height)
        self.move_to_start_button.grid(row=4, column=0, padx=10, pady=10)
        move_to_start_button_tip = tix.Balloon(self.move_to_start_button)
        move_to_start_button_tip.bind_widget(
            self.move_to_start_button,
            balloonmsg=(
                "The 'Move to start' button will move the 'FOCUS PIEZO' \n" + 
                "and 'XY STAGE' to the first position in the position list.\n" +
                "NOTE: this is only active in 'Scout mode' and if the \n" +
                "position is not already at the start of the position list."))
        # move back:
        self.move_back = tk.BooleanVar()
        self.move_back_button = tk.Checkbutton(
            self.positions_frame,
            text="Move back (-1)",
            variable=self.move_back,
            indicatoron=0,
            width=button_width,
            height=button_height)
        self.move_back_button.grid(row=5, column=0, padx=10, pady=10)
        move_back_button_tip = tix.Balloon(self.move_back_button)
        move_back_button_tip.bind_widget(
            self.move_back_button,
            balloonmsg=(
                "The 'Move back (-1)' button will move the 'FOCUS PIEZO' \n" + 
                "and 'XY STAGE' to the previous (n - 1) position in the \n" +
                "position list.\n" +
                "NOTE: this is only active in 'Scout mode' and if the \n" +
                "position is not already at the start of the position list."))
        # current position:
        self.current_position_spinbox = tkcw.CheckboxSliderSpinbox(
            self.positions_frame,
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
        self.move_forward = tk.BooleanVar()
        self.move_forward_button = tk.Checkbutton(
            self.positions_frame,
            text="Move forward (+1)",
            variable=self.move_forward,
            indicatoron=0,
            width=button_width,
            height=button_height)
        self.move_forward_button.grid(row=7, column=0, padx=10, pady=10)
        move_forward_button_tip = tix.Balloon(self.move_forward_button)
        move_forward_button_tip.bind_widget(
            self.move_forward_button,
            balloonmsg=(
                "The 'Move forward (+1)' button will move the 'FOCUS \n" + 
                "PIEZO' and 'XY STAGE' to the next (n + 1) position in \n" +
                "the position list.\n" +
                "NOTE: this is only active in 'Scout mode' and if the \n" +
                "position is not already at the end of the position list."))
        # move to end:
        self.move_to_end = tk.BooleanVar()
        self.move_to_end_button = tk.Checkbutton(
            self.positions_frame,
            text="Move to end",
            variable=self.move_to_end,
            indicatoron=0,
            width=button_width,
            height=button_height)
        self.move_to_end_button.grid(row=8, column=0, padx=10, pady=10)
        move_to_end_button_tip = tix.Balloon(self.move_to_end_button)
        move_to_end_button_tip.bind_widget(
            self.move_to_end_button,
            balloonmsg=(
                "The 'Move to end' button will move the 'FOCUS PIEZO' \n" + 
                "and 'XY STAGE' to the last position in the position list.\n" +
                "NOTE: this is only active in 'Scout mode' and if the \n" +
                "position is not already at the end of the position list."))        
        return None

    def make_empty_position_list(self):
        self.focus_piezo_position_list = []
        self.XY_stage_position_list = []
        with open(self.session_folder +
                  "focus_piezo_position_list.txt", "w") as file:
            file.write(self.session_folder + '\n')
        with open(self.session_folder +
              "XY_stage_position_list.txt", "w") as file:
            file.write(self.session_folder + '\n')
        return None

    def load_positions_from_folder(self):
        # get folder from user:
        folder_path = tk.filedialog.askdirectory(
            parent=self.root,
            initialdir=os.getcwd(),
            title='Please choose a previous "gui session" folder')
        # read files, parse into lists and update attributes:
        focus_piezo_file_path = folder_path + '\\focus_piezo_position_list.txt'
        XY_stage_file_path = folder_path + '\\XY_stage_position_list.txt'
        with open(focus_piezo_file_path, 'r') as file:
            focus_piezo_position_list = file.read().splitlines()[1:] # skip 1st
        with open(XY_stage_file_path, 'r') as file:
            XY_stage_position_list = file.read().splitlines()[1:] # skip 1st
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

    def delete_all_positions(self):
        self.make_empty_position_list()
        self.total_positions_spinbox.update_and_validate(0)
        self.current_position_spinbox.update_and_validate(0)
        return None

    def delete_current_position(self):
        if self.total_positions_spinbox.value == 0:
            return
        i = self.current_position_spinbox.value - 1
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

    def update_position_list(self):
        # update list:
        self.focus_piezo_position_list.append(
            self.applied_settings['focus_piezo_z_um'])
        self.XY_stage_position_list.append(
            self.applied_settings['XY_stage_position_mm'])
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

    def init_gui_acquire(self):
        self.acquire_frame = tk.LabelFrame(
            self.root, text='ACQUIRE', font=('Segoe UI', '10', 'bold'), bd=6)
        self.acquire_frame.grid(
            row=3, column=6, rowspan=2, padx=10, pady=10, sticky='n')
        self.acquire_frame.bind( # force update
            '<Enter>', lambda event: self.acquire_frame.focus_set())
        button_width, button_height = 25, 2
        bold_width_adjust = -3
        spinbox_width = 20
        # snap volume:
        snap_volume_button = tk.Button(
            self.acquire_frame,
            text="Snap volume",
            command=self.snap_volume,
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
        self.running_live = tk.BooleanVar()
        live_mode_button = tk.Checkbutton(
            self.acquire_frame,
            text='Live mode (On/Off)',
            variable=self.running_live,
            command=self.init_live_mode,
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
        self.running_scout = tk.BooleanVar()
        scout_mode_button = tk.Checkbutton(
            self.acquire_frame,
            text='Scout mode (On/Off)',
            variable=self.running_scout,
            command=self.init_scout_mode,
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
        save_volume_and_position_button = tk.Button(
            self.acquire_frame,
            text="Save volume and position",
            command=self.save_volume_and_position,
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
        self.running_acquire = tk.BooleanVar()
        run_acquire_button = tk.Button(
            self.acquire_frame,
            text="Run acquire",
            command=self.init_acquire,
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
        cancel_acquire_button = tk.Button(
            self.acquire_frame,
            text="Cancel acquire",
            command=self.cancel_acquire,
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

    def snap_volume(self):
        self.apply_settings(single_volume=True)
        self.update_gui_settings_output()
        self.last_acquire_task.join() # don't accumulate acquires
        self.scope.acquire()
        return None

    def init_live_mode(self):
        self.set_running_mode('live')
        self.apply_settings(single_volume=True)
        self.update_gui_settings_output()
        self.run_live_mode()
        return None

    def run_live_mode(self):
        if self.running_live.get():
            self.apply_settings(single_volume=True, check_XY_stage=False)
            self.last_acquire_task.join() # don't accumulate acquires
            self.last_acquire_task = self.scope.acquire()
            self.root.after(self.gui_delay_ms, self.run_live_mode)
        return None

    def enable_XYZ_navigation_buttons(self, enable): # pass True or False
        state = 'normal'
        if not enable: state = 'disabled'
        # focus:
        for child in self.gui_focus_piezo.position_um.winfo_children():
            child.configure(state=state)
        self.gui_focus_piezo.button_large_move_up.config(state=state)
        self.gui_focus_piezo.button_small_move_up.config(state=state)
        self.gui_focus_piezo.button_center_move.config(state=state)
        self.gui_focus_piezo.button_small_move_down.config(state=state)
        self.gui_focus_piezo.button_large_move_down.config(state=state)
        # XY stage:
        self.gui_xy_stage.button_up.config(state=state)
        self.gui_xy_stage.button_down.config(state=state)
        self.gui_xy_stage.button_left.config(state=state)
        self.gui_xy_stage.button_right.config(state=state)
        # position list:
        self.move_to_start_button.config(state=state)
        self.move_back_button.config(state=state)
        self.move_forward_button.config(state=state)
        self.move_to_end_button.config(state=state)
        return None

    def init_scout_mode(self):
        self.set_running_mode('scout')
        self.enable_XYZ_navigation_buttons(True)
        self.apply_settings(single_volume=True)
        self.update_gui_settings_output()        
        if self.running_scout.get():
            self.last_acquire_task.join() # don't accumulate acquires
            self.last_acquire_task = self.scope.acquire()
        self.run_scout_mode()
        return None

    def check_XY_buttons(self):
        def update_XY_position(): # only called if button pressed
            self.XY_button_pressed = True
            # current position:
            XY_stage_position_mm = self.gui_xy_stage.position_mm
            # calculate move size:
            move_pct = self.gui_xy_stage.move_pct.value / 100
            scan_width_um = (
            self.applied_settings['width_px'] * sols.sample_px_um)
            ud_move_mm = (
                1e-3 * self.applied_settings['scan_range_um'] * move_pct)
            lr_move_mm = 1e-3 * scan_width_um * move_pct
            # check which direction:
            if self.XY_stage_last_move == 'up (+Y)':
                move_mm = (0, ud_move_mm)
            if self.XY_stage_last_move == 'down (-Y)':
                move_mm = (0, -ud_move_mm)
            if self.XY_stage_last_move == 'left (-X)':
                move_mm = (-lr_move_mm, 0)
            if self.XY_stage_last_move == 'right (+X)':
                move_mm = (lr_move_mm, 0)
            # update position and gui:
            XY_stage_position_mm = tuple(map(sum, zip(
                XY_stage_position_mm, move_mm)))
            self.gui_xy_stage.update_position(XY_stage_position_mm)
            # toggle buttons back:
            self.gui_xy_stage.move_up.set(0)
            self.gui_xy_stage.move_down.set(0)
            self.gui_xy_stage.move_left.set(0)
            self.gui_xy_stage.move_right.set(0)
        # run minimal code for speed:
        self.XY_button_pressed = False
        if self.gui_xy_stage.move_up.get():
            self.XY_stage_last_move = 'up (+Y)'
            update_XY_position()
        elif self.gui_xy_stage.move_down.get():
            self.XY_stage_last_move = 'down (-Y)'
            update_XY_position()
        elif self.gui_xy_stage.move_left.get():
            self.XY_stage_last_move = 'left (-X)'
            update_XY_position()
        elif self.gui_xy_stage.move_right.get():
            self.XY_stage_last_move = 'right (+X)'
            update_XY_position()
        return None

    def check_position_buttons(self):
        def update_position(go_to): # only called if button pressed
            # check total and current position:
            total_positions  = self.total_positions_spinbox.value
            current_position = self.current_position_spinbox.value
            if total_positions == 0:
                return None
            self.position_button_pressed = True
            # check which direction:
            if go_to == 'start':
                new_position = 1
                if new_position == current_position:
                    self.position_button_pressed = False
            if go_to == 'back':
                if current_position > 1:
                    new_position = current_position - 1
                else:
                    new_position = current_position
                    self.position_button_pressed = False
            if go_to == 'forward':
                if current_position < total_positions:
                    new_position = current_position + 1
                else:
                    new_position = current_position
                    self.position_button_pressed = False
            if go_to == 'end':
                new_position = total_positions
                if new_position == current_position:
                    self.position_button_pressed = False
            if total_positions == 1: # refresh to the only position
                self.position_button_pressed = True
            index = new_position - 1
            # get positions:
            focus_piezo_z_um = self.focus_piezo_position_list[index]
            XY_stage_position_mm = self.XY_stage_position_list[index]
            # update gui:
            self.gui_focus_piezo.position_um.update_and_validate(
                focus_piezo_z_um)
            self.gui_xy_stage.update_position(XY_stage_position_mm)
            self.current_position_spinbox.update_and_validate(new_position)
            # toggle buttons back:
            self.move_to_start.set(0)
            self.move_back.set(0)
            self.move_forward.set(0)
            self.move_to_end.set(0)
        # run minimal code for speed:
        self.position_button_pressed = False
        if self.move_to_start.get():
            update_position('start')
        elif self.move_back.get():
            update_position('back')
        elif self.move_forward.get():
            update_position('forward')
        elif self.move_to_end.get():
            update_position('end')
        return None

    def run_scout_mode(self):
        if self.running_scout.get():
            def snap():
                self.apply_settings(single_volume=True, check_XY_stage=False)
                self.last_acquire_task.join() # don't accumulate acquires
                self.last_acquire_task = self.scope.acquire()
            # Check Z:
            focus_piezo_z_um = self.gui_focus_piezo.position_um.value
            if self.applied_settings['focus_piezo_z_um'] != focus_piezo_z_um:
                snap()
            # Check XY buttons:
            self.check_XY_buttons()
            if self.XY_button_pressed:
                snap() # before gui update
                self.gui_xy_stage.update_last_move(self.XY_stage_last_move)
            # Check position buttons:
            self.check_position_buttons()
            if self.position_button_pressed:
                snap()
            # Check XY joystick:
            XY_stage_position_mm = self.check_XY_stage()
            if self.XY_joystick_active:
                snap() # before gui update
                self.gui_xy_stage.update_last_move(self.XY_stage_last_move)
            else: # (avoids erroneous XY updates)
                self.gui_xy_stage.update_position(XY_stage_position_mm)
            self.root.after(self.gui_delay_ms, self.run_scout_mode)
        else:
            self.enable_XYZ_navigation_buttons(False)
        return None

    def save_volume_and_position(self):
        self.apply_settings(single_volume=True)
        self.update_position_list()
        self.update_gui_settings_output()
        folder_name = self.get_folder_name() + '_snap'
        self.last_acquire_task.join() # don't accumulate acquires
        self.scope.acquire(filename='snap.tif',
                           folder_name=folder_name,
                           description=self.description_textbox.text)
        return None

    def init_acquire(self):
        print('\nAcquire -> started')
        self.set_running_mode('acquire', enable=True)
        self.apply_settings()
        self.update_gui_settings_output()
        self.folder_name = self.get_folder_name() + '_acquire'
        self.description = self.description_textbox.text
        self.acquire_count = 0
        self.saved_delay_s = False
        self.current_position = 0
        self.total_positions = 0
        if self.loop_over_position_list.get():
            self.total_positions = len(self.XY_stage_position_list)
        self.run_acquire()
        return None

    def run_acquire(self):
        if not self.running_acquire.get(): # check for cancel
            return None
        # don't launch all tasks: either wait 1 buffer time or apply delay:
        wait_ms = int(round(1e3 * self.scope.buffer_time_s))
        # check mode -> either single position or loop over positions:
        if self.loop_over_position_list.get():
            if self.current_position == 0:
                self.loop_t0_s = time.perf_counter()
            self.gui_focus_piezo.position_um.update_and_validate(
                self.focus_piezo_position_list[self.current_position])
            self.gui_xy_stage.update_position(
                self.XY_stage_position_list[self.current_position])
            self.current_position_spinbox.update_and_validate(
                self.current_position + 1)
            self.apply_settings(check_XY_stage=False)
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
                if self.delay_spinbox.value > loop_time_s:
                    wait_ms = int(round(1e3 * (
                        self.delay_spinbox.value - loop_time_s)))                   
        else:
            self.scope.acquire(filename='%06i.tif'%self.acquire_count,
                               folder_name=self.folder_name,
                               description=self.description)
            self.acquire_count += 1
            if self.delay_spinbox.value > self.scope.buffer_time_s:
                wait_ms = int(round(1e3 * self.delay_spinbox.value))
        # record gui delay:
        if (not self.saved_delay_s and os.path.exists(self.folder_name)):
            with open(self.folder_name + '\\'  "gui_delay_s.txt", "w") as file:
                file.write(self.folder_name + '\n')
                file.write('gui_delay_s: %i'%self.delay_spinbox.value + '\n')
                self.saved_delay_s = True
        # check acquire count before re-run:
        if self.acquire_count < self.acquire_number_spinbox.value:
            self.root.after(wait_ms, self.run_acquire)
        else:
            self.scope.finish_all_tasks()
            self.running_acquire.set(0)
            print('Acquire -> finished\n')
        return None

    def cancel_acquire(self):
        self.running_acquire.set(0)
        print('\n ***Acquire -> canceled*** \n')
        return None

    def init_quit_button(self):
        quit_frame = tk.LabelFrame(
            self.root, text='QUIT', font=('Segoe UI', '10', 'bold'), bd=6)
        quit_frame.grid(row=5, column=6, padx=10, pady=10, sticky='n')
        quit_gui_button = tk.Button(
            quit_frame,
            text="EXIT GUI",
            command=self.close,
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

    def close(self):
        if self.init_microscope: self.scope.close()
        self.root.quit()
        return None

if __name__ == '__main__':
    gui_microscope = GuiMicroscope(init_microscope=True)
