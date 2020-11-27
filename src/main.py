from pygame_app.app import PygameApp

from keymap import KeyMap, KeyboardPlayer
from midi import MidiConfig, init_midi
from script import Script, ScriptPlayer


class App(PygameApp):
    FPS = 30

    def __init__(
            self,
            *,
            z_note: int,
            script: str,
            bpm: float,
            delay: float,
            repeat: bool,
    ):
        super().__init__()
        self.midi_config = MidiConfig(
            velocity=127,
        )

        self.keymap = KeyMap(z_note)
        self.keyboard_player: KeyboardPlayer = None

        if script is None:
            self.script = None
        else:
            self.script = Script(script)
        self._script_player_params = {
            'bpm': bpm,
            'delay': delay,
            'repeat': repeat,
        }
        self.script_player: ScriptPlayer = None

    @property
    def screen_size(self):
        return 720, 480

    def update(self, dt):
        if self.script_player is not None:
            self.script_player(self.game_time)

    def handle_event(self, event):
        self.keyboard_player(event)

    def run(self):
        with init_midi(self.midi_config) as midi_output:
            self.keyboard_player = KeyboardPlayer(
                midi_output,
                self.keymap,
            )
            if self.script is not None:
                self.script_player = ScriptPlayer(
                    midi_output,
                    self.script,
                    **self._script_player_params,
                )
            super().run()


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '--z-note',
        type=int, default=48,
        help='The MIDI note number Z key is mapped to. Default 48 (C3).',
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
    parser.add_argument(
        '--repeat',
        action='store_true',
        help='Repeat script.',
    )
    args = parser.parse_args()

    App(**vars(args)).run()


if __name__ == '__main__':
    main()
