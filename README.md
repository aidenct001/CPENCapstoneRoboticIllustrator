# CPENCapstoneRoboticIllustrator
Code for a capstone project to make a 3 axis robot draw an image from an image file

# Setup
Install dependencies

    $ sudo apt-get install build-essential python3-dev python3-pip libagg-dev libpotrace-dev pkg-config

Install libraries

    $ pip install numpy
    $ pip install pillow
    $ pip install tkinter
    $ pip install pypotrace
    $ pip install RPi.GPIO

Alternate libraries (pure python but slower)

    $ pip install potracer 

Must run this command for gpiozero

    $ sudo pigpiod