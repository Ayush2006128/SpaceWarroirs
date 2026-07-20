from __future__ import annotations

import random
from pathlib import Path

import pygame


class MusicManager:
	"""State-driven music playback manager for the game."""

	def __init__(self, volume: float = 0.45) -> None:
		self._root_dir = Path(__file__).resolve().parents[3]
		self._music_dir = self._root_dir / "assets" / "music"

		self._playing_tracks = [
			self._music_dir / "playing" / "playing1.mp3",
			self._music_dir / "playing" / "playing2.mp3",
		]
		self._screen_tracks = {
			"init": self._music_dir / "screens" / "intro_music.mp3",
			"game_over": self._music_dir / "screens" / "game_over_music.mp3",
			"win": self._music_dir / "screens" / "game_win_music.mp3",
		}

		self._current_state: str | None = None
		self._current_playing_track_index: int | None = None
		self._track_end_event = pygame.USEREVENT + 11

		self._volume = volume
		pygame.mixer.music.set_endevent(self._track_end_event)
		pygame.mixer.music.set_volume(volume)
		self._muted = False

	def play_for_state(self, state: str) -> None:
		if state == self._current_state:
			return

		if state == "playing":
			self._start_random_playing_track()
			return

		if state in self._screen_tracks:
			self._current_state = state
			self._current_playing_track_index = None
			self._load_and_play(self._screen_tracks[state], loops=-1)
			return

		self.stop()

	def handle_event(self, event: pygame.event.Event) -> bool:
		if event.type != self._track_end_event:
			return False

		if self._current_state == "playing":
			self._play_other_playing_track()
		return True

	def stop(self) -> None:
		pygame.mixer.music.stop()
		self._current_state = None
		self._current_playing_track_index = None

	def set_muted(self, muted: bool) -> None:
		self._muted = muted
		if muted:
			# Zero volume first for an instant cutoff, then stop.
			pygame.mixer.music.set_volume(0)
			pygame.mixer.music.stop()
		else:
			pygame.mixer.music.set_volume(self._volume)
			state = self._current_state
			self._current_state = None
			if state:
				self.play_for_state(state)

	def _start_random_playing_track(self) -> None:
		available_tracks = self._available_playing_tracks()
		if not available_tracks:
			self.stop()
			return

		self._current_state = "playing"
		self._current_playing_track_index = random.randrange(len(available_tracks))
		self._load_and_play(available_tracks[self._current_playing_track_index], loops=0)

	def _play_other_playing_track(self) -> None:
		available_tracks = self._available_playing_tracks()
		if not available_tracks:
			self.stop()
			return

		if len(available_tracks) == 1:
			self._current_playing_track_index = 0
		elif self._current_playing_track_index is None:
			self._current_playing_track_index = random.randrange(len(available_tracks))
		else:
			self._current_playing_track_index = 1 - self._current_playing_track_index

		self._load_and_play(available_tracks[self._current_playing_track_index], loops=0)

	def _load_and_play(self, track_path: Path, loops: int) -> None:
		if self._muted:
			return
		if not track_path.exists():
			return
		pygame.mixer.music.load(str(track_path))
		pygame.mixer.music.play(loops=loops)

	def _available_playing_tracks(self) -> list[Path]:
		return [track for track in self._playing_tracks if track.exists()]
