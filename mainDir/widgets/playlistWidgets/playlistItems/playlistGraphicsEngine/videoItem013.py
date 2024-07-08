import shutil

from PyQt6.QtWidgets import *

from mainDir.widgets.playlistWidgets.playlistItems.playListData.videoData import VideoData
from mainDir.widgets.playlistWidgets.playlistItems.playlistGraphicsEngine.baseItem import BaseItem
from mainDir.widgets.playlistWidgets.playlistItems.playListData.audioData import AudioDataThread


class ItemVideo(BaseItem):
    """
    Classe per gestire l'interfaccia utente PyQt per i dati video.
    """

    def __init__(self, filePath=None, parent=None):
        """
        Inizializza la classe ItemVideo.

        :param filePath: Percorso del file video
        :param parent: Oggetto padre
        """
        super().__init__(parent)
        self.initConnections()
        self.name = ""
        self.path = ""
        self.video_data = None
        if filePath:
            self.loadVideoFile(filePath)

    def initConnections(self):
        """
        Inizializza le connessioni dei segnali.
        """
        super().initConnections()
        self.btnLoad.clicked.connect(self.loadItem)
        self.btnEdit.clicked.connect(self.editItem)
        self.btnRefresh.clicked.connect(self.refreshItem)

    def loadItem(self):
        """
        Apre una finestra di dialogo per selezionare un file video e caricarlo.
        """
        container_filters = []
        for container in VideoData.codec.keys():
            container_filters.append(f"*.{container}")
        all_containers_filter = f"Video Files ({' '.join(container_filters)})"
        all_files_filter = "All Files (*)"
        codec_filters = []
        for container, codecs in VideoData.codec.items():
            for codec in codecs:
                codec_filters.append(f"{codec.upper()} Files (*.{container})")

        file_filter = ";;".join([all_containers_filter, all_files_filter] + codec_filters)
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select Video', '', file_filter)
        if filePath:
            self.loadVideoFile(filePath)

    def loadVideoFile(self, filePath):
        """
        Carica il file video e aggiorna l'interfaccia utente.

        :param filePath: Percorso del file video
        """
        self.video_data = VideoData(filePath)
        self.name = self.video_data.name
        self.path = self.video_data.filePath

        self.setThumbnail(self.video_data.thumbnail)
        self.setFileName(self.name)
        self.setStartAt("00:00")
        self.update()
        self.updateVideoLabels(self.video_data.video_info)

        self.audio_thread = AudioDataThread(filePath, self.video_data.temp_folder)
        self.audio_thread.audioInfoCalculated.connect(self.updateAudioLabels)
        self.audio_thread.start()

    def updateVideoLabels(self, video_info_dict):
        """
        Aggiorna le etichette dell'interfaccia utente con le informazioni del video.

        :param video_info_dict: Dizionario con le informazioni del video
        """
        video_codec = video_info_dict.get('codec_name', 'Unknown')
        width = video_info_dict.get('width', '0000')
        height = video_info_dict.get('height', '0000')
        fps = video_info_dict.get('fps', '0')
        duration = float(video_info_dict.get('duration', '0'))
        duration_minutes, duration_seconds = divmod(int(duration), 60)
        self.setMediaCodec(f"{video_codec}: {width}x{height}@{fps}fps")
        self.setEndAt(f"{duration_minutes:02}:{duration_seconds:02}")

    def updateAudioLabels(self, audio_info_dict):
        """
        Aggiorna le etichette dell'interfaccia utente con le informazioni audio.

        :param audio_info_dict: Dizionario con le informazioni audio
        """
        audio_codec = audio_info_dict.get('codec_name', 'Unknown')
        sample_rate = audio_info_dict.get('sample_rate', '0000')
        channels = int(audio_info_dict.get('channels', '0'))
        minutes = audio_info_dict.get('duration_minutes', 0)
        seconds = audio_info_dict.get('duration_seconds', 0)
        avg_volumes = audio_info_dict.get('avg_volumes', [])
        avg_volume_str = ', '.join([f"Ch{idx + 1}: {vol:.2f}dB" for idx, vol in enumerate(avg_volumes)])
        snr = audio_info_dict.get('snr', 0)
        self.setAudioCodec(f"{audio_codec}: {sample_rate}Hz {channels}ch duration {minutes:02}:{seconds:02}")
        self.setVolume(f"Avg Vol: {avg_volume_str} SNR: {snr:.2f}dB")

    def refreshItem(self):
        """
        Aggiorna l'interfaccia utente con le informazioni del video.
        """
        if self.path:
            shutil.rmtree(self.video_data.temp_folder, ignore_errors=True)
        self.loadVideoFile(self.path)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = ItemVideo()
    win.show()
    sys.exit(app.exec())
