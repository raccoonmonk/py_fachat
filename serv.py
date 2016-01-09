import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import coder
import re

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.template", rooms = self.application.chans)

class RoomHandler(tornado.web.RequestHandler):
    def get(self, room):
        self.render("room.template", room = room)

class WebsocketHandler(tornado.websocket.WebSocketHandler):
    """ self - ws connection
        chan - channel
        nick - nick """    

    nick = None
    chan = None

    def open(self, chan):

        # str has no attribute 'decode'
        #chan = chan.decode("utf-8")
        self.set_nodelay(True)
        self.chan = str(chan)
        self.application.prep_list.add(self)

        if self.nick:
            nn = re.search(r'\W*(\w+)\W*', self.nick)
            if nn:
                self.nick = nn.group(1)
            else:
                self.nick = "guest"  
            self.application.prep_list.discard(self)
            if self.chan in self.application.chans:
                #if channel exist --> add user
                self.application.chans[self.chan].add(self)
            else:
                #create set of users on the channel
                self.application.chans[self.chan] = {self}
            #send new roster to all    
            for user in self.application.chans[self.chan]:
                user.write_message(coder.formJson("roster", self.application.chans[self.chan]))
        else:
            self.write_message(coder.formJson("srv", "Enter your nickname"))

    def on_message(self, message):
        if self in self.application.prep_list:
            #if user in temp list, give him a name
            #escape
            self.nick = tornado.escape.xhtml_escape(message)
            nn = re.search(r'\W*(\w+)\W*', message)
            if nn:
                self.nick = nn.group(1)
            else:
                self.nick = "guest"
            self.application.prep_list.discard(self)
            if self.chan in self.application.chans:
                #if channel exist --> add user
                self.application.chans[self.chan].add(self)
            else:
                #create set of users on the channel
                self.application.chans[self.chan] = {self}
            #send new roster to all    
            for user in self.application.chans[self.chan]:
                user.write_message(coder.formJson("roster", self.application.chans[self.chan]))
            return

        for user in self.application.chans[self.chan]:
            if user != self:
                user.write_message(coder.formJson("usr", self.nick, message))

    def on_close(self):
        self.application.prep_list.discard(self)
        if not self.chan in self.application.chans:
            # no such channel
            return
        # discard user
        self.application.chans[self.chan].discard(self)
        if not self.application.chans[self.chan]:
            # if no users on the channel --> del channel 
            del self.application.chans[self.chan]
        else:
            #send new roster to all    
            for user in self.application.chans[self.chan]:
                user.write_message(coder.formJson("roster", self.application.chans[self.chan]))

    def _not_supported(self, *args, **kwargs):
        pass

settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "www/static"),
            "template_path": os.path.join(os.path.dirname(__file__), "www/template"),
            "cookie_secret": os.urandom(64),
}

application = tornado.web.Application([
                                           (r'.*/ws/(\w+)$', WebsocketHandler),
                                           (r".*/room/(\w+)$", RoomHandler),
                                           (r".*", MainHandler),
                                           ], **settings)
application.chans = {}
application.prep_list = set()

if __name__ == "__main__":
    try:
        ip = os.environ['OPENSHIFT_DIY_IP']
        port = os.environ['OPENSHIFT_DIY_PORT']
    except KeyError:
        ip = "localhost"
        port = 15001
    application.listen(port, ip)
    tornado.ioloop.IOLoop.instance().start()
