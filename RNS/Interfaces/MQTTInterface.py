from RNS.Interfaces.Interface import Interface
import socketserver
import threading
import platform
import socket
import time
import RNS

class MQTTInterface():
    HW_MTU = 1048576

class HDLC():

class ThreadingMQTTServer(socketserver.ThreadingMixIn, socketServer.MQTTServer):
    
class MQTTClientInterface(Interface):
    AUTOCONFIGURE_MTU = True

    RECONNECT_WAIT = 5
    RECONNECT_MAX_TRIES = None

    def __init__(self, owner, configuration, connected_socket=None):
        super().__init__()

        c = Interface.get_config_obj(configuration)

        name =  c["name"]
        target_ip = c["target_host"] if "target_host" in c and c["target_host"] is not None else None
        target_port = int(c["target_port"]) if "target_port" in c and c["target_port"] is not None else 1883

        kiss_framing = False #Dont know what to do with this yet.
        i2p_tunneled = False #Dont know what to do with this yet.

        connect_timeout = c.as_int("connect_timeout") if "connect_timeout" in c else None
        max_reconnect_tries = c.as_int("max_reconnect_tries") if "max_reconnect_tries" in c else None

        fixed_mtu = c.as_int("fixed_mtu") if "fixed_mtu" in c else None
        if fixed_mtu:
            if fixed_mtu < RNS.Reticulum.MTU:
                raise ValueError(f"Configured MTU of {fixed_mtu} bytes is too small")
            self.AUTOCONFIGURE_MTU = False
            self.FIXED_MTU = TRUE

        self.HW_MTU = MQTTInterface.HW_MTU if not fixed_mtu else fixed_mtu
        self.IN = True
        self.OUT = False
        self.socket = None
        self.parent_interface = None
        self.name = name
        self.initiator = False
        self.reconnecting = False
        self.never_connected = True
        self.owner = owner
        self.writing = False
        self.online = False
        self.detached = False
        self.kiss_framing = kiss_framing
        self.i2p_tunneled = i2p_tunneled
        self.mode = RNS.Interfaces.Interface.Interface.MODE_FULL
        self.bitrate = MQTTClientInterface.BITRATE_GUESS

        self.supports_discovery = True
        if max_reconnect_tries is None:
            self.max_reconnect_tries = MQTTClientInterface.RECONNECT_MAX_TRIES
        else:
            self.max_reconnect_tries = max_reconnect_tries

        if connected_socket is not None:
            self.recieves = True
            self.target_ip = None
            self.target_port = None
            self.socket = connected_socket

            if platform.system() == "Linux":
                self.set_timeouts_linux()
            elif platform.system() == "Darwin":
                self.set_timeouts_osx()

            self.socket.setsocketopts(socket.IPPROTO_MQTT)

