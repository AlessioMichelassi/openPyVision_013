import sys

from mainDir.inputs.testClass.uMat_vs_NumpyTest.UMatTest_02_ScreenCapture import VideoApp, FrameConverter

"""
Una simulazione montecarlo è un metodo che generalmente permette di ottenere una soluzione approssimata di un problema
complesso attraverso la generazione di numeri casuali. In questo caso, vogliamo eseguire una simulazione montecarlo
per confrontare le prestazioni di due metodi di elaborazione di frame: UMat e Numpy. Giusto per capire se mediamente 
il frame rate di un metodo è migliore dell'altro visto che ad ogni run si possono ottenere risultati diversi.

Per fare ciò, creeremo una classe
MonteCarloSimulation che eseguirà un numero di test specificato e restituirà i risultati ottenuti. Ogni test verrà
eseguito utilizzando un'applicazione video che acquisisce frame da uno schermo e li visualizza in una finestra. La
classe MonteCarloSimulation conterrà un metodo run_test che eseguirà un test utilizzando un determinato convertitore di
frame (UMat o Numpy). I risultati dei test verranno memorizzati in un dizionario con i nomi dei metodi di elaborazione
dei frame come chiavi e una lista di risultati come valori. Infine, verrà eseguita la simulazione e i risultati verranno
stampati a schermo.
"""


class MonteCarloSimulation:
    def __init__(self, num_tests=10, duration=60):
        self.num_tests = num_tests
        self.duration = duration
        self.results = {'UMat': [], 'Numpy': [], 'UMat_External': []}

    def run_test(self, converter):
        app = VideoApp(sys.argv, converter, duration=self.duration)
        app.exec()
        return app.media_fps

    def run(self):
        for _ in range(self.num_tests):
            fps = self.run_test(FrameConverter())  # Use UMat test
            self.results['UMat'].append(fps)
            # Add other tests as needed with their respective converters
            # self.results['Numpy'].append(self.run_test(NumpyFrameConverter()))
            # self.results['UMat_External'].append(self.run_test(UMatExternalFrameConverter()))
        return self.results


def main():
    simulation = MonteCarloSimulation(num_tests=10, duration=20)
    results = simulation.run()
    print(results)


if __name__ == '__main__':
    main()
