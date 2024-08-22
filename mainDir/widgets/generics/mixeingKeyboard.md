Descrizione della Logica del Sistema di Segnali e Pulsanti del Codice

Il MixerPanelWidget_012 è un'interfaccia utente progettata per simulare un pannello di controllo di un mixer video. Il codice organizza e gestisce i pulsanti necessari per il controllo delle transizioni, la selezione degli input, e le operazioni chiave (keying). Questo widget è fortemente orientato verso l'interazione con segnali, che vengono emessi quando l'utente interagisce con l'interfaccia, e consente di attivare determinate azioni nel sistema.
Segnali Principali

Il sistema utilizza un segnale principale chiamato tally_SIGNAL, che è responsabile della comunicazione tra l'interfaccia utente e la logica di backend del mixer. Questo segnale viene emesso in diversi punti del codice quando l'utente interagisce con i pulsanti o le slider, e passa un dizionario che descrive l'azione richiesta.

Il dizionario passato dal segnale tally_SIGNAL contiene informazioni come il tipo di azione ("previewChange", "programChange", "auto", "cut", "fade", "keyChange", "transitionChange") e l'input selezionato o il valore del fade.
Sistema di Pulsanti

Il pannello contiene diversi gruppi di pulsanti:

Pulsanti di Preview e Program:
    Questi pulsanti consentono di selezionare gli input che andranno in anteprima o in diretta.
    I pulsanti di preview e program sono collegati a funzioni che emettono segnali ogni volta che vengono cliccati, informando il sistema del cambiamento di input.

Pulsanti di Transizione:
    Gestiscono il tipo di transizione da applicare quando si passa da un input all'altro.
    I pulsanti di transizione inviano un segnale che specifica il tipo di transizione selezionata.

Pulsanti Key:
    Questi pulsanti sono utilizzati per applicare sovrapposizioni grafiche come sottopancia, ticker, loghi, ecc.
    Anche questi pulsanti emettono segnali per informare il sistema delle modifiche allo stato dei key.

Pulsanti di Controllo (Auto e Cut):
    Auto: Inizia una transizione automatica che viene gestita da un timer e una slider.
    Cut: Esegue un cambio immediato tra preview e program.

Logica di Controllo

Transizioni Automatiche:
    Quando viene premuto il pulsante Auto, inizia una transizione automatica che cambia gradualmente il valore della slider e inverte gli input di preview e program una volta completata.
    La transizione è gestita da un timer che controlla la durata e la progressione del fade.

Shift e Multi-Pulsanti:
    Il pulsante Shift permette di passare a una seconda serie di input (da 9 a 16), cambiando dinamicamente le etichette e lo stato dei pulsanti visualizzati.
    La logica di Shift assicura che gli input visualizzati corrispondano correttamente agli stati attuali dei pulsanti, sia in modalità normale che con Shift attivato.

Gestione dello Stato dei Pulsanti:
    Lo stato dei pulsanti viene continuamente aggiornato in base alle interazioni dell'utente, mantenendo sempre coerenti gli input selezionati.
    Funzioni come restoreButtonState e updateLabelsAndButtons aiutano a mantenere l'integrità dello stato dei pulsanti, specialmente durante il cambio di input o la modifica delle impostazioni di transizione.

Considerazioni

Questo sistema è progettato per essere altamente modulare, permettendo di estendere o modificare le funzionalità senza impattare negativamente la logica esistente. La chiara separazione tra la logica di controllo e l'interfaccia utente, mediata dall'uso dei segnali, assicura che il codice rimanga manutenibile e facilmente espandibile.