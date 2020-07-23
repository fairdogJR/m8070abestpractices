#!/usr/bin/env python
# coding: utf-8

# this example demonstrates the newer short hand method of loading a basic generator/ analyzer state
# for the M8070B instead of using the xml method.
# July 15, 2020 tim_fairfield@keysight.com
# July 17 added polling versus blocking wait code for instrument setup waits

# # Short form for setting non-sequence patterns

# ---------First, connect to the Instrument and do a sanity check with *IDN? query

import visa
import time

counter=0

def progress_bar():
    global counter
    time.sleep(.01)
    counter+=1
    print( "*", end='')
    if counter>=18 :
        print('\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b', end='')
        counter=0



rm = visa.ResourceManager()

print("------Initialization and some setup")
M8070B = rm.open_resource('TCPIP0::M8040A-DEMPC43::hislip0::INSTR')
M8070B.timeout = 60000

idn = M8070B.query('*IDN?')
print(idn)

# Turn off output brfore changing state or it wont change
M8070B.write(":OUTPut:STATe 'M1.DataOut1',0")
# turn on outputs ac coupled
M8070B.write(":OUTPut:COUPling 'M1.DataOut1',AC")
# turn on Amp output
M8070B.write(":OUTPut:STATe 'M1.DataOut1',1")
# turn on globals
M8070B.write(":OUTP:GLOB 'M1.System', on")



# # Using Short hand method of changing Analyzer PRBS Pattern
print("------Using the Short hand method of changing the Analyzer/Generator Patterns")
analyzer_pattern = M8070B.query(':DATA:SEQ:SET? "Analyzer" ')
print(analyzer_pattern)

M8070B.write(':DATA:SEQ:SET "Analyzer",PRBS,"2^9-1"')
analyzer_pattern = M8070B.query(':DATA:SEQ:SET? "Analyzer" ')
print(analyzer_pattern)

# ----------Using Short hand method of changing Generator PRBS Pattern
generator_pattern = M8070B.query(':DATA:SEQ:SET? "Generator" ')
print(generator_pattern)

M8070B.write(':DATA:SEQ:SET "Generator",PRBS,"2^9-1"')
generator_pattern = M8070B.query(':DATA:SEQ:SET? "Generator" ')
print(generator_pattern)

# shorthand method of loading a memory(file) based pattern

M8070B.write(':DATA:SEQ:SET "Generator",MEMORY,"factory:CEI/CEIstress_bit"')
generator_pattern = M8070B.query(':DATA:SEQ:SET? "Generator" ')
print(generator_pattern)

M8070B.write(':DATA:SEQ:SET "Analyzer",MEMORY,"factory:CEI/CEIstress_bit"')
analyzer_pattern = M8070B.query(':DATA:SEQ:SET? "Analyzer" ')
print(analyzer_pattern)

# # Line Encoding Setting

# Line encoding test
# This next line will not work and will generate warning on the M8070A sw and not set the value
# The two Generators need to be set to the same encoding

# You will need to set both in a compound SCPI statement in one write call
# You simply add the second statement in the "" seperated by ;
# also do not forget to set the analyzer if you are using it . This does not have to be in the same compound line however

print("Line Encoding, set both Generators to be the same output")
M8070B.write(":DATA:LIN:VALue 'M1.DataOut1', NRZ ; :DATA:LINecoding:VALue 'M1.DataOut2',NRZ")
val = M8070B.query(":DATA:LIN:Value? 'M1.DataOut1'")
print(val)

coding = "PAM4"
M8070B.write(":DATA:LIN:VALue 'M1.DataOut1'," + coding + " ; :DATA:LINecoding:VALue 'M1.DataOut2'," + coding)
val = M8070B.query(":DATA:LIN:Value? 'M1.DataOut1'")
print(val)




# # Waiting until Pattern Gens are loaded and ready Blocking method
# *OPC? is not the recommended way with processes that take a long time
# the RUN:WAIT? Query is the way to go.
#
#     This query waits until the addressed channel is in running state.
#     • The VISA timeout must be set to at least the timeout value that is
# used for :STAT:INST:RUN:WAIT?
#     • *OPC? does not wait until the individual channels are running, since
# this cannot be ensured for channels that are clocked by externally
# provided signals, or for error detector channels that operate on a
# recovered clock signal.
#
# You should generally use this as a compound statement.
#
# Syntax :STATus:INSTrument:RUN:WAIT? 'identifier'[,timeout]
# The VISA timeout must be set to at least the timeout value that is
# used for :STAT:INST:RUN:WAIT?

# this command for visa timeout be set at the top of the main
#M8070B.timeout = 60000

print ("------Using Run:Wait? blocking method for Bert ready")
print ('Setting 16Gig  clock checking with STAT:INST:RUN:WAIT?')
M8070B.write(":SOUR:FREQ 'M1.ClkGen',16e9")

valstr = M8070B.query("STAT:INST:RUN:WAIT? 'M1.DataOut1';:STAT:INST:RUN:WAIT? 'M1.DataOut2';:STAT:INST:RUN:WAIT? 'M2.DataIn'")
print (valstr)


print ('Setting 17Gig  clock checking with STAT:INST:RUN:WAIT?')
M8070B.write(":SOUR:FREQ 'M1.ClkGen',17e9")
valstr = M8070B.query("STAT:INST:RUN:WAIT? 'M1.DataOut1';:STAT:INST:RUN:WAIT? 'M1.DataOut2';:STAT:INST:RUN:WAIT? 'M2.DataIn'")
print (valstr)

print ('Setting 29Gig clock checking with STAT:INST:RUN:WAIT?')
M8070B.write(":SOUR:FREQ 'M1.ClkGen',29e9")
valstr = M8070B.query("STAT:INST:RUN:WAIT? 'M1.DataOut1';:STAT:INST:RUN:WAIT? 'M1.DataOut2';:STAT:INST:RUN:WAIT? 'M2.DataIn'")
print (valstr)


# # #######Waiting until Pattern Gens are ready polling method
print ("-----Using Run:? polling method for Bert ready")
print ('Setting 16Gig  clock, checking with STAT:INST:RUN? ')
M8070B.write(":SOUR:FREQ 'M1.ClkGen',16e9")

print("Checking ED status first")
valstr = M8070B.query("STAT:INST:RUN:WAIT? 'M2.DataIn'")
print (valstr)

val = 0
while (val == 0):

    valstr = M8070B.query("STAT:INST:RUN? 'M1.DataOut1';:STAT:INST:RUN? 'M1.DataOut2'")
    val = int(valstr[0])
    #print ("polling, val="+str(val))
    progress_bar()
print(val)

print ('Setting 17Gig  clock, checking with STAT:INST:RUN? ')
M8070B.write(":SOUR:FREQ 'M1.ClkGen',17e9")
val = 0
while (val == 0):

    valstr = M8070B.query("STAT:INST:RUN? 'M1.DataOut1';:STAT:INST:RUN? 'M1.DataOut2'")
    val = int(valstr[0])
    # print ("polling, val="+str(val))
    progress_bar()
print(val)

print ('Setting 29Gig  clock, checking with STAT:INST:RUN? ')
M8070B.write(":SOUR:FREQ 'M1.ClkGen',29e9")

val = 0
while (val == 0):

    valstr = M8070B.query("STAT:INST:RUN? 'M1.DataOut1';:STAT:INST:RUN? 'M1.DataOut2'")
    val = int(valstr[0])
    # print ("polling, val="+str(val))
    progress_bar()
print(val)

print ("Finished!")
M8070B.close()
rm.close()



