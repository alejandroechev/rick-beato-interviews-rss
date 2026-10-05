import json
from clean import clean_description

src = json.load(open('videos.json'))
order = {}
for i, l in enumerate(open('scratch/channel_videos.jsonl')):
    order.setdefault(json.loads(l)['id'], i)
out = [{"id": v["id"], "title": v["title"].strip(),
        "uploadDate": v.get("uploadDate"), "duration": v.get("duration"),
        "description": clean_description(v.get("description", ""))} for v in src]
out.sort(key=lambda v: order.get(v["id"], 10**6))
json.dump(out, open('data/videos.json', 'w'), indent=1, ensure_ascii=False)
print(len(out), "entries;", sum(1 for v in out if not v['uploadDate']), "without date")
