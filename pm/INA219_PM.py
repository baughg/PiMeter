#!/usr/bin/python

import time
import math
from Adafruit_I2C import Adafruit_I2C

# ============================================================================
# Adafruit PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class INA219 :
  i2c = None


  #I2C ADDRESS/BITS
  INA219_ADDRESS                         =  0x40    # 1000000 (A0+A1=GND)
  INA219_READ                            =  0x01

  #CONFIG REGISTER (R/W)  
  INA219_REG_CONFIG                      =  0x00
  INA219_CONFIG_RESET                    =  0x8000  # Reset Bit
  
  INA219_CONFIG_BVOLTAGERANGE_MASK       =  0x2000  # Bus Voltage Range Mask
  INA219_CONFIG_BVOLTAGERANGE_16V        =  0x0000  # 0-16V Range
  INA219_CONFIG_BVOLTAGERANGE_32V        =  0x2000  # 0-32V Range
  
  INA219_CONFIG_GAIN_MASK                =  0x1800  # Gain Mask
  INA219_CONFIG_GAIN_1_40MV              =  0x0000  # Gain 1, 40mV Range
  INA219_CONFIG_GAIN_2_80MV              =  0x0800  # Gain 2, 80mV Range
  INA219_CONFIG_GAIN_4_160MV             =  0x1000  # Gain 4, 160mV Range
  INA219_CONFIG_GAIN_8_320MV             =  0x1800  # Gain 8, 320mV Range
  
  INA219_CONFIG_BADCRES_MASK             =  0x0780  # Bus ADC Resolution Mask
  INA219_CONFIG_BADCRES_9BIT             =  0x8000  # 9-bit bus res = 0..511
  INA219_CONFIG_BADCRES_10BIT            =  0x0100  # 10-bit bus res = 0..1023
  INA219_CONFIG_BADCRES_11BIT            =  0x0200  # 11-bit bus res = 0..2047
  INA219_CONFIG_BADCRES_12BIT            =  0x0400  # 12-bit bus res = 0..4097
    
  INA219_CONFIG_SADCRES_MASK             =  0x0078  # Shunt ADC Resolution and Averaging Mask  
  INA219_CONFIG_SADCRES_9BIT_1S_84US     =  0x0000  # 1 x 9-bit shunt sample
  INA219_CONFIG_SADCRES_10BIT_1S_148US   =  0x0008  # 1 x 10-bit shunt sample
  INA219_CONFIG_SADCRES_11BIT_1S_276US   =  0x0010  # 1 x 11-bit shunt sample
  INA219_CONFIG_SADCRES_12BIT_1S_532US   =  0x0018  # 1 x 12-bit shunt sample
  INA219_CONFIG_SADCRES_12BIT_2S_1060US  =  0x0048  # 2 x 12-bit shunt samples averaged together
  INA219_CONFIG_SADCRES_12BIT_4S_2130US  =  0x0050  # 4 x 12-bit shunt samples averaged together
  INA219_CONFIG_SADCRES_12BIT_8S_4260US  =  0x0058  # 8 x 12-bit shunt samples averaged together
  INA219_CONFIG_SADCRES_12BIT_16S_8510US =  0x0060  # 16 x 12-bit shunt samples averaged together
  INA219_CONFIG_SADCRES_12BIT_32S_17MS   =  0x0068  # 32 x 12-bit shunt samples averaged together
  INA219_CONFIG_SADCRES_12BIT_64S_34MS   =  0x0070  # 64 x 12-bit shunt samples averaged together
  INA219_CONFIG_SADCRES_12BIT_128S_69MS  =  0x0078  # 128 x 12-bit shunt samples averaged together
  
  INA219_CONFIG_MODE_MASK                =  0x0007  # Operating Mode Mask
  INA219_CONFIG_MODE_POWERDOWN           =  0x0000
  INA219_CONFIG_MODE_SVOLT_TRIGGERED     =  0x0001
  INA219_CONFIG_MODE_BVOLT_TRIGGERED     =  0x0002
  INA219_CONFIG_MODE_SANDBVOLT_TRIGGERED =  0x0003
  INA219_CONFIG_MODE_ADCOFF              =  0x0004
  INA219_CONFIG_MODE_SVOLT_CONTINUOUS    =  0x0005
  INA219_CONFIG_MODE_BVOLT_CONTINUOUS    =  0x0006
  INA219_CONFIG_MODE_SANDBVOLT_CONTINUOUS = 0x0007  

  # SHUNT VOLTAGE REGISTER (R)
  INA219_REG_SHUNTVOLTAGE                =  0x01

  # BUS VOLTAGE REGISTER (R)
  INA219_REG_BUSVOLTAGE                  =  0x02

  # POWER REGISTER (R)
  INA219_REG_POWER                       =  0x03

  # CURRENT REGISTER (R)  
  INA219_REG_CURRENT                     =  0x04

  # CALIBRATION REGISTER (R/W)
  INA219_REG_CALIBRATION                 =  0x05

  # Convert to big-endian
  def bigEndian(self,value) :
    value_be = ((value & 0xff) << 8) | ((value >> 8) & 0xff)
    return value_be

  # @brief  Gets the raw current value (16-bit signed integer, so +-32767)

  def getCurrent_raw(self) :  
    # Sometimes a sharp load will reset the INA219, which will
    # reset the cal register, meaning CURRENT and POWER will
    # not be available ... avoid this by always setting a cal
    # value even if it's an unfortunate extra step
    #self.i2c.write16(self.INA219_REG_CALIBRATION, self.ina219_calValue)
  
    # Now we can safely read the CURRENT register!    
    value = self.i2c.readU16(self.INA219_REG_CURRENT)
    return value

  # Get the raw power value (16-bit signed integer)
  def getPower_raw(self) :
    #self.i2c.write16(self.INA219_REG_CALIBRATION, self.ina219_calValue)
    value = self.i2c.readU16(self.INA219_REG_POWER)    
    return value


  def getPower_mW(self) :
    value = self.getPower_raw()
    value = float(value)*self.ina219_powerDivider_mW
    return value
  # @brief  Gets the current value in mA, taking into account the
  #         config settings and current LSB

  def getCurrent_mA(self) :
    valueDec = self.getCurrent_raw()     
    valueDec = float(valueDec)
    valueDec /= self.ina219_currentDivider_mA
    return valueDec


  # @brief  Gets the raw shunt voltage (16-bit signed integer, so +-32767)
  def getShuntVoltage_raw(self) :  
    return self.i2c.readU16(self.INA219_REG_SHUNTVOLTAGE)


  # @brief  Gets the shunt voltage in mV (so +-327mV)
  def getShuntVoltage_mV(self) :  
    value = self.getShuntVoltage_raw()
    return value * 0.01;

  # @brief  Gets the raw bus voltage (16-bit signed integer, so +-32767)
  def getBusVoltage_raw(self) :  
    value = self.i2c.readU16(self.INA219_REG_BUSVOLTAGE)

    # Shift to the right 3 to drop CNVR and OVF and multiply by LSB
    return ((value >> 3) * 4)


  # @brief  Gets the bus voltage in volts

  def getBusVoltage_V(self) :
    value = self.getBusVoltage_raw()
    return value * 0.001;


  def __init__(self, debug=False):
    self.i2c = Adafruit_I2C(self.INA219_ADDRESS)
    self.address = self.INA219_ADDRESS
    self.debug = debug
    self.ina219_i2caddr = 0
    self.ina219_calValue = 0
    # The following multipliers are used to convert raw current and power
    # values to mA and mW, taking into account the current config settings
    self.ina219_currentDivider_mA = 1
    self.ina219_powerDivider_mW = 1

    if (self.debug):
      print "Reseting INA219"

    #config = 0x3C1F
    #self.i2c.write16(self.INA219_REG_CONFIG, self.bigEndian(config))
    self.setCalibration_32V_2A()
    
    #self.i2c.write8(self.__MODE1, 0x00)

# @brief  Configures to INA219 to be able to measure up to 32V and 2A
#          of current.  Each unit of current corresponds to 100uA, and
#           each unit of power corresponds to 2mW. Counter overflow
#           occurs at 3.2A.      
# @note   These calculations assume a 0.1 ohm resistor is present

  def setCalibration_32V_2A(self):
    # By default we use a pretty huge range for the input voltage,
    # which probably isn't the most appropriate choice for system
    # that don't use a lot of power.  But all of the calculations
    # are shown below if you want to change the settings.  You will
    # also need to change any relevant register settings, such as
    # setting the VBUS_MAX to 16V instead of 32V, etc.

    # VBUS_MAX = 32V             (Assumes 32V, can also be set to 16V)
    # VSHUNT_MAX = 0.32          (Assumes Gain 8, 320mV, can also be 0.16, 0.08, 0.04)
    # RSHUNT = 0.1               (Resistor value in ohms)
    
    # 1. Determine max possible current
    # MaxPossible_I = VSHUNT_MAX / RSHUNT
    # MaxPossible_I = 3.2A
    
    # 2. Determine max expected current
    # MaxExpected_I = 2.0A
    
    # 3. Calculate possible range of LSBs (Min = 15-bit, Max = 12-bit)
    # MinimumLSB = MaxExpected_I/32767
    # MinimumLSB = 0.000061              (61uA per bit)
    # MaximumLSB = MaxExpected_I/4096
    # MaximumLSB = 0,000488              (488uA per bit)
    
    # 4. Choose an LSB between the min and max values
    #    (Preferrably a roundish number close to MinLSB)
    # CurrentLSB = 0.0001 (100uA per bit)
    
    # 5. Compute the calibration register
    # Cal = trunc (0.04096 / (Current_LSB * RSHUNT))
    # Cal = 4096 (0x1000)
    
    # self.ina219_calValue = 4096
    self.ina219_calValue = 4096
    # 6. Calculate the power LSB
    # PowerLSB = 20 * CurrentLSB
    # PowerLSB = 0.002 (2mW per bit)
    
    # 7. Compute the maximum current and shunt voltage values before overflow
    #
    # Max_Current = Current_LSB * 32767
    # Max_Current = 3.2767A before overflow
    #
    # If Max_Current > Max_Possible_I then
    #    Max_Current_Before_Overflow = MaxPossible_I
    # Else
    #    Max_Current_Before_Overflow = Max_Current
    # End If
    #
    # Max_ShuntVoltage = Max_Current_Before_Overflow * RSHUNT
    # Max_ShuntVoltage = 0.32V
    #
    # If Max_ShuntVoltage >= VSHUNT_MAX
    #    Max_ShuntVoltage_Before_Overflow = VSHUNT_MAX
    # Else
    #    Max_ShuntVoltage_Before_Overflow = Max_ShuntVoltage
    # End If
    
    # 8. Compute the Maximum Power
    # MaximumPower = Max_Current_Before_Overflow * VBUS_MAX
    # MaximumPower = 3.2 * 32V
    # MaximumPower = 102.4W
    
    # Set multipliers to convert raw current/power values
    self.ina219_currentDivider_mA = 10.4845  # Current LSB = 100uA per bit (1000/100 = 10)
    self.ina219_powerDivider_mW = 2.0     # Power LSB = 1mW per bit (2/1)

    # Set Calibration register to 'Cal' calculated above     
    self.i2c.write16(self.INA219_REG_CALIBRATION, self.bigEndian(self.ina219_calValue))
    # Set Config register to take into account the settings above
    config = self.INA219_CONFIG_BVOLTAGERANGE_32V | self.INA219_CONFIG_GAIN_8_320MV | self.INA219_CONFIG_BADCRES_12BIT | self.INA219_CONFIG_SADCRES_12BIT_1S_532US | self.INA219_CONFIG_MODE_SANDBVOLT_CONTINUOUS
    
    self.i2c.write16(self.INA219_REG_CONFIG, self.bigEndian(config))
    time.sleep(0.1)




 




