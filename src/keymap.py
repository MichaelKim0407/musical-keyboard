import typing

import pygame

from midi import MidiOutput


class KeyMap:
    """
    Map keyboard keys to MIDI note numbers using the layout of a piano keyboard.

    http://newt.phys.unsw.edu.au/jw/notes.html
    """

    KEYBOARD_PRIMARY = (
        pygame.K_z,
        pygame.K_x,
        pygame.K_c,
        pygame.K_v,
        pygame.K_b,
        pygame.K_n,
        pygame.K_m,
        pygame.K_COMMA,
        pygame.K_PERIOD,
        pygame.K_SLASH,
        pygame.K_RSHIFT,

        pygame.K_q,
        pygame.K_w,
        pygame.K_e,
        pygame.K_r,
        pygame.K_t,
        pygame.K_y,
        pygame.K_u,
        pygame.K_i,
        pygame.K_o,
        pygame.K_p,
        pygame.K_LEFTBRACKET,
        pygame.K_RIGHTBRACKET,
        pygame.K_BACKSLASH,
    )
    KEYBOARD_SECONDARY = (
        pygame.K_a,
        pygame.K_s,
        pygame.K_d,
        pygame.K_f,
        pygame.K_g,
        pygame.K_h,
        pygame.K_j,
        pygame.K_k,
        pygame.K_l,
        pygame.K_SEMICOLON,
        pygame.K_QUOTE,

        pygame.K_1,
        pygame.K_2,
        pygame.K_3,
        pygame.K_4,
        pygame.K_5,
        pygame.K_6,
        pygame.K_7,
        pygame.K_8,
        pygame.K_9,
        pygame.K_0,
        pygame.K_MINUS,
        pygame.K_EQUALS,
        pygame.K_BACKSPACE,
    )

    SEQUENCE_PRIMARY = (
        0, 2, 4, 5, 7, 9, 11,
    )
    SEQUENCE_SECONDARY = (
        1, 3, None, 6, 8, 10, None,
    )

    class InvalidOffsetValue(Exception):
        pass

    def __init__(self, z_note: int):
        """
        :param z_note: The MIDI note number that Z key is mapped to.
        """
        self.z_note = z_note
        seq_pos_offset = z_note % 12
        if seq_pos_offset not in self.SEQUENCE_PRIMARY:
            raise self.InvalidOffsetValue
        self.pos_offset = self.SEQUENCE_PRIMARY.index(seq_pos_offset) + 7 * (z_note // 12)

    def get_note(self, key: int) -> typing.Optional[int]:
        if key in self.KEYBOARD_PRIMARY:
            rel_pos = self.KEYBOARD_PRIMARY.index(key)
            seq = self.SEQUENCE_PRIMARY
        elif key in self.KEYBOARD_SECONDARY:
            # -1 because the secondary row is to the left of primary
            rel_pos = self.KEYBOARD_SECONDARY.index(key) - 1
            seq = self.SEQUENCE_SECONDARY
        else:
            return None

        abs_pos = rel_pos + self.pos_offset
        seq_note = seq[abs_pos % 7]
        if seq_note is None:
            return None
        return seq_note + (abs_pos // 7) * 12

    def get_key(self, note: int) -> typing.Optional[int]:
        seq_count = note // 12
        seq_note = note - seq_count * 12
        if seq_note in self.SEQUENCE_PRIMARY:
            keys = self.KEYBOARD_PRIMARY
            seq_pos = self.SEQUENCE_PRIMARY.index(seq_note)
        elif seq_note in self.SEQUENCE_SECONDARY:
            keys = self.KEYBOARD_SECONDARY
            seq_pos = self.SEQUENCE_SECONDARY.index(seq_note) + 1
        else:
            return None
        abs_pos = seq_count * 7 + seq_pos
        rel_pos = abs_pos - self.pos_offset
        if rel_pos < 0 or rel_pos >= len(keys):
            return None
        return keys[rel_pos]


class KeyboardPlayer:
    def __init__(
            self,
            midi_output: MidiOutput,
            keymap: KeyMap,
    ):
        self.midi_output = midi_output
        self.keymap = keymap

    def _handle_keydown(self, event):
        note = self.keymap.get_note(event.key)
        if note is None:
            return
        self.midi_output.note_on(note)

    def _handle_keyup(self, event):
        note = self.keymap.get_note(event.key)
        if note is None:
            return
        self.midi_output.note_off(note)

    def __call__(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

        if event.type == pygame.KEYUP:
            self._handle_keyup(event)
