__signature__ = 0x8740c0656306defbfde1bad09b3bc066
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example helps you to define arbitrary waveforms read out from a file."""

# (c)2016-2020 Physik Instrumente (PI) GmbH & Co. KG
# Software products that are provided by PI are subject to the
# General Software License Agreement of Physik Instrumente (PI) GmbH & Co. KG
# and may incorporate and/or make use of third-party software components.
# For more information, please read the General Software License Agreement
# and the Third Party Software Note linked below.
# General Software License Agreement:
# http://www.physikinstrumente.com/download/EULA_PhysikInstrumenteGmbH_Co_KG.pdf
# Third Party Software Note:
# http://www.physikinstrumente.com/download/TPSWNote_PhysikInstrumenteGmbH_Co_KG.pdf


from time import sleep, time

from pipython import GCSDevice, pitools

CONTROLLERNAME = 'C-413'
STAGES = ['V-524.1AA']  # connect stages to axes
REFMODES = ['FRF']  # reference the connected stages
DATAFILE = r'C:\\Users\\OPT\\Desktop\\waveform.txt'
NUMCYLES = 2  # number of cycles for wave generator output
TABLERATE = 100  # duration of a wave table point in multiples of servo cycle times as integer
AXIS = ['1']
WAVE_GENERATOR_IDS = [1]
WAVE_TABLE_IDS = [1]
TIMEOUT = 300

def main():
    """Connect controller, setup wave generator, move axes to startpoint and start wave generator."""
    with GCSDevice(CONTROLLERNAME) as pidevice:
        pidevice.ConnectUSB(serialnum='0119024343')
        pitools.startup(pidevice, stages=STAGES, refmodes=REFMODES)
        runwavegen(pidevice)

def runwavegen(pidevice):
    """Read wave data, set up wave generator and run them.
    @type pidevice : pipython.gcscommands.GCSCommands
    """
    wavedata = readwavedata()
    axes = pidevice.axes[:len(wavedata)]
    assert len(wavedata) == len(axes), 'this sample requires {} connected axes'.format(len(wavedata))
    if pidevice.HasWCL():  # you can remove this code block if your controller does not support WCL()
        print('clear wave tables {}'.format(WAVE_TABLE_IDS))
        pidevice.WCL(WAVE_TABLE_IDS)
    for wavetable in WAVE_TABLE_IDS:
        for point in wavedata[wavetable-1]:
            pidevice.WAV_PNT(table=wavetable, firstpoint=1, numpoints=1, append='&', wavepoint=point)
    if pidevice.HasWSL():  # you can remove this code block if your controller does not support WSL()
        print('connect wave tables {} to wave generators {}'.format(WAVE_TABLE_IDS, WAVE_GENERATOR_IDS))
        pidevice.WSL(WAVE_GENERATOR_IDS, WAVE_TABLE_IDS)
    if pidevice.HasWGC():  # you can remove this code block if your controller does not support WGC()
        print('set wave generators {} to run for {} cycles'.format(WAVE_GENERATOR_IDS, NUMCYLES))
        pidevice.WGC(WAVE_GENERATOR_IDS, NUMCYLES * len(WAVE_GENERATOR_IDS))
    if pidevice.HasWTR():  # you can remove this code block if your controller does not support WTR()
        print('set wave table rate to {} for wave generators {}'.format(TABLERATE, WAVE_GENERATOR_IDS))
        pidevice.WTR(WAVE_GENERATOR_IDS, TABLERATE * len(WAVE_GENERATOR_IDS), 0 * len(WAVE_GENERATOR_IDS))
    start_position = [wavedata[i][0] for i in range(len(AXIS))]
    print('move axes {} to start positions {}'.format(axes, start_position))
    pidevice.MOV(AXIS, start_position)
    maxtime = time() + TIMEOUT
    while not all(list(pidevice.qONT(AXIS).values())):
        if time() > maxtime:
            raise SystemError('waitontarget() timed out after %.1f seconds' % TIMEOUT)
        sleep(0.1)

    print('start wave generators {}'.format(WAVE_GENERATOR_IDS))
    pidevice.WGO(1, mode=1)
    while any(list(pidevice.IsGeneratorRunning([1]).values())):
        print('.', end='')
        sleep(1.0)
    print('\nreset wave generators {}'.format(WAVE_GENERATOR_IDS))
    pidevice.WGO(1, mode=0)
    print('done')


def readwavedata():
    """Read DATAFILE, must have a column for each wavetable.
    @return : Datapoints as list of lists of values.
    """
    print('read wave points from file {}'.format(DATAFILE))
    data = None
    with open(DATAFILE) as datafile:
        for line in datafile:
            items = line.strip().split()
            if data is None:
                print('found {} data columns in file'.format(len(items)))
                data = [[] for _ in range(len(items))]
            for i, item in enumerate(items):
                data[i].append(item)
    return data


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
