#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# sends advertisement via wispering on top n channel of game X

import socket
import json
import time
import random
import re
import requests



from settings import server, oauth_password, nickname,quality,http_proxy

import time
from sys import stdin
import socks


class IRC(object):
    'defines IRC connection object'
    irc = socks.socksocket() 

    def joinChannel(self, chan):        
        print "Joining Channel:" + chan
        self.irc.send("JOIN %s\r\n" % chan)
        self.irc.send('CAP REQ :twitch.tv/membership\r\n')
        self.irc.send('CAP REQ :twitch.tv/tags\r\n')
        self.irc.send("CAP REQ :twitch.tv/commands\r\n")

    def leaveChannel(self, chan):
        print "Leaving Channel:" + chan
        self.irc.send("PART %s\r\n" % chan)

   
    def listUsers(self,chan ):
        url = "http://tmi.twitch.tv/group/user/%s/chatters" % chan
        r = requests.get(url)
        viewers= r.json() #
        clients = viewers['chatters']['viewers']#
        return clients

    def listChannels(self,game, limit ):
    
        url = "https://api.twitch.tv/kraken/streams/?game=%s&limit=%d&client_id=kgvf8epqezfb5u3wwmlc58n681v5jj&language=en" % (game, limit)

        r = requests.get(url)

        streams= r.json() #

        streamNames = [];

        for stream in streams["streams"]:
            streamNames.append(  stream["channel"]["name"] );


        return streamNames



    def send(self, chan, msg):
        'sends message to irc'
        self.irc.send("PRIVMSG %s :%s\n" % (chan, msg.encode('utf-8')))
    
    def privateMessage(self,channel, nick,msg):
        self.irc.send("PRIVMSG %s :/w %s %s\r\n" % (channel,nick , msg.encode('utf-8')))



    def connect(self, server, botnick, oauth_password,proxy =None):
        if proxy != None:
          ip,port = proxy.split(":")
          print "set proxy"
	  print ip
          print port
          self.irc.set_proxy(socks.HTTP, ip,int(port) )
        
        print "Connecting to:" + server
        self.irc.connect((server, 6667))
       
        print "login....."

        self.irc.send("USER %s\r\n" % botnick)
        self.irc.send("PASS %s\r\n" % oauth_password)
        self.irc.send("NICK %s\r\n" % botnick)
 

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
    irc.connect(server,  nickname, oauth_password,http_proxy)

    #get the list of channels where you want to advertise game and how many top channels
    channelList = irc.listChannels("IRL",5)

    for ch in channelList:
        print ch
  

    while True:
        try:
            chat_message = irc.get_text()
            print chat_message
	
	    ####
	     #join channel

            for ch in channelList: #for each channel
                print "Joining:%s"% ch
                irc.joinChannel(ch)
                #get all users
                usersList = irc.listUsers(ch)
                for user in usersList: #send all users
		    print "sending user:%s"%user
                    irc.privateMessage(ch,user,"Hello friend. Join tonights comedy show on the channel: https://www.twitch.tv/dude707")

	        irc.leaveChannel(ch)
                #do i have to take care of the received text ?
                chat_message = irc.get_text()
                print chat_message
	

	    break

        except KeyboardInterrupt:
            break;

    print "Done with sending!"
   

if __name__ == "__main__":
    main()
