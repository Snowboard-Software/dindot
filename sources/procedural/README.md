# Historical procedural generator

This folder preserves the Python drawing pipeline that produced DINDOT's
0.22-era releases. The maintained editable font sources are now the sibling
`DINDOT-*.ufo` directories. Running this historical pipeline does not update
those UFOs or the current candidate fonts.

The pinned environment is recorded in this folder's `requirements.txt`.
With that environment active, run `python build.py` here. Intermediate and
final outputs remain within this folder. The original released files,
original release verifier and release checksums can be inspected at the
repository's `v0.22.0` Git tag.

`source/` contains the original licensed DINish binary inputs. These are
historical inputs, not the editable sources used by the current build.
See `source/README.md`, the root `AUTHORS.txt`, and the root `OFL.txt`.
