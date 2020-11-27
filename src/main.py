import pygame
import pygame.midi
from pygame_app.app import PygameApp

from keymap import KeyMap


class App(PygameApp):
    def __init__(self, *, a_note):
        super().__init__()
        self.midi_out: pygame.midi.Output = None
        self.keymap = KeyMap(a_note)
        self.velocity = 127

    @property
    def screen_size(self):
        return 720, 480

    def _handle_keydown(self, event):
        note = self.keymap.get_note(event.key)
        if note is None:
            return
        self.midi_out.note_on(note, self.velocity)

    def _handle_keyup(self, event):
        note = self.keymap.get_note(event.key)
        if note is None:
            return
        self.midi_out.note_off(note, self.velocity)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

        if event.type == pygame.KEYUP:
            self._handle_keyup(event)

    def run(self):
        pygame.midi.init()
        assert pygame.midi.get_init()
        self.midi_out = pygame.midi.Output(pygame.midi.get_default_output_id())
        try:
            super().run()
        finally:
            pygame.midi.quit()


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '--a-note',
        type=int, default=48,
        help='The MIDI note number A key is mapped to. Default 48 (Middle C).',
    )
    args = parser.parse_args()

    App(**vars(args)).run()


if __name__ == '__main__':
    main()
