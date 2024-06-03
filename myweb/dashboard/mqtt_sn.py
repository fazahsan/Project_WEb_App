import ctypes
import time
from RF24 import RF24

# Cargar la biblioteca MQTT-SN compilada
mqtt_sn_lib = ctypes.CDLL('com_in/assignment/libMQTTSNPacket.so')

# Definir argumentos ctypes y tipos de retorno para las funciones contenedoras
mqtt_sn_lib.create_connect_packet.argtypes = [ctypes.c_char_p, ctypes.c_int]
mqtt_sn_lib.create_connect_packet.restype = ctypes.c_void_p

mqtt_sn_lib.create_subscribe_packet.argtypes = [ctypes.c_char_p, ctypes.c_int]
mqtt_sn_lib.create_subscribe_packet.restype = ctypes.c_void_p

mqtt_sn_lib.create_publish_packet.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
mqtt_sn_lib.create_publish_packet.restype = ctypes.c_void_p

mqtt_sn_lib.create_puback_packet.argtypes = [ctypes.c_int, ctypes.c_int]
mqtt_sn_lib.create_puback_packet.restype = ctypes.c_void_p

# Inicializar nRF24
radio = RF24(22, 0)  # CE, CSN
radio.begin()
radio.setPALevel(RF24.PA_LOW)
radio.openReadingPipe(1, 0xF0F0F0F0E1)
radio.startListening()

class MQTT_SN_Client:
    def __init__(self, radio):
        self.radio = radio
        self.subscribed_topics = {}

    def connect(self, client_id="RaspberryPi", duration=60):
        connect_packet = mqtt_sn_lib.create_connect_packet(client_id.encode('utf-8'), duration)
        self.radio.stopListening()
        self.radio.write(ctypes.string_at(connect_packet, 16)) 
        self.radio.startListening()

    def subscribe(self, topic_name, topic_id):
        subscribe_packet = mqtt_sn_lib.create_subscribe_packet(topic_name.encode('utf-8'), topic_id)
        self.radio.stopListening()
        self.radio.write(ctypes.string_at(subscribe_packet, 16))  
        self.radio.startListening()
        self.subscribed_topics[topic_id] = topic_name

    def publish(self, topic_id, message, qos=0):
        publish_packet = mqtt_sn_lib.create_publish_packet(topic_id, message.encode('utf-8'), qos)
        self.radio.stopListening()
        self.radio.write(ctypes.string_at(publish_packet, 16))  
        self.radio.startListening()

    def send_puback(self, topic_id, msg_id):
        puback_packet = mqtt_sn_lib.create_puback_packet(topic_id, msg_id)
        self.radio.stopListening()
        self.radio.write(ctypes.string_at(puback_packet, 16)) 
        self.radio.startListening()

    def process_message(self, data):
        packet = mqtt_sn_lib.MQTTSNPacket(data)
        if packet.msgType == mqtt_sn_lib.MQTTSNPacket.ADVERTISE:
            print("Received ADVERTISE")
        elif packet.msgType == mqtt_sn_lib.MQTTSNPacket.PUBLISH:
            topic_id = packet.topicId
            if topic_id in self.subscribed_topics:
                print(f"Received message on topic {self.subscribed_topics[topic_id]}: {packet.data.decode()}")
                if packet.flags & 0x06 == 0x02:  # QoS 1
                    # Enviar PUBACK para QoS 1
                    self.send_puback(packet.topicId, packet.msgId)
                elif packet.flags & 0x06 == 0x04:  # QoS 2
                    #  QoS 2 (PUBREC, PUBREL, PUBCOMP) flow
                    print("Received QoS 2 message, additional handling required.")
        else:
            print("Received unknown packet")


client = MQTT_SN_Client(radio)
client.connect()

while True:
    if radio.available():
        length = radio.getDynamicPayloadSize()
        if length > 0:
            data = radio.read(length)
            client.process_message(data)
    
   

    time.sleep(1)
