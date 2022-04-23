from gpiozero import LED


# define GPIO pins for the shift register that sets the RAM data lines, D0-D7
SerialData = LED(21)    #serial data for the shift register, LSB first
RegisterClock = LED(20) #rising edge transfers shift register into the output register
SerialClock = LED(16)   #rising edge clocks SerialData into the shift register
SerialClear = LED(12)   #LOW clears the shift register contents

# define GPIO pins for the counter that sets RAM address lines A0-A11 (good for a 4k RAM)
AddressClear = LED(7)   #HIGH resets the counter to zero
AddressClock = LED(8)   #falling edge clocks the counter

# define GPIO pins for the left side of the dual port RAM (pi400)
# note that the output enable pin is hardwired inactive so data pins are always inputs
RWleft = LED(25)        #read/~write pin;  HIGH=read, LOW=write
CEleft = LED(24)        #chip enable pin;  active LOW

# define GPIO pins for right side of the dual port RAM (console)
CEright = LED(23)       # chip enable pin; active low



def init_interface():
    ''' Sets all signals to their inactive state '''
    # deactivate RAM
    CEleft.on()             # disable Pi side of RAM
    CEright.on()            # disable console side of RAM
    RWleft.on()             # read mode for Pi side
    # address counter inputs
    AddressClock.on()
    AddressClear.off()
    # data register inputs
    SerialClear.on()
    SerialClock.off()
    RegisterClock.off()
    

def output(binary):
    '''outputs list of bytes'''
    init_interface()
    # reset the address counter
    AddressClear.on()
    AddressClear.off()
    # write the list of bytes
    for output_byte in binary:
        # write one byte to shared RAM
        for count in range(8):
            # output bit0 to shift register
            if output_byte&1 ==0: 
                SerialData.off()
            else:
                SerialData.on()  
            SerialClock.on()     # clock it into the shift register
            SerialClock.off()
            output_byte >>= 1    # shift right
        RegisterClock.on()     # transfer byte to output of shift register
        RegisterClock.off()
        CEleft.off()           # enable left side of shared RAM 
        RWleft.off()           # begin write pulse  
        RWleft.on()            # end write pulse (measured 8us)
        CEleft.on()            # disable left side of shared RAM
        AddressClock.off()     # increment address
        AddressClock.on()
    CEright.off()            # enable console side of RAM
