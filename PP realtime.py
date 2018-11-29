import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
from random import *

data_name = "data.txt"
pp_threshold = 0
wait = 1

#osu track settings
user_data = []
data = []
prompt = "n"
flag = False
pp = 0
pp_old = 0

#proxy settings
use_proxies = True
proxy_list = []
#wait = 2
timeout_connect = 1
timeout_read = 1
proxy_loops = 0

def init():
    global user_data,proxy_list,user_proxies
    try:
        if use_proxies == True:
            proxy_list = update_proxies()
            print(proxy_list)
        else:
            proxy_list = None
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

##def request_url(url): #to make getting proxies and custom headers easy
##    global wait
##    #proxies = get_proxies() #maybe if it has been 10 minutes since the last one?
##    try:
##        req = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"})
##        data = req.text
##        return data
##    except:
##        time.sleep(wait)
##        request_url(url)

def request_url(url,headers=None):
    global wait,proxy_counter,use_proxies,proxy_list,proxy_loops
    maximum_loops = 50
    try:
        if proxy_loops >= maximum_loops:
            if use_proxies == True:
                print("Updating Proxies")
                proxy_list = update_proxies()
                print(proxy_list)
            else:
                proxy_list = None
            proxy_loops = 0
        if proxy_counter > (len(proxy_list)-1):
            proxy_counter = 0
            proxy_loops += 1
    except:
        proxy_counter = 0
    try:
        if headers == None:
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
        try:
            headers["User-Agent"]
        except:
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
        if use_proxies == True:
            #proxy_ip = proxy_list[randint(0,len(proxy_list)-1)][0]
            proxy_ip = proxy_list[proxy_counter][0]
            #print("Counter: ("+str(proxy_counter)+"/"+str(len(proxy_list)-1)+")","Loop: ("+str(proxy_loops)+"/"+str(maximum_loops)+")")
            proxy = {"https":proxy_ip,"http":proxy_ip}
            #print("Proxy Ip:",proxy_ip)
            proxy_counter += 1 #track position in the proxy list
            
            req = requests.get(url, headers=headers, proxies=proxy,timeout=3)
            status = req.status_code
            if status != 200:
                #print(data)
                request_url(url,headers)
            data = req.text
            
        else: #don't use proxies
            req = requests.get(url, headers=headers)
            if status != 200:
                #print(data)
                request_url(url,headers)
            data = req.text
        if data == None:
            #print("Page returned nothing! Reloading")
            request_url(url,headers)
        elif data == "None":
            #print("Page returned nothing string! Reloading")
            request_url(url,headers)
        else:
            #print(data)
            title = BeautifulSoup(data, "lxml").find("title").text
            if title == "Attention Required! | Cloudflare":
                #print("cloudflare")
                request_url(url,headers)
            else:
                return data
    except Exception as e:
        #print("Page failed to load or Request timed out! Reloading",e)
        if use_proxies != True:
            time.sleep(wait)
        request_url(url,headers)

def update_proxies():
    unchecked_proxies = get_proxies()
    checked_proxies = check_proxies(unchecked_proxies)
    if (len(checked_proxies) == 0):
        update_proxies()
    else:
        return checked_proxies
    
def get_proxies():
    unchecked_proxies = []
    proxies_page = requests.get("http://spys.one/en/anonymous-proxy-list/").text
    soup = BeautifulSoup(proxies_page, "lxml")
    legend_code = soup.find("script", attrs={"type": "text/javascript"}).text.split(";")
    legend_code2 = []
    legend = {}
    for code in legend_code:
        code_clean = code.split("^")[0]
        if code_clean != code:
            legend_code2.append(code_clean.split("="))
    for code2 in legend_code2:
        legend[code2[0]] = code2[1]
    rows = soup.findAll("tr", attrs={"onmouseover": "this.style.background='#002424'"})
    for row in rows:
        proxy_row = row.findAll("td", attrs={"colspan": "1"})
        proxy = proxy_row[0].find("font", attrs={"class": "spy14"}).text
        proxy_type = proxy_row[1].text
        proxy_code = proxy.split("(")
        port_code = []
        for proxy_code_segment in proxy_code:
            proxy_code_segment = proxy_code_segment.split(")")
            port_code.append(proxy_code_segment[0].split("^")[0])
            
        proxy_ip = port_code[0].split("d")[0]
        proxy_numbers = []
        for code_to_solve in port_code[2:]:
            number = legend[code_to_solve]
            proxy_numbers.append(number)
        proxy_port = "".join(proxy_numbers)
        proxy = str(proxy_ip)+":"+str(proxy_port)
        unchecked_proxies.append([proxy,proxy_type])
##    for i in unchecked_proxies:
##        print(i)
    return unchecked_proxies

def get_ip():
    status = 0
    while status != 200:
        try:
            url = "http://ip-check.info/?lang=en"
            req = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            html = req.text
            soup = BeautifulSoup(html, "lxml")
            current_ip = soup.findAll("script", attrs={"type":"text/javascript"})[3].text.split("'\">")[1].split(r"</a>")[0]
            status = req.status_code
        except:
            pass
    return current_ip

def check_proxies(unchecked_proxies):
    global timeout_connect,timeout_read
    checked_proxies = []
    
    current_ip = get_ip()
    
    for host in unchecked_proxies:
        try:
            proxy = {"https":host[0],"http":host[0]}
            url = "http://ip-check.info/?lang=en"
            time1 = datetime.datetime.now()
            req = requests.get(url, headers={"User-Agent": "fight me"}, proxies=proxy, timeout=(timeout_connect, timeout_read))
            time2 = datetime.datetime.now()
            ping = str(int((time2 - time1).total_seconds() * 1000))+"ms"
            html = req.text
            soup = BeautifulSoup(html, "lxml")
            ip = soup.findAll("script", attrs={"type":"text/javascript"})[3].text.split("'\">")[1].split(r"</a>")[0]
            status = req.status_code
            if ip == host[0].split(":")[0]:
                print("Working:",ping, host[0])
                checked_proxies.append(host)
            elif ip == current_ip:
                print("Not Working:",host[0])
            else:
                print("MultiLayered Working:",ping, ip, host[0])
                checked_proxies.append(host)
        except requests.exceptions. Timeout:
            print("Timed Out:",host[0])
        except:
            print("Not Working Fatal:",host[0])
    return checked_proxies

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


