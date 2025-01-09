from boton import setup_gpio_boton_led, get_button_state, encendido
from sr_temp_humedad import setup_sensor_tyh, read_sensor_tyh
from distancia import GroveUltrasonicRanger
from zumbador import zumbador
from inicio_bicicleta import obtener_distancia_actual, obtener_km_total_anterior
from datetime import date  # Librería para obtener la fecha actual
import RPi.GPIO as GPIO  # Biblioteca para control de GPIO en Raspberry Pi
import time
from grove.gpio import GPIO as GroveGPIO  # Librería para manejar sensores Grove
import smbus2 as smbus  # Biblioteca para comunicación I2C
import csv  # Para trabajar con archivos CSV
import pandas as pd  # Para manipulación de datos tabulares
import threading  # Para manejar múltiples hilos
from flask import Flask, jsonify  # Librerías para crear una API con Flask

# --- Parámetros configurables ---
LED_PIN = 16  # Pin GPIO para el LED
BUTTON_PIN = 17  # Pin GPIO para el botón

# Configuración inicial de GPIO
GPIO.setmode(GPIO.BCM)  # Usa numeración BCM
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Configura resistencia pull-up en el botón
distancia_acumulada = 0  # Variable para acumular distancia recorrida

# Inicialización del bus I2C
bus = smbus.SMBus(1)
ADC_ADDRESS = 0x04  # Dirección del ADC
CHANNEL_A0 = 0x10  # Canal analógico A0

# Configuración de sensores y retardo
DISTANCE_SENSOR_PIN = 5  # Pin para el sensor de distancia
DELAY = 0.1  # Retardo entre lecturas (en segundos)

SENSOR_HyT = "11"  # Tipo de sensor de temperatura y humedad (DHT11)
SENSOR_PIN = 12  # Pin GPIO del sensor
Z_PIN = 18  # Pin GPIO para el zumbador

# Archivos CSV para almacenamiento de datos
CSV_FILE = "datos_sensores.csv"  # Archivo para guardar datos iniciales
csv_recorrido = "valores_analogicos.csv"  # Archivo para guardar datos del recorrido
#distance_sensor = GroveUltrasonicRanger(DISTANCE_SENSOR_PIN)
# Crear la aplicación Flask para la visualización de datos
app = Flask(__name__)

# --- Funciones auxiliares ---

def read_analog(channel):
    """
    Lee el valor analógico del canal especificado del ADC.
    """
    try:
        bus.write_byte(ADC_ADDRESS, channel)  # Selecciona el canal
        time.sleep(0.1)  # Tiempo para estabilizar el ADC
        value = bus.read_word_data(ADC_ADDRESS, channel)  # Lee el valor analógico
        return value
    except Exception as e:
        print("Error leyendo el valor:", e)
        return None

def transform(valor_analógico):
    """
    Convierte un valor analógico en velocidad (km/h).
    """
    kmh = round(valor_analógico * 100 / 4095, 3)  # Escalado de la lectura
    return kmh

def guardar_datos_csv_iniciales(dia, distancia, humedad, temperatura, alarma, km_total, presion):
    """
    Almacena los datos iniciales en un archivo CSV.
    """
    encabezados = ["Fecha", "Grosor Pastilla (cm)", "Humedad (%)", "Temperatura (°C)", "Alarma", "Km Total", "Presión"]
    try:
        with open(CSV_FILE, mode='a', newline='') as archivo:
            escritor = csv.writer(archivo)
            if archivo.tell() == 0:  # Si el archivo está vacío, agregar encabezados
                escritor.writerow(encabezados)
            escritor.writerow([dia, distancia, humedad, temperatura, alarma, km_total, presion])
        print("Datos guardados en el CSV correctamente.")
    except Exception as e:
        print(f"Error al guardar datos en CSV: {e}")

def home():
    """
    Espera a que el botón sea presionado para iniciar las acciones del sistema.
    """
    print("Esperando pulsación del botón...")
    try:
        while True:
            button_pressed = get_button_state(BUTTON_PIN)  # Verifica el estado del botón
            if button_pressed:
                print("Botón presionado. Saliendo de 'home'.")
                break  # Sale del bucle si el botón es presionado
            time.sleep(DELAY)  # Retardo para evitar lecturas excesivas
    except KeyboardInterrupt:
        GPIO.cleanup()  # Limpia la configuración de GPIO en caso de interrupción
        print("Programa interrumpido manualmente.")

def calcular_presion(temperatura):
    """
    Calcula la presión adecuada (en bares) según la temperatura exterior.
    Si la temperatura no está en la tabla, realiza una interpolación lineal.
    """
    # Tabla de temperaturas y presiones
    tabla = {
        4.4: 6.7,
        10.0: 7.1,
        15.6: 7.6,
        26.7: 8.4
    }
    
    # Si la temperatura está exactamente en la tabla
    if temperatura in tabla:
        return tabla[temperatura]

    # Ordenar las temperaturas en la tabla
    temperaturas = sorted(tabla.keys())

    # Si la temperatura está fuera del rango definido en la tabla
    if temperatura < temperaturas[0]:  # Menor que el mínimo
        return tabla[temperaturas[0]]
    elif temperatura > temperaturas[-1]:  # Mayor que el máximo
        return tabla[temperaturas[-1]]

    # Si la temperatura está entre dos valores, realizar interpolación lineal
    for i in range(len(temperaturas) - 1):
        t_actual = temperaturas[i]
        t_siguiente = temperaturas[i + 1]

        if t_actual <= temperatura <= t_siguiente:
            p_actual = tabla[t_actual]
            p_siguiente = tabla[t_siguiente]

            # Fórmula de interpolación lineal
            presion = p_actual + (p_siguiente - p_actual) * ((temperatura - t_actual) / (t_siguiente - t_actual))
            return round(presion, 2)  # Redondear a 2 decimales
    
def csv_has_rows(csv_recorrido):
    """
    Verifica si el archivo CSV del recorrido tiene filas de datos.
    """
    with open(csv_recorrido, 'r') as file:
        reader = csv.reader(file)
        try:
            next(reader)  # Salta el encabezado
            return any(row for row in reader)  # Comprueba si hay filas
        except StopIteration:
            return False  # El archivo está vacío

def condiciones_iniciales():
    """
    Ejecuta las configuraciones iniciales al iniciar el sistema.
    """
    print("Condiciones iniciales")
    alarma = 'buen estado'
    today = date.today()  # Fecha actual

    # Inicialización de sensores
    distance_sensor = GroveUltrasonicRanger(DISTANCE_SENSOR_PIN)
    sensor_tyh = setup_sensor_tyh(SENSOR_HyT, SENSOR_PIN)

    try:
        # Lectura de distancia
        distance = distance_sensor.get_distance()
        print(f"Distancia detectada: {distance:.2f} cm")
        if distance > 4.00:  # Activar zumbador si la distancia es mayor a 5 cm
            zumbador(Z_PIN, high_time=1, low_time=2)
            alarma = 'urgente cambiar pastillas de freno'
        if distance > 3.00:  # Encender LED si la distancia es mayor a 4 cm
            encendido(LED_PIN, delay=1000)
            alarma = 'recomendacion cambiar pastillas de freno'
    except Exception as e:
        print("Error al leer distancia:", e)

    humi, temp = read_sensor_tyh(sensor_tyh)  # Lectura de temperatura y humedad

    if csv_has_rows(csv_recorrido):
        print("tiene columnas ")
        if csv_has_rows(CSV_FILE):
            df = pd.read_csv(csv_recorrido)
            df2 = pd.read_csv(CSV_FILE)
            print(df['Distancia (km)'].iloc[-1])
            km_total = df['Distancia (km)'].iloc[-1] + df2['Km Total'].iloc[-1]
        else:
            km_total = 0  # Valor inicial para nuevos usuarios
    else:
        print("NO tiene columnas ")
        km_total = 0  # Valor inicial para nuevos usuarios

    presion = calcular_presion(temp)
    guardar_datos_csv_iniciales(today, distance, humi, temp, alarma, km_total, presion)

@app.route('/data_visualization', methods=['GET'])
def data_visualization():
    """Simula la pulsación del botón."""
    try:
        # Leer los valores del sensor
        sensor_tyh = setup_sensor_tyh(SENSOR_HyT, SENSOR_PIN)
        humi, temp = read_sensor_tyh(sensor_tyh)


        distance_sensor = GroveUltrasonicRanger(DISTANCE_SENSOR_PIN)
        distance = distance_sensor.get_distance()
        
        alarma = 'buen estado de las pastillas de frenos'
        if distance > 4.00:
            alarma = 'urgencia de cambio de pastillas'
        elif distance > 3.00:
            #encendido(LED_PIN, delay=1000)
            alarma = 'recomendacion de cambio de pastillas'
        # Obtener el último km_total desde datos_sensores.csv
        km_total_anterior = obtener_km_total_anterior()

        # Obtener la última distancia registrada en valores_analogicos.csv
        distancia_actual = obtener_distancia_actual()

        presion = calcular_presion(temp)

        # Calcular el nuevo valor acumulado de kilómetros
        km_total = km_total_anterior + distancia_actual

        # Retorna una respuesta JSON
        return jsonify({
            "status": "success",
            "message": "Datos registrados correctamente",
            "fecha": str(date.today()),
            "grosor_pastilla": round(distance, 2),
            "humedad": round(humi, 1) if humi is not None else "N/A",            
            "temperatura": round(temp, 1) if temp is not None else "N/A",
            "alarma": alarma,
            "km_total": round(km_total, 3),
            "presion" : presion
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Ejecutar la aplicación Flask
def inicio_recorrido():

    distancia_acumulada = 0


    # Abre el archivo CSV en modo escritura y agrega el encabezado
    with open(csv_recorrido, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Velocidad (km/h)", "Tiempo (s)", "Distancia (km)"])

        print("Esperando que se presione el botón para empezar...")

        estado = False  # Variable para controlar el estado de lectura
        start_time = None  # Para almacenar el tiempo de inicio
        try:
            while True:
                button_pressed = GPIO.input(BUTTON_PIN) == GPIO.LOW
                if button_pressed:
                    time.sleep(0.2)  # Anti-rebote
                    estado = not estado  # Alternar estado
                    if estado:
                        print("¡Iniciando lectura de datos!")
                        start_time = time.time()
                    else:
                        print("¡Lectura detenida!")
                        return True
                        break  # Sale del bucle y termina la ejecución

                if estado:
                    valor_analogico = read_analog(CHANNEL_A0)
                    if valor_analogico is not None:

                        velocidad = transform(valor_analogico)
                        tiempo_transcurrido = time.time() - start_time
                        distancia = (velocidad * tiempo_transcurrido) / 3600  # Distancia en km
                        print(distancia)
                        distancia_acumulada = distancia + distancia_acumulada
                        # Escribe los datos en el archivo CSV
                        writer.writerow([velocidad, round(tiempo_transcurrido, 2), round(distancia_acumulada, 3)])

                        # Imprime los valores en la consola
                        print(f"Velocidad: {velocidad} km/h, Tiempo: {round(tiempo_transcurrido, 2)} s, Distancia: {round(distancia_acumulada, 3)} km")
                    else:
                        print("Error al leer el valor analógico.")

                    time.sleep(1)  # Espera 1 segundo entre lecturas

        except KeyboardInterrupt:
            print("\nLectura detenida por el usuario.")
        finally:
            GPIO.cleanup()  # Limpia la configuración de GPIO al final de la ejecución
            print("GPIO limpiado y ejecución finalizada.")


def run_flask_app():
    """Función para ejecutar el servidor Flask."""
    app.run(host="0.0.0.0", port=5002, use_reloader=False)

def main():
    print("Inicio del programa")

    # Configurar GPIO para botón y LED
    setup_gpio_boton_led(LED_PIN, BUTTON_PIN)

    # Crear un hilo para ejecutar el servidor Flask
    hilo_flask = threading.Thread(target=run_flask_app, name="HiloFlask", daemon=True)

    # Iniciar el hilo Flask
    hilo_flask.start()
    
    # Llamar a la función home para esperar el botón
    home()

    # Realizar acciones iniciales después de la pulsación del botón
    condiciones_iniciales()


    inicio_recorrido()
    print("Programa finalizado.")


if __name__ == "__main__":
    main()
    
