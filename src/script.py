import typing
from dataclasses import dataclass
from functools import cached_property

import pygame.midi
from returns import returns

from midi import MidiConfig


@dataclass(frozen=True)
class MidiEvent:
    NOTE_ON = 'note_on'
    NOTE_OFF = 'note_off'

    _NAME_SORT = (
        NOTE_OFF,
        NOTE_ON,
    )

    time: float
    name: str
    note: int

    def __call__(
            self,
            midi_out: pygame.midi.Output,
            midi_config: MidiConfig,
    ):
        getattr(midi_out, self.name)(self.note, midi_config.velocity)

    @cached_property
    def _sort(self):
        return self.time, self._NAME_SORT.index(self.name), self.note

    def __lt__(self, other: 'MidiEvent'):
        return self._sort < other._sort


class Script:
    def __init__(self, filename: str):
        self.filename = filename

    @cached_property
    @returns(list)
    def notes(self) -> typing.Sequence[typing.Tuple[int, float, float]]:
        offset = 0
        bar = 0
        base = 0

        import csv
        with open(self.filename) as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or row[0].startswith('#'):
                    continue

                if row[0] == 'SET':
                    if row[1] == 'BAR':
                        bar = int(row[2])
                    elif row[1] == 'BASE':
                        base = int(row[2])
                    continue

                if row == ['-']:
                    offset += bar
                    continue

                yield (
                    base + int(row[0]),
                    offset + float(row[1]),
                    float(row[2]),
                )

    @cached_property
    @returns(sorted)
    def midi_events(self) -> typing.Sequence[MidiEvent]:
        for note, start, duration in self.notes:
            yield MidiEvent(
                start,
                MidiEvent.NOTE_ON,
                note,
            )
            yield MidiEvent(
                start + duration,
                MidiEvent.NOTE_OFF,
                note,
            )


class ScriptPlayer:
    def __init__(
            self,
            midi_out: pygame.midi.Output,
            midi_config: MidiConfig,
            script: Script,
            bpm: float,
            delay: float,
    ):
        self.midi_out = midi_out
        self.midi_config = midi_config

        self.script = script
        self.bps = bpm / 60.0
        self.delay = delay

        self._next_idx = 0

    def get_script_time(self, timestamp: float) -> float:
        return (timestamp - self.delay) * self.bps

    @property
    def _next_midi_event(self) -> MidiEvent:
        return self.script.midi_events[self._next_idx]

    @property
    def finished(self) -> bool:
        return self._next_idx >= len(self.script.midi_events)

    def _get_new_midi_events(self, timestamp: float) -> typing.Iterator[MidiEvent]:
        if self.finished:
            return

        script_time = self.get_script_time(timestamp)
        while self._next_midi_event.time <= script_time:
            yield self._next_midi_event
            self._next_idx += 1
            if self.finished:
                return

    def __call__(self, timestamp: float) -> None:
        for midi_event in self._get_new_midi_events(timestamp):
            midi_event(self.midi_out, self.midi_config)
