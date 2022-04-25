import tkinter as StreamController
import os
import subprocess
import threading
import paramiko
import sys
import signal
import time
import psutil
from tkinter import *
test = StreamController.Tk() #THIS CONSTRUCTS THE WINDOW OBJECT WHICH CONTROLS THE STREAM
sys.path.append('/home/mitch/NetCatSocketRead.py')
print(sys.path)


def radio():
    # THIS IS THE SERIES OF COMMANDS THAT GENERATE A RADIO STREAM AND THE BUTTONS TO CONTROL IT
    # UPON BUTTON CLICK, GENERATES A TEXT BOX AND WAITS TO GENERATE THE BUTTONS UNTIL THE FILE NAME IS INPUT
    label = StreamController.Label(text="Enter A Radio Filename")
    entry = StreamController.Entry()
    okVar = StreamController.IntVar()
    #CONFIRMATION BUTTON
    button5 = StreamController.Button(test, text="Submit", pady=5, font=("Arial Bold", 10),
                        bg='lightgray', command=lambda: okVar.set(1))
    label.place(x=125, y=150)
    entry.place(x=115, y=200)
    button5.place(x=150, y=250)
    test.wait_variable(okVar) # WAIT FOR SUBMIT TO BE PRESSED
    filename = entry.get()
    print(filename)
    filename = str(filename) # This confirms the file name we have entered
    # Generate our Resolution Buttons
    Rad480pButton = StreamController.Button(test, text="480p20fps", pady=5, font=("Arial Bold", 10),
                                        bg='red', command=lambda: start_radio_stream(filename,20, 640, 480))
    Rad480p25Button = StreamController.Button(test, text="480p25fps", pady=5, font=("Arial Bold", 10),
                                        bg='red', command=lambda: start_radio_stream(filename, 25, 640, 480))
    Rad720pButton = StreamController.Button(test, text="576p20fps", pady=5, font=("Arial Bold", 10),
                                        bg='red', command=lambda: start_radio_stream(filename, 20, 1024, 576))
    Rad480pButton.place(x = 35, y = 300)
    Rad480p25Button.place(x = 135, y = 300 )
    Rad720pButton.place(x = 235, y = 300)


def cellular(): # This does all the same things the radio code does, but for cellular
    label = StreamController.Label(text="Enter Cellular Filename")
    entry=StreamController.Entry()
    okVar=StreamController.IntVar()
    button5=StreamController.Button(test, text="Submit", pady=5, font=("Arial Bold", 10),
        bg='lightgray', command=lambda: okVar.set(1))
    label.place(x=125, y = 150)
    entry.place(x = 115, y = 200)
    button5.place(x = 150, y = 250)
    test.wait_variable(okVar)
    filename = entry.get()
    print(filename)
    filename = str(filename)
    Cell480pButton = StreamController.Button(test, text="480p20fps", pady=5, font=("Arial Bold", 10), bg='blue', command=lambda: start_cellular_stream(filename,20, 640, 480))
    Cell480p30Button = StreamController.Button(test, text="480p25fps", pady=5, font=("Arial Bold", 10),
                                        bg='blue', command=lambda: start_cellular_stream(filename, 25, 640, 480))
    Cell720pButton = StreamController.Button(test, text="576p20fps", pady=5, font=("Arial Bold", 10),
                                        bg='blue', command=lambda: start_cellular_stream(filename, 20, 1024, 576))
    # Place buttons
    Cell480pButton.place(x = 35, y = 300)
    Cell480p30Button.place(x = 135, y = 300 )
    Cell720pButton.place(x = 235, y = 300)


def start_cellular_stream(filename, fps, width, height): #Function which starts stream based on parameters passed by the resolution buttons.
    if fps == 25:
        client = paramiko.SSHClient()
        print("We're running 480p25fps cellular!")
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname="76.70.161.20", port=22, username="pi", password="********", timeout=10) # IP address used to connect to the cellular header via SSL, if the address changes, change this to connect again.
# Generate our stream using GStreamer commands
        p = subprocess.Popen(
                f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}480p25fpsCellularlatencydata.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                shell=True)
# Generate an ID for the subprocess so we can shut it down later
        p.pid = p.pid + 1
# Allow for a small amount of time for the connection to go through
        time.sleep(4)
# Need to start our code which tracks all our peripherals
        q = subprocess.Popen(['python3', "/home/mitch/NetCatSocketRead.py", f"{filename}{height}p25fpsCellularReceiver"])
        stdin, stdout, stderr = client.exec_command('sudo ifconfig eth0 down') # Need to disable radio connection when working with cellular
# Send command to Pi to send video back to us
        stdin, stdout, stderr = client.exec_command(
            f'python3 PiCell.py {filename}{height}p25fpsCellularPiData  & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}480p25fpsRasPiCell.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
 f'! \'video/x-raw,width={width}, height={height}, framerate=25/1\' ! timestampoverlay ! timeoverlay ! queue !  videoconvert !'
                                                        f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc control-rate=2 target-bitrate=500000 ! video/x-h264, profile=\"baseline\" ! queue ! rtph264pay !  '
                                                        'udpsink host=70.28.202.51 port=4200')
        print("Returning to main loop")
    else:
        if height==576:
            client = paramiko.SSHClient()
            print(f"We're running {height}p {fps} fps cellular!")
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname="76.70.161.20", port=22, username="pi", password="********", timeout=10)
            p = subprocess.Popen(
                f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}{height}p{fps}fpsCellularlatencydata.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",shell=True)
            p.pid = p.pid + 1 # Generate ID
            time.sleep(4) # Sleep for 4 seconds
            q = subprocess.Popen(
                ['python3.6', "/home/mitch/NetCatSocketRead.py", f"{filename}{height}p{fps}fpsCellularReceiver"])
            stdin, stdout, stderr = client.exec_command('sudo ifconfig eth0 down') # Disable radio connection so we can transmit over cellular
            # Run GStreamer code
            stdin, stdout, stderr = client.exec_command(f'python3 PiCell.py {filename}{height}p{fps}fpsCellularPiData  & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}{height}p{fps}fpsRasPiCell.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
                                                            f'! \'video/x-raw,width={width}, height={height}, framerate={fps}/1\' ! timestampoverlay !  timeoverlay! queue !  videoconvert !'
                                                        f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc control-rate=2 target-bitrate=600000 ! video/x-h264, profile=\"baseline\" ! queue ! rtph264pay !  '
                                                        'udpsink host=70.28.202.51 port=4200')
        else:
            client = paramiko.SSHClient()
            print(f"We're running {height}p {fps} fps cellular!")
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname="76.70.161.20", port=22, username="pi", password="********", timeout=10)
            p = subprocess.Popen(
                f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}{height}p{fps}fpsCellularlatencydata.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                shell=True)
            # Generate ID for connection shutdown
            p.pid = p.pid + 1
            time.sleep(4)
            q = subprocess.Popen(
                ['python3.6', "/home/mitch/NetCatSocketRead.py", f"{filename}{height}p{fps}fpsCellularReceiver"])
            stdin, stdout, stderr = client.exec_command('sudo ifconfig eth0 down')
            stdin, stdout, stderr = client.exec_command(
                f'python3 PiCell.py {filename}{height}p{fps}fpsCellularPiData  & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}{height}p{fps}fpsRasPiCell.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
                f'! \'video/x-raw,width={width}, height={height}, framerate={fps}/1\' ! timestampoverlay !  timeoverlay ! queue !  videoconvert !'
                f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc control-rate=2 target-bitrate=400000 ! video/x-h264, profile=\"baseline\" ! queue ! rtph264pay !  '
                'udpsink host=70.28.202.51 port=4200')
        print("Returning to main loop")
    # button6 = StreamController.Button(test, text="Close Cell", pady=5, font=("Arial Bold", 10),
    #                                   bg='lightgray',
    #                                   command=lambda: [subprocess.Popen([q.kill(),
    #                                                    client.exec_command("pkill -fi gst-launch"), client.close()])])
    button6 = StreamController.Button(test, text="Close Cell", pady=5, font=("Arial Bold", 10),
                                      bg='lightgray',
                                      command=lambda: [subprocess.Popen(["kill", "{}".format(p.pid)]), q.kill(),
                                                       client.exec_command("pkill -fi gst-launch"), client.close()])
    button6.place(x=125, y=375)


def start_radio_stream(filename, fps, width, height):
    if fps == 25:
        client = paramiko.SSHClient()
        print("We're running 480p25fps radio!")
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname="192.168.168.170", port=22, username="pi", password="********", timeout=5) #IP address to connect over radio, if you use a different device or adjust the IP addresses make sure to change this.
        p = subprocess.Popen(
            f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}{height}p25fpsRadiolatencydata.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
            f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
            shell=True)
        p.pid = p.pid + 1
        time.sleep(4)
        q = subprocess.Popen(['python3', '/home/mitch/LaptopRadioRead.py', f'{filename}{height}p25fpsRadioReceiver'])
        stdin, stdout, stderr = client.exec_command((f'python3 PiRadio.py {filename}{height}p25fpsRadioData  &  GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}{height}p25fpsRasPiRadio.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
                                                        f'! \'video/x-raw,width={width}, height={height}, framerate=25/1\' ! timestampoverlay ! timeoverlay !  queue !  videoconvert !'
                                                        f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc control-rate=2 target-bitrate=500000 ! video/x-h264, profile=\"baseline\" ! queue ! rtph264pay !  '
                                                        'udpsink host=192.168.168.127 port=4200'))
        print("Radio Connection Finished")
    else:
        if height==576:
            client = paramiko.SSHClient()
            print("We're running 576p20fps radio!")
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname="192.168.168.170", port=22, username="pi", password="********", timeout=5)
            p = subprocess.Popen(
                f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}{height}p{fps}fpsRadiolatencydata.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                shell=True)
            p.pid = p.pid + 1
            time.sleep(4)
            print("Beginning Stream:")
            q = subprocess.Popen(['python3', "/home/mitch/LaptopRadioRead.py", f"{filename}{height}p{fps}fpsRadioReceiver"])
            stdin, stdout, stderr = client.exec_command((f"python3 PiRadio.py {filename}{height}p{fps}fpsRadioData  & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}{height}p{fps}fpsRasPiRadio.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false ! \'video/x-raw,width={width}, height={height}, framerate={fps}/1\' ! timestampoverlay ! timeoverlay !  queue ! videoconvert !"            
            f" \'video/x-raw, format=I420, width={width}, height={height}\' ! queue ! omxh264enc control-rate=2 target-bitrate=600000 ! video/x-h264, profile=\"baseline\" ! queue ! rtph264pay !"
                "udpsink host=192.168.168.127 port=4200"))
        else:
            client = paramiko.SSHClient()
            print("We're running 480p20fps radio!")
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname="192.168.168.170", port=22, username="pi", password="********", timeout=5)
            p = subprocess.Popen(
                f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}{height}p{fps}fpsRadiolatencydata.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                shell=True)
            p.pid = p.pid + 1
            time.sleep(4)
            print("Beginning Stream:")
            q = subprocess.Popen(
                ['python3', "/home/mitch/LaptopRadioRead.py", f"{filename}{height}p{fps}fpsRadioReceiver"])
            stdin, stdout, stderr = client.exec_command((
                                                            f"python3 PiRadio.py {filename}{height}p{fps}fpsRadioData  & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}{height}p{fps}fpsRasPiRadio.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false ! \'video/x-raw,width={width}, height={height}, framerate={fps}/1\' ! timestampoverlay ! timeoverlay !  queue ! videoconvert !"            
            f" \'video/x-raw, format=I420, width={width}, height={height}\' ! queue ! omxh264enc control-rate=2 target-bitrate=400000 ! video/x-h264, profile=\"baseline\" ! queue ! rtph264pay !"
                "udpsink host=192.168.168.127 port=4200"))
    print("Radio Connection Finished")
    print("Button Should Be Generated")
    button6 = StreamController.Button(test, text="Close Radio", pady=5, font=("Arial Bold", 10),
                                      bg='lightgray',
                                      command=lambda: [subprocess.Popen(["kill", "{}".format(p.pid)]), q.kill(),
                                                       client.exec_command("pkill -fi gst-launch"), client.close()])
    button6.place(x=125, y=375)


def start_submit_thread(event, identifier):
    global submit_thread
    submit_thread = threading.Thread(target=identifier)
    submit_thread.daemon = True
    submit_thread.start()
    test.after(20, check_submit_thread)


def reboot():
    # Code to connect to the Raspberry Pi and restart it over cellular connection
    client = paramiko.SSHClient()
    print("We're rebooting the Pi!")
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname="76.70.161.20", port=22, username="pi", password="********", timeout=10)
    stdin, stdout, stderr = client.exec_command('sudo reboot -h')
    print("stderr: ", stderr.readlines())
    print("pwd: ", stdout.readlines())


def reboot_over_radio():
    # Code to connect to the Raspberry Pi and restart it over radio connection
    client = paramiko.SSHClient()
    print("We're rebooting the Pi!")
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname="192.168.168.170", port=22, username="pi", password="********", timeout=10)
    stdin, stdout, stderr = client.exec_command('sudo reboot -h')
    print("stderr: ", stderr.readlines())
    print("pwd: ", stdout.readlines())


def attemptsynchronize():
    # Button to try to synchronize the clocks as closely as possible. Recommended to run this before each trial.
    client = paramiko.SSHClient()
    print("Trying to synchronize clocks!")
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname="192.168.168.170", port=22, username="pi", password="********")
    #q = subprocess.Popen(['sudo ntpd ********'], shell=TRUE)
    stdin, stdout, stderr = client.exec_command('sudo ntpdate -b 192.168.168.127')
    print("stderr: ", stderr.readlines())
    print("pwd: ", stdout.readlines())
    client.close()


def check_time_difference():
    # Code to check the difference between clocks.
    print("Getting our clock difference!")
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname="192.168.168.170", port=22, username="pi", password="********")
    # q = subprocess.Popen(['sudo ntpd ********'], shell=TRUE)
    stdin, stdout, stderr = client.exec_command('sudo service ntp stop ********')
    stdin, stdout, stderr = client.exec_command('sudo ntpdate -q 192.168.168.127')
    print("stderr: ", stderr.readlines())
    print("pwd: ", stdout.readlines())
    client.close()


def reconnect_radio():
    client = paramiko.SSHClient()
    print("Re-enabling the connection for Radio Tests!")
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname="76.70.161.20", port=22, username="pi", password="********")
    stdin, stdout, stderr = client.exec_command(('sudo ifconfig eth0 up ********'))
    time.sleep(5)
    client.close()
def close_stream():


    #Code to close the stream
    client = paramiko.SSHClient()
    print("Closing current video stream on Pi")
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname="76.70.161.20", port=22, username="pi", password="********")
    stdin, stdout, stderr = client.exec_command(('pkill -fi gst-launch'))
    time.sleep(5)
    client.close()


def check_submit_thread():
    if submit_thread.is_alive():
        test.after(20, check_submit_thread)


def ethernet():
    # Same code as the radio and cellular connections, generates the buttons through the same procedure to connect via ethernet.
    label = StreamController.Label(text="Enter Ethernet Test Name")
    entry = StreamController.Entry()
    okVar = StreamController.IntVar()
    button5 = StreamController.Button(test, text="Submit", pady=5, font=("Arial Bold", 10),
                                      bg='lightgray', command=lambda: okVar.set(1))
    label.place(x=125, y=150)
    entry.place(x=115, y=200)
    button5.place(x=150, y=250)
    test.wait_variable(okVar)
    filename = entry.get()
    print(filename)
    filename = str(filename)
    Rad480pButton = StreamController.Button(test, text="480p20fps", pady=5, font=("Arial Bold", 10),
                                            bg='green', command=lambda: start_ethernet_stream(filename, 20, 640, 480))
    Rad480p25Button = StreamController.Button(test, text="480p25fps", pady=5, font=("Arial Bold", 10),
                                              bg='green', command=lambda: start_ethernet_stream(filename, 25, 640, 480))
    Rad720pButton = StreamController.Button(test, text="576p20fps", pady=5, font=("Arial Bold", 10),
                                            bg='green', command=lambda: start_ethernet_stream(filename, 20, 1024, 576))
    Rad480pButton.place(x=35, y=300)
    Rad480p25Button.place(x=135, y=300)
    Rad720pButton.place(x=235, y=300)


def start_ethernet_stream(filename, fps, width, height):
    # Similar overall code as the radio and cellular stream configurations, runs the same processes but for connection to Ethernet.
    if fps == 25:
        client = paramiko.SSHClient()
        print("Running ethernet calibration...")
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname="192.168.168.170", port=22, username="pi", password="********", timeout=10) #
        p = subprocess.Popen(
            f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}25fpsEthernetData.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
            f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
            shell=True)
        print(p.pid)
        p.pid = p.pid + 1
        time.sleep(4)
        # stdin, stdout, stderr = client.exec_command(f' gst-launch-1.0 -e -v --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
        #                                                 f'! \'video/x-raw,width={width}, height={height}, framerate=50/1\' ! timestampoverlay !  timeoverlay!  videoconvert !'
        #                                                 f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc ! rtph264pay !  '
        #                                                 'udpsink host=192.168.168.127 port=4200')
        stdin, stdout, stderr = client.exec_command(
                                                        f' python PiCell.py {filename}{height}p{fps}fpsPiEthernetData & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}480p30fpsRasPiEthernetData.csv '
                                                        ' gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
                                                        f'! \'video/x-raw,width={width}, height={height}, framerate=25/1\' ! timestampoverlay !  timeoverlay!  videoconvert !'
                                                        f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc control-rate=2 target-bitrate=500000 ! video/x-h264, profile=\"baseline\" ! queue ! rtph264pay !  '
                                                        'udpsink host=192.168.168.200 port=4200')
    else:
        if height == 576:
            client = paramiko.SSHClient()
            print("Running ethernet calibration...")
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname="192.168.168.170", port=22, username="pi", password="********", timeout=10)
            p = subprocess.Popen(
                f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}{height}p{fps}fpsEthernetData.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                f" rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                shell=True)
            print(p.pid)
            p.pid = p.pid + 1
            time.sleep(4)
            stdin, stdout, stderr = client.exec_command(
                (f' python PiCell.py {filename}{height}p{fps}fpsPiEthernetData & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}{height}p{fps}fpsRasPiEthernetData.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
                 f'! \'video/x-raw,width={width}, height={height}, framerate={fps}/1\' ! timestampoverlay !  timeoverlay!  videoconvert !'
                                                        f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc control-rate=2 target-bitrate=600000 ! video/x-h264, profile=\"baseline\" ! queue ! rtph264pay !  '
                                                        'udpsink host=192.168.168.200 port=4200'))
        else:
            client = paramiko.SSHClient()
            print("Running ethernet calibration...")
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname="192.168.168.170", port=22, username="pi", password="********", timeout=10)
            p = subprocess.Popen(
                f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}{height}p{fps}fpsEthernetData.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                f" rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                shell=True)
            print(p.pid)
            p.pid = p.pid + 1
            time.sleep(4)
            stdin, stdout, stderr = client.exec_command((
                    f' python PiCell.py {filename}{height}p{fps}fpsPiEthernetData & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}{height}p{fps}fpsRasPiEthernetData.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
                    f'! \'video/x-raw,width={width}, height={height}, framerate={fps}/1\' ! timestampoverlay !  timeoverlay!  videoconvert !'
                                                        f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc control-rate=2 target-bitrate=400000 ! video/x-h264, profile=\"baseline\" ! queue ! rtph264pay !  '
                                                        'udpsink host=192.168.168.200 port=4200'))
    print("Button Should Be Generated")
    # button6 = StreamController.Button(test, text="Close Ethernet", pady=5, font=("Arial Bold", 10),
    #                                   command=lambda: [client.exec_command("pkill -fi gst-launch"), client.close()])
    button6 = StreamController.Button(test, text="Close Ethernet", pady=5, font=("Arial Bold", 10),
                                      command=lambda: [subprocess.Popen(["kill", "{}".format(p.pid)]), client.exec_command("pkill -fi gst-launch"), client.close()])
    button6.place(x = 125, y = 375)


def ntp_reconnect():
    #Reconnects to the NTP server if synchronization issues are encountered.
    print("Joining new NTP server!")
    q = subprocess.Popen(['sudo service ntp stop ********'], shell=TRUE)
    o = subprocess.Popen(['sudo service ntp start ********'], shell=TRUE)


def radio_play():
    # Code to enable radio to play without the timestamp embedded.
    Rad480pButton = StreamController.Button(test, text="480p20fps", pady=5, font=("Arial Bold", 10),
                                        bg='red', command=lambda: start_radio_play(20, 640, 480, "192.168.168.127", "192.168.168.170"))
    Rad480p50Button = StreamController.Button(test, text="480p25fps", pady=5, font=("Arial Bold", 10),
                                        bg='red', command=lambda: start_radio_play(25, 640, 480, "192.168.168.170", "192.168.168.127"))
    Rad720pButton = StreamController.Button(test, text="576p20fps", pady=5, font=("Arial Bold", 10),
                                        bg='red', command=lambda: start_radio_play(20, 1024, 576, "192.168.168.127", "192.168.168.170"))
    Rad480pButton.place(x=35, y=300)
    Rad480p50Button.place(x=135, y=300)
    Rad720pButton.place(x=235, y=300)


def start_radio_play(fps, width, height, connectionip, filename):
    # Same code as in the radio streaming, but no timestamp overlaid into the video feed
    if fps == 25:
        client = paramiko.SSHClient()
        print("We're running 480p25fps radio!")
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=f"{connectionip}", port=22, username="pi", password="********", timeout=5)
        p = subprocess.Popen(
            f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
            f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
            shell=True)
        p.pid = p.pid + 1
        time.sleep(4)
        stdin, stdout, stderr = client.exec_command((f'GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
                                                        f'! \'video/x-raw,width={width}, height={height}, framerate=25/1\' ! timeoverlay !  queue !  videoconvert !'
                                                        f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc control-rate=2 target-bitrate=500000 ! video/x-h264, profile=\"baseline\" ! queue ! rtph264pay !  '
                                                       f'udpsink host={filename} port=4200'))
        print("Radio Connection Finished")
    else:
        if height==576:
            client = paramiko.SSHClient()
            print("We're running 576p20fps!")
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=f"{filename}", port=22, username="pi", password="********", timeout=5)
            p = subprocess.Popen(
                f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                shell=True)
            p.pid = p.pid + 1
            time.sleep(4)
            print("Beginning Stream:")
            stdin, stdout, stderr = client.exec_command((f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false ! \'video/x-raw,width={width}, height={height}, framerate={fps}/1\' ! timeoverlay !  queue ! videoconvert !"            
            f" \'video/x-raw, format=I420, width={width}, height={height}\' ! queue ! omxh264enc ! queue ! rtph264pay !"
                f"udpsink host={filename} port=4200"))
        else:
            client = paramiko.SSHClient()
            print("We're running 480p20fps radio!")
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=f"{filename}", port=22, username="pi", password="********", timeout=5)
            p = subprocess.Popen(
                f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                shell=True)
            p.pid = p.pid + 1
            time.sleep(4)
            print("Beginning Stream:")
            stdin, stdout, stderr = client.exec_command((
                                                            f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false ! \'video/x-raw,width={width}, height={height}, framerate={fps}/1\' ! timeoverlay !  queue ! videoconvert !"            
            f" \'video/x-raw, format=I420, width={width}, height={height}\' ! queue ! omxh264enc ! queue ! rtph264pay !"
                f"udpsink host={filename} port=4200"))
    print("Radio Connection Finished")
    print("Button Should Be Generated")
    button15 = StreamController.Button(test, text="Close Radio", pady=5, font=("Arial Bold", 10),
                                      bg='lightgray',
                                      command=lambda: [subprocess.Popen(["kill", "{}".format(p.pid)]),
                                                       client.exec_command("pkill -fi gst-launch"), client.close()])
    button15.place(x=125, y=375)


def cell_play():
    Cell480pButton = StreamController.Button(test, text="480p20fps", pady=5, font=("Arial Bold", 10),
                                        bg='blue', command=lambda: start_radio_play(20, 640, 480, "76.70.161.20", "70.28.202.51"))
    Cell480p30Button = StreamController.Button(test, text="480p25fps", pady=5, font=("Arial Bold", 10),
                                        bg='blue', command=lambda: start_radio_play(25, 640, 480, "76.70.161.20", "70.28.202.51"))
    Cell720pButton = StreamController.Button(test, text="576p20fps", pady=5, font=("Arial Bold", 10),
                                        bg='blue', command=lambda: start_radio_play(20, 1024, 576, "76.70.161.20", "70.28.202.51"))
    Cell480pButton.place(x=35, y=300)
    Cell480p30Button.place(x=135, y=300)
    Cell720pButton.place(x=235, y=300)


def VBR_Cellular():
    # Code to run the stream with a variable bitrate, as opposed to constant bitrate.
    label = StreamController.Label(text="Enter VBR Cellular Filename")
    entry=StreamController.Entry()
    okVar=StreamController.IntVar()
    button5=StreamController.Button(test, text="Submit", pady=5, font=("Arial Bold", 10),
        bg='lightgray', command=lambda: okVar.set(1))
    label.place(x=125, y = 150)
    entry.place(x = 115, y = 200)
    button5.place(x = 150, y = 250)
    test.wait_variable(okVar)
    filename = entry.get()
    print(filename)
    filename = str(filename)
    Cell480pButton = StreamController.Button(test, text="480p20fps", pady=5, font=("Arial Bold", 10), bg='white', command=lambda: start_VBR_cellular_stream(filename,20, 640, 480))
    Cell480p30Button = StreamController.Button(test, text="480p25fps", pady=5, font=("Arial Bold", 10),
                                        bg='white', command=lambda: start_VBR_cellular_stream(filename, 25, 640, 480))
    Cell720pButton = StreamController.Button(test, text="576p20fps", pady=5, font=("Arial Bold", 10),
                                        bg='white', command=lambda: start_VBR_cellular_stream(filename, 20, 1024, 576))
    Cell480pButton.place(x = 35, y = 300)
    Cell480p30Button.place(x = 135, y = 300 )
    Cell720pButton.place(x = 235, y = 300)


def start_VBR_cellular_stream(filename, fps, width, height):
        if fps == 25:
            client = paramiko.SSHClient()
            print("We're running 480p25fps cellular!")
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname="76.70.161.20", port=22, username="pi", password="********", timeout=10)
            p = subprocess.Popen(
                f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}VBR480p25fpsCellularlatencydata.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                shell=True)
            p.pid = p.pid + 1
            time.sleep(4)
            q = subprocess.Popen(
                ['python3', "/home/mitch/NetCatSocketRead.py", f"{filename}VBR{height}p25fpsCellularReceiver"])
            stdin, stdout, stderr = client.exec_command('sudo ifconfig eth0 down')
            stdin, stdout, stderr = client.exec_command(
                f'python3 PiCell.py {filename}VBR{height}p25fpsCellularPiData  & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}VBR480p25fpsRasPiCell.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
                f'! \'video/x-raw,width={width}, height={height}, framerate=25/1\' ! timestampoverlay ! timeoverlay ! queue !  videoconvert !'
                f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc  ! queue ! rtph264pay !  '
                'udpsink host=70.28.202.51 port=4200')
            print("Returning to main loop")
        else:
            if height == 576:
                client = paramiko.SSHClient()
                print(f"We're running {height}p {fps} fps VBR cellular!")
                client.load_system_host_keys()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname="76.70.161.20", port=22, username="pi", password="********", timeout=10)
                p = subprocess.Popen(
                    f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}VBR{height}p{fps}fpsCellularlatencydata.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                    f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                    shell=True)
                p.pid = p.pid + 1
                time.sleep(4)
                q = subprocess.Popen(
                    ['python3.6', "/home/mitch/NetCatSocketRead.py", f"{filename}VBR{height}p{fps}fpsCellularReceiver"])
                stdin, stdout, stderr = client.exec_command('sudo ifconfig eth0 down')
                stdin, stdout, stderr = client.exec_command(
                    f'python3 PiCell.py {filename}VBR{height}p{fps}fpsCellularPiData  & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}VBR{height}p{fps}fpsRasPiCell.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
                    f'! \'video/x-raw,width={width}, height={height}, framerate={fps}/1\' ! timestampoverlay !  timeoverlay! queue !  videoconvert !'
                    f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc ! queue ! rtph264pay !  '
                    'udpsink host=70.28.202.51 port=4200')
            else:
                client = paramiko.SSHClient()
                print(f"We're running {height}p {fps} fps VBR cellular!")
                client.load_system_host_keys()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname="76.70.161.20", port=22, username="pi", password="********", timeout=10)
                p = subprocess.Popen(
                    f"GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/mitch/{filename}VBR{height}p{fps}fpsCellularlatencydata.csv gst-launch-1.0 --gst-debug=4  udpsrc port=4200 ! 'application/x-rtp, encoding-name=H264, width={width}, height={height}, payload=96'!"
                    f"  rtph264depay ! avdec_h264 ! videoconvert ! \'video/x-raw\' ! timeoverlayparse ! glimagesink sync=false",
                    shell=True)
                p.pid = p.pid + 1
                time.sleep(4)
                q = subprocess.Popen(
                    ['python3.6', "/home/mitch/NetCatSocketRead.py", f"{filename}VBR{height}p{fps}fpsCellularReceiver"])
                stdin, stdout, stderr = client.exec_command('sudo ifconfig eth0 down')
                stdin, stdout, stderr = client.exec_command(
                    f'python3 PiCell.py {filename}VBR{height}p{fps}fpsCellularPiData  & GST_DEBUG=\"GST_TRACER:7\" GST_TRACERS=\"framerate;bitrate;interlatency\" GST_DEBUG_FILE=/home/pi/{filename}VBR{height}p{fps}fpsRasPiCell.csv gst-launch-1.0 --gst-debug=4 rpicamsrc bitrate=3000000  preview=false   '
                    f'! \'video/x-raw,width={width}, height={height}, framerate={fps}/1\' ! timestampoverlay !  timeoverlay ! queue !  videoconvert !'
                    f' \'video/x-raw, format=I420, width={width}, height={height}\' ! omxh264enc ! queue ! rtph264pay !  '
                    'udpsink host=70.28.202.51 port=4200')
            print("Returning to main loop")
        # button6 = StreamController.Button(test, text="Close Cell", pady=5, font=("Arial Bold", 10),
        #                                   bg='lightgray',
        #                                   command=lambda: [subprocess.Popen([q.kill(),
        #                                                    client.exec_command("pkill -fi gst-launch"), client.close()])])
        button19 = StreamController.Button(test, text="Close Cell", pady=5, font=("Arial Bold", 10),
                                          bg='lightgray',
                                          command=lambda: [subprocess.Popen(["kill", "{}".format(p.pid)]), q.kill(),
                                                           client.exec_command("pkill -fi gst-launch"), client.close()])
        button19.place(x=125, y=375)
# Generate all buttons for the window at startup corresponding to each command function


def main():
    button = StreamController.Button(test, bg= "red", text='Radio', command=(lambda: start_submit_thread(None, radio)))
    button2 = StreamController.Button(test, bg = "blue", text='Cellular', command=(lambda: start_submit_thread(None, cellular)))
    button3 = StreamController.Button(test, text='Reboot Pi', command=(lambda: start_submit_thread(None, reboot)))
    button5 = StreamController.Button(test, text='Check Time', command=(lambda: start_submit_thread(None, checktime)))
    buttonntp = StreamController.Button(test, text='NTP Sync', command=(lambda: start_submit_thread(None, attemptsynchronize)))
    button7 = StreamController.Button(test, text="Quit", fg="red", command=(lambda: sys.exit()))
    button8 = StreamController.Button(test, text='Reconnect Radio', command=(lambda: start_submit_thread(None, reconnect_radio)))
    button9 = StreamController.Button(test, text= 'Reboot Pi Rad', command=(lambda: start_submit_thread(None, reboot_over_radio)))
    button10 = StreamController.Button(test, text="Ethernet Test", bg = "green", command=(lambda: start_submit_thread(None, ethernet)))
    button11 = StreamController.Button(test, text= 'Check Time Difference', command=(lambda: start_submit_thread(None, check_time_difference())))
    button12 = StreamController.Button(test, text= 'New NTP', command=(lambda: start_submit_thread(None, ntp_reconnect())))
    button13 = StreamController.Button(test, text= 'Close Stream', command=(lambda: start_submit_thread(None, close_stream)))
    button16 = StreamController.Button(test, text= 'Play Radio', command=(lambda: start_submit_thread(None, radio_play)))
    button17 = StreamController.Button(test, text= 'Play Cell', command=(lambda: start_submit_thread(None, cell_play)))
    button18 = StreamController.Button(test, text="VBR Cell", bg = "white", command=(lambda: start_submit_thread(None, VBR_Cellular)))
    button.place(x = 5, y = 0)
    button2.place(x =70 , y = 0)
    button3.place(x=150, y = 0)
    button9.place(x = 240, y = 0)
    button10.place(x= 5, y=40)
    buttonntp.place(x = 145, y=40)
    button8.place(x = 235, y = 40)
    button7.place(x = 320, y = 80)
    button11.place(x =5, y = 80)
    button12.place(x = 200, y = 80)
    button13.place(x = 5, y = 120)
    button16.place(x=120, y=120)
    button17.place(x=220, y=120)
    button18.place(x=310, y=120)
    print("Test")
    test.title("GStreamer Interface Controller")
    test.geometry("400x500")
    test.bind('q', quit)
    print("Before Loop")
    test.mainloop()
    print("After Loop")


if __name__ == "__main__":
    main()

