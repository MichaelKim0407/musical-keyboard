from contextlib import contextmanager
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
            output: m.Output,
            config: MidiConfig,
    ):
        self.output = output
        self.config = config

    def note_on(
            self,
            note: int,
            *,
            velocity: int = None,
            channel: int = 0,
    ) -> None:
        if velocity is None:
            velocity = self.config.velocity

        self.output.note_on(
            note,
            velocity=velocity,
            channel=channel,
        )

    def note_off(
            self,
            note: int,
            *,
            velocity: int = None,
            channel: int = 0,
    ) -> None:
        if velocity is None:
            velocity = self.config.velocity

        self.output.note_off(
            note,
            velocity=velocity,
            channel=channel,
        )

    def __call__(self, method, *args, **kwargs):
        getattr(self, method)(*args, **kwargs)


@contextmanager
def init_midi(config: MidiConfig) -> MidiOutput:
    try:
        m.init()
        assert m.get_init()
        port = m.get_default_output_id()
        output = m.Output(port)
        yield MidiOutput(output, config)
    finally:
        m.quit()
