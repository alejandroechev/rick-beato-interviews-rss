# Rick Beato Interviews — RSS

An RSS 2.0 feed of the long-form **interviews** from [Rick Beato's YouTube channel](https://www.youtube.com/@RickBeato) — conversations with musicians, producers and engineers — without the lessons, rants, reactions, "What Makes This Song Great?" episodes or top-20 lists.

## Subscribe

```
https://alejandroechev.github.io/rick-beato-interviews-rss/feed.xml
```

Browsable index: <https://alejandroechev.github.io/rick-beato-interviews-rss/>

Each entry links directly to the YouTube video.

## How the list was built

Sources, unioned and de-duplicated:

1. Rick Beato's own **"The Interviews"** playlist.
2. Channel videos whose titles contain *Interview*, *In The Room*, or *Sounding Off*.
3. Channel videos that are clearly guest conversations but aren't labelled as such — e.g. *"Michael McDonald: The Voice That Defined a Generation"*, *"My Dinner With Joni Mitchell"*, *"Glyn Johns: Recording The Beatles…"*.

Excluded: solo commentary, analysis/tribute videos about a musician who isn't present, lessons, gear reviews, list videos and livestream archives.

## Layout

| Path | Purpose |
| --- | --- |
| `data/videos.json` | Curated video list (id, title, upload date, duration, description). |
| `scripts/build_feed.py` | Generates the feed and index page. |
| `docs/feed.xml` | The published RSS feed. |
| `docs/index.html` | The published browsable index. |

## Rebuild

```bash
python3 scripts/build_feed.py
```

No dependencies beyond the Python 3 standard library.

## Adding videos

Append an entry to `data/videos.json` and rebuild:

```json
{
  "id": "YOUTUBE_VIDEO_ID",
  "title": "The Someone Interview",
  "uploadDate": "2026-01-31T09:00:00-08:00",
  "duration": 4200,
  "description": "Short summary."
}
```

`uploadDate` may be any ISO-8601 timestamp; entries are sorted newest first.
