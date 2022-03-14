# SOLS_microscope
Python control code for the original 'high NA single-objective light-sheet' microscope (SOLS): https://andrewgyork.github.io/high_na_single_objective_lightsheet/
## Quick start:
- (see **'power_sequence'** folder for how to power up the microscope)
- 'sols_microscope.py' contains the 'Microscope' class for running the original SOLS hardware and various 'data processing' methods for **converting raw data into more conventional formats**.
- 'sols_microscope_gui.py' provides a simple graphical user interface for sample and microscope exploration (see https://github.com/amsikking/tkinter for a version with simulated hardware).
- 'sols_microscope_acquisition_template.py' is a good start for users who need more advanced control (beyond the gui).
## Details:
Whilst this exact code is very specific to the hardware (and microscope) of the original SOLS prototype it may serve as a valuable template for a (reasonably minimal) open source microscope control architecture. One of the main advantages of this tool chain is the ability to push hardware (and microscope design) to its limits and extract a level of performance beyond the status quo. In addition when problems do arise (bugs, hardware failure) it's within the power of the builder/designer to fix it, and the 'all Python' environment allows rapid integration of additional features... Hopefully this can serve as an example/inspiration to other builders considering such a project.

## Acknowledgments:
Much of this code was either written with (or inspired by) https://github.com/nhthayer and https://github.com/AndrewGYork
