
# MixBus

Il **MixBus** è una componente fondamentale del nostro sistema di mixing video, responsabile della creazione del clean feed, ovvero il mix tra il segnale di preview e quello di program. Questo permette di ottenere una transizione fluida e professionale tra diverse sorgenti video. È possibile applicare diversi effetti di transizione come il fade, il dissolve, il wipe e lo stinger.

## Funzionamento del MixBus

### Class: `MixBus014`

La classe `MixBus014` è il cuore del mixer video e permette di mixare due oggetti input. Di default, restituisce tramite il metodo `getMix` una tupla: `(preview, program)`.

#### Metodo: `getMix`

- **Descrizione**: Questo metodo restituisce il mix dei due input `preview` e `program`.
- **Output**: 
  - Se l'effetto è impostato su `MIX`, restituisce: 
    ```python
    preview, cv2.addWeighted(_preview_frame, self._fade, _program_frame, 1 - self._fade, 0)
    ```
    Dove `_preview_frame` è il frame di preview e `_program_frame` è il frame di program. La variabile `_fade` è aumentata gradualmente tramite un `QTimer`, generalmente attivato premendo il pulsante "auto" o usando la slide bar per fare il mix.

### Effetti Disponibili

- **MIX**: Effettua una transizione graduale tra `preview` e `program` usando la funzione `cv2.addWeighted`.
- **WIPE**: Effetto di transizione che sposta una sorgente sopra l'altra.
- **STINGER**: Usa una sequenza di immagini con canale alpha per creare un effetto di transizione animato.
- **STILL**: Mostra un'immagine fissa come frame di program.

### Componenti della Classe `MixBus014`

#### `setPreviewInput(videoObject)`

- **Descrizione**: Imposta l'input di preview.
- **Parametri**:
  - `videoObject`: L'oggetto video da impostare come input di preview.

#### `setProgramInput(videoObject)`

- **Descrizione**: Imposta l'input di program.
- **Parametri**:
  - `videoObject`: L'oggetto video da impostare come input di program.

#### `setStill(videoObject)`

- **Descrizione**: Imposta l'immagine di tappo.
- **Parametri**:
  - `videoObject`: L'oggetto immagine da impostare come still.

#### `setEffectType(mixType)`

- **Descrizione**: Imposta il tipo di effetto di transizione.
- **Parametri**:
  - `mixType`: Tipo di effetto (`MIX`, `WIPE`, `STINGER`, etc.).

#### `cut()`

- **Descrizione**: Effettua un taglio immediato, invertendo gli input di preview e program.

#### `startMix()`

- **Descrizione**: Avvia il timer per eseguire il mix.
- **Note**: La variabile `_fade` viene incrementata gradualmente per creare l'effetto di transizione.

### Utilizzo di `MixBus014`

Per testare le funzionalità del MixBus, è possibile utilizzare il file `testMixBus.py`. Questo file include esempi pratici di come impostare e utilizzare la classe `MixBus014` per creare diversi effetti di transizione tra i video.
