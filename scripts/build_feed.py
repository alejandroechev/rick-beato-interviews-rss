#!/usr/bin/env python3
"""Build an RSS 2.0 feed and a browsable index page from data/videos.json."""

import html
import json
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "videos.json"
DOCS = ROOT / "docs"

SITE_URL = "https://alejandroechev.github.io/rick-beato-interviews-rss"
FEED_TITLE = "Rick Beato Interviews"
FEED_DESC = (
    "Long-form interviews and in-depth conversations with musicians, producers "
    "and engineers from Rick Beato's YouTube channel."
)
CHANNEL_URL = "https://www.youtube.com/@RickBeato"


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def fmt_duration(seconds):
    if not seconds:
        return ""
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def load_videos():
    videos = json.loads(DATA.read_text())
    fallback = datetime(2015, 1, 1, tzinfo=timezone.utc)
    for v in videos:
        v["_date"] = parse_date(v.get("uploadDate"))
        v["url"] = f"https://www.youtube.com/watch?v={v['id']}"
        v["thumbnail"] = f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg"
    videos.sort(key=lambda v: (v["_date"] or fallback), reverse=True)
    return videos


def short_description(text, limit=600):
    if not text:
        return ""
    text = re.split(r"\n\s*(?:Subscribe|My links|SUPPORT|http)", text)[0].strip()
    text = re.sub(r"\n{2,}", "\n", text)
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "\u2026"
    return text


def build_rss(videos, now):
    items = []
    for v in videos:
        pub = v["_date"] or now
        desc = short_description(v.get("description", ""))
        body = (
            f'<p><a href="{html.escape(v["url"])}">'
            f'<img src="{html.escape(v["thumbnail"])}" alt="" /></a></p>'
            f'<p><a href="{html.escape(v["url"])}">Watch on YouTube</a>'
            + (f' &middot; {fmt_duration(v.get("duration"))}' if v.get("duration") else "")
            + "</p>"
            + (f"<p>{html.escape(desc)}</p>" if desc else "")
        )
        items.append(
            "    <item>\n"
            f"      <title>{html.escape(v['title'])}</title>\n"
            f"      <link>{html.escape(v['url'])}</link>\n"
            f'      <guid isPermaLink="false">yt:video:{v["id"]}</guid>\n'
            f"      <pubDate>{format_datetime(pub)}</pubDate>\n"
            f"      <description>{html.escape(body)}</description>\n"
            f'      <enclosure url="{html.escape(v["thumbnail"])}" type="image/jpeg" length="0" />\n'
            "    </item>"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{FEED_TITLE}</title>\n"
        f"    <link>{CHANNEL_URL}</link>\n"
        f"    <description>{html.escape(FEED_DESC)}</description>\n"
        "    <language>en-us</language>\n"
        f"    <lastBuildDate>{format_datetime(now)}</lastBuildDate>\n"
        f'    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml" />\n'
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )


def build_index(videos, now):
    rows = []
    for v in videos:
        date = v["_date"].strftime("%b %d, %Y") if v["_date"] else "\u2014"
        dur = fmt_duration(v.get("duration"))
        rows.append(
            "      <li>\n"
            f'        <a class="t" href="{html.escape(v["url"])}">{html.escape(v["title"])}</a>\n'
            f'        <span class="m">{date}{" &middot; " + dur if dur else ""}</span>\n'
            "      </li>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{FEED_TITLE}</title>
<link rel="alternate" type="application/rss+xml" title="{FEED_TITLE}" href="feed.xml" />
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         max-width: 820px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
  h1 {{ margin-bottom: .25rem; }}
  .sub {{ opacity: .7; margin-top: 0; }}
  .feed {{ display: inline-block; background: #ee802f; color: #fff; text-decoration: none;
          padding: .5rem .9rem; border-radius: 6px; font-weight: 600; }}
  code {{ background: rgba(127,127,127,.18); padding: .15rem .35rem; border-radius: 4px; }}
  ul {{ list-style: none; padding: 0; }}
  li {{ padding: .55rem 0; border-bottom: 1px solid rgba(127,127,127,.25); }}
  .t {{ text-decoration: none; font-weight: 600; }}
  .t:hover {{ text-decoration: underline; }}
  .m {{ display: block; font-size: .85rem; opacity: .65; }}
</style>
</head>
<body>
  <h1>{FEED_TITLE}</h1>
  <p class="sub">{html.escape(FEED_DESC)}</p>
  <p><a class="feed" href="feed.xml">RSS feed</a></p>
  <p>Subscribe with: <code>{SITE_URL}/feed.xml</code></p>
  <p><strong>{len(videos)}</strong> interviews &middot; updated {now.strftime("%b %d, %Y")}</p>
  <ul>
{chr(10).join(rows)}
  </ul>
</body>
</html>
"""


def main():
    now = datetime.now(timezone.utc)
    videos = load_videos()
    DOCS.mkdir(exist_ok=True)
    (DOCS / "feed.xml").write_text(build_rss(videos, now))
    (DOCS / "index.html").write_text(build_index(videos, now))
    (DOCS / ".nojekyll").write_text("")
    print(f"Wrote {len(videos)} items to docs/feed.xml and docs/index.html")


if __name__ == "__main__":
    main()
