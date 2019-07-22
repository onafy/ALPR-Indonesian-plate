# Main.py

import cv2
import numpy as np
import os
import imutils
import math

import Preprocess as pp
import DetectChars
import DetectPlates
import PossiblePlate


import requests
import time

# module level variables ##########################################################################
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)

showSteps = False
showStepss = False
###################################################################################################
def main():
        
    #response = requests.get('http://localhost/getImage2.php').text
    #print(response)
    # do something
    
    start = time.time()
    blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()         # attempt KNN training
    if blnKNNTrainingSuccessful == False:                               # if KNN training was not successful
        print("\nerror: KNN traning was not successful\n")  # show error message
        return                                                          # and exit program
    # end if
    

    imgOriginalScene  = cv2.imread("/home/pi/Downloads/gambar/banyak/81.jpg")
    imgOriginalScene  = imutils.resize(imgOriginalScene, width = 1355)

    #imgGrayscale, imgThresh = pp.preprocess(imgOriginalScene)
    if imgOriginalScene is None:                            # if image was not read successfully
        print("\nerror: image not read from file \n\n")  # print error message to std out
        os.system("pause")                                  # pause so user can see error message
        return                                              # and exit program
    # end if



    plateResult = detectPlate(imgOriginalScene)
    end = time.time()
    print(end-start)
    
    #verify before send to db
    #twoChar = plateResult[:2]
    #oneChar = plateResult[:1]
    #ValidTwoChars = ["DD", "DP", "DW", "DC"]
    #ValidOneChars = [ord('B')]
    #    print("Hasil huruf awal sesuai")
        #sendRequest(plateResult, response)
    #elif oneChar in ValidOneChars :
        #sendRequest(plateResult, response)
     #   print("Hasil huruf awal sesuai")
    #else :
        #plateResult = "bukan plat terdeteksi"
    #sendRequest(plateResult, response)
     #   print("Hasil tidak sesuai")
    
    
    cv2.waitKey(0)					# hold windows open until user presses a key

    return
# end main

###################################################################################################

def sendRequest(plateResult, response):
    # api-endpoint 
    URL = "http://localhost/update.php"
    # defining a params dict for the parameters to be sent to the API 
    PARAMS = {'id':response, 'result': plateResult} 
    # sending get request and saving the response as response object 
    r = requests.get(url = URL, params = PARAMS).text 
    # extracting data in json format 
    print(r)
    

###################################################################################################
def detectPlate(imgOriginalScene):
    listBetulan = []
    listCadangan = []
    listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)           # detect plates
   
    listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)        # detect chars in plates

    cv2.imshow("imgOriginalScene", imgOriginalScene)            # show scene image

    if len(listOfPossiblePlates) == 0:                          # if no plates were found
        print("\nno license plates were detected\n")  # inform user no plates were found
        plateResult= "Tidak ada plat terdeteksi"
    else:                                                       # else
                # if we get in here list of possible plates has at leat one plate

                # sort the list of possible plates in DESCENDING order (most number of chars to least number of chars)
        listOfPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)
        
        for i in range(0, len(listOfPossiblePlates)):
            print("chars found in plate number " + str(i) + " = " + listOfPossiblePlates[i].strChars )
            charini = listOfPossiblePlates[i]
            twoChari = (charini.strChars)[:2]
            oneChari = (charini.strChars)[:1]
            threeChari = ((charini.strChars)[:3])[1:]
            ValidTwoChars = ["DD", "DP", "DW", "DC", "DT", "AB", "KT"]
            ValidOneChars = ["B", "N"]
            if twoChari in ValidTwoChars :
                listBetulan.append(charini)
            elif oneChari in ValidOneChars :
                listBetulan.append(charini)
            else :
                if threeChari in ValidTwoChars :
                    listCadangan.append(charini)
                else :
                    continue
    
                # suppose the plate with the most recognized chars (the first plate in sorted by string length descending order) is the actual plate
        if len(listBetulan) == 0:
            if len(listCadangan) == 0 :
                print("\nno characters were detected\n\n")
                plateResult = "Tidak ada plat terdeteksi"
                return
            else :
                licPlate = listCadangan[0]
                print("\nlicense plate read from image = " + (licPlate.strChars)[1:] + "\n")  # write license plate text to std out
                print("----------------------------------------")
                cv2.imshow("imgPlate", licPlate.imgPlate)           # show crop of plate and threshold of plate
                plateResult = (licPlate.strChars)[1:]
                cv2.imshow("imgThresh", licPlate.imgThresh)
        else :
            if len(listCadangan) == 0 :
                licPlate = listBetulan[0]
                plateResult = licPlate.strChars
            else :
                if (len(listCadangan[0].strChars) > len(listBetulan[0].strChars)) :
                    licPlate = listCadangan[0]
                    plateResult = licPlate.strChars[1:]
                else :
                    licPlate = listBetulan[0]
                    plateResult = licPlate.strChars
            print("\nlicense plate read from image = " + plateResult + "\n")  # write license plate text to std out
            print("----------------------------------------")
            cv2.imshow("imgPlate", licPlate.imgPlate)           # show crop of plate and threshold of plate
            cv2.imshow("imgThresh", licPlate.imgThresh)
            cv2.imshow("inbvert", np.invert(licPlate.imgThresh))
            cv2.imwrite("invert02.jpg", np.invert(licPlate.imgThresh))
        #writeLicensePlateCharsOnImage(imgOriginalScene, licPlate)           # write license plate text on the image

        cv2.imshow("imgOriginalScene", imgOriginalScene)                # re-show scene image

        cv2.imwrite("imgOriginalScene.png", imgOriginalScene)           # write image out to file

    # end if else

    return plateResult
###################################################################################################
if __name__ == "__main__":
    main()



















