import serial
import time
import requests
import mysql.connector as mysql
import struct
# Configuración Serial
SER_port = "/dev/ttyUSB0"  # Se ajusta segun el puerto en donde se tenga conectado el sensor por medio de USB
SER_baud = 9600
SER_timeout = 1
SLAVE=1

# Configuración Base de Datos
BD_host = 'localhost' # Nombre del localhost
BD_user = 'daniel'  # Usuario de la Base de datos
BD_passwd = '123'   # Contraseña de la base de datos
BD = 'Sensor'       # Nombre de la base de datos
BD_tabla = 'Datos'  # Nombre de la tabla
mostrar=1
class SensorData:

    def __init__(self):
        # Inicialización de la conexión serial
        self.initialize_serial()

        # Definición de registros Modbus
        self.define_modbus_registers()

    def initialize_serial(self):
        try:
            self.ser = serial.Serial(port=SER_port, baudrate=SER_baud, parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=SER_timeout)
            self.edo_ser = 1
        except serial.SerialException:
            print("No hay comunicación SERIAL")
            self.edo_ser = 0
        return self.edo_ser

    # Estructura de los registros del Modbus
    def define_modbus_registers(self):
        self.B0 = [['0x000A', 2, 'Import kWh', 'kWh', 'kWh', 'XXXXXX.XX', 'datos', 'r', 0],
                   ['0x200C', 1, 'Voltage', 'v', 'V', 'XXX.X', 'datos', 'r', 0],
                   ['0x200D', 1, 'Current', 'i', 'A', 'XX.XX', 'datos', 'r', 0],
                   ['0x200E', 1, 'Active Power', 'P', 'kW', 'XXX.XXX', 'datos', 'r', 0],
                   ['0x200F', 1, 'Reactive Power', 'Q', 'kVArh', 'XXX.XXX', 'datos', 'r', 0],
                   ['0x2010', 1, 'Power Factor', 'pf', ' ', 'X.XXX', 'datos', 'r', 0],
                   ['0x2011', 1, 'Frequency', 'f', 'Hz', 'XX.XX', 'datos', 'r', 0]]

    # Aquí van las funciones CRCMODBUS, CHECAR_msjRESP, ENVIAR_MSJ, LECTURA_BLOQUE
    def CRCMODBUS(self,MSJ):         # calcula CRC a 2 bytes
       crcsum = 0xFFFF
       for x in range(0, len(MSJ)):
          crcsum = crcsum ^ (MSJ[x] & 0x00FF)
          for y in range(0,8):
             crcshift = (crcsum >> 1) & 0x7FFF
             if (crcsum & 0x0001):
                crcsum = crcshift ^ 0xA001
             else:
                crcsum = crcshift
       crc = [crcsum & 0x00FF,crcsum >> 8]
       return crc


    def CHECAR_msjRESP(self,msj_pet,msj_resp):    # verifica esclavo, funcion, num. de bytes y CRC del mensaje recibido
       n = len(msj_resp)                                              # Longitud del msj_resp
       msj = msj_resp[0:n-2]
       crc = self.CRCMODBUS(msj)                                           # Calcula el crc de msj
       if msj_pet[0]==msj_resp[0] and msj_pet[1]==msj_resp[1] and msj_resp[n-2]==crc[0] and msj_resp[n-1]==crc[1]:
          #Bytes 1 y 2 recibidos deben ser igual a la peticion    CRC recien calculado igual al del mensaje recibido
          if msj_pet[1] == 3 and (msj_pet[5]*2+5)==n:                 
             msj_check = 1                                           # En caso de que sea instruccion 0x03
          elif msj_pet[1] == 16 and n==8 and msj_resp[3]==msj_pet[3] and msj_resp[5]==msj_pet[5]:
             msj_check = 1                                            # En caso de que sea instruccion 0x10
          else:
             print("Se esperaban otra cantidad de datos en la respuesta")
             msj_check = 0
       else:
          msj_check = 0   
       return msj_check


    def ENVIAR_MSJ(self,mensaje):     # Envia mensaje MODBUS a un esclavo y espera recibir la respuesta de este
       lon = len(mensaje)
       s_mensaje = struct.pack(lon * 'B', *mensaje)
       resp_lista = intentos = 0
       while resp_lista == 0 and intentos < 6:                       # Se haran 2 intentos de lectura
          time.sleep(0.0005)
          self.ser.write(s_mensaje)                                       # Se transmite el mensaje MODBUS formado
          #time.sleep(0.0008)
          time.sleep(0.0025)
              # ----------- Nueva rutina para leer byte por byte ------------
          tf=time.time()+ 0.15
          cont_bytes = 0
          buff = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # Maximo 150 bytes leidos
          while (time.time() < tf):
             if(self.ser.inWaiting()>0):
                data=self.ser.read(1)
                buff[cont_bytes] = data
                cont_bytes += 1
             msj_resp = buff[0:cont_bytes]
              # --------------- sustituye a ser.readline() --------------
          intentos = intentos+1
          if msj_resp:                                         # Si se recibe mensaje de respuesta
             resp_ascii = [ord(j) for j in msj_resp]                 # Los bytes recibidos por serial deben hacerse ASCII uno por uno
             if self.CHECAR_msjRESP(mensaje,resp_ascii) == 1:             # Se verifica el mesnaje recibido
                resp_lista=1                                         # Si el mensaje recibido cumple se indica que esta listo
                if mostrar==1:
                   print(" mensaje de respuesta: " + str(resp_ascii))
             else:
                print(" mensaje de respuesta con error: " + str(resp_ascii))
                resp_ascii = 'error'                                 # Si no cumple todos los requisitos manda error
                edo_resp = 'ERROR,  la respuesta recibida no cumple con lo esperado'
          else:                                                       
             resp_ascii = 'error'                                    # Si no se recibe respuesta
             edo_resp = ' ERROR, no hubo respuesta por parte del dispositivo'
          if resp_lista != 1 and intentos == 2:
             time.sleep(1)
             
       if resp_ascii == 'error':   
          print(edo_resp)
       return resp_ascii


    def MODBUS_REGS(self):
    #---------------------------------------------------------------------------
    #           REG  words  description  item  unit  format     database  state  
       global B0
       B0 = [['0x000A',2,'Import kWh','kWh','kWh','XXXXXX.XX','datos','r',0],
             ['0x200C',1,'Voltage','v','V','XXX.X','datos','r',0],
             ['0x200D',1,'Current','i','A','XX.XX','datos','r',0],
             ['0x200E',1,'Active Power','P','kW','XXX.XXX','datos','r',0],
             ['0x200F',1,'Reactive Power','Q','kVArh','XXX.XXX','datos','r',0],
             ['0x2010',1,'Power Factor','pf',' ','X.XXX','datos','r',0],
             ['0x2011',1,'Frequency','f','Hz','XX.XX','datos','r',0]]
         
         
    def LECTURA_BLOQUE(self):     # Envia mensaje MODBUS a un esclavo y espera recibir la respuesta de este
    #---------------------------------------------------------------------------
        num_variables = len(self.B0)
        reg0 = self.B0[0][0]       # Aqui viene la primera direccion modbus a leer
        
        num_words = 0         # Se cuentan cuantos registros (words) se leeran en el bloque
        for h in range(num_variables):
            num_words = num_words + self.B0[h][1]
            
        print('   Leyendo registros del medidor...')

        mensaje = [SLAVE,3,(int(reg0,16) & 0xFF00)>>8,int(reg0,16) & 0x00FF,0,num_words] 
        crc = self.CRCMODBUS(mensaje)
        mensaje.extend(crc)
        if mostrar == 1: print(mensaje)
        respuesta = self.ENVIAR_MSJ(mensaje)

        if respuesta:
            for j in range(num_variables):
                for k in range(len(self.B0[j][5])):
                    if self.B0[j][5][k] == '.':
                        decs = len(self.B0[j][5])-k-1
                        break
                     
                if self.B0[j][1] == 2:   #####  Si el tipo de variable es 
                    valor = (respuesta[j+3]<<24) + (respuesta[j+4]<<16) + (respuesta[j+5]<<8) + respuesta[j+6]
                elif self.B0[j][1] == 1:
                    valor = (respuesta[(j*2)+3+2]<<8) + respuesta[(j*2)+3+2+1]
                valor = valor/(10.0**decs)
                self.B0[j][8] = valor
                self.B0[j][7] = 'ok'
                
                if mostrar == 1: print(self.B0[j][2] +': '+ str(valor) +'  '+self.B0[j][4])
            error_resp = 'ok'
            
        else:
            print("Error al leer el BLOQUE ")
            for g in range(num_variables):
                self.B0[7] = 'er'
            error_resp = 'error'
        
        return error_resp
    

    def get_sensor_data(self):
        self.LECTURA_BLOQUE()
        sensor_data = {
            'voltaje': self.B0[1][8],
            'corriente': self.B0[2][8],
            'potencia_activa': self.B0[3][8],
            'potencia_reactiva': self.B0[4][8],
            'factor_de_potencia': self.B0[5][8]
        }
        return sensor_data

    def save_data_to_db(self, data):
        """Guarda los datos en la base de datos."""
        try:
            connection = mysql.connect(host=BD_host, user=BD_user, passwd=BD_passwd, db=BD)
            cursor = connection.cursor()

            query = """
                INSERT INTO {} (voltaje, corriente, potencia_activa, potencia_reactiva, factor_de_potencia)
                VALUES (%s, %s, %s, %s, %s)
            """.format(BD_tabla)
            
            values = (data['voltaje'], data['corriente'], data['potencia_activa'], 
                      data['potencia_reactiva'], data['factor_de_potencia'])

            cursor.execute(query, values)
            connection.commit()
            connection.close()
            print("Datos guardados en la base de datos con éxito.")
        except mysql.Error as e:
            print(f"Error al guardar los datos en la base de datos: {e}")

    def send_to_php(self, data):
        url = "http://148.202.13.95/Sensor.php"
        try:
            response = requests.post(url, data)
            if response.status_code == 200:
                print("Datos enviados correctamente")
            else:
                print(f"Error al enviar los datos. Código: {response.status_code}")
        except Exception as e:
            print(f"Error al enviar los datos: {e}")


if __name__ == "__main__":
    sensor = SensorData()
    while True:
        data = sensor.get_sensor_data()
        sensor.save_data_to_db(data)  # Guardar en la base de datos
        sensor.send_to_php(data)  # Enviar a PHP de ser necesario
        time.sleep(1)
