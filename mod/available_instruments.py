"""
Namespace with all available instruments. Can differ from station to station.

An entry must be written as shown below:
name = [list of arguments] 

name is the same that will be used for the instrument as a Lab attribute
[list of arguments] is [module, class, (optional arguments,), {optional key arguments}]

module: name of the module from the instruments package
class: name of the instrument class located in module.
(optional arguments,): has to be a tuple, so don't forget the coma before closing the parenthesis. 
{optional key arguments}: has to be a dictionnary. 

When attributing an instrument to a lab instance, something like this is called: lab.name = mod.instruments.module.class(..., (optional_arguments, ), {optional_key_arguments})

As you add instruments to the program, you need to update this list (and code a new instrument class if needed).

It's possible to connect to a generic VISA instrument with no specific class, more info in Lab.add_instrument() documentation.
"""

## name         ## Module             ## class                ## optional arguments                           ## optional key arguments
awg =         [ "awg",                "Awg_M8190A",           ("PXI13::0::0::INSTR",),                        {}  ]
pb =          [ "pulse_blaster",      "Pulse_blaster_USB",    (),                                             {}  ]
usb_counter = [ "usb_counter",        "Usb_counter_CTR04",    (0,),                                           {}  ]
lockin =      [ "visa_instruments",   "Lockin_5210",          ("GPIB0::12::INSTR",),                          {}  ]
laser =       [ "visa_instruments",   "Laser_ITC4001",        ("USB0::0x1313::0x804A::M00243388::INSTR",),    {}  ]
sig_gen =     [ "visa_instruments",   "Sig_gen_E8257D",       ("GPIB0::19::INSTR",),                          {}  ]
sig_gen_srs = [ "visa_instruments",   "Sig_gen_SRS",          ("GPIB0::3::INSTR",),                           {}  ]
wavemeter =   [ "wavemeter",          "Wavemeter",            (3,),                                           {}  ]
