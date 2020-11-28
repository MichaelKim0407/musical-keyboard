from dataclasses import dataclass

import pygame.midi as m


@dataclass
class MidiConfig:
    velocity: int = 127


class MidiOutput:
    NOTE_ON = 'note_on'
    NOTE_OFF = 'note_off'

    def __init__(
            self,
            config: MidiConfig,
    ):
        self.config = config

        self._output: m.Output = None
        self._on_notes = set()

    def __enter__(self) -> 'MidiOutput':
        if not m.get_init():
            m.init()

        port = m.get_default_output_id()
        self._output = m.Output(port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for note in set(self._on_notes):
            self.note_off(note)

    def note_on(
            self,
            note: int,
            *,
            velocity: int = None,
            channel: int = 0,
    ) -> None:
        if velocity is None:
            velocity = self.config.velocity

        self._output.note_on(
            note,
            velocity=velocity,
            channel=channel,
        )
        self._on_notes.add(note)

    def note_off(
            self,
            note: int,
            *,
            velocity: int = None,
            channel: int = 0,
    ) -> None:
        if velocity is None:
            velocity = self.config.velocity

        self._output.note_off(
            note,
            velocity=velocity,
            channel=channel,
        )
        if note in self._on_notes:
            self._on_notes.remove(note)

    def __call__(self, method, *args, **kwargs):
        getattr(self, method)(*args, **kwargs)
