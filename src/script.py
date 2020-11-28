import logging
import typing
from dataclasses import dataclass
from functools import cached_property

import pygame
import pygame.font as f
from pygame.surface import Surface
from returns import returns

from midi import MidiOutput

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MidiEvent:
    _NAME_SORT = (
        MidiOutput.NOTE_OFF,
        MidiOutput.NOTE_ON,
    )

    time: float
    name: str
    note: int

    def __call__(self, midi_output: MidiOutput):
        midi_output(self.name, self.note)

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
                MidiOutput.NOTE_ON,
                note,
            )
            yield MidiEvent(
                start + duration,
                MidiOutput.NOTE_OFF,
                note,
            )

    def init(self) -> None:
        _ = self.midi_events


class AbstractScriptRenderer:
    def __init__(
            self,
            script: Script,
            *,
            bpm: float,
            delay: float,
            repeat: bool = False,
    ):
        self.script = script
        self.bps = bpm / 60.0
        self.delay = delay
        self.repeat = repeat

        self._next_idx = 0
        self._repeat_offset = self.delay * self.bps

    def get_script_time(self, timestamp: float) -> float:
        return timestamp * self.bps - self._repeat_offset

    def get_game_time(self, script_time: float) -> float:
        return (script_time + self._repeat_offset) / self.bps

    @property
    def _next_midi_event(self) -> MidiEvent:
        return self.script.midi_events[self._next_idx]

    @property
    def finished(self) -> bool:
        return self._next_idx >= len(self.script.midi_events)

    def _repeat(self):
        self._repeat_offset += self.script.midi_events[-1].time + self.delay * self.bps
        self._next_idx = 0

    def _get_new_midi_events(self, timestamp: float) -> typing.Iterator[MidiEvent]:
        if self.finished:
            return

        script_time = self.get_script_time(timestamp)
        while self._next_midi_event.time <= script_time:
            yield self._next_midi_event
            self._next_idx += 1

            if self.finished:
                if self.repeat:
                    self._repeat()
                return


class ScriptPlayer(AbstractScriptRenderer):
    def __init__(
            self,
            midi_output: MidiOutput,
            script: Script,
            *,
            bpm: float,
            delay: float,
            repeat: bool = False,
    ):
        self.midi_output = midi_output
        super().__init__(
            script,
            bpm=bpm,
            delay=delay,
            repeat=repeat,
        )

    def update(self, timestamp: float) -> None:
        for midi_event in self._get_new_midi_events(timestamp):
            midi_event(self.midi_output)


class ScriptRenderer(AbstractScriptRenderer):
    KEYS = {
        pygame.K_z: 'Z',
        pygame.K_x: 'X',
        pygame.K_c: 'C',
        pygame.K_v: 'V',
        pygame.K_b: 'B',
        pygame.K_n: 'N',
        pygame.K_m: 'M',
        pygame.K_COMMA: ',',
        pygame.K_PERIOD: '.',
        pygame.K_SLASH: '/',
        pygame.K_RSHIFT: '\u21e7',

        pygame.K_q: 'Q',
        pygame.K_w: 'W',
        pygame.K_e: 'E',
        pygame.K_r: 'R',
        pygame.K_t: 'T',
        pygame.K_y: 'Y',
        pygame.K_u: 'U',
        pygame.K_i: 'I',
        pygame.K_o: 'O',
        pygame.K_p: 'P',
        pygame.K_LEFTBRACKET: '[',
        pygame.K_RIGHTBRACKET: ']',
        pygame.K_BACKSLASH: '\\',

        pygame.K_a: 'A',
        pygame.K_s: 'S',
        pygame.K_d: 'D',
        pygame.K_f: 'F',
        pygame.K_g: 'G',
        pygame.K_h: 'H',
        pygame.K_j: 'J',
        pygame.K_k: 'K',
        pygame.K_l: 'L',
        pygame.K_SEMICOLON: ';',
        pygame.K_QUOTE: "'",

        pygame.K_1: '1',
        pygame.K_2: '2',
        pygame.K_3: '3',
        pygame.K_4: '4',
        pygame.K_5: '5',
        pygame.K_6: '6',
        pygame.K_7: '7',
        pygame.K_8: '8',
        pygame.K_9: '9',
        pygame.K_0: '0',
        pygame.K_MINUS: '-',
        pygame.K_EQUALS: '=',
        pygame.K_BACKSPACE: '\u232b',
    }

    def __init__(
            self,
            script: Script,
            keymap: 'KeyMap',
            *,
            bpm: float,
            delay: float,
            repeat: bool = False,

            font_size: int,
            font_color,

            lead: float,
            pps: float,  # pixel per second
    ):
        super().__init__(
            script,
            bpm=bpm,
            delay=delay,
            repeat=repeat,
        )

        self.keymap = keymap

        self.font_size = font_size
        self.font_color = font_color

        self.lead = lead
        self.pps = pps

        self._on_screen = []

    @cached_property
    def font_path(self) -> str:
        from os.path import dirname, join
        return join(dirname(__file__), 'Inconsolata-Bold.ttf')

    @cached_property
    def font(self) -> f.Font:
        return f.Font(self.font_path, self.font_size)

    def init(self):
        if not f.get_init():
            f.init()
        _ = self.font

    def _render_text(self, s: str) -> Surface:
        return self.font.render(s, True, self.font_color)

    def _update_on_screen(self, on_screen, timestamp: float):
        for text, text_rect, text_ts in on_screen:
            if text_ts < timestamp:
                continue
            yield text, text_rect, text_ts

        for midi_event in self._get_new_midi_events(timestamp + self.lead):
            if midi_event.name != MidiOutput.NOTE_ON:
                continue

            key = self.keymap.get_key(midi_event.note)
            if key is None:
                logger.error(f'Unmapped key for note {midi_event.note}; z_note = {self.keymap.z_note}')
                continue

            s = self.KEYS[key]
            text = self._render_text(s)
            text_rect = text.get_rect()
            text_ts = self.get_game_time(midi_event.time)
            yield text, text_rect, text_ts

    def _update_positions(self, on_screen, timestamp: float):
        for text, text_rect, text_ts in on_screen:
            rect = text.get_rect()
            rect.left += (text_ts - timestamp) * self.pps
            yield text, rect, text_ts

    def update(self, timestamp: float) -> None:
        on_screen = self._on_screen
        on_screen = self._update_on_screen(on_screen, timestamp)
        on_screen = self._update_positions(on_screen, timestamp)
        self._on_screen = list(on_screen)

    def render(self, screen: Surface) -> None:
        screen.blits((
            (text, text_rect)
            for text, text_rect, text_ts in self._on_screen
        ))


from keymap import KeyMap
