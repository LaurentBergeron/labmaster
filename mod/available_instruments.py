"""
Namespace with all available instruments. Can differ from station to station.

An entry must be written as shown below:
name = [module, class, (optional arguments,), {optional key arguments}]

where:
    - name is the same that will be used for the instrument as a Lab attribute.
    - module: name of the python module file from the instruments package folder.
    - class: name of the instrument class located in the module file.
    - (optional arguments,): has to be a tuple, so don't forget the coma before closing the parenthesis. 
    - {optional key arguments}: has to be a dictionnary. 

When attributing an instrument to a lab instance, something like this is called: lab.name = mod.instruments.module.class(..., (optional_arguments, ), {optional_key_arguments})

As you add instruments to the program, you need to update this list (and code a new instrument class if needed).

It's possible to connect to a generic VISA instrument with no specific class, more info in Lab.add_instrument() documentation.
"""

## name         ## Module              ## class                  ## optional arguments to the class              ## optional key arguments to the class
awg =         [ "awgs",                "Awg_M8190A",             ("PXI13::0::0::INSTR",),                        {}  ]
dds =         [ "pulse_blasters",      "Pulse_blaster_DDSII300", (),                                             {}  ]
# pb =          [ "pulse_blasters",      "Pulse_blaster_USB",      (),                                             {}  ]
counter =     [ "usb_counters",        "USB_counter_CTR04",      (0,),                                           {}  ]
lockin =      [ "lockins",             "Lockin_5210",            ("GPIB0::4::INSTR",),                           {}  ]
# lockin =      [ "lockins",             "Lockin_SR844",           ("GPIB0::8::INSTR",),                           {}  ]
laserITC =    [ "lasers",              "Laser_ITC4001",          ("USB0::0x1313::0x804A::M00456813::INSTR",),    {}  ]
laserSRS =    [ "lasers",              "Laser_LDC500",           ("GPIB0::2::INSTR",),                           {}  ]
sig_gen =     [ "sig_gens",            "Sig_gen_E8257D",         ("GPIB0::19::INSTR",),                          {}  ]
sig_gen_srs = [ "sig_gens",            "Sig_gen_SRS",            ("GPIB0::3::INSTR",),                           {}  ]
wavemeter =   [ "wavemeters",          "Wavemeter",              (3,),                                           {}  ]
