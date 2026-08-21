# transcript

The Grok Bot (Math) thread from 16 August 2026.

Open `transcript.html`, or from this folder:

```bash
python3 -m http.server 8765
```

then [http://127.0.0.1:8765/transcript.html](http://127.0.0.1:8765/transcript.html).

`transcript.json` is the chat: every user message and every reply, in order. `transcript.html` embeds the same JSON, so `file://` works if fetch is blocked.

Play walks the thread. Every image the transcript references is in `media/`.
