#!/usr/bin/env python3
"""Build an RSS 2.0 feed and a browsable index page from data/videos.json."""

import html
import json
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


STYLE = """
  :root { color-scheme: light dark; }
  body { font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         max-width: 820px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }
  h1 { margin-bottom: .25rem; }
  .sub { opacity: .7; margin-top: 0; }
  .feed { display: inline-block; background: #ee802f; color: #fff; text-decoration: none;
          padding: .5rem .9rem; border-radius: 6px; font-weight: 600; }
  .nav { display: inline-block; margin-left: .5rem; text-decoration: none; font-weight: 600;
         border: 1px solid rgba(127,127,127,.5); padding: .5rem .9rem; border-radius: 6px;
         color: inherit; }
  code { background: rgba(127,127,127,.18); padding: .15rem .35rem; border-radius: 4px; }
  ul { list-style: none; padding: 0; }
  li { padding: .55rem 0; border-bottom: 1px solid rgba(127,127,127,.25);
       display: flex; align-items: flex-start; gap: .6rem; }
  li[hidden] { display: none; }
  li .body { flex: 1; min-width: 0; }
  .t { text-decoration: none; font-weight: 600; }
  .t:hover { text-decoration: underline; }
  .m { display: block; font-size: .85rem; opacity: .65; }
  .fav { background: none; border: 0; cursor: pointer; font-size: 1.25rem; line-height: 1.3;
         padding: 0 .2rem; opacity: .45; color: inherit; }
  .fav:hover { opacity: .8; }
  .fav[aria-pressed="true"] { opacity: 1; color: #ee802f; }
  .empty { opacity: .7; }
"""

SCRIPT = """
(function () {
  var KEY = 'rbi:favorites';
  var favoritesOnly = document.body.dataset.favoritesOnly === 'true';

  function load() {
    try {
      var raw = JSON.parse(localStorage.getItem(KEY));
      return Array.isArray(raw) ? raw.filter(function (x) { return typeof x === 'string'; }) : [];
    } catch (e) {
      return [];
    }
  }

  function save(ids) {
    try {
      localStorage.setItem(KEY, JSON.stringify(ids));
    } catch (e) { /* storage unavailable or full */ }
  }

  var favorites = load();

  function isFav(id) { return favorites.indexOf(id) !== -1; }

  function toggle(id) {
    var i = favorites.indexOf(id);
    if (i === -1) { favorites.push(id); } else { favorites.splice(i, 1); }
    save(favorites);
  }

  function paint(btn) {
    var on = isFav(btn.dataset.id);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.textContent = on ? '\\u2605' : '\\u2606';
    btn.title = on ? 'Remove from favorites' : 'Add to favorites';
    btn.setAttribute('aria-label', btn.title);
  }

  function render() {
    var shown = 0;
    document.querySelectorAll('li[data-id]').forEach(function (li) {
      var on = isFav(li.dataset.id);
      if (favoritesOnly) { li.hidden = !on; }
      if (!li.hidden) { shown++; }
      paint(li.querySelector('.fav'));
    });
    var count = document.getElementById('count');
    if (count) { count.textContent = String(favoritesOnly ? shown : count.dataset.total); }
    var empty = document.getElementById('empty');
    if (empty) { empty.hidden = shown > 0; }
  }

  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest('.fav');
    if (!btn) { return; }
    toggle(btn.dataset.id);
    render();
  });

  window.addEventListener('storage', function (ev) {
    if (ev.key === KEY) { favorites = load(); render(); }
  });

  render();
})();
"""


def build_page(videos, now, favorites_only=False):
    rows = []
    for v in videos:
        date = v["_date"].strftime("%b %d, %Y") if v["_date"] else "\u2014"
        dur = fmt_duration(v.get("duration"))
        rows.append(
            f'      <li data-id="{html.escape(v["id"])}">\n'
            f'        <button class="fav" type="button" data-id="{html.escape(v["id"])}"'
            ' aria-pressed="false" aria-label="Add to favorites">&#9734;</button>\n'
            '        <span class="body">\n'
            f'          <a class="t" href="{html.escape(v["url"])}">{html.escape(v["title"])}</a>\n'
            f'          <span class="m">{date}{" &middot; " + dur if dur else ""}</span>\n'
            "        </span>\n"
            "      </li>"
        )

    title = f"{FEED_TITLE} &middot; Favorites" if favorites_only else FEED_TITLE
    if favorites_only:
        header = (
            '  <p><a class="nav" href="index.html">&larr; All interviews</a></p>\n'
            '  <p><strong id="count" data-total="0">0</strong> favorites</p>\n'
            '  <p class="empty" id="empty" hidden>No favorites yet. '
            'Star an interview on the <a href="index.html">main page</a>.</p>'
        )
    else:
        header = (
            '  <p><a class="feed" href="feed.xml">RSS feed</a>'
            '<a class="nav" href="favorites.html">&#9733; Favorites</a></p>\n'
            f"  <p>Subscribe with: <code>{SITE_URL}/feed.xml</code></p>\n"
            f'  <p><strong id="count" data-total="{len(videos)}">{len(videos)}</strong>'
            f' interviews &middot; updated {now.strftime("%b %d, %Y")}</p>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<link rel="alternate" type="application/rss+xml" title="{FEED_TITLE}" href="feed.xml" />
<style>{STYLE}</style>
</head>
<body data-favorites-only="{str(favorites_only).lower()}">
  <h1>{title}</h1>
  <p class="sub">{html.escape(FEED_DESC)}</p>
{header}
  <ul>
{chr(10).join(rows)}
  </ul>
<script>{SCRIPT}</script>
</body>
</html>
"""


def main():
    now = datetime.now(timezone.utc)
    videos = load_videos()
    DOCS.mkdir(exist_ok=True)
    (DOCS / "feed.xml").write_text(build_rss(videos, now))
    (DOCS / "index.html").write_text(build_page(videos, now))
    (DOCS / "favorites.html").write_text(build_page(videos, now, favorites_only=True))
    (DOCS / ".nojekyll").write_text("")
    print(f"Wrote {len(videos)} items to docs/feed.xml, docs/index.html and docs/favorites.html")


if __name__ == "__main__":
    main()
