import time
from grove.gpio import GPIO as GroveGPIO


class GroveUltrasonicRanger:
    """
    Clase para interactuar con el sensor ultrasónico Grove.
    """

    def __init__(self, pin, timeout1=1000, timeout2=10000):
        """
        Inicializa el sensor ultrasónico en el pin especificado.

        :param pin: Número de pin GPIO utilizado.
        :param timeout1: Tiempo máximo para detectar una señal de inicio.
        :param timeout2: Tiempo máximo para detectar el final de la señal.
        """
        self.dio = GroveGPIO(pin)
        self.timeout1 = timeout1
        self.timeout2 = timeout2

    def _get_distance(self):
        """
        Realiza la medición de distancia interna.
        :return: Distancia medida en cm o None si hay error.
        """
        # Enviar señal de disparo
        self.dio.dir(GroveGPIO.OUT)
        self.dio.write(0)
        time.sleep(0.000002)
        self.dio.write(1)
        time.sleep(0.00001)
        self.dio.write(0)

        # Cambiar a modo entrada para recibir señal de eco
        self.dio.dir(GroveGPIO.IN)

        t0 = time.time()
        count = 0
        while count < self.timeout1:
            if self.dio.read():
                break
            count += 1
        if count >= self.timeout1:
            return None

        t1 = time.time()
        count = 0
        while count < self.timeout2:
            if not self.dio.read():
                break
            count += 1
        if count >= self.timeout2:
            return None

        t2 = time.time()

        # Validación de tiempo
        dt = int((t1 - t0) * 1000000)
        if dt > 530:
            return None

        # Calcular distancia en cm
        distance = ((t2 - t1) * 1000000 / 29 / 2 / 10)
        return distance

    
    def get_distance(self):
        """
        Obtiene la distancia medida por el sensor.

        :return: Distancia medida en cm.
        """
        while True:
            dist = self._get_distance()
            if dist:
                return dist
