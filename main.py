# importar paquetes necesarios
from imutils.video import VideoStream
from pyzbar import pyzbar
from pygame import mixer
import argparse
import datetime
import imutils
import time
import cv2


# construye nuestro parser de argumentos y hace el parseo de los argumentos
ap = argparse.ArgumentParser()

# ap.add_argument("-o", "--output", type=str, default="barcodes.csv", help="path to output CSV file containing barcodes")
ap.add_argument("-o", "--output", type=str, default="barcodes.csv", help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())


#Entrada
apAddEntrada = argparse.ArgumentParser()
apAddEntrada.add_argument("-o", "--output", type=str, default="entrada.csv", help="path to output CSV file containing barcodes")
argsEntrada = vars(apAddEntrada.parse_args())

#Salida
apAddSalida = argparse.ArgumentParser()
apAddSalida.add_argument("-o", "--output", type=str, default="salida.csv", help="path to output CSV file containing barcodes")
argsSalida = vars(apAddSalida.parse_args())

while True:
    option = input("Escanear para...\nEntrada: e\nSalida: s\nOpcion ?: ")
    if option == "s" or option == "e":
        if option == "e":
            thisCsv = open(argsEntrada["output"], "a")
        else:
            thisCsv = open(argsSalida["output"], "a")
        break;
    elif option == "csv":
        thisCsv = open(args["output"], "a")
        break;


# inicializa el video y permite que el sensor de la camara comience a escanear
print("[INFO] Iniciando video...")
# para webcam usa este>
# src=0 es la camara de la lap, src=1 es una webcam externa
vs = VideoStream(src=0).start()

time.sleep(2.0)
found = set()

blackList = set()

# loop de frames del video
while True:
    # toma el cuadro(frame) del video y le cambia el tama;o a un maximo de 400 pixeles
    frame = vs.read()
    frame = imutils.resize(frame, width=500, height=600)

    # Encuentra los barcodes o QR y los decodifica:
    barcodes = pyzbar.decode(frame)

    for barcode in barcodes:

        if barcode.data not in blackList:
            blackList.add(barcode.data)

            # extrae los limites de la imagen del codigo de barras y crea una caja alrededor
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # los datos del codigo de barras estan en bytes, si queremos escribirlo en una imagen debemos convertirlo a string primero
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

            # escribe los datos y el tipo de codigo de barras en la imagen
            text = "{} ({}) NO. CONTROL LEIDO".format(barcodeData, barcodeType)
            image = cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 2)
            print(f"BarcodeData (Decode(utf-8)): {barcodeData}")
            mixer.init()
            sound = mixer.Sound('beep.wav')
            sound.play()

            while True:
                cv2.imshow("img", image)
                if cv2.waitKey(2000):
                    break

            cv2.destroyWindow("img")

            thisCsv.write("{}, {}\n".format(datetime.datetime.now(), barcodeData))

            thisCsv.flush()

        else:
            print("Ya se encuentra en registro")


    cv2.imshow("BarcodeScanner", frame)
    key = cv2.waitKey(1) & 0xFF
    # waitkey originalmente tenía valor =1

    # si la tecla 'q' se puls[o, break del loop
    if key == ord("q"):
        break
    elif key == ord("c"):
        blackList.clear()

# End While True


# cierra el archivo CSV de salida y hace limpieza
print("[INFO] limpiando...")
thisCsv.close()
cv2.destroyAllWindows()
vs.stop()
