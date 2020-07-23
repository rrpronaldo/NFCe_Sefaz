from imutils.video import VideoStream
from pyzbar import pyzbar
import datetime
import imutils
import time
import cv2
import re
import requests
import pandas as pd
from NFCeDecode import NFCeDecode

import warnings
warnings.filterwarnings("ignore")

found = set()
regex_chave = "p=(\\d{44})"
path_csv_cupons = "./data/cupons.csv"

def detectImage():
    cam = cv2.VideoCapture(0)
    nfce = NFCeDecode()
    data = pd.read_csv(path_csv_cupons)
    print(data)
    found = set(data['Chave'])
    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it to
        # have a maximum width of 400 pixels
        #frame = vs.read()
        _, frame = cam.read()
        #frame = imutils.resize(frame, width=400)
        # find the barcodes in the frame and decode each of the barcodes
        barcodes = pyzbar.decode(frame)

        # loop over the detected barcodes
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw
            # the bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # the barcode data is a bytes object so if we want to draw it
            # on our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            #Extract key of NFCe from QRCode URL
            chave = re.findall(regex_chave, barcodeData)[0]
            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(frame, text, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            # if the barcode text is currently not in our CSV file, write
            # the timestamp + barcode to disk and update the set
            
            if chave not in found:
                print("[INFO] Connecting to NFCe URL ...")
                
                url = "https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-COM_2.asp?chaveNFe="+ chave +"&HML=false&NFFCBA06010"

                page = requests.post(url)
                
                if page.status_code == 200:
                    found.add(chave)

                    new_data = nfce.get_data(page)
                    new_data['Chave'] = chave
                    data = pd.concat([data, new_data],axis=0, ignore_index=True)
                    print(data)
                else:
                    print("Problem with connecting to the page of Sefaz: ", page.status_code)


            #	csv.write("{},{}\n".format(datetime.datetime.now(),
            #		barcodeData))
            #	csv.flush()

        # show the output frame
        cv2.imshow("Barcode Scanner", frame)
    
        # if the `q` or 'ESC' key was pressed, break from the loop
        #print(cv2.waitKey(1))
        key = cv2.waitKey(1)
        if (key == 27) or (key == 113):
            break  # esc to quit
    
    data.to_csv(path_csv_cupons, index=False)
    # close the output CSV file do a bit of cleanup
    print("[INFO] cleaning up...")
    #csv.close()
    cv2.destroyAllWindows()


def main():
    detectImage()


if __name__ == '__main__':
    print("[INFO] starting video stream...")
    time.sleep(1.0)
    main()