# Pygame MIDI Musical keyboard

Disclaimer: I have zero knowledge on playing musical instruments.
This is a project purely for fun.
If something doesn't make sense, suggestions are welcome.

## Prerequisites

* Python >= 3.8
* A MIDI synthesizer (can be an external device or an application)

## Installation

A virtual environment is recommended!

```
pip install -r requirements/00-base-locked.txt
```

## Run

The main executable is `src/main.py`. See `--help` for more info.

## Using the keyboard

The notes on the keyboard follows the layout of a piano,
with the `Z`-`Right Shift` row and `Q`-`\` row being white keys,
and `A`-`'` row and `1`-`Backspace` row being black keys.

You can specify which key `Z` is mapped to with the `--z-note` argument.

See [here](http://newt.phys.unsw.edu.au/jw/notes.html) for an illustration.
