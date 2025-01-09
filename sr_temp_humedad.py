import time
import seeed_dht

def setup_sensor_tyh(sensor_type, pin):
    """
    Configura y devuelve una instancia del sensor DHT.
    
    :param sensor_type: Tipo de sensor DHT (e.g., "11" para DHT11, "22" para DHT22).
    :param pin: Número del pin GPIO al que está conectado el sensor.
    :return: Objeto sensor configurado.
    """
    return seeed_dht.DHT(sensor_type, pin)

def read_sensor_tyh(sensor):
    """
    Lee los valores de temperatura y humedad del sensor.
    
    :param sensor: Objeto del sensor DHT configurado.
    :return: Una tupla (humi, temp) con los valores de humedad y temperatura.
    """
    humi, temp = sensor.read()
    return humi, temp

def log_sensor_data_tyh(sensor, delay=1):
    """
    Lee y registra datos de humedad y temperatura en intervalos regulares.
    
    :param sensor: Objeto del sensor DHT configurado.
    :param delay: Tiempo de espera entre lecturas en segundos.
    """
    while True:
        humi, temp = read_sensor(sensor)
        if humi is not None:
            print('DHT{0}, Humedad: {1:.1f}%, Temperatura: {2:.1f}°C'.format(sensor.dht_type, humi, temp))
        else:
            print('DHT{0}, no se pudo leer la humedad. Temperatura: {1:.1f}°C'.format(sensor.dht_type, temp))
        time.sleep(delay)

