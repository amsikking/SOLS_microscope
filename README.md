# SOLS_microscope
Python control code for the original 'high NA single-objective light-sheet' (SOLS) microscope.
## Key features:
A fast, gentle, 3D fluorescence microscope using the single-objective light-sheet ([SOLS](https://andrewgyork.github.io/high_na_single_objective_lightsheet/)) architecture and an [AMS-AGY v1.0 objective](https://andrewgyork.github.io/high_na_single_objective_lightsheet/appendix.html#AMS-AGY_v1.0) (a.k.a Snouty).
- **Primary objective**: 100x silicone oil immersion (with correction collar).
- **XYZ field of view**: ~100x100x30um.
- **Light-sheet**: Gaussian with cylindrical lens, manual adjustment.
- **Excitation**: fast lasers at 405, 488, 561 and 640 (nm).
- **Emission**: fast filter wheel with ET450/50M, ET525/50M, ET600/50M, ET690/50M, ZET405/488/561/640, LP02-488RU and LP02-561RU filters.
- **Course/fine focus**: manual z stage and fast piezo.
- **XY stage**: fast piezo walking.
- **Scanning**: fast galvo.
- **Autofocus**: software based.
- **Incubation**: stage top temperature and CO2 can be used.
- **Control**: basic GUI and open source API in Python.

![social_preview](https://github.com/amsikking/SOLS_microscope/blob/main/social_preview.png)

## Quick start:
- See the '**power_sequence**' folder for how to power up the microscope.
- Run '**sols_microscope_gui.py**' for a basic GUI to explore samples and microscope settings.
- For more advanced control modify and run '**sols_microscope_acquisition_template.py**'.
- For **GUI based data visualization** see: https://github.com/aelefebv/snouty-viewer.
- For a script based data processing example see: https://github.com/amsikking/SOLS_microscope_data_processing.

## Details:
Whilst this exact code is very specific to the hardware (and microscope) of the original SOLS prototype it may serve as a valuable template for a (reasonably minimal) open source microscope control architecture. One of the main advantages of this tool chain is the ability to push hardware (and microscope design) to its limits and extract a level of performance beyond the status quo. In addition when problems do arise (bugs, hardware failure) it's within the power of the builder/designer to fix it, and the 'all Python' environment allows rapid integration of additional features... Hopefully this can serve as an example/inspiration to other builders considering such a project.

## Acknowledgments:
Much of this code was either written with (or inspired by) https://github.com/nhthayer and https://github.com/AndrewGYork
