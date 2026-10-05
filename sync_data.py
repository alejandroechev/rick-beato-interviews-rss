import json,re
src=json.load(open('videos.json'))
order={}
for i,l in enumerate(open('scratch/channel_videos.jsonl')):
    order.setdefault(json.loads(l)['id'], i)
def clean(d):
    if not d: return ""
    d=re.split(r"\n\s*(?:Subscribe|My links|SUPPORT|Support |http|Check out|BUY |Get )", d)[0].strip()
    d=re.sub(r"\n{2,}","\n",d)
    return d[:900].rsplit(" ",1)[0]+"\u2026" if len(d)>900 else d
out=[]
for v in src:
    out.append({"id":v["id"],"title":v["title"].strip(),
                "uploadDate":v.get("uploadDate"),
                "duration":v.get("duration"),
                "description":clean(v.get("description",""))})
out.sort(key=lambda v: order.get(v["id"], 10**6))
json.dump(out,open('data/videos.json','w'),indent=1,ensure_ascii=False)
print(len(out),"entries;",sum(1 for v in out if not v['uploadDate']),"without date")
