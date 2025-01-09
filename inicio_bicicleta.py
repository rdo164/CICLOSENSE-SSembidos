import smbus2 as smbus
import time
import csv
import RPi.GPIO as GPIO  # Biblioteca para manejar GPIO en Raspberry Pi

# Configuración del GPIO
BUTTON_PIN = 17  # Pin GPIO donde está conectado el botón
GPIO.setmode(GPIO.BCM)  # Usa la numeración BCM
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Configura el pin con resistencia pull-up
distancia_acumulada = 0
# Inicializa el bus I2C
bus = smbus.SMBus(1)
ADC_ADDRESS = 0x04
CHANNEL_A0 = 0x10  

# Función para leer el valor analógico
def read_analog(channel):
    try:
        bus.write_byte(ADC_ADDRESS, channel)
        time.sleep(0.1)  # Tiempo para que el ADC se estabilice
        value = bus.read_word_data(ADC_ADDRESS, channel)
        return value
    except Exception as e:
        print("Error leyendo el valor:", e)
        return None

# Función para transformar los valores analógicos
def transform(valor_analógico):
    kmh = round(valor_analógico * 100 / 4095, 3)
    return kmh

# Archivo CSV donde se guardarán los datos
csv_file = "valores_analogicos.csv"

# Abre el archivo CSV en modo escritura y agrega el encabezado
with open(csv_file, mode="w", newline="") as file:
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
                    break  # Sale del bucle y termina la ejecución

            if estado:
                valor_analogico = read_analog(CHANNEL_A0)
                if valor_analogico is not None:
                    velocidad = transform(valor_analogico)
                    tiempo_transcurrido = time.time() - start_time
                    distancia = (velocidad * tiempo_transcurrido) / 3600  # Distancia en km
                    distancia_acumulada += distancia
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
