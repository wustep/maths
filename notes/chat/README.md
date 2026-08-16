# Grok Bot (Math) chat transcript — draft

This folder is a **visual test** of the 16 August 2026 Grok Bot (Math) working chat. It is **not** the covering-code proof, and it is **not on `main`**. The draft PR may be deleted.

## Open it

From this folder:

```bash
python3 -m http.server 8765
```

Then open [http://127.0.0.1:8765/](http://127.0.0.1:8765/).

`index.html` also embeds `transcript.json`, so opening the HTML via `file://` still works if fetch is blocked.

**Play** walks the bubbles in order. The default view is the full static thread.

## What is in the JSON

`transcript.json` is the **visible chat** Stephen saw:

- Unique user bubbles, first `[tNu]` only (conversation-summary replays re-inject old user messages; those duplicates are dropped).
- Every `SendMessage` that reached the chat (text, images, widgets, attachment chips, cursor-agent cards, secret-request cards).
- Timestamps from the user-turn `<timestamp>` tags. Assistant bubbles keep send order after the user turn they belong to.

Stripped from displayed user text (not what was typed): `[SAND_HIDDEN_PROMPT]`, `<system_reminder>`, `<agent_profile_update>`, the `<timestamp>` wrapper, and the leading `[tNu]` tag.

Skipped as user bubbles: empty hidden wakes (routine / background completions with no `user_query` body) and summary-replay duplicates.

The raw ~2MB agent jsonl (system prompts, tool results, host paths) is **not** in this repo. This JSON is the chat-accurate extract.

## Images

Resolved figures were copied into `media/`. Overnight paths such as `file:///maths/problems/...` are remapped to the recovered repo copies when those files still exist. If a figure is gone, the bubble stays and the page shows a **missing figure** placeholder with the original path. No replacement image was invented.

## Recovered / not recovered

- `t36u` and `t37u` were not in the jsonl (the file lagged). Their text was taken from the conversation that followed and marked `reconstructed`.
- `t22u` and `t27u` were never present as unique user_query bodies, including in later summary blocks. They are listed under `extraction.unrecovered_user_messages`.
