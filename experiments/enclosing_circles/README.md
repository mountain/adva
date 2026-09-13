# A bipolar circle-family drawing, its output, and two third-party reference images

Status: one drawing script, the output it produces, and two external reference
images. There is no contract, no checker, no evidence file and no geometric
claim here. Nothing in this directory is a calibration, a native admission, a
Seal, or a plate admitted as a witness.

## What each file is

| File | SHA256 | What it is |
| --- | --- | --- |
| `enclosing_circles.py` | `c7745d005c93e48e5a667f8e0a8730dbff59fdf25fea9eec17edbbd92b2c091f` | a self-contained matplotlib drawing script (66 lines). Red circles pass through the two foci `(±a, 0)`; blue circles are orthogonal to them and centred on the x-axis; one white circle encloses everything. Defaults `a = 1.0`, `radius = 4.0`, with the guard `0 < a < radius` |
| `enclosing_circles.png` | `60bafac12eb90b865d47335e5f12841326c16c62f8429a015974fc7a9442a889` | the script's own output at those defaults: 1280 × 1280 RGBA PNG, carrying one `tEXt` chunk, `Software = Matplotlib version3.10.6`. The pixel size is consistent with the script's declared `figsize=(8, 8)`, `dpi=160` |
| `Apollonian_gasket.svg.webp` | `b9436578ef41de5403a4b4a980cf1ce19587f0c1cbb086913be7ae1b35a046ba` | third-party reference image, 500 × 500 lossless WebP (`VP8L`): an enclosing circle with four large mutually tangent circles and the recursive packing between them |
| `Cicle_inversion.svg.webp` | `20721f50ff08107ac2ee38d22354157da673c6f3f2bbcdf475434bf5ef533d72` | third-party reference image, 1280 × 1280 lossless WebP (`VP8L`): the same kind of packing with three dashed red arcs and coloured lens regions overlaid |

The two descriptions of the WebP files are **visual readings** of the retained
bytes, not the results of a check. The digest is a byte-integrity record only:
never authentication, never semantic identity, never proof.

## The one check that was run

The retained PNG reproduces **byte for byte** from the retained script at its
default parameters, with matplotlib 3.10.6:

```sh
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 \
  experiments/enclosing_circles/enclosing_circles.py --output /tmp/out.png
shasum -a 256 /tmp/out.png experiments/enclosing_circles/enclosing_circles.png
```

Both lines report `60bafac12eb90b865d47335e5f12841326c16c62f8429a015974fc7a9442a889`.

The interpreter is named by absolute path because on this host the PATH entries
do not carry matplotlib: `python3` is 3.14.6 with no matplotlib, and
`python3.13` resolves to the Homebrew 3.13 build, which also has none. Only the
python.org framework 3.13 build carries matplotlib 3.10.6 here. That is a
statement about one machine's interpreters, not a pinned toolchain: this record
pins bytes and names the interpreter that produced them.
The run happened on 2026-09-13 on the author's macOS host, with the matplotlib
configuration and font caches falling back to temporary directories, which the
run reported on stderr and which did not affect the bytes.

This establishes one thing only: **that output and script match at these
defaults on this host**. A different matplotlib version is not claimed to
reproduce the same bytes, and no parameter other than the defaults was tried.

## Provenance: what is known, and what is not

- The script and its output were created locally on 2026-09-13 (07:48 and 07:52)
  and remained untracked until this admission.
- Both WebP names end in `.svg.webp`, and one misspells `Circle` as `Cicle`.
  That shape is consistent with a raster thumbnail of an SVG original, but **no
  source URL, author or licence is recorded anywhere in this working tree**.
- A printable-run scan of both WebP files found no EXIF, XMP, ICC or text chunk,
  so the source cannot be recovered from the bytes themselves.
- The two images are therefore recorded as **unattributed third-party
  material**. Source, author, licence and the exact source file are `Unknown`.
  They are independent files: if a licence later requires attribution, or if the
  source cannot be established, they can be attributed or removed without
  touching the script or its output.

## What this directory does not do

- It establishes no geometric claim. The script draws a family and guards its
  own parameter domain; it does not prove tangency, orthogonality, inversion
  behaviour or any packing property. Those would each need their own bounded
  contract, checker and retained residual.
- It creates no home in `adva-library/math`. An illustration, a screenshot or a
  drawing can never witness an arithmetic or geometric claim, and this directory
  adds no geometry entry, no Pascal descendant and nothing to the growth
  obligation, which stays `Open` with no native `Seal`.
- It adds no native operation, no builtin, no `OperationSpec` row and no entry
  in `docs/claims.toml`.
- It does not assert what the third-party images depict beyond the visual
  reading above, and it does not assert that the dashed arcs are geodesics of
  any particular disk model.

## Open obligations

- Source, author and licence of the two WebP files: `Unknown`.
- No contract, no checker and no evidence file exist for this directory; the
  single reproduction check above is recorded in prose rather than as a
  replayed artifact.
- The relationship between the two reference images and the script — whether
  they were references for it, targets of comparison, or independent downloads
  — is not recorded anywhere and is not asserted here.
