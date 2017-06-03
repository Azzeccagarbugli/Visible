# -*- coding: utf-8 -*-
import argparse
import numpy as np
import cv2

frame = None
roiPts = []
inputMode = False

# Una funzione callback che ci permetterà di acquisire 4 punti ROI dal mouse
def SelectROI(event, x, y, flags, param):
    global frame, roiPts, inputMode

    # Posizionerò un punto solamente se:
    # - Ci troviamo nella modalità INPUT
    # - Abbiamo premuto il pulsante sinistro del mouse
    # - Abbiamo posizionato < di 4 punti
    if inputMode and event == cv2.EVENT_LBUTTONDOWN and len(roiPts) < 4:
        roiPts.append((x, y))                           # Passo le coordinate alla lista
        cv2.circle(frame, (x, y), 4, (0, 255, 0), 2)    # Disegno il cerchio
        cv2.imshow("Visible", frame)                    # Mostro il frame aggiornato


# Acquisizione di un eventuale video in entrata
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help = "Indirizzo per il video da utilizzare per il tracking (opzionale)")
args = vars(ap.parse_args())

if not args.get("video", False):
    cap = cv2.VideoCapture(0)               # Seleziono la webcam
else:
    cap = cv2.VideoCapture(args["video"])   # Seleziono il video

# Inizializzo le finestre che utilizzerò
cv2.namedWindow("Visible")
cv2.moveWindow("Visible", 300, 200)
cv2.namedWindow("Visible - HSV (22)")
cv2.moveWindow("Visible - HSV (22)", 1000, 200)

#Indico che ogni evento causato dal mouse sarà gestito dalla funzione SelectROI
cv2.setMouseCallback("Visible", SelectROI)

# Preparo i criteri di terminazione, il Camshift farà 10 iterazioni o si muoverà al massimo di 1 pt
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
roiBox = None

# Comincio ad analizzare frame per frame
while(1):
    # Ottengo 2 valori:
    # - grabbed è una boleana che mi indica se la lettura del frame ha avuto successo
    # - frame è il frame effettivo del video
    grabbed, frame = cap.read()

    # Se il video è finito, esco dal ciclo
    if not grabbed:
        break

    # Controllo se non ho già una roiBOX pronta
    if roiBox is not None:
        # Converto il frame dal range di colore RGB a quello HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)

        # Applico l'algoritmo CamShift ai punti dati, basandoci sulla roiBOX ottenuta in INPUTMODE
        ret, roiBox = cv2.CamShift(dst, roiBox, term_crit)

        # Disegno la roiBOX traslata nel nuovo frame
        pts = cv2.boxPoints(ret)
        pts = np.int0(pts)
        cv2.polylines(frame,[pts],True, 255,2)

    # Aggiorno le due finestre
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.imshow("Visible", frame)
    cv2.imshow("Visible - HSV (22)", hsv)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("i") and len(roiPts) < 4:
        # Sono entrato nella INPUTMODE. A questo punto clono il frame per poter
        # selezionare comodamente la roiBOX
        inputMode = True
        orig = frame.copy()

        # Continuo il loop fino al termine dell'inserimento dei 4 angoli della roiBOX
        while len(roiPts) < 4:
            cv2.imshow("Visible", frame)
            cv2.waitKey(300)

        # Converto il mio array di punti in uno adatto a numpy e sfrutto la
        # libreria per ricavarmi l'angolo in alto a sinistra e in basso a destra
        roiPts = np.array(roiPts)
        s = roiPts.sum(axis = 1)
        tl = roiPts[np.argmin(s)]
        br = roiPts[np.argmax(s)]

        # Ho finalmente la roi finalizzata e la converto in HSV
        roi = orig[tl[1]:br[1], tl[0]:br[0]]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Mi calcolo l'istogramma per l'istogramma HSV e restituisco la roiBOX finale
        mask = cv2.inRange(roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
        roi_hist = cv2.calcHist([roi], [0], mask, [180], [0, 180])
        roi_hist = cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
        roiBox = (tl[0], tl[1], br[0], br[1])

    # Controllo che il tasto 'q' venga premuto per poter uscire dal programma
    if key == ord("q"):
        break

cv2.destroyAllWindows()
cap.release()
