# Visible

Software in grado di eseguire un _object tracking_ di un qualsisi oggetto attraverso una sorgente video, sviluppato assieme allo studente Antonio Strippoli.

## Esecuzione

Installare innanzitutto OpenCV e poi lanciare il seguente comando per soddisfare le dipendenze:

`sudo pip install -r requirements.txt`

In seguito, eseguire lo script principale attraverso il comando seguente se la sorgente selezionata è la WebCam:

`python Visible.py `

Altrimenti, per tracciare un oggetto in un qualsiasi video:

`python Visible.py --video /home/videoexample.mov `
