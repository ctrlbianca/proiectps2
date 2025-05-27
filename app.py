
from threading import Thread
import smtplib
from flask import Flask, render_template, request, jsonify
from serial import Serial
import datetime as dt
import sys

app = Flask(__name__)
LED_STATUS = None
MESSAGES = []
EMAIL_SEND = False
TEMPERATURE = 0
FLOOD_DATE = "No flood happened"
SERIAL_PORT = sys.argv[1] if len(sys.argv) > 1 else 'COM3'
BAUD_RATE = 9600
serial_com = Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=3)

def ledOn():
    serial_com.write("A".encode())

def ledOff():
    serial_com.write("S".encode())

def readSerialData():
    global TEMPERATURE, FLOOD_DATE
    while True:
        if serial_com.in_waiting > 0:
            data = serial_com.readline().decode('utf-8').strip()
            if data.startswith("Temperature: "):
                TEMPERATURE = data.split(": ")[1]
            elif data == "Flood":
                FLOOD_DATE = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
                sendEmail()

def saveMessage(message):
    serial_com.write(("M" + message + "\n").encode())

def sendEmail():
    global EMAIL_SEND
    if not EMAIL_SEND:
        sender = "faminee@yahoo.com"
        receiver = "mihaibianca034@gmail.com"
        password = "zambila"

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
            connection.login(user=sender, password=password)
            connection.sendmail(
                from_addr=sender,
                to_addrs=receiver,
                msg='Subject:Flood Warning!\n'
                    '\nThe water level is growing, it can cause a flood!!!'
            )
        EMAIL_SEND = True

@app.route("/", methods=['GET', 'POST'])
def index():
    global LED_STATUS, EMAIL_SEND
    if request.method == 'POST':
        if 'on' in request.form.to_dict():
            ledOn()
            LED_STATUS = "ON"
        if 'off' in request.form.to_dict():
            ledOff()
            LED_STATUS = "OFF"
        if 'message' in request.form:
            message = request.form['message']
            MESSAGES.append(message)
            saveMessage(message)

    EMAIL_SEND = False
    return render_template('index.html', temp=TEMPERATURE, led_status=LED_STATUS, messages=MESSAGES, flood_event=FLOOD_DATE)

@app.route("/get_data", methods=['GET'])
def get_data():
    return jsonify(temp=TEMPERATURE, flood_event=FLOOD_DATE)

if __name__ == "__main__":
    serial_thread = Thread(target=readSerialData)
    serial_thread.daemon = True
    serial_thread.start()
    app.run(host='0.0.0.0', port=5000)
