import json
import queue

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options

import serialporttask

define("port", default=8080, help="port to listen on", type=int)

clients = []

serialport = None

input_queue = queue.Queue()
output_queue = queue.Queue()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("./public/index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("connection opened")
        clients.append(self)

    def on_message(self, message):
        data = json.loads(message)
        msg = serialport.command(data)
        if msg:
            self.write_message(msg)
        else:
            input_queue.put(data['args']['data'])

    def on_close(self):
        print("connection closed")
        clients.remove(self)


# check the queue for pending messages to all connected clients
def checkQueue():
    if not output_queue.empty():
        message = output_queue.get()
        for c in clients:
            c.write_message(message)


if __name__ == "__main__":
    # start the serial port task in background (as a deamon)
    serialport = serialporttask.SerialPortThread(input_queue, output_queue)
    serialport.daemon = True
    serialport.start()

    tornado.options.parse_command_line()

    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path":  "./public/"}),
            (r"/ws", WebSocketHandler)
        ]
    )

    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    print("Listening on port:", options.port)

    mainLoop = tornado.ioloop.IOLoop.instance()
    # adjust the scheduler_interval according to the frames sent by the serial port
    scheduler_interval = 100
    scheduler = tornado.ioloop.PeriodicCallback(checkQueue, scheduler_interval)
    scheduler.start()
    mainLoop.start()