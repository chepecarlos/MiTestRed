import argparse
import subprocess
import csv
import re
from datetime import datetime
import time

parser = argparse.ArgumentParser(description='Heramienta para guardar mediciones de red')
parser.add_argument('--intervalo', '-i', help="Intervalo entre toma de datos", type=int)
parser.add_argument('--archivo', '-f', help="Archovo a guardar la data")


def ObtenerEstadoRed():
    comando = 'speedtest'
    NivelAcptable = 4  # Velocidad mas baja aceptable de subida

    print("Empezando a test con speedtest ...")
    RespuestaComando = subprocess.Popen([comando, '-p', 'no'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    R = RespuestaComando.communicate()

    Data = list()
    Fecha = datetime.now().strftime('%d-%m-%Y')
    Hora = datetime.now().strftime('%H:%M:%S')
    Data.append(Fecha)
    Data.append(Hora)

    R = R[0].decode('utf-8')
    if R == "":
        print("@" * 20)
        print("Error Fatal de Speedtest")
        print("@" * 20)
        Data.append("Error Fatal")
        return Data
    
    R = R.split('\n')

    print("-" * 40)
    print(f"Data Actual {Hora}")
    Error = False
    for Linea in R:
        if "Latency" in Linea:
            Numero = re.findall("\d+\.\d+", Linea)
            Data.append(Numero[0])
            print(f"Delay-> {Numero[0]}")
        elif "Download" in Linea:
            Numero = re.findall("\d+\.\d+", Linea)
            Data.append(Numero[0])
            print(f"Descarga-> {Numero[0]}")
        elif "Upload" in Linea:
            Numero = re.findall("\d+\.\d+", Linea)
            Data.append(Numero[0])

            if float(Numero[0]) <= NivelAcptable:
                Error = True

            print(f"Subida-> {Numero[0]}")
        elif "Result" in Linea:
            url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', Linea)
            Data.append(url[0])
            print(f"URL-> {url[0]}")

    if Error:
        print("*" * 40)
        print("Eror en Velocidad de Red " * 5)
        Data.append("1")
        print("*" * 40)

    return Data


def AgregarDato(Archivo):
    with open(Archivo, mode='a') as csv_file:
        Data = ObtenerEstadoRed()
        writer = csv.writer(csv_file)
        writer.writerow(Data)


if __name__ == "__main__":

    args = parser.parse_args()
    Intervalo = 1
    archivo = 'Data.csv'

    if args.intervalo:
        print(f"Configurando cada {args.intervalo} Minutos")
        Intervalo = args.intervalo

    if args.archivo:
        archivo = args.archivo
    print(f"Salvando en {archivo}")

    while True:
        AgregarDato(archivo)
        print(f"Esperando {Intervalo} Minutos")
        time.sleep(Intervalo * 60)
