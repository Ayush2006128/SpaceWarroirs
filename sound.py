import pygame
import numpy as np


class SoundEngine:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # Initialize mixer for mono (1 channel), 16-bit signed audio
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=1, buffer=512)
        self.channels = pygame.mixer.get_init()[2]

        # Pre-generate sounds so they are ready in memory
        self.sfx_shoot = self._generate_pew()
        self.sfx_boom = self._generate_boom()

    def _make_sound(self, samples):
        audio = np.asarray(samples, dtype=np.int16)
        if self.channels > 1:
            audio = np.column_stack([audio] * self.channels)
        return pygame.sndarray.make_sound(np.ascontiguousarray(audio))

    def _generate_pew(self):
        duration = 0.15
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        frequencies = np.linspace(880, 110, len(t))
        wave = np.sin(2 * np.pi * frequencies * t)
        envelope = np.linspace(1, 0, len(t))
        audio = (wave * envelope * 32767).astype(np.int16)
        return self._make_sound(audio)

    def _generate_boom(self):
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        noise = np.random.uniform(-1, 1, len(t))
        envelope = np.linspace(1, 0, len(t))
        audio = (noise * envelope * 32767).astype(np.int16)
        return self._make_sound(audio)

    def play_shoot(self):
        self.sfx_shoot.play()

    def play_boom(self):
        self.sfx_boom.play()
