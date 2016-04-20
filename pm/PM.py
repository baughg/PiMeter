import time
import csv
import argparse
from sys import stdout
from INA219_PM import INA219

ina219 = INA219(True)
ina219.setCalibration_32V_2A()



sample_count = 0.0
sample_period = 0.01

if __name__ == "__main__":
  capture_file = "pipower.csv"
  

  parser = argparse.ArgumentParser(description='PiPower v1.0')
  parser.add_argument(
        '-o',
        '--output',
        help='The name of the csv file with captured data.',
        required=False)
  parser.add_argument(
        '-s',
        '--step',
        help='The sampling period in ms.',
        required=False)

  args = vars(parser.parse_args())

  if args['output'] != None:
    capture_file = args['output']

  if args['step'] != None:
    sample_period = float(args['step'])

  if sample_period <= 0.0 :
    sample_period = 10

  sample_period = sample_period * 0.001

  extension_pos = capture_file.rfind(".csv")

  if extension_pos == -1 :
    capture_file += '.csv'

  csvfile = open(capture_file, 'wb')
  
  sample_writer = csv.writer(csvfile, delimiter=',',quotechar=',', quoting=csv.QUOTE_MINIMAL)
  sample_writer.writerow(['SampleTime /S'] + ['Vss /V'] + ['Iss /mA'] + ['Power /mW'])

  start_time = -1.0
  last_display_time = -1.0

  while(1) :
    V_supply = ina219.getBusVoltage_V()
    I_supply = ina219.getCurrent_mA()
    #power_mW = ina219.getPower_mW()
    power_cal = V_supply*I_supply
    current_time = time.time()

    if start_time < 0.0 :
      start_time = current_time

    sample_time = current_time - start_time

    if V_supply < 0.05 :
      I_supply = 0.0
      power_cal = 0.0

    sample_time_int = round(sample_time)
    if last_display_time != sample_time_int :
      stdout.write("\rVss (V): %.2f    Iss (mA): %.2f    Power (mW): %.2f                 " % (V_supply,I_supply,power_cal)) 
      stdout.flush()
      last_display_time = sample_time_int

    sample_writer.writerow([str(sample_time)] + [str(V_supply)] + [str(I_supply)] + [str(power_cal)]) 
    sample_count += 1.0
    time.sleep(sample_period)

