import serial
import threading

class SerialPortThread(threading.Thread):

    def __init__(self, input_queue, output_queue):
        threading.Thread.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = serial.Serial()

    def command(self, value):
        method = getattr(self, value['method'], lambda: 'Invalid')
        return method(value['args'])

    def open(self, value):
        try:
            self.sp.port = value['port']
            self.sp.baudrate = int(value['baudrate'])
            self.sp.timeout = 1
            self.sp.open()
        except serial.serialutil.SerialException as err:
            return "Port name not found."
        
        #print("Serial port opened...")
        return value["msg"]

    def close(self, value):
        self.sp.close()
        #print("Serial port closed...")
        return value["msg"]

    def send(self, value):
        if not self.sp.isOpen():
            return "Not sending data, port is closed."
        
        #print("Sending data...")
        return value["msg"]

    def writeSerial(self, data):
        self.sp.write(bytes(data + "\n", "utf-8"))
        
    def readSerial(self):
        return self.sp.readline()

    def run(self):
        while True:
            if self.sp.isOpen():
                # look for incoming tornado request
                if not self.input_queue.empty():
                    data = self.input_queue.get()
                    # send it to the serial device
                    self.writeSerial(data)

                # look for incoming serial data
                try:
                    if (self.sp.inWaiting() > 0):
                        data = self.readSerial()
                        # send it back to tornado
                        self.output_queue.put(data.decode("utf-8").replace("\n", ""))
                except serial.SerialException:
                    pass
                except Exception:
                    pass