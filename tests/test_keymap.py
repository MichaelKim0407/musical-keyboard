from keymap import KeyMap


def test_keymap_reverse():
    keymap = KeyMap(z_note=48)
    for key in KeyMap.KEYBOARD_PRIMARY:
        note = keymap.get_note(key)
        assert keymap.get_key(note) == key, (key, note)
    for key in KeyMap.KEYBOARD_SECONDARY:
        note = keymap.get_note(key)
        if note is None:
            continue
        assert keymap.get_key(note) == key, (key, note)
