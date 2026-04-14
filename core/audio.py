import os
import random
import pygame

class AudioController:
    def __init__(self):
        """Inizializza il mixer audio e carica i file in memoria."""
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
        
        try:
            pygame.mixer.init(buffer=512)
            self.enabled = True
        except Exception:
            self.enabled = False
            return

        self.beep_sounds = [] # Ora è una lista vuota che conterrà i nostri suoni
        self.alarm_sound = None

        # Caricamento dinamico dei suoni di battitura
        beep_files = ["audio/beep1.wav", "audio/beep2.wav", "audio/beep3.wav"]
        for file in beep_files:
            try:
                sound = pygame.mixer.Sound(file)
                sound.set_volume(0.1) # Mantieni il volume basso
                self.beep_sounds.append(sound) # Aggiunge il suono caricato alla lista
            except FileNotFoundError:
                # Se un file manca, lo salta senza far crashare il programma
                pass 

        # Caricamento Allarme
        try:
            self.alarm_sound = pygame.mixer.Sound("audio/alarm.wav")
            self.alarm_sound.set_volume(0.8)
        except FileNotFoundError:
            pass # Se mancano i file, passa in modalità silenziosa

    def play_bgm(self, file_path: str):
        """Carica e avvia una traccia specifica per il livello."""
        if not self.enabled: return
        try:
            # Se c'è già una musica in esecuzione, la sfumiamo (fadeout) per un cambio dolce
            pygame.mixer.music.fadeout(1000) 
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1) # Loop infinito
        except Exception as e:
            print(f"Errore caricamento audio {file_path}: {e}")

    def stop_bgm(self):
        """Ferma la musica."""
        if self.enabled:
            pygame.mixer.music.stop()

    def play_beep(self):
        """Sceglie casualmente un suono dalla lista e lo riproduce."""
        # Controlliamo che l'audio sia abilitato e che ci sia almeno un suono caricato
        if self.enabled and self.beep_sounds:
            # random.choice estrae un elemento a caso dalla lista
            sound_to_play = random.choice(self.beep_sounds)
            sound_to_play.play()

    def play_alarm(self):
        """Ferma la musica e fa partire l'allarme."""
        if self.enabled and self.alarm_sound:
            self.stop_bgm()
            self.alarm_sound.play()