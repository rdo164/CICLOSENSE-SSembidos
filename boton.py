import RPi.GPIO as GPIO
import time

def setup_gpio_boton_led(led_pin, button_pin):
    """
    Configura los pines GPIO para el LED y el botón.
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def control_led(led_pin, button_pin, delay):
    """
    Controla el LED en función del estado del botón.
    """
    button_pressed = get_button_state(button_pin)
    if button_pressed:
        GPIO.output(led_pin, GPIO.HIGH)  # Enciende el LED
    else:
        GPIO.output(led_pin, GPIO.LOW)  # Apaga el LED

def encendido(led_pin, delay):
    GPIO.output(led_pin, GPIO.HIGH)  # Enciende el LED
    delay(delay)
    GPIO.output(led_pin, GPIO.LOW)  # Apaga el LED


def get_button_state(button_pin):
    """
    Obtiene el estado del botón.
    :return: True si el botón está presionado, False en caso contrario.
    """
    return GPIO.input(button_pin) == GPIO.LOW
