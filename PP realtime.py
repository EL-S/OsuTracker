import requests
from bs4 import BeautifulSoup
import json
import time

data_name = "data.txt"
pp_threshold = 0
wait = 1

user_data = []
data = []
prompt = "n"
flag = False
pp = 0
pp_old = 0

def init():
    global user_data
    try:
        read_data()
        update_user_names()
        add_new_users()
        write_data()
        print("Now Tracking...")
    except IOError:
        print("Creating Data File...")
        with open(data_name, "w") as file:
            file.write("")
        init()

def read_data():
    global user_data
    user_data = [] #clear all data
    with open(data_name, "r+") as file:
        for line in file:
            data = line.strip().split(",")
            #user_id = data[0]
            #user_name = data[1]
            #pp = data[2]
            user_data.append(data)

def write_data():
    global user_data
    with open(data_name, "w") as file:
        for data_packet in user_data:
            data = ",".join(data_packet)+"\n"
            file.write(data)

def update_user_names(): #might not be needed at all, already done in the loop
    global user_data
    if user_data != []:
        flag_1 = False
        prompt_update = "n"
        while (prompt_update != "y") and (flag_1 == False):
            prompt_update = input("Validate Usernames?: ").lower()
            if (prompt_update == "yes"):
                prompt_update = "y"
            elif (prompt_update == "no"):
                prompt_update = "n"
            if (prompt_update == "y") or (prompt_update == "n"):
                flag_1 = True
        new_user_names = []
        if prompt_update == "y":
            print("Validating Usernames...")
            for data_packet in user_data:
                    user_id = data_packet[0]
                    old_user_name = data_packet[1]
                    new_user_name,user_id,pp = get_user_data(user_id) #get new username for human readability
                    data_packet[1] = new_user_name
                    if new_user_name != None:
                        new_user_names.append(new_user_name)
                        if new_user_name != old_user_name:
                            print(old_user_name,"changed their username to",new_user_name+"!")
                        print("Validated {}".format(new_user_name))
                    #else maybe remove the person because their account is gone?
        else:
            for data_packet in user_data:
                new_user_names.append(data_packet[1])
        if new_user_names != []:
            print("Currently Tracking: "+", ".join(new_user_names))

def get_user_data(user_id):
    global wait
    try:
        time.sleep(wait)
        url = 'https://osu.ppy.sh/u/'+str(user_id)
        data = request_url(url)
        soup = BeautifulSoup(data, "lxml")
        try:
            data_profile = soup.find("script", attrs={"id": "json-user"}).text.strip()
            json_data = json.loads(data_profile)
            username_on_page = json_data["username"]
            userid_on_page = json_data["id"]
            try:
                pp = float(json_data['statistics']['pp'])
            except:
                #never submitted a score
                pp = float(0)
            return [username_on_page,userid_on_page,pp]
        except Exception as e:
            print("Invalid user: {}".format(user_id))
            return None
    except:
        get_user_data(user_id)

def request_url(url): #to make getting proxies and custom headers easy
    global wait
    #proxies = get_proxies() #maybe if it has been 10 minutes since the last one?
    try:
        req = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"})
        data = req.text
        return data
    except:
        time.sleep(wait)
        request_url(url)

def add_new_users():
    try:
        global prompt, flag, user_data
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
            userdata_to_add = []
            for user in users_to_add:
                user_name = str(user).strip()
                data = get_user_data(user_name)
                if data != None:
                    user_name,user_id,pp = data[0],data[1],data[2]
                    print("Acquired {}'s Data".format(user_name))
                    if user_id != None:
                        userdata_to_add.append([str(user_id).strip(),str(user_name),str(pp)])
                    else:
                        print("Error finding UserID for user: {}".format(user_name))
            currently_tracked = []
            for data_packet in user_data:
                currently_tracked.append(data_packet[1])
            for data_packet in userdata_to_add:
                if data_packet[1] in currently_tracked:
                    print("Already Tracking {}".format(data_packet[1])) #do nothing
                else:
                    user_data.append(data_packet) #add the user to the user_data
                    print("Validated {}".format(data_packet[1]))
            if user_data != []:
                user_names = []
                for data_packet in user_data:
                    user_names.append(data_packet[1])
                print("Now Tracking: "+", ".join(user_names))
        else:
            pass #no users to add
    except Exception as e:
        print("error2",e)

def main():
    for data_packet in user_data:
        user_id = data_packet[0]
        old_pp = data_packet[2]
        data = get_user_data(user_id)
        if data != None:
            user_name,user_id,new_pp = data[0],data[1],data[2]
            if user_name != data_packet[1]:
                print(data_packet[1],"changed their username to",user_name+"!")
                data_packet[1] = str(user_name)
            if user_id != None:
                try:
                    time_current = time.strftime("%I:%M:%S %p %d/%m/%y", time.localtime(int(time.time())))
                except:
                    pass
                pp_new_rounded = "{0:.2f}".format(round(float(new_pp),2))
                pp_old_rounded = "{0:.2f}".format(round(float(old_pp),2))
                pp_change = float(pp_new_rounded)-float(pp_old_rounded)
                if (pp_new_rounded != pp_old_rounded) and ((pp_change >= pp_threshold) or (pp_threshold == 0)):
                    data_packet[2] = str(new_pp)
                    pp_change = float("{0:.2f}".format(round(float(pp_change),2)))
                    if (pp_change < 0):
                        print(user_name+":","NEW PP("+str(pp_new_rounded)+")"+" -> ""RAW PP LOSS("+str(abs(pp_change))+")",time_current)
                    else:
                        print(user_name+":","NEW PP("+str(pp_new_rounded)+")"+" -> ""RAW PP GAIN("+str(pp_change)+")",time_current)
        else:
            print("User {} does not exist! Banned?".format(data_packet[1]))
            user_data.remove(data_packet) #stop tracking them and remove all data
        write_data()

init()
while True:
    main()


