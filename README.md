# MANUAL DE USUARIO
## Requisitos Previos

### 1. Hardware Necesario:
- *Raspberry Pi* con GPIO habilitado.
- *Módulo ADC* compatible con I2C.
- *Sensor de distancia ultrasónico* Grove.
- *Zumbador*.
- *Sensor de temperatura y humedad*.
- *Potenciómetro*.
- *LED*.

### 2. Software Necesario:
- Sistema operativo configurado en la Raspberry Pi.
- Python 3 instalado.
- Bibliotecas necesarias:
  - smbus2
  - GPIO
  - csv
  - pandas (importado como pd)
  - threading
  - Flask
  - jsonify
 
## Instrucciones para la conexión
Necesito los pines

## Instrucciones para le ejecución del sistema

### Paso 1: Enciende la Raspberry Pi y accede a ella por SSH.

### Paso 2: Asegúrate de que el bus I2C esté habilitado:
1. Abre el menú de configuración con sudo raspi-config.
2. Ve a Interface Options > I2C > Habilitar.

### Paso 3: Verifica la conexión a Internet:
Ejecuta el siguiente comando para comprobar si está conectado:
bash
ping -c 4 8.8.8.8


### Paso 4: Configura la red inalámbrica:
1. Ejecuta sudo raspi-config.
2. Navega a 1 System Options > S1 Wireless LAN.
3. Introduce el país.
4. Ingresa el SSID (nombre de tu red) y la contraseña.

### Paso 5: Ejecuta el entorno y el programa principal:
1. Activa el entorno virtual:
   bash
   source myenv/bin/activate
   
2. Navega al directorio del proyecto:
   bash
   cd pruebasunitarias
   cd pr_final
   
3. Ejecuta el programa principal:
   bash
   python3 main_f.py
   

### Paso 6: Interacción con el sistema:
1. Una vez ejecutado con éxito, pulsa el pulsador.
2. Accede a la interfaz web con la URL http://192.168.0.8:5002/data_visualization o al archivo CSV para realizar el mantenimiento preventivo de la bicicleta.
3. Pulsa nuevamente el botón antes de comenzar la ruta.
4. Al finalizar, pulsa otra vez el botón.
