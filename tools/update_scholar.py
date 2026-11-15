"""Refresh scholar.json with the latest Google Scholar citation counts.

Uses SerpAPI when SERPAPI_KEY is set (reliable from CI), otherwise reads the
public profile page directly. On any failure the existing scholar.json is kept.
"""
import datetime, json, os, re, sys, urllib.request

USER = "K3_HjboAAAAJ"
OUT = os.path.join(os.path.dirname(__file__), "..", "scholar.json")


def via_serpapi(key):
    url = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id={USER}&api_key={key}"
    d = json.load(urllib.request.urlopen(url, timeout=30))
    t = {list(r.keys())[0]: list(r.values())[0]["all"] for r in d["cited_by"]["table"]}
    return t["citations"], t["h_index"], t["i10_index"]


def via_page():
    req = urllib.request.Request(
        f"https://scholar.google.com/citations?user={USER}&hl=en",
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/124 Safari/537.36"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    nums = re.findall(r'class="gsc_rsb_std">(\d+)<', html)
    if len(nums) < 6:
        raise RuntimeError("stats table not found (Scholar may have blocked the request)")
    return int(nums[0]), int(nums[2]), int(nums[4])


def main():
    key = os.environ.get("SERPAPI_KEY")
    try:
        c, h, i10 = via_serpapi(key) if key else via_page()
    except Exception as e:
        print("Keeping existing scholar.json:", e)
        return 0
    data = {"citations": c, "h_index": h, "i10_index": i10, "updated": datetime.date.today().isoformat()}
    json.dump(data, open(OUT, "w"))
    print(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
