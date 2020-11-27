import pygame
import pygame.midi
from pygame_app.app import PygameApp

from keymap import KeyMap
from midi import MidiConfig
from script import Script, ScriptPlayer


class App(PygameApp):
    FPS = 30

    def __init__(
            self,
            *,
            a_note: int,
            script: str,
            bpm: float,
            delay: float,
    ):
        super().__init__()
        self.midi_out: pygame.midi.Output = None
        self.midi_config = MidiConfig(
            velocity=127,
        )

        self.keymap = KeyMap(a_note)

        if script is None:
            self.script = None
        else:
            self.script = Script(script)

        self.script_player: ScriptPlayer = None
        self.bpm = bpm
        self.delay = delay

    @property
    def screen_size(self):
        return 720, 480

    def update(self, dt):
        if self.script_player is not None:
            self.script_player(self.game_time)

    def _handle_keydown(self, event):
        note = self.keymap.get_note(event.key)
        if note is None:
            return
        self.midi_out.note_on(note, self.midi_config.velocity)

    def _handle_keyup(self, event):
        note = self.keymap.get_note(event.key)
        if note is None:
            return
        self.midi_out.note_off(note, self.midi_config.velocity)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

        if event.type == pygame.KEYUP:
            self._handle_keyup(event)

    def run(self):
        pygame.midi.init()
        assert pygame.midi.get_init()
        self.midi_out = pygame.midi.Output(pygame.midi.get_default_output_id())
        if self.script is not None:
            self.script_player = ScriptPlayer(
                self.midi_out,
                self.midi_config,
                self.script,
                self.bpm,
                self.delay,
            )
        try:
            super().run()
        finally:
            pygame.midi.quit()


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '--a-note',
        type=int, default=60,
        help='The MIDI note number A key is mapped to. Default 60 (Middle C / C4).',
    )
    parser.add_argument(
        '--script', '-s',
        type=str,
        help='Script csv to load.',
    )
    parser.add_argument(
        '--bpm',
        type=float, default=100,
        help='Beats per minutes when playing the script. Default 100.'
    )
    parser.add_argument(
        '--delay',
        type=float, default=3,
        help='Delay in seconds before starting to play script. Default: 3.',
    )
    args = parser.parse_args()

    App(**vars(args)).run()


if __name__ == '__main__':
    main()
