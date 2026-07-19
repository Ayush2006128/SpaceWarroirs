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
        self.sfx_start = self._generate_start()
        self.sfx_win = self._generate_win()
        self.sfx_game_over = self._generate_game_over()

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

    def _generate_start(self):
        """A short rising arpeggio for a new game."""
        duration = 0.32
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        notes = np.array([440, 554.37, 659.25])
        note_index = np.minimum((t / duration * len(notes)).astype(int), len(notes) - 1)
        wave = np.sin(2 * np.pi * notes[note_index] * t)
        envelope = np.minimum(1, (duration - t) * 8)
        return self._make_sound(wave * envelope * 18000)

    def _generate_win(self):
        """A bright ascending fanfare when all enemies are defeated."""
        duration = 0.62
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        notes = np.array([523.25, 659.25, 783.99, 1046.5])
        note_index = np.minimum((t / duration * len(notes)).astype(int), len(notes) - 1)
        wave = np.sin(2 * np.pi * notes[note_index] * t)
        envelope = np.minimum(1, (duration - t) * 3)
        return self._make_sound(wave * envelope * 20000)

    def _generate_game_over(self):
        """A descending tone with a soft noise tail for game over."""
        duration = 0.7
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        frequency = np.linspace(330, 70, len(t))
        tone = np.sin(2 * np.pi * frequency * t)
        noise = np.random.uniform(-1, 1, len(t)) * 0.12
        envelope = np.linspace(1, 0, len(t)) ** 1.5
        return self._make_sound((tone + noise) * envelope * 22000)

    def play_shoot(self):
        self.sfx_shoot.play()

    def play_boom(self):
        self.sfx_boom.play()

    def play_start(self):
        self.sfx_start.play()

    def play_win(self):
        self.sfx_win.play()

    def play_game_over(self):
        self.sfx_game_over.play()
