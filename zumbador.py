import RPi.GPIO as GPIO
import time

def zumbador(pin, high_time, low_time):
    """
    Función para hacer parpadear un LED conectado a un pin GPIO específico.

    Parámetros:
        pin (int): Número del pin GPIO en modo BCM.
        high_time (float): Tiempo en segundos que el LED permanecerá encendido.
        low_time (float): Tiempo en segundos que el LED permanecerá apagado.
    """
    GPIO.setwarnings(False)  # Desactiva las advertencias
    GPIO.setmode(GPIO.BCM)   # Usa numeración BCM
    GPIO.setup(pin, GPIO.OUT)  # Configura el pin como salida
    
    try:
        GPIO.output(pin, GPIO.HIGH)  # Enciende el Zumbador
        time.sleep(high_time)        # Espera el tiempo configurado
        GPIO.output(pin, GPIO.LOW)   # Apaga el LED
        time.sleep(low_time)         # Espera el tiempo configurado
    except KeyboardInterrupt:
        GPIO.cleanup()  # Limpia los pines GPIO al interrumpir el programa

# Ejemplo de uso:
# blink_led(pin=18, high_time=1, low_time=2)
