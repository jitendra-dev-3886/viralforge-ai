# Overlay text rendering

Install `requirements.txt` in the backend virtual environment. Captions use
Pillow's RAQM engine to shape Hindi consonant combinations and vowel marks,
measure word wrapping, and render a transparent PNG for FFmpeg to composite.
All words and explicit line breaks are retained. Text that cannot fit raises
an error asking the creator to shorten it instead of silently dropping lines.

On Windows, install FriBiDi or set `FRIBIDI_DLL_PATH` to an existing compatible
`libfribidi-0.dll`. A standard `C:/Program Files/Tesseract-OCR` installation is
detected automatically. Restart the backend after changing this dependency.
On Linux, install the distribution's FriBiDi library and Noto Devanagari fonts.

Nirmala UI is used on Windows, and Noto Sans Devanagari on Linux. Set
`OVERLAY_FONT_PATH` to override this with another Hindi-capable TrueType font.
An incompatible font override may render missing glyphs.

Pillow documents the runtime dependency in its
[installation guide](https://pillow.readthedocs.io/en/stable/installation/building-from-source.html).

Run regression checks from `backend`:

```powershell
venv/Scripts/python.exe -m unittest test_text_overlay -v
```

Existing MP4 files must be rendered again to apply the new typography. The
browser preview uses the system's Hindi font; final layout is fitted separately
to each video's resolution and may wrap differently from the preview.
