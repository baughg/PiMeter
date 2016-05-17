# PiMeter
Raspberry Pi Power Meter


There a reference design for the INA219 power monitor from TI in the datasheet.

http://www.ti.com/lit/ds/symlink/ina219.pdf

The I2C pull-up resistors values are 1K Ohms. The address lines for the INA219 are both tied to ground via 10k resistors.

The INA219 is connected to the Pi using the I2C bus. A diagram identifying the I2C (SCL, SDA) on the Pi can be found here:

http://mtherkildsen.dk/post/the-sunpi/

Enable I2C on the Raspberry Pi.

`sudo raspi-config`

Install I2C tools.

`sudo apt-get update`
`sudo apt-get install -y python-smbus i2c-tools`

Check if the Pi can communicate with the INA219

`sudo i2cdetect -y 1`


Running power measurement capture on the Pi

`sudo python PM.py -o sample_capture`

This will create a sample_capture.csv file with all the power samples. There is a sample every 10mS.