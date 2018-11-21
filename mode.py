import requests
from bs4 import BeautifulSoup

modes = ["Standard","Taiko","CatchTheBeat","osu!mania"]
mode_id_dict = {"standard":0,"taiko":1,"catchthebeat":2,"osu!mania":3,"s":0,"osu":0,"t":1,"ctb":2,"catch":2,"osu!catch":2,"osucatch":2,"c":2,"osumania":3,"mania":3,"m":3}
user_id = 5385123

def get_mode_pp(user_id,mode):
    mode_id = mode_id_dict[mode.lower()]
    url = "https://osu.ppy.sh/pages/include/profile-general.php?u="+str(user_id)+"&m="+str(mode_id)
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    pp_str = soup.find("b").text
    pp = pp_str.split("pp")[0]
    if pp != pp_str:
        pp = pp.split(" ")[1]
    else:
        pp = 0
    print(modes[mode_id],pp)

def get_top_plays(user_id,mode):
    mode_id = mode_id_dict[mode.lower()]
    url = "https://osu.ppy.sh/pages/include/profile-leader.php?u="+str(user_id)+"&m="+str(mode_id)
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    plays = soup.findAll("div", attrs={"class":"prof-beatmap"})
    for play in plays:
        score = play.find("div", attrs={"class":"h"}).text
        time = play.find("div", attrs={"class":"c"}).text
        pp = play.find("div", attrs={"class":"pp-display"}).text
        pp_weighted = play.find("div", attrs={"class":"pp-display-weighted"}).text
        print(modes[mode_id],score,time,pp,pp_weighted)

for mode in modes:
    get_mode_pp(5385123,mode)
    try:
        get_top_plays(5385123,mode)
    except:
        print("No Scores")


