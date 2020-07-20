from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2

import warnings
warnings.filterwarnings("ignore")

found = set()

def detectImage():
    cam = cv2.VideoCapture(0)
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
            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(frame, text, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            # if the barcode text is currently not in our CSV file, write
            # the timestamp + barcode to disk and update the set
            if barcodeData not in found:
                found.add(barcodeData)
                print(barcodeData)
            #	csv.write("{},{}\n".format(datetime.datetime.now(),
            #		barcodeData))
            #	csv.flush()

        # show the output frame
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF
    
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
    # close the output CSV file do a bit of cleanup
    print("[INFO] cleaning up...")
    #csv.close()
    cv2.destroyAllWindows()


def main():
    detectImage()


if __name__ == '__main__':
    # initialize the video stream and allow the camera sensor to warm up
    print("[INFO] starting video stream...")
    time.sleep(2.0)
    main()