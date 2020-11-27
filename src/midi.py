from dataclasses import dataclass


@dataclass
class MidiConfig:
    velocity: int = 127
