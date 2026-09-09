# Render Reliability

Use this reference before previewing or exporting a Remotion, HyperFrames, or
other renderer composition, especially when the output is longer than a short
test or contains audio and external media.

## Preflight

Resolve these facts before starting an expensive render:

- composition ID, width, height, fps, total frames, and expected duration from
  the project contracts—not from an output filename;
- SRT end time, source audio duration, and the intended local audio range;
- JSON/data references, asset IDs, resolved media paths, fonts, subtitles, and
  any generated visual dependencies;
- available `ffmpeg`/`ffprobe`, configured browser executable, writable temp
  directory, and enough free disk for the bundle, working files, segments, and
  final output.
- available memory and active Studio/Chrome renderer instances. Each parallel
  Remotion worker may own a browser, media decoder, and cache; a machine can
  support parallel rendering in principle while still being unable to render
  this composition safely at the requested concurrency.

For a media-heavy 1080p composition, warn the user before starting a long
render that closing unnecessary browsers and Studio windows can improve
stability. Smoke-test a representative range at concurrency 1, then try a
higher concurrency only when the memory budget supports it. Choose the highest
setting that completes the smoke test. If `delayRender`, root-component loading,
or media decoding times out only when more than one worker is active, treat
that as resource pressure and lower concurrency before changing composition
code or repeatedly downloading a browser.

Run a short smoke render before a long export. Probe at least one opening frame,
one data/evidence-heavy frame, and one context-media frame when those modes are
present. A smoke render checks that the root loads, media paths resolve, fonts
load, and the renderer can seek to representative frames; it is not a visual
approval of the whole piece.

If the local browser and the renderer's preferred browser version differ,
prefer an explicitly configured compatible local browser or a known cached
headless shell. Do not repeatedly download large browser binaries without user
approval; a network failure is an environment issue to report, not a reason to
rewrite the composition.

## Render plan

Use the least fragile plan that fits the job:

1. Preview a short representative excerpt or a lower-resolution full-length
   version when the visual language is not yet approved.
2. For a long or resource-heavy composition, render deterministic frame
   segments. Choose an initial segment size based on scene complexity and
   available disk; there is no universal segment length.
3. Keep a render ledger with composition ID, segment start/end frames, output
   path, attempt count, status, and error log. Segment filenames must contain
   numeric frame starts so concatenation can sort by timeline position.
   Keep ledger values JSON-serializable: store paths as strings and timestamps,
   statuses, counts, and errors as primitive values. Write and read the ledger
   once before the expensive render begins so a serialization bug cannot waste
   the render window.
4. Reuse completed, verified segments. Apply a bounded retry with short backoff
   to transient browser-start or connection failures, recording every attempt.
   Choose the attempt limit and launch timeout from the smoke render, machine,
   and segment cost; do not turn one successful value into a universal timeout.
   If a segment hits a repeated timeout, browser
   load failure, memory error, or disk-space error, retry only that range with a
   smaller segment and/or lower concurrency. Do not silently skip a range or
   concatenate segments in filesystem listing order.
5. Represent timeline gaps as exact integer frame counts. A gap filler must be
   transparent video normalized to the segment contract: codec, resolution,
   fps, time base, pixel format, alpha mode, and relevant color metadata. Do not
   feed a single still image directly into a video concat contract unless it is
   explicitly looped and normalized into a compatible video stream. Probe the
   filler before assembly and verify:
   `sum(shot_frames) + sum(gap_frames) = total_frames`.

Do not start a full MP4 render from an ambiguous preview acknowledgement. Keep
preview approval and the explicit export request as separate checkpoints. If an
overwrite attempt is cancelled, inspect the pre-existing final file and record
the cancelled attempt; do not assume that the interrupted output replaced it.

When the composition has a source voice track, render segmented video muted and
assemble the correctly trimmed or source-ranged audio once on the final video.
For an excerpt, map source audio time to local composition time explicitly. Do
not encode the same audio into every segment, and do not change speech content
while solving a timing or render problem. SRT remains the timing authority when
the user has supplied final subtitles.

## Temporary files and cleanup

Use a task-owned temporary directory when possible. Check that an external
volume is writable before selecting it as a render target. Cleanup is limited to
verified files created by the current render attempt after successful assembly;
never delete a broad cache, browser installation, project directory, or another
task's temporary files merely to recover space. If disk pressure prevents a
safe continuation, report the exact space constraint and preserve completed
segments for a later retry.

## Final verification and handoff

Inspect the assembled file rather than trusting the renderer's progress bar.
Verify:

- file exists and is readable;
- actual duration and frame count match the intended timeline within the
  renderer's frame-duration convention;
- resolution, fps, codec, and audio stream are present and correct;
- audio starts at the intended local time and ends with the SRT-driven piece;
- concatenation did not introduce a gap, duplicate segment, or wrong ordering.
- transparent segment and gap-filler alpha was preserved rather than flattened
  to opaque black.

Report actual duration, composition/frame facts, segment count and retries,
audio source/range, concurrency, browser/memory warnings, preview/rendered
revision, and the output path. A failed attempt is useful diagnostic
information only when the valid artifacts and remaining failed ranges are
recorded. When preview code is newer than the verified MP4, report the MP4 as
stale rather than silently presenting it as the current preview.

Keep verification evidence proportional to failure risk. Frame coverage,
stream compatibility, alpha preservation, and a clean final decode are core
checks for segmented transparent output. Add per-segment checksums or a
boundary contact sheet when provenance, transfer, cache integrity, or a
suspected join defect makes them useful; do not impose them on every routine
render.
