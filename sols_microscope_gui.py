import os
import copy
from datetime import datetime
import tkinter as tk
from tkinter import font
from tkinter import filedialog

import sols_microscope as sols
import tkinter_compound_widgets as tkcw

class GuiTransmittedLight:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='TRANSMITTED LIGHT', bd=6)
        frame.grid(row=1, column=0, padx=10, pady=10, sticky='n')
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
        self.current_emission_filter = tk.StringVar()
        self.current_emission_filter.set('ZET405/488/561/640m') # set default
        option_menu = tk.OptionMenu(
            inner_frame,
            self.current_emission_filter,
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
            slider_length=350,
            tickinterval=9,
            min_value=100,
            max_value=1000,
            default_value=1000,
            columnspan=2,
            row=0,
            width=5)
        self.illumination_time_ms = tkcw.CheckboxSliderSpinbox(
            frame,
            label='+ illumination time (ms)',
            checkbox_enabled=False,
            slider_length=350,
            tickinterval=10,
            min_value=0,
            max_value=1000,
            default_value=0,
            columnspan=2,
            row=1,
            width=5)
        self.height_px = tkcw.CheckboxSliderSpinbox(
            frame,
            label='height pixels',
            orient='vertical',
            checkbox_enabled=False,
            slider_length=150,
            tickinterval=3,
            slider_flipped=True,
            min_value=12,
            max_value=500,
            default_value=250,
            row=2,
            width=5)
        self.width_px = tkcw.CheckboxSliderSpinbox(
            frame,
            label='width pixels',
            checkbox_enabled=False,
            slider_length=250,
            tickinterval=4,
            min_value=60,
            max_value=1000,
            default_value=1000,
            row=3,
            column=1,
            sticky='s',
            width=5)
        tkcw.CanvasRectangleSliderTrace2D(
            frame,
            self.width_px,
            self.height_px,
            row=2,
            column=1,
            fill='yellow')

class GuiGalvo:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='GALVO', bd=6)
        frame.grid(row=3, column=1, rowspan=2, padx=10, pady=10, sticky='n')
        slider_length = 365 # match to camera
        button_width, button_height = 10, 2
        # scan slider:
        self.scan_range_um_min, self.scan_range_um_max = 1, 100
        self.scan_range_um_center = int(round((
        self.scan_range_um_max - self.scan_range_um_min) / 2))
        self.scan_range_um = tkcw.CheckboxSliderSpinbox(
            frame,
            label='~scan range (um)',
            checkbox_enabled=False,
            slider_length=slider_length,
            tickinterval=10,
            min_value=self.scan_range_um_min,
            max_value=self.scan_range_um_max,
            default_value=self.scan_range_um_center,
            row=0,
            width=5)
        # scan min button:
        button_scan_range_um_min = tk.Button(
            frame,
            text="min",
            command=self.set_scan_range_um_min,
            width=button_width,
            height=button_height)
        button_scan_range_um_min.grid(
            row=1, column=0, padx=10, pady=10, sticky='w')
        # scan center button:
        button_scan_range_um_center = tk.Button(
            frame,
            text="center",
            command=self.set_scan_range_um_center,
            width=button_width,
            height=button_height)
        button_scan_range_um_center.grid(
            row=1, column=0, padx=5, pady=5)
        # scan max button:
        button_scan_range_um_max = tk.Button(
            frame,
            text="max",
            command=self.set_scan_range_um_max,
            width=button_width,
            height=button_height)
        button_scan_range_um_max.grid(
            row=1, column=0, padx=10, pady=10, sticky='e')
        # voxel slider:
        self.voxel_aspect_ratio_min, self.voxel_aspect_ratio_max = 2, 32
        self.voxel_aspect_ratio_center = int(round((
            self.voxel_aspect_ratio_max - self.voxel_aspect_ratio_min) / 2))
        self.voxel_aspect_ratio = tkcw.CheckboxSliderSpinbox(
            frame,
            label='~voxel aspect ratio',
            checkbox_enabled=False,
            slider_length=slider_length,
            tickinterval=10,
            min_value=self.voxel_aspect_ratio_min,
            max_value=self.voxel_aspect_ratio_max,
            default_value=self.voxel_aspect_ratio_max,
            row=2,
            width=5)
        # voxel min button:
        button_voxel_aspect_ratio_min = tk.Button(
            frame,
            text="min",
            command=self.set_voxel_aspect_ratio_min,
            width=button_width,
            height=button_height)
        button_voxel_aspect_ratio_min.grid(
            row=3, column=0, padx=10, pady=10, sticky='w')
        # voxel center button:
        button_voxel_aspect_ratio_center = tk.Button(
            frame,
            text="center",
            command=self.set_voxel_aspect_ratio_center,
            width=button_width,
            height=button_height)
        button_voxel_aspect_ratio_center.grid(
            row=3, column=0, padx=5, pady=5)
        # voxel max button:
        button_voxel_aspect_ratio_max = tk.Button(
            frame,
            text="max",
            command=self.set_voxel_aspect_ratio_max,
            width=button_width,
            height=button_height)
        button_voxel_aspect_ratio_max.grid(
            row=3, column=0, padx=10, pady=10, sticky='e')

    def set_scan_range_um_min(self):
        self.scan_range_um.update_and_validate(self.scan_range_um_min)
        return None

    def set_scan_range_um_center(self):
        self.scan_range_um.update_and_validate(self.scan_range_um_center)
        return None

    def set_scan_range_um_max(self):
        self.scan_range_um.update_and_validate(self.scan_range_um_max)
        return None

    def set_voxel_aspect_ratio_min(self):
        self.voxel_aspect_ratio.update_and_validate(self.voxel_aspect_ratio_min)
        return None

    def set_voxel_aspect_ratio_center(self):
        self.voxel_aspect_ratio.update_and_validate(
            self.voxel_aspect_ratio_center)
        return None

    def set_voxel_aspect_ratio_max(self):
        self.voxel_aspect_ratio.update_and_validate(self.voxel_aspect_ratio_max)
        return None

class GuiFocusPiezo:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='FOCUS PIEZO', bd=6)
        frame.grid(row=1, column=2, rowspan=2, padx=10, pady=10, sticky='n')
        self.min, self.max = 0, 100
        self.center = int(round((self.max - self.min) / 2))
        self.large_move, self.small_move = 5, 1
        # slider:
        self.position_spinbox = tkcw.CheckboxSliderSpinbox(
            frame,
            label='position (um)',
            orient='vertical',
            checkbox_enabled=False,
            slider_length=460, # match to camera
            tickinterval=10,
            min_value=self.min,
            max_value=self.max,
            rowspan=5,
            width=5)
        button_width, button_height = 10, 2
        # up buttons:
        self.button_large_move_up = tk.Button(
            frame,
            text="up %ium"%self.large_move,
            command=self.large_move_up,
            width=button_width,
            height=button_height)
        self.button_large_move_up.grid(row=0, column=1, padx=10, pady=10)
        self.button_small_move_up = tk.Button(
            frame,
            text="up %ium"%self.small_move,
            command=self.small_move_up,
            width=button_width,
            height=button_height)
        self.button_small_move_up.grid(row=1, column=1, sticky='s')
        # center button:
        self.button_center_move = tk.Button(
            frame,
            text="center",
            command=self.move_center,
            width=button_width,
            height=button_height)
        self.button_center_move.grid(row=2, column=1, padx=5, pady=5)
        # down buttons:
        self.button_small_move_down = tk.Button(
            frame,
            text="down %ium"%self.small_move,
            command=self.small_move_down,
            width=button_width,
            height=button_height)
        self.button_small_move_down.grid(row=3, column=1, sticky='n')
        self.button_large_move_down = tk.Button(
            frame,
            text="down %ium"%self.large_move,
            command=self.large_move_down,
            width=button_width,
            height=button_height)
        self.button_large_move_down.grid(row=4, column=1, padx=10, pady=10)

    def large_move_up(self):
        self.position_spinbox.update_and_validate(
            self.position_spinbox.value - self.large_move)
        return None

    def small_move_up(self):
        self.position_spinbox.update_and_validate(
            self.position_spinbox.value - self.small_move)
        return None

    def move_center(self):
        self.position_spinbox.update_and_validate(self.center)
        return None

    def small_move_down(self):
        self.position_spinbox.update_and_validate(
            self.position_spinbox.value + self.small_move)
        return None

    def large_move_down(self):
        self.position_spinbox.update_and_validate(
            self.position_spinbox.value + self.large_move)
        return None

class GuiXYStage:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='XY STAGE', bd=6)
        frame.grid(row=3, column=2, rowspan=2, columnspan=2,
                   padx=10, pady=10, sticky='n')
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
        # buttons
        button_width, button_height = 10, 2
        # up button:
        padx, pady = 10, 10
        self.button_up = tk.Button(
            frame,
            text="up",
            command=self.move_up,
            width=button_width,
            height=button_height)
        self.button_up.grid(row=0, column=1, padx=padx, pady=pady)
        self.move_up = False
        # down button:
        self.button_down = tk.Button(
            frame,
            text="down",
            command=self.move_down,
            width=button_width,
            height=button_height)
        self.button_down.grid(row=2, column=1, padx=padx, pady=pady)
        self.move_down = False
        # left button:
        self.button_left = tk.Button(
            frame,
            text="left",
            command=self.move_left,
            width=button_width,
            height=button_height)
        self.button_left.grid(row=1, column=0, padx=padx, pady=pady)
        self.move_left = False
        # right button:
        self.button_right = tk.Button(
            frame,
            text="right",
            command=self.move_right,
            width=button_width,
            height=button_height)
        self.button_right.grid(row=1, column=2, padx=padx, pady=pady)
        self.move_right = False
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

    def move_up(self):
        self.move_up = True
        return None

    def move_down(self):
        self.move_down = True
        return None

    def move_left(self):
        self.move_left = True
        return None

    def move_right(self):
        self.move_right = True
        return None

class GuiMicroscope:
    def __init__(self, init_microscope=True): # set False for GUI design...
        self.init_microscope = init_microscope 
        self.root = tk.Tk()
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
            self.gui_focus_piezo.position_spinbox.update_and_validate(
                focus_piezo_z_um)
            self.gui_xy_stage.update_position(XY_stage_position_mm)
            self.XY_joystick_active = False
            self.XY_stage_last_move = 'None'
            self.focus_piezo_position_list = []
            self.XY_stage_position_list = []
            # get XY stage limits for feedback in scout mode:
            self.XY_stage_x_min = self.scope.XY_stage.x_min
            self.XY_stage_y_min = self.scope.XY_stage.y_min
            self.XY_stage_x_max = self.scope.XY_stage.x_max
            self.XY_stage_y_max = self.scope.XY_stage.y_max
            # init settings attributes:
            self.applied_settings = {}
            for k in gui_settings.keys():
                self.applied_settings[k] = None
            self.apply_settings(check_XY_stage=False) # mandatory call
            # get scope ready:
            self.loop_snoutfocus()
            self.last_acquire_task = self.scope.acquire() # snap a volume
            # make session folder and position lists:
            dt = datetime.strftime(datetime.now(),'%Y-%m-%d_%H-%M-%S_')
            self.session_folder = dt + 'sols_gui_session\\'
            os.makedirs(self.session_folder)
            with open(self.session_folder +
                  "focus_piezo_position_list.txt", "w") as file:
                file.write(self.session_folder + '\n')
            with open(self.session_folder +
                  "XY_stage_position_list.txt", "w") as file:
                file.write(self.session_folder + '\n')
        # start event loop:
        self.root.mainloop() # blocks here until 'QUIT'
        self.root.destroy()

    def init_quit_button(self):
        quit_frame = tk.LabelFrame(self.root, text='QUIT', bd=6)
        quit_frame.grid(
            row=6, column=0, columnspan=6, padx=10, pady=10, sticky='n')
        quit_gui_button = tk.Button(
            quit_frame,
            text="QUIT GUI",
            command=self.close,
            height=2,
            width=25)
        quit_gui_button.grid(row=0, column=0, padx=10, pady=10, sticky='n')

    def init_gui_settings(self):
        self.settings_frame = tk.LabelFrame(
            self.root, text='SETTINGS', bd=6)
        self.settings_frame.grid(
            row=1, column=4, rowspan=2, padx=10, pady=10, sticky='n')
        self.settings_frame.bind('<Enter>', self.get_tkfocus) # force update
        button_width, button_height = 25, 2
        spinbox_width = 20
        # load from file:
        load_from_file_button = tk.Button(
            self.settings_frame,
            text="Load from metadata file",
            command=self.load_settings_from_file,
            width=button_width,
            height=button_height)
        load_from_file_button.grid(row=0, column=0, padx=10, pady=10)
        # label textbox:
        self.label_textbox = tkcw.Textbox(
            self.settings_frame,
            label='Folder label',
            default_text='sols',
            row=1,
            width=spinbox_width,
            height=1)
        # description textbox:
        self.description_textbox = tkcw.Textbox(
            self.settings_frame,
            label='Description',
            default_text='what are you doing?',
            row=2,
            width=spinbox_width,
            height=3)
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
        # acquire number spinbox:
        self.acquire_number_spinbox = tkcw.CheckboxSliderSpinbox(
            self.settings_frame,
            label='Acquire number',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=1e6,
            default_value=1,
            row=4,
            width=spinbox_width)
        # delay spinbox:
        self.delay_spinbox = tkcw.CheckboxSliderSpinbox(
            self.settings_frame,
            label='Inter-acquire delay (s)',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=0,
            max_value=3600,
            default_value=0,
            row=5,
            width=spinbox_width)
        return None

    def init_gui_settings_output(self):
        self.output_frame = tk.LabelFrame(
            self.root, text='SETTINGS OUTPUT', bd=6)
        self.output_frame.grid(
            row=3, column=4, rowspan=2, padx=10, pady=10, sticky='n')
        self.output_frame.bind('<Enter>', self.get_tkfocus) # force update
        button_width, button_height = 25, 2
        spinbox_width = 20
        # auto update settings button:
        self.auto_update_settings_enabled = tk.BooleanVar()
        auto_update_settings_button = tk.Checkbutton(
            self.output_frame,
            text='Auto update (On/Off)',
            variable=self.auto_update_settings_enabled,
            command=self.init_auto_update_settings,
            indicatoron=0,
            width=button_width,
            height=button_height)
        auto_update_settings_button.grid(row=0, column=0, padx=10, pady=10)
        # volumes per second textbox:
        self.volumes_per_s_textbox = tkcw.Textbox(
            self.output_frame,
            label='Volumes per second',
            default_text='None',
            row=1,
            width=spinbox_width,
            height=1)
        # total memory textbox:
        self.total_memory_textbox = tkcw.Textbox(
            self.output_frame,
            label='Total memory (GB)',
            default_text='None',
            row=2,
            width=spinbox_width,
            height=1)
        # total storage textbox:
        self.total_storage_textbox = tkcw.Textbox(
            self.output_frame,
            label='Total storage (GB)',
            default_text='None',
            row=3,
            width=spinbox_width,
            height=1)
        # total time textbox:
        self.total_time_textbox = tkcw.Textbox(
            self.output_frame,
            label='Total acquire time (s)',
            default_text='None',
            row=4,
            width=spinbox_width,
            height=1)
        return None

    def init_gui_grid_navigator(self):
        self.grid_frame = tk.LabelFrame(
            self.root, text='GRID NAVIGATOR', bd=6)
        self.grid_frame.grid(
            row=1, column=3, rowspan=2, padx=10, pady=10, sticky='n')
        self.grid_frame.bind('<Enter>', self.get_tkfocus) # force update
        button_width, button_height = 25, 2
        spinbox_width = 20
        # load from file:
        load_from_file_button = tk.Button(
            self.grid_frame,
            text="Load grid from file",
            command=self.load_grid_from_file,
            width=button_width,
            height=button_height)
        load_from_file_button.grid(row=0, column=0, padx=10, pady=10)
        # generate grid:
        generate_grid_button = tk.Button(
            self.grid_frame,
            text="Generate grid",
            command=self.generate_grid_popup,
            width=button_width,
            height=button_height)
        generate_grid_button.grid(row=1, column=0, padx=10, pady=10)
        # set current location:
        self.set_current_location_button = tk.Button(
            self.grid_frame,
            text="Set current location",
            command=self.set_current_location_popup,
            width=button_width,
            height=button_height)
        self.set_current_location_button.grid(row=2, column=0, padx=10, pady=10)
        self.set_current_location_button.config(state='disabled')
        # current position:
        self.current_position_textbox = tkcw.Textbox(
            self.grid_frame,
            label='Current location',
            default_text='None',
            height=1,
            width=20)
        self.current_position_textbox.grid(row=3, column=0, padx=10, pady=10)
        # move to selection:
        self.move_to_selection_button = tk.Button(
            self.grid_frame,
            text="Move to selection",
            command=self.move_to_selection_popup,
            width=button_width,
            height=button_height)
        self.move_to_selection_button.grid(row=4, column=0, padx=10, pady=10)
        self.move_to_selection_button.config(state='disabled')
        return None

    def load_grid_from_file(self):
        # get file from user:
        file_path = tk.filedialog.askopenfilename(
            parent=self.root,
            initialdir=os.getcwd(),
            title='Please choose a previous "grid" file (.txt)')        
        with open(file_path, 'r') as file:
            grid_data = file.read().splitlines()
        # format:
        self.grid_rows = int(grid_data[0].split(':')[1])
        self.grid_cols = int(grid_data[1].split(':')[1])
        self.grid_spacing_um = int(grid_data[2].split(':')[1])
        # show user:
        self.load_grid_from_file_popup = tk.Toplevel()
        self.load_grid_from_file_popup.title('Grid from file')
        self.load_grid_from_file_popup.grab_set() # force user to interact
        x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
        self.load_grid_from_file_popup.geometry("+%d+%d" % (x + 800, y + 400))
        button_width, button_height = 25, 2
        exit_button = tk.Button(
            self.load_grid_from_file_popup, text="Exit",
            command=self.load_grid_from_file_popup.destroy,
            height=button_height, width=button_width)
        exit_button.grid(row=1, column=0, padx=10, pady=10, sticky='n')
        self.generate_grid_buttons(
            self.load_grid_from_file_popup, enabled=False)
        self.set_current_location_button.config(state='normal')
        self.move_to_selection_button.config(state='disabled')            
        return None

    def generate_grid_popup(self):
        # popup:
        self.generate_grid_popup = tk.Toplevel()
        self.generate_grid_popup.title('Generate grid')
        self.generate_grid_popup.grab_set() # force user to interact
        x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
        self.generate_grid_popup.geometry("+%d+%d" % (x + 800, y + 400))
        button_width, button_height = 25, 2
        spinbox_width = 20
        # user input:
        self.grid_rows_spinbox = tkcw.CheckboxSliderSpinbox(
            self.generate_grid_popup,
            label='How many rows? (1-16)',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=16,
            default_value=2,
            row=0,
            width=spinbox_width,
            sticky='n')
        self.grid_cols_spinbox = tkcw.CheckboxSliderSpinbox(
            self.generate_grid_popup,
            label='How many columns? (1-24)',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=24,
            default_value=4,
            row=1,
            width=spinbox_width,
            sticky='n')
        self.grid_spacing_spinbox = tkcw.CheckboxSliderSpinbox(
            self.generate_grid_popup,
            label='What is the spacing (um)?',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=20000,
            default_value=1000,
            row=2,
            width=spinbox_width,
            sticky='n')
        generate_button = tk.Button(
            self.generate_grid_popup, text="Generate",
            command=self.generate_grid,
            height=button_height, width=button_width)
        generate_button.grid(row=3, column=0, padx=10, pady=10, sticky='n')
        def get_focus(event):
            self.generate_grid_popup.focus_set()
        generate_button.bind('<Enter>', get_focus) # force update
        exit_button = tk.Button(
            self.generate_grid_popup, text="Exit",
            command=self.generate_grid_popup.destroy,
            height=button_height, width=button_width)
        exit_button.grid(row=4, column=0, padx=10, pady=10, sticky='n')
        self.generate_grid(clear_buttons=False)
        return None

    def generate_grid(self, clear_buttons=True):
        if clear_buttons:
            self.generate_grid_buttons_frame.destroy()
        self.grid_rows = self.grid_rows_spinbox.value
        self.grid_cols = self.grid_cols_spinbox.value
        self.grid_spacing_um = self.grid_spacing_spinbox.value
        self.generate_grid_buttons(self.generate_grid_popup, enabled=False)
        self.set_current_location_button.config(state='normal')
        self.move_to_selection_button.config(state='disabled')
        with open(self.session_folder +
                  "grid_navigator_parameters.txt", "w") as file:
            file.write('rows:%i'%self.grid_rows + '\n')
            file.write('columns:%i'%self.grid_cols + '\n')
            file.write('spacing_um:%i'%self.grid_spacing_um + '\n')
        return None

    def generate_grid_buttons(self, master, enabled=True):
        self.generate_grid_buttons_frame = tk.LabelFrame(
            master, text='XY GRID', bd=6)
        self.generate_grid_buttons_frame.grid(
            row=0, column=1, rowspan=5, padx=10, pady=10)
        button_width, button_height = 5, 2
        self.check_button_array = [
            [None for c in range(self.grid_cols)] for r in range(
                self.grid_rows)]
        self.check_button_enabled_array = [
            [None for c in range(self.grid_cols)] for r in range(
                self.grid_rows)]
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                name = '%s%i'%(chr(ord('@')+r + 1), c + 1)
                self.check_button_enabled_array[r][c] = tk.BooleanVar()
                self.check_button_array[r][c] = tk.Checkbutton(
                    self.generate_grid_buttons_frame,
                    text=name,
                    variable=self.check_button_enabled_array[r][c],
                    indicatoron=0,
                    width=button_width,
                    height=button_height)
                self.check_button_array[r][c].grid(
                    row=r, column=c, padx=10, pady=10)
                if not enabled:
                    self.check_button_array[r][c].config(state='disabled')
        return None

    def set_current_location_popup(self):
        self.set_current_location_popup = tk.Toplevel()
        self.set_current_location_popup.title('Set current location')
        self.set_current_location_popup.grab_set() # force user to interact
        x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
        self.set_current_location_popup.geometry("+%d+%d" % (x + 800, y + 400))
        self.generate_grid_buttons(self.set_current_location_popup)
        self.run_set_current_location()
        return None

    def run_set_current_location(self):
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                if self.check_button_enabled_array[r][c].get():
                    self.current_location = [r, c]
                    self.update_current_location()
                    self.move_to_selection_button.config(state='normal')
                    self.set_current_location_popup.destroy()
                    return None
        self.root.after(self.gui_delay_ms, self.run_set_current_location)
        return None

    def update_current_location(self):
        name = '%s%i'%(chr(ord('@')+ self.current_location[0] + 1),
                       self.current_location[1] + 1)
        self.current_position_textbox.textbox.delete('1.0', '10.0')
        self.current_position_textbox.textbox.insert('1.0', name)
        return None

    def move_to_selection_popup(self):
        self.move_to_selection_popup = tk.Toplevel()
        self.move_to_selection_popup.title('Move to selection')
        self.move_to_selection_popup.grab_set() # force user to interact
        x, y = self.root.winfo_x(), self.root.winfo_y() # center popup
        self.move_to_selection_popup.geometry("+%d+%d" % (x + 800, y + 400))
        button_width, button_height = 25, 2
        cancel_button = tk.Button(
            self.move_to_selection_popup, text="Cancel",
            command=self.move_to_selection_popup.destroy,
            height=button_height, width=button_width)
        cancel_button.grid(row=1, column=0, padx=10, pady=10, sticky='n')
        self.generate_grid_buttons(self.move_to_selection_popup)
        r, c = self.current_location
        self.check_button_enabled_array[r][c].set(1)
        self.check_button_array[r][c].config(state='disabled')
        self.run_move_to_selection()
        return None

    def run_move_to_selection(self):
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                if (self.check_button_enabled_array[r][c].get() and
                    [r, c] != self.current_location):
                    move_rows = r - self.current_location[0]
                    move_cols = c - self.current_location[1]
                    Y_move_mm =   move_rows * self.grid_spacing_um / 1000
                    X_move_mm = - move_cols * self.grid_spacing_um / 1000
                    XY_stage_position_mm = [
                        self.applied_settings['XY_stage_position_mm'][0] +
                        X_move_mm,
                        self.applied_settings['XY_stage_position_mm'][1] +
                        Y_move_mm]
                    self.gui_xy_stage.update_position(XY_stage_position_mm)
                    self.apply_settings(
                        single_volume=True, check_XY_stage=False)
                    self.last_acquire_task.join() # don't accumulate acquires
                    self.last_acquire_task = self.scope.acquire()
                    self.current_location = [r, c]
                    self.update_current_location()
                    self.move_to_selection_popup.destroy()
                    return None
        self.root.after(self.gui_delay_ms, self.run_move_to_selection)
        return None

    def init_gui_position_list(self):
        self.positions_frame = tk.LabelFrame(
            self.root, text='POSITION LIST', bd=6)
        self.positions_frame.grid(
            row=1, column=5, rowspan=2, padx=10, pady=10, sticky='n')
        self.positions_frame.bind('<Enter>', self.get_tkfocus) # force update
        button_width, button_height = 25, 2
        spinbox_width = 20
        # load from folder:
        load_from_folder_button = tk.Button(
            self.positions_frame,
            text="Load from session folder",
            command=self.load_positions_from_folder,
            width=button_width,
            height=button_height)
        load_from_folder_button.grid(row=0, column=0, padx=10, pady=10)
        # total positions:
        self.total_positions_spinbox = tkcw.CheckboxSliderSpinbox(
            self.positions_frame,
            label='Total positions',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=0,
            max_value=1e6,
            default_value=0,
            row=1,
            width=spinbox_width)
        self.total_positions_spinbox.spinbox.config(state='disabled')
        # move to start:
        self.move_to_start_button = tk.Button(
            self.positions_frame,
            text="Move to start",
            command=self.move_to_start_position,
            width=button_width,
            height=button_height)
        self.move_to_start_button.grid(row=2, column=0, padx=10, pady=10)
        # move back:
        self.move_back_button = tk.Button(
            self.positions_frame,
            text="Move back",
            command=self.move_back_one_position,
            width=button_width,
            height=button_height)
        self.move_back_button.grid(row=3, column=0, padx=10, pady=10)
        # current position:
        self.current_position_spinbox = tkcw.CheckboxSliderSpinbox(
            self.positions_frame,
            label='Current position',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=0,
            max_value=1e6,
            default_value=0,
            row=4,
            width=spinbox_width)
        self.current_position_spinbox.spinbox.config(state='disabled')
        # go forwards:
        self.move_forward_button = tk.Button(
            self.positions_frame,
            text="Move forward",
            command=self.move_forward_one_position,
            width=button_width,
            height=button_height)
        self.move_forward_button.grid(row=5, column=0, padx=10, pady=10)
        # move to end:
        self.move_to_end_button = tk.Button(
            self.positions_frame,
            text="Move to end",
            command=self.move_to_end_position,
            width=button_width,
            height=button_height)
        self.move_to_end_button.grid(row=6, column=0, padx=10, pady=10)
        return None

    def move_to_start_position(self):
        self.move_to_start_position = True
        
    def move_back_one_position(self):
        self.move_back_one_position = True
        
    def move_forward_one_position(self):
        self.move_forward_one_position = True

    def move_to_end_position(self):
        self.move_to_end_position = True

    def init_gui_acquire(self):
        self.acquire_frame = tk.LabelFrame(
            self.root, text='ACQUIRE', bd=6)
        self.acquire_frame.grid(
            row=3, column=5, rowspan=2, padx=10, pady=10, sticky='n')
        self.acquire_frame.bind('<Enter>', self.get_tkfocus) # force update
        button_width, button_height = 25, 2
        spinbox_width = 20
        # live mode button:
        self.live_mode_enabled = tk.BooleanVar()
        live_mode_button = tk.Checkbutton(
            self.acquire_frame,
            text='Live mode (On/Off)',
            variable=self.live_mode_enabled,
            command=self.init_live_mode,
            indicatoron=0,
            width=button_width,
            height=button_height)
        live_mode_button.grid(row=0, column=0, padx=10, pady=10)
        # scout mode button:
        self.scout_mode_enabled = tk.BooleanVar()
        scout_mode_button = tk.Checkbutton(
            self.acquire_frame,
            text='Scout mode (On/Off)',
            variable=self.scout_mode_enabled,
            command=self.init_scout_mode,
            indicatoron=0,
            width=button_width,
            height=button_height)
        scout_mode_button.grid(row=1, column=0, padx=10, pady=10)
        # snap volume button:
        snap_volume_button = tk.Button(
            self.acquire_frame,
            text="Snap volume",
            command=self.snap_volume,
            width=button_width,
            height=button_height)
        snap_volume_button.grid(row=2, column=0, padx=10, pady=10)
        # snap and save button:
        snap_volume_and_save_button = tk.Button(
            self.acquire_frame,
            text="Snap volume and save",
            command=self.snap_volume_and_save,
            width=button_width,
            height=button_height)
        snap_volume_and_save_button.grid(row=3, column=0, padx=10, pady=10)
        # run acquire button:
        self.running_acquire = tk.BooleanVar()
        run_acquire_button = tk.Button(
            self.acquire_frame,
            text="Run acquire",
            command=self.init_acquire,
            width=button_width,
            height=button_height)
        run_acquire_button.grid(row=4, column=0, padx=10, pady=10)
        run_acquire_button.bind('<Enter>', self.get_tkfocus)
        # cancel acquire button:
        self.canceled_acquire = tk.BooleanVar()
        cancel_acquire_button = tk.Button(
            self.acquire_frame,
            text="Cancel acquire",
            command=self.cancel_acquire,
            width=button_width,
            height=button_height)
        cancel_acquire_button.grid(row=5, column=0, padx=10, pady=10)
        return None

    def get_tkfocus(self, event):   # event is not used here (.bind)
        self.acquire_frame.focus_set() # take from widgets to force update
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
        emission_filter = self.gui_filter_wheel.current_emission_filter.get()
        illumination_time_us = (
            1000 * self.gui_camera.illumination_time_ms.value
            + self.gui_camera.illumination_time_us.value)
        height_px = self.gui_camera.height_px.value
        width_px  = self.gui_camera.width_px.value
        voxel_aspect_ratio = self.gui_galvo.voxel_aspect_ratio.value
        scan_range_um = self.gui_galvo.scan_range_um.value
        volumes_per_buffer = self.volumes_spinbox.value
        focus_piezo_z_um = self.gui_focus_piezo.position_spinbox.value
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
        if   XY_stage_position_mm[0] == self.XY_stage_x_min: # moving
            self.XY_joystick_active = True
            self.XY_stage_last_move = 'left (-X)'
        elif XY_stage_position_mm[0] == self.XY_stage_x_max: # moving
            self.XY_joystick_active = True
            self.XY_stage_last_move = 'right (+X)'
        elif XY_stage_position_mm[1] == self.XY_stage_y_min: # moving
            self.XY_joystick_active = True
            self.XY_stage_last_move = 'down (-Y)'
        elif XY_stage_position_mm[1] == self.XY_stage_y_max: # moving
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
        total_illumination_time_us = int(file_settings['illumination_time_us'])
        illumination_time_ms = int(total_illumination_time_us / 1000)
        illumination_time_us = (
            total_illumination_time_us - 1000 * illumination_time_ms)
        if illumination_time_us == 0:
            illumination_time_us = 1000
            illumination_time_ms -= 1
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
        if file_settings['delay_s'] == 'None':
            delay_s = None
        else:
            delay_s = int(file_settings['delay_s'])
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
        self.gui_filter_wheel.current_emission_filter.set(emission_filter)
        self.gui_camera.illumination_time_us.update_and_validate(
            illumination_time_us)
        self.gui_camera.illumination_time_ms.update_and_validate(
            illumination_time_ms)
        self.gui_camera.height_px.update_and_validate(height_px)
        self.gui_camera.width_px.update_and_validate(width_px)
        self.gui_galvo.voxel_aspect_ratio.update_and_validate(
            voxel_aspect_ratio)
        self.gui_galvo.scan_range_um.update_and_validate(scan_range_um)
        self.volumes_spinbox.update_and_validate(volumes_per_buffer)
        if delay_s is not None:
            self.delay_spinbox.update_and_validate(delay_s)
        # apply the file settings:
        self.apply_settings(check_XY_stage=False)
        return None

    def load_positions_from_folder(self):
        # get folder from user:
        folder_path = tk.filedialog.askdirectory(
            parent=self.root,
            initialdir=os.getcwd(),
            title='Please choose a previous "gui session" folder')
        # read files and parse positions into lists:
        focus_piezo_file_path = folder_path + '\\focus_piezo_position_list.txt'
        XY_stage_file_path = folder_path + '\\XY_stage_position_list.txt'
        with open(focus_piezo_file_path, 'r') as file:
            focus_piezo_position_list = file.read().splitlines()[1:] # skip 1st
        with open(XY_stage_file_path, 'r') as file:
            XY_stage_position_list = file.read().splitlines()[1:] # skip 1st
        for i, position in enumerate(focus_piezo_position_list):
            focus_piezo_position_list[i] = int(position.strip(','))
        for i, position in enumerate(XY_stage_position_list):
            XY_stage_position_list[i] = [
                float(position.strip('[').strip(']').split(',')[0]),
                float(position.strip('[').split(',')[1].strip(']').lstrip())]
        # reset gui to position zero:
        total_positions = len(focus_piezo_position_list)
        self.total_positions_spinbox.update_and_validate(total_positions)
        self.current_position_spinbox.update_and_validate(0)
        if total_positions != 0:
            self.gui_focus_piezo.position_spinbox.update_and_validate(
                focus_piezo_position_list[0])
            self.gui_xy_stage.update_position(XY_stage_position_list[0])
            self.current_position_spinbox.update_and_validate(1)
        # update attributes:
        self.focus_piezo_position_list = focus_piezo_position_list
        self.XY_stage_position_list = XY_stage_position_list
        # apply the file settings:
        self.apply_settings()
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
        # calculate storage:
        data_gb = 1e-9 * self.scope.bytes_per_data_buffer
        preview_gb = 1e-9 * self.scope.bytes_per_preview_buffer
        total_storage_gb = (data_gb + preview_gb) * (
            self.acquire_number_spinbox.value)
        text = '%0.3f'%total_storage_gb
        self.total_storage_textbox.textbox.delete('1.0', '10.0')
        self.total_storage_textbox.textbox.insert('1.0', text)        
        # calculate time:
        acquire_time_s = (self.scope.buffer_time_s +
                          self.delay_spinbox.value)
        total_time_s = (
            acquire_time_s * self.acquire_number_spinbox.value)
        text = '%0.6f (%0.0f min)'%(total_time_s, (total_time_s / 60))
        self.total_time_textbox.textbox.delete('1.0', '10.0')
        self.total_time_textbox.textbox.insert('1.0', text)
        return None

    def init_auto_update_settings(self):
        self.live_mode_enabled.set(0)
        self.scout_mode_enabled.set(0)
        self.auto_update_settings()

    def auto_update_settings(self):
        if self.auto_update_settings_enabled.get():
            self.apply_settings(check_XY_stage=False)
            self.update_gui_settings_output()
            self.root.after(self.gui_delay_ms, self.auto_update_settings)
        return None

    def loop_snoutfocus(self):
        if not self.running_acquire.get(): self.scope.snoutfocus()
        wait_ms = int(round(5 * 60 * 1e3))
        self.root.after(wait_ms, self.loop_snoutfocus)
        return None

    def snap_volume(self):
        self.apply_settings(single_volume=True)
        self.update_gui_settings_output()
        self.last_acquire_task.join() # don't accumulate acquires
        self.scope.acquire()
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

    def update_position_list(self):
        num_folders   = len(next(os.walk(self.session_folder))[1])
        num_positions = len(self.focus_piezo_position_list)
        if num_folders == (num_positions + 1): # folder has landed on disk
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
        else: # wait for folder
            self.root.after(self.gui_delay_ms, self.update_position_list)
        return None

    def snap_volume_and_save(self):
        self.apply_settings(single_volume=True)
        self.update_gui_settings_output()
        folder_name = self.get_folder_name() + '_snap'
        self.last_acquire_task.join() # don't accumulate acquires
        self.scope.acquire(filename='snap.tif',
                           folder_name=folder_name,
                           description=self.description_textbox.text)
        self.update_position_list()
        return None

    def init_live_mode(self):
        self.auto_update_settings_enabled.set(0)
        self.scout_mode_enabled.set(0)
        self.apply_settings(single_volume=True)
        self.update_gui_settings_output()
        self.run_live_mode()
        return None

    def run_live_mode(self):
        if self.live_mode_enabled.get():
            self.apply_settings(single_volume=True, check_XY_stage=False)
            self.last_acquire_task.join() # don't accumulate acquires
            self.last_acquire_task = self.scope.acquire()
            self.root.after(self.gui_delay_ms, self.run_live_mode)
        return None

    def enable_XYZ_navigation_buttons(self, enable): # pass True or False
        state = 'normal'
        if not enable: state = 'disabled'
        # focus:
        for child in self.gui_focus_piezo.position_spinbox.winfo_children():
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
        self.auto_update_settings_enabled.set(0)
        self.live_mode_enabled.set(0)
        self.enable_XYZ_navigation_buttons(True)
        self.apply_settings(single_volume=True)
        self.update_gui_settings_output()        
        if self.scout_mode_enabled.get():
            self.last_acquire_task.join() # don't accumulate acquires
            self.last_acquire_task = self.scope.acquire()
        self.run_scout_mode()
        return None

    def check_XY_buttons(self):
        def update_XY_position(): # only called if button pressed
            self.XY_button_pressed = True
            # toggle buttons back:
            self.gui_xy_stage.move_up    = False
            self.gui_xy_stage.move_down  = False
            self.gui_xy_stage.move_left  = False
            self.gui_xy_stage.move_right = False
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
        # run minimal code for speed:
        self.XY_button_pressed = False
        if self.gui_xy_stage.move_up:
            self.XY_stage_last_move = 'up (+Y)'
            update_XY_position()
        elif self.gui_xy_stage.move_down:
            self.XY_stage_last_move = 'down (-Y)'
            update_XY_position()
        elif self.gui_xy_stage.move_left:
            self.XY_stage_last_move = 'left (-X)'
            update_XY_position()
        elif self.gui_xy_stage.move_right:
            self.XY_stage_last_move = 'right (+X)'
            update_XY_position()
        return None

    def check_position_buttons(self):
        def update_position(go_to): # only called if button pressed
            # toggle buttons back:
            self.move_to_start_position     = False
            self.move_back_one_position     = False
            self.move_forward_one_position  = False
            self.move_to_end_position       = False            
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
            index = new_position - 1
            # get positions:
            focus_piezo_z_um = self.focus_piezo_position_list[index]
            XY_stage_position_mm = self.XY_stage_position_list[index]
            # update gui:
            self.gui_focus_piezo.position_spinbox.update_and_validate(
                focus_piezo_z_um)
            self.gui_xy_stage.update_position(XY_stage_position_mm)
            self.current_position_spinbox.update_and_validate(new_position)
        # run minimal code for speed:
        self.position_button_pressed = False
        if self.move_to_start_position:
            update_position('start')
        elif self.move_back_one_position:
            update_position('back')
        elif self.move_forward_one_position:
            update_position('forward')
        elif self.move_to_end_position:
            update_position('end')
        return None

    def run_scout_mode(self):
        if self.scout_mode_enabled.get():
            def snap():
                self.apply_settings(single_volume=True, check_XY_stage=False)
                self.last_acquire_task.join() # don't accumulate acquires
                self.last_acquire_task = self.scope.acquire()
            # Check Z:
            focus_piezo_z_um = self.gui_focus_piezo.position_spinbox.value
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

    def init_acquire(self):
        print('\nAcquire -> started')
        self.auto_update_settings_enabled.set(0)
        self.live_mode_enabled.set(0)
        self.scout_mode_enabled.set(0)
        self.canceled_acquire.set(0)
        self.running_acquire.set(1)
        self.apply_settings()
        self.update_gui_settings_output()
        self.folder_name = self.get_folder_name() + '_acquire'
        self.description = self.description_textbox.text
        self.delay_s = self.delay_spinbox.value
        self.acquire_number = self.acquire_number_spinbox.value
        self.acquire_count = 0
        self.run_acquire()
        return None

    def run_acquire(self):
        delay_s = self.delay_s
        if self.acquire_count == 0: delay_s = 0 # avoid first delay_s
        self.scope.acquire(filename='%06i.tif'%self.acquire_count,
                           folder_name=self.folder_name,
                           description=self.description,
                           delay_s=delay_s)
        self.update_position_list()
        self.acquire_count += 1
        if (self.acquire_count < self.acquire_number
            and not self.canceled_acquire.get()): # acquire again
                wait_ms = int(round(
                    0.99 * 1e3 * (self.scope.buffer_time_s + delay_s)))
                self.root.after(wait_ms, self.run_acquire) 
        else: # finish up
            self.scope.finish_all_tasks()
            self.running_acquire.set(0)
            print('Acquire -> finished\n')
        return None

    def cancel_acquire(self):
        self.canceled_acquire.set(1)
        print('\n ***Acquire -> canceled*** \n')
        return None

    def close(self):
        if self.init_microscope: self.scope.close()
        self.root.quit()
        return None

if __name__ == '__main__':
    gui_microscope = GuiMicroscope(init_microscope=True)
