# Sample Video

This directory should contain a sample video file (e.g., `sample.mp4`).

For testing purposes, you can:
1. Use a small sample video file
2. Create a minimal test video with ffmpeg
3. Skip video processing and use the provided transcript directly

## Creating a Test Video

If you have ffmpeg installed, you can create a test video:

```bash
ffmpeg -f lavfi -i testsrc=duration=10:size=640x480:rate=1 -f lavfi -i sine=frequency=1000:duration=10 sample.mp4
```

This creates a 10-second test video with audio.

**Note:** The .gitignore file excludes .mp4 files to keep the repository size small.
