import re
import cfg
import socket
import time
import threading


class MyThread (threading.Thread):
    def __init__(self, key):
        threading.Thread.__init__(self)
        self.condition = key

    def run(self):
        if self.condition == 1:
            program_1()
        elif self.condition == 2:
            program_2()


CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

s = socket.socket()
s.connect((cfg.HOST, cfg.PORT))
s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))


def chat(sock, msg):
    sock.send("PRIVMSG {} :{}\n".format(cfg.CHAN, msg).encode("utf-8"))
    print(msg)


def ban(sock, user):
    chat(sock, "/ban {} \n".format(user))


def timeout(sock, user, seconds):
    chat(sock, "/timeout {} {} \n".format(user, seconds))


def pyramid(sock, emote, height, msg):
    counter = 1
    back = False
    if len(msg) == 3:
        try:
            if 0 < int(msg[2]) < 8:
                while counter <= int(height) and not back:
                    chat(sock, (emote + " ") * counter)
                    counter += 1
                if counter == int(height) + 1:
                    back = True
                    counter -= 2
                while back and counter:
                    chat(sock, (emote + " ") * counter)
                    counter -= 1
        except ValueError:
            chat(s, "Wut")
    else:
        chat(s, "Nope")

COMM = {
    "!pyramid": pyramid
}


def program_1():
    while True:
        response = s.recv(4096).decode("utf-8")
        if response == "PING :tmi.twitch.tv\r\n":
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            username = re.search(r"\w+", response).group(0)
            message = CHAT_MSG.sub("", response)
            print(username + ": " + message)
            for pattern in cfg.PATT:
                if re.match(pattern, message):
                    chat(s, "o shit waddup")
                    break
            commandmsg = message.split(" ")
            if commandmsg[0] in COMM:
                COMM[commandmsg[0]](s, commandmsg[1], commandmsg[2], commandmsg)
            time.sleep(1/cfg.RATE)


def program_2():
    while True:
        shellmsg = input(">> ")
        words = shellmsg.split(" ")
        if len(shellmsg) > 0:
            if words[0] in COMM:
                COMM[words[0]](s, words[1], words[2], words)
            else:
                chat(s, shellmsg)

thread1 = MyThread(1)
thread2 = MyThread(2)

thread1.start()
thread2.start()
