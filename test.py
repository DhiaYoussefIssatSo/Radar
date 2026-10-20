import json, urllib.request, urllib.parse
N = ["beach","river","forest","mountain","desert","storm","winter","night","school","hospital",
     "airport","train","bicycle","kitchen","window","sofa","bread","cheese","chocolate","coffee",
     "computer","phone","internet","football","music","guitar","cat","horse"]
T = [
 (0,"seaside","tres proche"),(0,"sand","proche"),(0,"sea","proche"),(0,"ocean","proche"),(0,"summer","lie"),(0,"car","sans rapport"),
 (0,"beac","faute"),(0,"beaches","pluriel"),(0,"beach","exact"),
 (2,"woods","tres proche"),(2,"tree","proche"),(2,"jungle","proche"),(2,"animal","lie"),(2,"forrest","faute"),(2,"banana","sans rapport"),
 (3,"hill","tres proche"),(3,"peak","proche"),(3,"snow","lie"),(3,"river","meme theme"),(3,"mountains","pluriel"),(3,"sofa","sans rapport"),
 (13,"fridge","proche"),(13,"oven","proche"),(13,"cook","proche"),(13,"bedroom","meme theme"),(13,"kitchn","faute"),(13,"horse","sans rapport"),
 (8,"teacher","proche"),(8,"student","proche"),(8,"university","tres proche"),(8,"book","lie"),(8,"hospital","meme theme"),(8,"banana","sans rapport"),
 (26,"kitten","tres proche"),(26,"dog","proche"),(26,"pet","proche"),(26,"horse","meme theme"),(26,"table","sans rapport"),
 (20,"laptop","tres proche"),(20,"keyboard","proche"),(20,"software","proche"),(20,"phone","meme theme"),(20,"bread","sans rapport"),
 (23,"soccer","tres proche"),(23,"ball","proche"),(23,"goal","proche"),(23,"guitar","sans rapport"),
 (19,"tea","proche"),(19,"espresso","tres proche"),(19,"cheese","meme theme"),(19,"mountain","sans rapport"),
]
def zone(r):
    if r["found"]: return "TROUVE (5)"
    s = r["s"]
    return "Burning (4)" if s>=.8 else "Hot (3)" if s>=.6 else "Warm (2)" if s>=.4 else "Cold (1)" if s>=.2 else "Freezing (0)"
print(f"{'secret':10} {'mot':11} {'attendu':13} {'cos':>6} {'s':>5}  zone")
for i,w,att in T:
    r = json.load(urllib.request.urlopen("http://localhost:8000/guess?id=%d&w=%s" % (i, urllib.parse.quote(w))))
    print(f"{N[i]:10} {w:11} {att:13} {r.get('cos',1.0):>6} {r['s']:>5}  {zone(r)}")
