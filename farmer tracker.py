import requests
from bs4 import BeautifulSoup
import time
import json

modes = ["Standard","Taiko","CatchTheBeat","osu!mania"]
mode_id_dict = {"standard":0,"taiko":1,"catchthebeat":2,"osu!mania":3,"s":0,"osu":0,"t":1,"ctb":2,"catch":2,"osu!catch":2,"osucatch":2,"c":2,"osumania":3,"mania":3,"m":3}
user_names = []
wait = 1

usernames_raw = input("Usernames (comma separated): ").split(",")
for username in usernames_raw:
    user_names.append(username.strip())

def get_user_id(user_name):
    global wait
    try:
        time.sleep(wait)
        url = 'https://osu.ppy.sh/u/'+str(user_name)
        data = requests.get(url).text
        soup = BeautifulSoup(data, "lxml")
        try:
            #print(soup)
            data_profile = soup.find("script", attrs={"id": "json-user"}).text.strip()
            json_data = json.loads(data_profile)
            id_on_page = json_data["id"]
            return id_on_page
        except Exception as e:
            print(e)
            print("Invalid user: {}".format(user_name))
            return None
    except Exception as e:
        print(e)
        get_user_id(user_name)
    

def get_mode_pp(user_id,mode):
    mode_id = mode_id_dict[mode.lower()]
    url = "https://osu.ppy.sh/pages/include/profile-general.php?u="+str(user_id)+"&m="+str(mode_id)
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    try:
        pp_str = soup.find("b").text
        pp = pp_str.split("pp")[0].replace(",","")
        if pp != pp_str:
            pp = pp.split(" ")[1]
        else:
            pp = 0
    except:
        #they've never actually played the gamemode
        pp = 0
    #print(modes[mode_id],pp)
    return [modes[mode_id],pp]

def get_top_plays(user_id,mode):
    scores = []
    mode_id = mode_id_dict[mode.lower()]
    url = "https://osu.ppy.sh/pages/include/profile-leader.php?u="+str(user_id)+"&m="+str(mode_id)
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    url2 = "https://osu.ppy.sh/pages/include/profile-leader.php?u="+str(user_id)+"&m="+str(mode_id)+"&pp=1"
    html2 = requests.get(url2).text
    soup2 = BeautifulSoup(html2, "lxml")
    try:
        plays = soup.findAll("div", attrs={"class":"prof-beatmap"})[:50] #don't want first places
        plays2 = soup2.findAll("div", attrs={"class":"prof-beatmap"})[:50] #don't want first places
        pp_estimate = 0
        for play in plays:
            try:
                score = " ".join(play.find("div", attrs={"class":"h"}).text.split())
                accuracy = score.split(" ")[-1][1:-1]
                artist = score.split(" - ")[0]
                try:
                    mods_potential = score.split(" ")[-2]
                    mods_potential2 = mods_potential.split("+")[-1]
                    mods = mods_potential2.split(",")
                    if mods_potential == mods_potential2:
                        mods = None
                except:
                    mods = None
                time = " ".join(play.find("div", attrs={"class":"c"}).text.split())
                pp_str = " ".join(play.find("div", attrs={"class":"pp-display"}).text.split())
                pp = pp_str[:-2]
                pp_w_object = play.find("div", attrs={"class":"pp-display-weight"})
                try:
                    replay_download = "https://osu.ppy.sh"+pp_w_object.find("a").get("href")
                except:
                    replay_download = None
                pp_weighted_str = " ".join(pp_w_object.text.split())
                pp_weighted = int(pp_weighted_str.split("(")[1].split(")")[0].split("pp")[0])
                pp_weighted_percent = pp_weighted_str.split(" ")[1]
                pp_estimate += pp_weighted
                #print(modes[mode_id],score,time,pp,pp_weighted,replay_download)
                scores.append([modes[mode_id],score,artist,accuracy,time,pp_str,pp,pp_weighted_str,pp_weighted,pp_weighted_percent,mods,replay_download])
            except:
                print("Error with score!")
        for play in plays2:
            try:
                score = " ".join(play.find("div", attrs={"class":"h"}).text.split())
                accuracy = score.split(" ")[-1][1:-1]
                artist = score.split(" - ")[0]
                try:
                    mods_potential = score.split(" ")[-2]
                    mods_potential2 = mods_potential.split("+")[-1]
                    mods = mods_potential2.split(",")
                    if mods_potential == mods_potential2:
                        mods = None
                except:
                    mods = None
                time = " ".join(play.find("div", attrs={"class":"c"}).text.split())
                pp_str = " ".join(play.find("div", attrs={"class":"pp-display"}).text.split())
                pp = pp_str[:-2]
                pp_w_object = play.find("div", attrs={"class":"pp-display-weight"})
                try:
                    replay_download = "https://osu.ppy.sh"+pp_w_object.find("a").get("href")
                except:
                    replay_download = None
                pp_weighted_str = " ".join(pp_w_object.text.split())
                pp_weighted = int(pp_weighted_str.split("(")[1].split(")")[0].split("pp")[0])
                pp_weighted_percent = pp_weighted_str.split(" ")[1]
                pp_estimate += pp_weighted
                #print(modes[mode_id],score,time,pp,pp_weighted,replay_download)
                scores.append([modes[mode_id],score,artist,accuracy,time,pp_str,pp,pp_weighted_str,pp_weighted,pp_weighted_percent,mods,replay_download])
            except:
                print("Error with score!")
        return scores,pp_estimate
    except:
        print("No Scores!")
for user_name in user_names:
    user_id = get_user_id(user_name)
    if user_id != None:
        for mode in modes:
            pp = get_mode_pp(user_id,mode)
            try:
                scores,pp_estimate = get_top_plays(user_id,mode)
            except:
                scores = []
                pp_estimate = 0
            #print(pp,scores)
            pp.append(pp_estimate)
            #print(pp)
            flag = 0
            pp_farm_plays = []
            for score in scores:
                #print(score)
                pp_list = ["sotarks","will stetson"]
                for farm_word in pp_list:
                    if farm_word in score[1].lower():
                        pp_farm_plays.append(score[1])
            value = 0
            for pp_farm_score in pp_farm_plays:
                #print(pp_farm_score)
                value += 1
            farmer_percent = str(value)+"%"
            print(user_name,mode+":",farmer_percent,"farmer")
    else:
        print("No User {}!".format(user_name))


