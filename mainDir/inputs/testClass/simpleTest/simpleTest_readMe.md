In questa cartella sono presenti i file per fare dei semplici test con gli input,
giusto per vedere se l'input singolarmente funziona, quante risorse usa e se è
possibile migliorare il numero di fotogrammi riprodotti.

Questi test sono stati utili ad esempio per capire che aggiungere un threading
per processare i fotogrammi in parallelo non è conveniente, in quanto il tempo
di processamento è già molto veloce e il threading aggiunge un overhead che
aggiunge una latenza di una decina di fotogrammi.

![Screenshot dei Timer](mainDir/inputs/testClass/simpleTest/bestLap.png)


Si può ad esempio eseguire uno screenshot di un video in play con un cronometro o di una pagina web con aperto un cronometro e affiancarlo
alla finestra di simple input per vedere di quanto si discosta ciò che è live da ciò che viene mostrato nell'interfaccia.

Per eseguire i file nella cartella è necessario inserire nel terminale:

```
$env:PYTHONPATH="C:\pythonCode\openPyVision_013"
python simpleTest\SimpleTest_01_FullBars.py
```
il test dura 10 secondi alla fine dei quali si chiude automaticamente e stampa
varie informazioni sulle risorse usate e i fotogrammi processati.

ES:
```
Media FPS: 62.46
         9315 function calls (9238 primitive calls) in 10.088 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   10.087   10.087 C:\pythonCode\openPyVision_013\mainDir\inputs\testClass\simpleTest\SimpleTest_01_FullBars.py:52(main)
        1    8.684    8.684    9.992    9.992 {built-in method exec}
      213    0.019    0.000    1.295    0.006 C:\pythonCode\openPyVision_013\mainDir\inputs\testClass\simpleTest\SimpleTest_01_FullBars.py:32(display_frame)
      213    0.780    0.004    0.780    0.004 {built-in method fromImage}
      213    0.488    0.002    0.488    0.002 {built-in method setPixmap}
        1    0.012    0.012    0.096    0.096 C:\pythonCode\openPyVision_013\mainDir\inputs\testClass\simpleTest\SimpleTest_01_FullBars.py:12(__init__)
        1    0.074    0.074    0.074    0.074 {built-in method show}
      624    0.004    0.000    0.013    0.000 C:\pythonCode\openPyVision_013\mainDir\inputs\synchObject.py:17(sync)
      624    0.005    0.000    0.009    0.000 {method 'emit' of 'PyQt6.QtCore.pyqtBoundSignal' objects}
        1    0.000    0.000    0.008    0.008 C:\pythonCode\openPyVision_013\mainDir\inputs\fullBarsGenerator.py:13(__init__)
        1    0.008    0.008    0.008    0.008 C:\pythonCode\openPyVision_013\mainDir\inputs\fullBarsGenerator.py:19(createBars)
      426    0.005    0.000    0.005    0.000 {built-in method setText}
      624    0.001    0.000    0.004    0.000 C:\pythonCode\openPyVision_013\mainDir\inputs\fullBarsGenerator.py:49(capture_frame)
      624    0.002    0.000    0.003    0.000 C:\pythonCode\openPyVision_013\mainDir\inputs\baseClass.py:47(update_fps)
        9    0.000    0.000    0.002    0.000 C:\Users\aless\AppData\Local\Programs\Python\Python312\Lib\enum.py:713(__call__)
        9    0.000    0.000    0.002    0.000 C:\Users\aless\AppData\Local\Programs\Python\Python312\Lib\enum.py:850(_create_)
     1052    0.001    0.000    0.001    0.000 {built-in method time.time}
        9    0.000    0.000    0.001    0.000 C:\Users\aless\AppData\Local\Programs\Python\Python312\Lib\enum.py:515(__new__)
     86/9    0.000    0.000    0.001    0.000 {built-in method __new__ of type object at 0x00007FFCA88198B0}
       77    0.000    0.000    0.001    0.000 C:\Users\aless\AppData\Local\Programs\Python\Python312\Lib\enum.py:249(__set_name__)
        1    0.001    0.001    0.001    0.001 C:\pythonCode\openPyVision_013\mainDir\inputs\baseClass.py:24(__del__)
      104    0.000    0.000    0.001    0.000 C:\Users\aless\AppData\Local\Programs\Python\Python312\Lib\enum.py:383(__setitem__)
      213    0.000    0.000    0.001    0.000 C:\Users\aless\AppData\Local\Programs\Python\Python312\Lib\enum.py:197(__get__)
      213    0.000    0.000    0.000    0.000 C:\pythonCode\openPyVision_013\mainDir\inputs\fullBarsGenerator.py:53(getFrame)
        1    0.000    0.000    0.000    0.000 C:\pythonCode\openPyVision_013\mainDir\inputs\synchObject.py:9(__init__)
        1    0.000    0.000    0.000    0.000 C:\pythonCode\openPyVision_013\mainDir\inputs\testClass\simpleTest\SimpleTest_01_FullBars.py:42(stop_app)
        2    0.000    0.000    0.000    0.000 {built-in method start}

```

Gli input al momento includono:

- videoCapture: cattura da una qualsiasi scheda di acquisizione usb ed è stato testato anche con una decklink 4k pci-e.
- desktopCapture: cattura il desktop e permette di fare un crop per selezionare la parte di desktop da catturare.
- image generator:
  -   fullBars: genera delle barre colorate che scorrono sullo schermo.
  -   smpteBars: genera le barre colorate dello standard SMPTE.
  -   colorGenerator: genera un colore pieno.
  -   checkerboard: genera una scacchiera di colori.
  -   gradient: genera un gradiente di colori che può essere lineare o radiale.
-noise generator: genera del rumore casuale.
    - randomNoise: genera del rumore casuale.
    - perlinNoise: genera del rumore di Perlin.
    - speckleNoise: genera del rumore di speckle.
    - saltAndPepperNoise: genera del rumore di salt and pepper.
- image loader:
    - stillLoader: carica una singola immagine da disco.
    - stingerLoader: carica una sequenza di immagini da disco.
videoPlayer: riproduce un video da disco.

Quando si mettono insieme più input è possibile è necessario che che siano sincronizzati tra loro, per fare questo è possibile usare la classe synchObject che permette di sincronizzare più input tra loro.
tramite il segnale pyqt synch_SIGNAL che può essere collegato ad una funzione di aggiornamento dell'interfaccia grafica.

Tutti gli input restituiscono il frame corrente utilizzando la funzione getFrame() e restituiscono un frame nero se non c'è nessun frame disponibile. Oltre a questo è disponibile una funzione, update_fps(), che permette di aggiornare il numero di fotogrammi al secondo che vengono processati.
E' una variabile quindi può essere presa tramite fps = inputName.frame.

Tutti gli input ereditano da una classe base che permette di avere un'interfaccia comune con alcune operazioni che possono risultare utili per migliorare la qualità dell'immagine:

- flip: permette di capovolgere l'immagine.
- gammaCorrection: permette di cambiare il gamma dell'immagine.
- negative: permette di invertire i colori dell'immagine.
- blur: permette di sfocare l'immagine.
- unSharpMask: permette di applicare un filtro di unSharp.
- selfScreen: che in pratica fa una somma del negativo di un immagine con se stessa e in pratica aumenta la luminosità dell'immagine senza saturare i colori, o aumentare il rumore.

Per aggiungere un nuovo input è necessario creare una nuova classe che erediti da baseClass e implementi
la funzione getFrame(). il frame viene restiruito dalla variabile _frame come oggetto numpy BGR a 8 bit.

