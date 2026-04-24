import numpy as np
import pygame


# =========================================================
# SOUND-GENERIERUNG  (synthetisches "Pew Pew" – kein File nötig)
# =========================================================
def make_pew_sound(freq_start=900, freq_end=300, duration=0.08, volume=0.4):
    """Erzeugt einen kurzen Frequenz-Sweep (Laser-/Pew-Sound)."""
    sample_rate = 44100
    n_samples   = int(sample_rate * duration)
    t           = np.linspace(0, duration, n_samples, endpoint=False)

    # Frequenz linear von freq_start nach freq_end sweepen
    freq  = np.linspace(freq_start, freq_end, n_samples)
    wave  = np.sin(2 * np.pi * freq * t)

    # Kurze Attack/Release-Hüllkurve
    envelope        = np.ones(n_samples)
    attack          = int(n_samples * 0.05)
    release         = int(n_samples * 0.3)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[-release:] = np.linspace(1, 0, release)
    wave *= envelope * volume

    # Zu int16 konvertieren und als Sound laden
    samples = (wave * 32767).astype(np.int16)
    sound   = pygame.mixer.Sound(buffer=samples.tobytes())
    return sound

# Laser-Summton (dauerhaftes Brummen)
def make_laser_sound(volume=0.25):
    sample_rate = 44100
    duration    = 0.5
    n_samples   = int(sample_rate * duration)
    t           = np.linspace(0, duration, n_samples, endpoint=False)
    # Zwei überlagerte Sinustöne → klassischer Sci-Fi-Laser-Hum
    wave = (np.sin(2 * np.pi * 180 * t) * 0.6 +
            np.sin(2 * np.pi * 360 * t) * 0.4)
    # Envelope: keine Attack/Release, konstant (loopt)
    samples = (wave * volume * 32767).astype(np.int16)
    return pygame.mixer.Sound(buffer=samples.tobytes())

def create_sound_map():
    LASER_SOUND = make_laser_sound()
    LASER_SOUND.set_volume(0.0)   # startet stumm, wird beim Feuern aufgedreht

    PEW_SOUNDS = [
        make_pew_sound(freq_start=1000, freq_end=250, duration=0.07),
        make_pew_sound(freq_start=850,  freq_end=200, duration=0.09),
        make_pew_sound(freq_start=1100, freq_end=300, duration=0.06),
    ]
    return {
            "laser": LASER_SOUND, 
            "pews": PEW_SOUNDS,
            }
