import os
from datetime import datetime
import tkinter as tk

import sols_microscope as sols
import tkinter_compound_widgets as tkcw

class GuiTransmittedLight:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='TRANSMITTED LIGHT', bd=6)
        frame.grid(row=0, column=0, padx=20, pady=20, sticky='n')
        self.power = tkcw.CheckboxSliderSpinbox(
            frame,
            label='470-850nm (%)',
            checkbox_default=True,
            slider_length=200,
            default_value=25)

class GuiLaserBox:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='LASER BOX', bd=6)
        frame.grid(row=1, column=0, padx=20, pady=20, sticky='n')
        self.power405 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='405nm (%)',
            color='magenta',
            slider_length=200,
            default_value=5)
        self.power488 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='488nm (%)',
            color='blue',
            slider_length=200,
            default_value=5,
            row=1)
        self.power561 = tkcw.CheckboxSliderSpinbox(
            frame,
            label='561nm (%)',
            color='green',
            slider_length=200,
            default_value=5,
            row=2)
        self.power640 = tkcw.CheckboxSliderSpinbox(
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
        self.filter = tkcw.RadioButtons(
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
        self.scan_range_um = tkcw.CheckboxSliderSpinbox(
            frame,
            label='~scan range (um)',
            checkbox_enabled=False,
            slider_length=350,
            tickinterval=10,
            min_value=1,
            max_value=100,
            default_value=50)
        self.voxel_aspect_ratio = tkcw.CheckboxSliderSpinbox(
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
        self.illumination_time_ms = tkcw.CheckboxSliderSpinbox(
            frame,
            label='illumination time (ms)',
            checkbox_enabled=False,
            slider_length=350,
            tickinterval=10,
            min_value=1,
            max_value=250,
            default_value=1,
            columnspan=2)
        self.height_px = tkcw.CheckboxSliderSpinbox(
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
        self.width_px = tkcw.CheckboxSliderSpinbox(
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
        tkcw.CanvasRectangleSliderTrace2D(
            frame, self.width_px, self.height_px, row=1, column=1)

class GuiFocusPiezo:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='FOCUS PIEZO', bd=6)
        frame.grid(row=0, column=3, rowspan=2, padx=20, pady=20, sticky='n')
        self.min_value = 0
        self.max_value = 100
        self.center_value = int(round((self.max_value - self.min_value) / 2))
        self.position_um = tkcw.CheckboxSliderSpinbox(
            frame,
            label='position (um)',
            orient='vertical',
            checkbox_enabled=False,
            tickinterval=10,
            min_value=self.min_value,
            max_value=self.max_value)
        button_width, button_height = 10, 2
        # up button:
        self.button_up = tk.Button(
            frame,
            text="up (5um)",
            command=self.move_up,
            width=button_width,
            height=button_height)
        self.button_up.grid(row=0, column=1, padx=10, pady=10, sticky='n')
        # center button:
        self.button_center = tk.Button(
            frame,
            text="center",
            command=self.move_center,
            width=button_width,
            height=button_height)
        self.button_center.grid(row=0, column=1, padx=10, pady=10)
        # down button:
        self.button_down = tk.Button(
            frame,
            text="down (5um)",
            command=self.move_down,
            width=button_width,
            height=button_height)
        self.button_down.grid(row=0, column=1, padx=10, pady=10, sticky='s')

    def move_up(self):
        up_value = self.position_um.spinbox_value - 5
        if self.min_value <= up_value <= self.max_value:
            self.update_position_value(up_value)
        return None

    def move_center(self):
        self.update_position_value(self.center_value)
        return None

    def move_down(self):
        down_value = self.position_um.spinbox_value + 5
        if self.min_value <= down_value <= self.max_value:
            self.update_position_value(down_value)
        return None

    def update_position_value(self, position_um):
        self.position_um.tk_spinbox_value.set(position_um)
        self.position_um.tk_slider_value.set(position_um)
        self.position_um.spinbox_value = position_um
        return None

class GuiXYStage:
    def __init__(self, master):
        frame = tk.LabelFrame(master, text='XY STAGE', bd=6)
        frame.grid(row=1, column=3, padx=20, pady=20, sticky='s')
        # last move textbox:
        self.last_move = tkcw.Textbox(
            frame,
            label='last move',
            default_text='None',
            height=1,
            width=15)
        self.last_move.grid(row=0, column=1, padx=10, pady=10)
        # position textbox:
        self.position = tkcw.Textbox(
            frame,
            label='position (mm)',
            height=1,
            width=20)
        self.position.grid(row=2, column=1, padx=10, pady=10)
        self.position_mm = None
        
        button_width, button_height = 10, 2
        # up button:
        self.button_up = tk.Button(
            frame,
            text="up",
            command=self.move_up,
            width=button_width,
            height=button_height)
        self.button_up.grid(row=1, column=1, padx=10, pady=10)
        self.move_up = False
        # down button:
        self.button_down = tk.Button(
            frame,
            text="down",
            command=self.move_down,
            width=button_width,
            height=button_height)
        self.button_down.grid(row=3, column=1, padx=10, pady=10)
        self.move_down = False
        # left button:
        self.button_left = tk.Button(
            frame,
            text="left",
            command=self.move_left,
            width=button_width,
            height=button_height)
        self.button_left.grid(row=2, column=0, padx=10, pady=10)
        self.move_left = False
        # right button:
        self.button_right = tk.Button(
            frame,
            text="right",
            command=self.move_right,
            width=button_width,
            height=button_height)
        self.button_right.grid(row=2, column=3, padx=10, pady=10)
        self.move_right = False
        
        # move size:
        self.step_size_pct = tkcw.CheckboxSliderSpinbox(
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
        return None

    def update_position(self, position_mm):
        self.position.textbox.delete('1.0', '10.0')
        self.position.textbox.insert(
            '1.0', 'X=%0.3f, Y=%0.3f'%(position_mm[0], position_mm[1]))
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
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('SOLS Microscope GUI')
        self.gui_delay_ms = int(1e3 * 1 / 30) # 30fps/video rate target
        # load nested GUI's for each element:
        self.gui_transmitted_light  = GuiTransmittedLight(self.root)
        self.gui_laser_box          = GuiLaserBox(self.root)
        self.gui_filter_wheel       = GuiFilterWheel(self.root)
        self.gui_galvo              = GuiGalvo(self.root)
        self.gui_camera             = GuiCamera(self.root)
        self.gui_focus_piezo        = GuiFocusPiezo(self.root)
        self.gui_xy_stage           = GuiXYStage(self.root)
        # load acquisition GUI with microscope methods:
        self.init_gui_acquisition()
        # add the quit button:
        quit_gui_button = tk.Button(
            self.root, text="QUIT GUI", command=self.close, height=5, width=30)
        quit_gui_button.grid(row=3, column=2, padx=20, pady=20, sticky='n')
        # get settings from gui:
        gui_settings = self.get_gui_settings()
        # init the microscope:
        self.scope = sols.Microscope(max_allocated_bytes=100e9, ao_rate=1e4)
        # configure any hardware preferences:
        self.scope.XY_stage.set_velocity(5, 5)
        # apply settings to microscope (avoiding motion):
        self.scope.apply_settings( # mandatory call
            channels_per_slice      = gui_settings['channels_per_slice'],
            power_per_channel       = gui_settings['power_per_channel'],
            filter_wheel_position   = gui_settings['filter_wheel_position'],
            illumination_time_us    = gui_settings['illumination_time_us'],
            height_px               = gui_settings['height_px'],
            width_px                = gui_settings['width_px'],
            voxel_aspect_ratio      = gui_settings['voxel_aspect_ratio'],
            scan_range_um           = gui_settings['scan_range_um'],
            volumes_per_buffer      = gui_settings['volumes_per_buffer'],
            focus_piezo_z_um        = (0, 'relative'),      # = don't move
            XY_stage_position_mm    = (0, 0, 'relative')    # = don't move
            ).join() # finish before accessing .scope attributes
        # init settings attributes and match XYZ to hardware:
        self.settings = {}
        for k,v in list(gui_settings.items())[:-2]: # avoid XYZ
            self.settings[k] = v # a lot like self.x = x
        self.settings['focus_piezo_z_um'] = int(round(
            self.scope.focus_piezo_z_um))
        self.settings['XY_stage_position_mm'] = (
            self.scope.XY_stage_position_mm)
        # match GUI to XYZ:
        self.gui_focus_piezo.update_position_value(
            self.settings['focus_piezo_z_um'])
        self.gui_xy_stage.update_position(
            self.settings['XY_stage_position_mm'])
        # get XY stage limits for feedback in scout mode:
        self.XY_stage_x_min = self.scope.XY_stage.x_min
        self.XY_stage_y_min = self.scope.XY_stage.y_min
        self.XY_stage_x_max = self.scope.XY_stage.x_max
        self.XY_stage_y_max = self.scope.XY_stage.y_max
        # get scope ready:
        self.loop_snoutfocus()
        self.scope.acquire() # snap a volume
        # start event loop:
        self.root.mainloop() # blocks here until 'QUIT'
        self.root.destroy()

    def init_gui_acquisition(self):
        self.aquisition_frame = tk.LabelFrame(
            self.root, text='ACQUISITION', bd=6)
        self.aquisition_frame.grid(
            row=0, column=4, rowspan=2, padx=20, pady=20, sticky='n')
        self.aquisition_frame.bind('<Enter>', self.get_tkfocus) # force update
        button_width, button_height = 25, 2
        spinbox_width = 20
        # live mode button:
        self.live_mode_enabled = tk.BooleanVar()
        live_mode_button = tk.Checkbutton(
            self.aquisition_frame,
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
            self.aquisition_frame,
            text='Scout mode (On/Off)',
            variable=self.scout_mode_enabled,
            command=self.init_scout_mode,
            indicatoron=0,
            width=button_width,
            height=button_height)
        scout_mode_button.grid(row=1, column=0, padx=10, pady=10)
        # snap volume button:
        snap_volume_button = tk.Button(
            self.aquisition_frame,
            text="Snap volume",
            command=self.snap_volume,
            width=button_width,
            height=button_height)
        snap_volume_button.grid(row=2, column=0, padx=10, pady=10)
        # snap and save button:
        snap_volume_and_save_button = tk.Button(
            self.aquisition_frame,
            text="Snap volume and save",
            command=self.snap_volume_and_save,
            width=button_width,
            height=button_height)
        snap_volume_and_save_button.grid(row=3, column=0, padx=10, pady=10)
        # volumes spinbox:
        self.volumes_spinbox = tkcw.CheckboxSliderSpinbox(
            self.aquisition_frame,
            label='Volumes per acquisition',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=1e3,
            default_value=1,
            row=4,
            width=spinbox_width)
        # acquisitions spinbox:
        self.acquisitions_spinbox = tkcw.CheckboxSliderSpinbox(
            self.aquisition_frame,
            label='Acquisition number',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=1,
            max_value=1e6,
            default_value=1,
            row=5,
            width=spinbox_width)
        # delay spinbox:
        self.delay_spinbox = tkcw.CheckboxSliderSpinbox(
            self.aquisition_frame,
            label='Inter-acquisition delay (s)',
            checkbox_enabled=False,
            slider_enabled=False,
            min_value=0,
            max_value=3600,
            default_value=0,
            row=6,
            width=spinbox_width)
        # print memory and time button:
        print_memory_and_time_button = tk.Button(
            self.aquisition_frame,
            text="Print memory and time",
            command=self.apply_settings,
            width=button_width,
            height=button_height)
        print_memory_and_time_button.grid(row=7, column=0, padx=10, pady=10)
        print_memory_and_time_button.bind('<Enter>', self.get_tkfocus)
        # label textbox:
        self.label_textbox = tkcw.Textbox(
            self.aquisition_frame,
            label='Folder label',
            default_text='sols_gui',
            row=8,
            width=spinbox_width)
        # description textbox:
        self.description_textbox = tkcw.Textbox(
            self.aquisition_frame,
            label='Description',
            default_text='what are you doing?',
            row=9,
            width=spinbox_width)
        # run aquisition button:
        self.running_aquisition = tk.BooleanVar()
        run_aquisition_button = tk.Button(
            self.aquisition_frame,
            text="Run aquisition",
            command=self.init_acquisition,
            width=button_width,
            height=button_height)
        run_aquisition_button.grid(row=10, column=0, padx=10, pady=10)
        run_aquisition_button.bind('<Enter>', self.get_tkfocus)
        # cancel aquisition button:
        self.cancel_aquisition = tk.BooleanVar()
        cancel_aquisition_button = tk.Button(
            self.aquisition_frame,
            text="Cancel aquisition",
            command=self.cancel_acquisition,
            width=button_width,
            height=button_height)
        cancel_aquisition_button.grid(row=11, column=0, padx=10, pady=10)
        return None

    def get_tkfocus(self, event):   # event is not used here (.bind)
        self.aquisition_frame.focus_set() # take from widgets to force update
        return None

    def get_gui_settings(self):
        # collect settings from gui and re-format for '.scope.apply_settings'
        channels_per_slice, power_per_channel = [], []
        if self.gui_transmitted_light.power.checkbox_value:
            channels_per_slice.append('LED')
            power_per_channel.append(
                self.gui_transmitted_light.power.spinbox_value)
        if self.gui_laser_box.power405.checkbox_value:
            channels_per_slice.append('405')
            power_per_channel.append(
                self.gui_laser_box.power405.spinbox_value)
        if self.gui_laser_box.power488.checkbox_value:
            channels_per_slice.append('488')
            power_per_channel.append(
                self.gui_laser_box.power488.spinbox_value)
        if self.gui_laser_box.power561.checkbox_value:
            channels_per_slice.append('561')
            power_per_channel.append(
                self.gui_laser_box.power561.spinbox_value)
        if self.gui_laser_box.power640.checkbox_value:
            channels_per_slice.append('640')
            power_per_channel.append(
                self.gui_laser_box.power640.spinbox_value)
        if len(channels_per_slice) == 0: # default TL if nothing selected
            self.gui_transmitted_light.power.tk_checkbox_value.set(1)
            channels_per_slice = ('LED',)
            power_per_channel = (
                self.gui_transmitted_light.power.spinbox_value,)
        filter_wheel_position = self.gui_filter_wheel.filter.position
        illumination_time_us = (
            1000 * self.gui_camera.illumination_time_ms.spinbox_value)
        height_px = self.gui_camera.height_px.spinbox_value
        width_px  = self.gui_camera.width_px.spinbox_value
        voxel_aspect_ratio = self.gui_galvo.voxel_aspect_ratio.spinbox_value
        scan_range_um = self.gui_galvo.scan_range_um.spinbox_value
        volumes_per_buffer = self.volumes_spinbox.spinbox_value
        focus_piezo_z_um = self.gui_focus_piezo.position_um.spinbox_value
        XY_stage_position_mm = self.gui_xy_stage.position_mm
        gui_settings = {'channels_per_slice'    :channels_per_slice,
                        'power_per_channel'     :power_per_channel,
                        'filter_wheel_position' :filter_wheel_position,
                        'illumination_time_us'  :illumination_time_us,
                        'height_px'             :height_px,
                        'width_px'              :width_px,
                        'voxel_aspect_ratio'    :voxel_aspect_ratio,
                        'scan_range_um'         :scan_range_um,
                        'volumes_per_buffer'    :volumes_per_buffer,
                        'focus_piezo_z_um'      :focus_piezo_z_um,
                        'XY_stage_position_mm'  :XY_stage_position_mm}
        return gui_settings

    def apply_settings(self, single_volume=False, verbose=True):
        gui = self.get_gui_settings() # short for 'gui_settings'
        new_settings = len(gui)*[None] # pass 'None' if no change
        # check gui settings against applied settings:
        if (self.settings['channels_per_slice'] != gui['channels_per_slice'] or
            self.settings['power_per_channel']  != gui['power_per_channel']):
            new_settings[0] = gui['channels_per_slice']
            new_settings[1] = gui['power_per_channel']
        for i, k in enumerate(list(self.settings.keys())[2:-2]): # -2 avoid XYZ
            if self.settings[k] != gui[k]:
                new_settings[i + 2] = gui[k] # + 2 since we start at setting 2
        if self.settings['focus_piezo_z_um'] != gui['focus_piezo_z_um']:
            new_settings[9] = (gui['focus_piezo_z_um'], 'absolute')
        # no update to XY here (new_settings[10] = None)
        # apply settings:
        if single_volume: new_settings[8] = 1
        self.scope.apply_settings(
            channels_per_slice      = new_settings[0],
            power_per_channel       = new_settings[1],
            filter_wheel_position   = new_settings[2],
            illumination_time_us    = new_settings[3],
            height_px               = new_settings[4],
            width_px                = new_settings[5],
            voxel_aspect_ratio      = new_settings[6],
            scan_range_um           = new_settings[7],
            volumes_per_buffer      = new_settings[8],
            focus_piezo_z_um        = new_settings[9],
            XY_stage_position_mm    = new_settings[10]).join()
        # update settings attributes:
        for k in self.settings.keys():
            self.settings[k] = gui[k]
        # calculate memory:
        total_memory_gb = 1e-9 * self.scope.total_bytes
        max_memory_gb = 1e-9 * self.scope.max_allocated_bytes
        memory_pct = 100 * total_memory_gb / max_memory_gb
        # calculate storage:
        data_gb = 1e-9 * self.scope.bytes_per_data_buffer
        preview_gb = 1e-9 * self.scope.bytes_per_preview_buffer
        total_storage_gb = (
            data_gb + preview_gb) * self.acquisitions_spinbox.spinbox_value
        # calculate time:
        acquire_time_s = (
            self.scope.buffer_time_s + self.delay_spinbox.spinbox_value)
        total_time_s = (
            acquire_time_s * self.acquisitions_spinbox.spinbox_value)
        if verbose:
            print('Total memory needed   (GB) = %0.6f (%0.2f%% of max)'%(
                total_memory_gb, memory_pct))
            print('Total storaged needed (GB) = %0.6f'%total_storage_gb)
            print('Total acquisition time (s) = %0.6f (%0.2f min)'%(
                total_time_s, (total_time_s / 60)))            
            print('Vps ~ %0.6f'%self.scope.volumes_per_s)
        return None

    def loop_snoutfocus(self):
        if not self.running_aquisition.get(): self.scope.snoutfocus()
        wait_ms = int(round(5 * 60 * 1e3))
        self.root.after(wait_ms, self.loop_snoutfocus)
        return None

    def snap_volume(self, verbose=True):
        self.apply_settings(single_volume=True, verbose=verbose)
        self.scope.finish_all_tasks() # don't accumulate acquire tasks
        self.scope.acquire()
        return None

    def get_folder_name(self):
        dt = datetime.strftime(datetime.now(),'%Y-%m-%d_%H-%M-%S_')
        folder_index = 0
        folder_name = dt + '%03i_'%folder_index + self.label_textbox.text
        while os.path.exists(folder_name): # check before overwriting
            folder_index +=1
            folder_name = dt + '%03i_'%folder_index + self.label_textbox.text
        return folder_name

    def snap_volume_and_save(self):
        self.apply_settings(single_volume=True)
        folder_name = self.get_folder_name() + '_snap'
        self.scope.acquire(filename='snap.tif',
                           folder_name=folder_name,
                           description=self.description_textbox.text)
        return None

    def init_live_mode(self):
        self.scout_mode_enabled.set(0)
        self.run_live_mode()
        return None

    def run_live_mode(self):
        if self.live_mode_enabled.get():
            self.snap_volume(verbose=False)
            self.root.after(self.gui_delay_ms, self.run_live_mode)
        return None

    def init_scout_mode(self):
        self.live_mode_enabled.set(0)
        self.run_scout_mode()
        return None

    def run_scout_mode(self):
        if self.scout_mode_enabled.get():
            # Check Z:
            Z = self.gui_focus_piezo.position_um.spinbox_value
            if Z != self.settings['focus_piezo_z_um']:
                self.snap_volume(verbose=False)
            # Check XY:
            def snap_volume_and_update_gui(gui_text): # save lines of code
                self.snap_volume(verbose=False)
                self.gui_xy_stage.update_last_move(gui_text)
            # -> apply GUI move requests:
            move_pct = self.gui_xy_stage.step_size_pct.spinbox_value / 100
            self.scope.apply_settings().join() # update attributes
            scan_width_um = self.scope.width_px * sols.sample_px_um
            ud_move_mm = 1e-3 * self.scope.scan_range_um * move_pct
            lr_move_mm = 1e-3 * scan_width_um * move_pct
            if self.gui_xy_stage.move_up:
                self.scope.apply_settings(
                    XY_stage_position_mm=(0, ud_move_mm, 'relative'))
                snap_volume_and_update_gui('up (+Y)')
                self.gui_xy_stage.move_up = False
            elif self.gui_xy_stage.move_down:
                self.scope.apply_settings(
                    XY_stage_position_mm=(0, -ud_move_mm, 'relative'))
                snap_volume_and_update_gui('down (-Y)')
                self.gui_xy_stage.move_down = False
            elif self.gui_xy_stage.move_left:
                self.scope.apply_settings(
                    XY_stage_position_mm=(-lr_move_mm, 0, 'relative'))
                snap_volume_and_update_gui('left (-X)')
                self.gui_xy_stage.move_left = False
            elif self.gui_xy_stage.move_right:
                self.scope.apply_settings(
                    XY_stage_position_mm=(lr_move_mm, 0, 'relative'))
                snap_volume_and_update_gui('right (+X)')
                self.gui_xy_stage.move_right = False
            # -> check for joystick motion:
            self.scope.apply_settings().join() # update attributes
            X, Y = self.scope.XY_stage_position_mm
            joystick_motion = False
            if   X == self.XY_stage_x_min: # moving
                snap_volume_and_update_gui('left (-X)')
                joystick_motion = True
            elif X == self.XY_stage_x_max: # moving
                snap_volume_and_update_gui('right (+X)')
                joystick_motion = True
            elif Y == self.XY_stage_y_min: # moving
                snap_volume_and_update_gui('down (-Y)')
                joystick_motion = True
            elif Y == self.XY_stage_y_max: # moving
                snap_volume_and_update_gui('up (+Y)')
                joystick_motion = True
            if joystick_motion: # snap again to reduce motion blur
                self.snap_volume(verbose=False)
            else: # update position in gui (avoids erroneous position updates)
                self.gui_xy_stage.update_position((X, Y))
            # update attribute:
            self.settings['XY_stage_position_mm'] = (X, Y)
            self.root.after(self.gui_delay_ms, self.run_scout_mode)
        return None

    def init_acquisition(self):
        print('\nAcquisition -> started')
        if self.live_mode_enabled.get(): self.live_mode_enabled.set(0)
        if self.scout_mode_enabled.get(): self.scout_mode_enabled.set(0)
        self.cancel_aquisition.set(0)
        self.running_aquisition.set(1)
        self.apply_settings()
        self.folder_name = self.get_folder_name()
        self.description = self.description_textbox.text
        self.delay_s = self.delay_spinbox.spinbox_value
        self.acquisitions = self.acquisitions_spinbox.spinbox_value
        self.acquisition_count = 0
        self.run_acquisition()
        return None

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
                self.root.after(wait_ms, self.run_acquisition) 
        else: # finish up
            self.scope.finish_all_tasks()
            self.running_aquisition.set(0)
            print('Acquisition -> finished\n')
        return None

    def cancel_acquisition(self):
        self.cancel_aquisition.set(1)
        print('\n ***Acquisition -> canceled*** \n')
        return None

    def close(self):
        self.scope.close()
        self.root.quit()
        return None

if __name__ == '__main__':
    gui_microscope = GuiMicroscope()
