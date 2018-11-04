import requests
from bs4 import BeautifulSoup
import json
import time

#change
config_name = "config.txt"
pp_data_name = "pp_data.txt"
pp_threshold = 0 #only show pp changes above this amount

#don't change
usernames_to_add = []
usernames = []
config_usernames = []
pp_data = {}
prompt = "n"
flag = False

def init():
    try:
        read_config()
        add_new_users_prompt()
        add_users()
        update_userlist()
        initialise_values()
        read_pp_data()
    except:
        with open(config_name, "w") as file:
            file.write("")
        init()

def initialise_values():
    for username in usernames:
        pp_data[username] = 0 #to prevent null errors

def read_config():
    global config_usernames
    with open(config_name, "r+") as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line not in config_usernames:
                config_usernames.append(stripped_line)
    if prompt == "y":
        print("Now Tracking: "+", ".join(config_usernames))
    else:
        print("Currently Tracking: "+", ".join(config_usernames))

def add_new_users_prompt():
    try:
        global usernames_to_add, prompt, flag
        while (prompt != "y") and (flag == False):
            prompt = input("Add new users to track? (y/n): ").lower()
            if (prompt == "yes"):
                prompt = "y"
            elif (prompt == "no"):
                prompt = "n"
            if (prompt == "y") or (prompt == "n"):
                flag = True
        if prompt == "y":
            users = input("New Users (eg. username1,username2): ")
            users_to_add = users.split(",")
            for user in users_to_add:
                usernames_to_add.append(user.strip())
        else:
            pass
    except Exception as e:
        print(e)

def add_users():
    global usernames_to_add,prompt
    with open(config_name, "a") as file:
        for username in usernames_to_add:
            if username not in config_usernames:
                file.write(username.strip()+"\n")
    if prompt == "y":
        read_config()
    

def update_userlist():
    global usernames
    with open(config_name, "r+") as file:
        for line in file:
            if line not in usernames:
                usernames.append(line.strip())

def read_pp_data():
    global pp_data_name, pp_data
    try:
        with open(pp_data_name, "r+") as file:
            for line in file:
                user_data = line.split(",")
                username = user_data[0].strip()
                pp = user_data[1].strip()
                pp_data[username] = float(pp)
    except:
        with open(pp_data_name, "w") as file:
            file.write("")

def write_pp_data():
    with open(pp_data_name, "w") as file:
        for data in pp_data.items():
            csv_data = data[0]+","+str(data[1])+"\n"
            file.write(csv_data)
    
    

init()

while True:
    for username in usernames:
        try:
            req = requests.get('https://osu.ppy.sh/u/'+str(username), headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"})
            data = req.text

            soup = BeautifulSoup(data, "lxml")
            data_profile = soup.find("script", attrs={"id": "json-user"}).text.strip()
            json_data = json.loads(data_profile)
            pp_old = pp_data[username]
            pp = json_data['statistics']['pp']
            time_current = time.strftime("%H:%M:%S %p %d/%m/%y", time.gmtime())
            pp_gain = float(pp)-float(pp_old)
            
            if (pp != pp_old) and (pp_gain >= pp_threshold):
                pp_data[username] = pp
                pp_gain = "{0:.2f}".format(round(pp_gain,2))
                print(username+":","NEW PP("+str(pp)+")"+" -> ""RAW PP GAIN("+str(pp_gain)+")",time_current)
        except:
            pass
    write_pp_data()
