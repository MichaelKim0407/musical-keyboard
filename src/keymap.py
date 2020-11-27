import pygame
import typing


class KeyMap:
    """
    Map keyboard keys to MIDI note numbers using the layout of a piano keyboard.

    http://newt.phys.unsw.edu.au/jw/notes.html
    """

    KEYBOARD_PRIMARY = (
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
    )
    KEYBOARD_SECONDARY = (
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
    )

    SEQUENCE_PRIMARY = (
        0, 2, 4, 5, 7, 9, 11,
    )
    SEQUENCE_SECONDARY = (
        1, 3, None, 6, 8, 10, None,
    )

    class InvalidOffsetValue(Exception):
        pass

    def __init__(self, a_note: int):
        """
        :param a_note: The MIDI note number that A key is mapped to.
        """
        seq_pos_offset = a_note % 12
        if seq_pos_offset not in self.SEQUENCE_PRIMARY:
            raise self.InvalidOffsetValue
        self.pos_offset = self.SEQUENCE_PRIMARY.index(seq_pos_offset) + 7 * (a_note // 12)

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
