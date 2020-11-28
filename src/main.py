from pygame.surface import Surface
from pygame_app.app import PygameApp

from keymap import KeyMap, KeyboardPlayer
from midi import MidiConfig, MidiOutput
from script import Script, ScriptPlayer, ScriptRenderer


class App(PygameApp):
    FPS = 60

    MODE_NORMAL = 'normal'
    MODE_AUTO = 'auto'
    MODES = {
        MODE_NORMAL,
        MODE_AUTO,
    }

    def __init__(
            self,
            *,
            z_note: int,
            mode: str,
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

        self.mode = mode
        assert mode in self.MODES
        if mode == self.MODE_AUTO and script is None:
            raise ValueError

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

        self.bg_color = (0, 0, 0)  # black
        self.font_color = (255, 255, 255)  # white

        self._script_renderer_params = {
            'font_size': 96,
            'font_color': self.font_color,
            'lead': 2,
            'pps': 300,
        }
        self.script_renderer: ScriptRenderer = None

    @property
    def screen_size(self):
        return 720, 480

    def update(self, dt):
        if self.script_player is not None:
            self.script_player.update(self.game_time)
        if self.script_renderer is not None:
            self.script_renderer.update(self.game_time)

    def render(self, screen: Surface):
        screen.fill(self.bg_color)
        if self.script_renderer is not None:
            self.script_renderer.render(screen)

    def handle_event(self, event):
        if self.keyboard_player is not None:
            self.keyboard_player(event)

    def run(self):
        if self.script is not None:
            self.script.init()
            self.script_renderer = ScriptRenderer(
                self.script,
                self.keymap,
                **self._script_player_params,
                **self._script_renderer_params,
            )
            self.script_renderer.init()

        with MidiOutput(self.midi_config) as midi_output:
            if self.mode == self.MODE_NORMAL:
                self.keyboard_player = KeyboardPlayer(
                    midi_output,
                    self.keymap,
                )
            if self.script is not None and self.mode == self.MODE_AUTO:
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
        help='The MIDI note number Z key is mapped to. Default: 48 (C3).',
    )
    parser.add_argument(
        '--mode', '-m',
        type=str, choices=App.MODES, default=App.MODE_NORMAL,
        help='Play mode. '
             'Normal: sound is played from keyboard input; '
             'Auto: sound is played from script and keyboard input is disabled. '
             'Default: normal.',
    )
    parser.add_argument(
        '--script', '-s',
        type=str,
        help='Script csv to load.',
    )
    parser.add_argument(
        '--bpm',
        type=float, default=100,
        help='Beats per minutes when playing the script. Default: 100.'
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
