# Code adapted from the awesome getting started guide by Raspberry Pi 
# https://projects.raspberrypi.org/en/projects/get-started-pico-w/0
# The program serves a webpage which enables simple monitoring and controlling 
# via WiFi within the local network.
# 
# This is a proof of concept on motor control using the Pico W + Maker Drive.
# Maker Drive provides 5V output which powers up the Pico W via its VSYS pin.


import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine


# Motor control library obtained from 
# https://github.com/CytronTechnologies/MAKER-PI-PICO/tree/main/Example%20Code/MicroPython/Motor%20Driver
from motor_driver import *


# Pico W GPIO2,3,4,5 are connected to Maker Drive M1A,M1B,M2A,M2B.
# Swap the pins depending on your applications.
motor = motor_driver(2,3,4,5)


ssid = 'YOUR_SSID'
password = 'YOUR_PASSWORD'


def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip


def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection


def webpage(temperature, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <p>LED is {state}</p>
            <p>Temperature is {temperature}</p>
            <form action="./motor_on">
            <input type="submit" value="Motor on" />
            </form>
            <form action="./motor_off">
            <input type="submit" value="Motor off" />
            </form>
            </body>
            </html>
            """
    return str(html)


def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            pico_led.on()
            state = 'ON'
        elif request =='/lightoff?':
            pico_led.off()
            state = 'OFF'
        elif request =='/motor_on?':
            motor.speed(50,50)
        elif request =='/motor_off?':
            motor.brake()
        temperature = pico_temp_sensor.temp
        html = webpage(temperature, state)
        client.send(html)
        client.close()


try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()