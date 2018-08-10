#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#very crude code, I coded this on stream, the skullbot was used as basis for this
""" simple Twitch bot https://github.com/skullvalanche/skullbot/blob/master/skullbot.py"""

import socket
import json
import time
import random
import re
from streamlink import Streamlink, StreamError, PluginError, NoPluginError



from settings import channel, server, oauth_password, nickname,quality,http_proxy

import threading
import time
from sys import stdin
import socks


class cmdThread (threading.Thread):
	
   def __init__(self,irc,channel):
      threading.Thread.__init__(self)
      self.irc = irc
      self.channel = channel
      self.run_v = False


   def run(self):
      print "Starting thread" 
      # Get lock to synchronize threads
      self.run_v = True
      while self.run_v:
         try:
           userinput = stdin.readline()
           self.irc.send(self.channel, userinput)
         except KeyboardInterrupt:
           print "Ctrl-c pressed ..."
           self.run_v=False

   def stop(self):
      self.run_v=False

 


class viewThread(threading.Thread):
  streamlink =  Streamlink()
  fd = None
  run_v = False
  fileHandle = None


  def __init__(self,channel,quality):
    threading.Thread.__init__(self)
    self.channel = channel
    self.quality = quality

 # Create the Streamlink session
    url = "http://twitch.tv/"
    url += channel[1:]
  #  print "url"+url 

    try:
      self.streamlink.set_option("http-proxy", http_proxy)
    #  self.streamlink.set_option("https-proxy", http_proxy)
      self.streamlink.set_option("rtmp-proxy", http_proxy)
      streams = self.streamlink.streams(url)
    except NoPluginError:
      exit("Streamlink is unable to handle the URL '{0}'".format(url))
    except PluginError as err:
      exit("Plugin error: {0}".format(err))
 

        # Look for specified stream
    if quality not in streams:
      exit("Unable to find '{0}' stream on URL '{1}'".format(quality, url))

        # We found the stream
    stream = streams[quality]
    self.fd = stream.open()
 	#
        #open fil
    self.fileHandle =open('videodump.flv','w')
	

  def run(self):
    print "Starting recording" 
    self.run_v= True
    # Get lock to synchronize threads
    while self.run_v:
      try:
        if self.fd:
          data = self.fd.read(1024)
	  self.fileHandle.write(data)
		
      except KeyboardInterrupt:
        print "Ctrl-c pressed ..."
        self.run_v=False

  def stop(self):
    self.run_v=False
    if self.fd:
      self.fd.close()
    if self.fileHandle:
      self.fileHandle.close()


class IRC(object):
    'defines IRC connection object'
    irc = socks.socksocket() 

    #def __init__(self):
     #   self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     # pas


    def send(self, chan, msg):
        'sends message to irc'
        self.irc.send("PRIVMSG %s :%s\n" % (chan, msg.encode('utf-8')))

    def connect(self, server, channel, botnick, oauth_password,proxy =None):
        if proxy != None:
          ip,port = proxy.split(":")
          print "set proxy"
	  print ip
          print port
          self.irc.set_proxy(socks.HTTP, ip,int(port) )
        
        print "Connecting to:" + server
        self.irc.connect((server, 6667))
       

 
        self.irc.send("USER %s\r\n" % botnick)
        self.irc.send("PASS %s\r\n" % oauth_password)
        self.irc.send("NICK %s\r\n" % botnick)
        self.irc.send("JOIN %s\r\n" % channel)

    def get_text(self):
        'receive the text'
        text = self.irc.recv(2040)

        if text.find('PING') != -1:
            self.irc.send('PONG %s\r\n' % text.split()[1])

        return text



def main():
    '''Checks incoming irc messages for trigger phrases,
    returns messages in response'''


    irc = IRC()
    irc.connect(server, channel, nickname, oauth_password,http_proxy)

 
    cmdtread = cmdThread(irc,channel)
    viewtread = viewThread(channel,quality)

	# Start new Threads
    cmdtread.start()
    viewtread.start()


    #irc.send(channel, "hi guys")

    while True:
        try:
            chat_message = irc.get_text()
            print chat_message


            if "PRIVMSG" in chat_message and channel in chat_message:
                with open("responses.json", "r") as f:
                    responses = json.loads(f.read())
                    for k in responses:
                        if re.search(k, chat_message.lower()):
                            if isinstance(responses.get(k), dict):
                                alias_key = responses.get(k).get("alias")
                                message = responses.get(alias_key)
                                if isinstance(message, list):
                                    message = random.choice(message)
                            elif isinstance(responses.get(k), list):
                                message = random.choice(responses.get(k))
                            else:
                                message = responses.get(k)
                            irc.send(channel, message)
                            time.sleep(5)
                            break
        except KeyboardInterrupt:
            break;

    cmdtread.stop()
    cmdtread.join()
    viewtread.stop()
    viewtread.join()
    print "Exiting Main Thread"


if __name__ == "__main__":
    main()
