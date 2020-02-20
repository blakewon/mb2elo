import network
import filewatch
import player
import time
import pickle
import math
Player = player.Player

#filewatch functions
get_ip = filewatch.get_ip
connection_id = filewatch.connection_id
remove_colorcode = filewatch.remove_colorcode

#TO DO: implement an id search for ppl who have retarded short names like "a" or "."



new_line = ""
wait_for_name = False
client = Player()
current_players = []
playerlist = []

#line separation
#examples:
# 0:25 ClientConnect: 0 (IP: 192.168.0.177:29071)
# 15:49 say: J^4|^7Y ^4b^7lake_^4w^7on: asdasdasd




        

timestamp = ""      #timestamp at beggining of each line
event = ""          #e.g. ClientConnect: , Say: , Kill: etc.
event_content = ""  #self-explanitory
chat = ""           #what people say
pickles = -1

test = filewatch.get_line() #delete this


def elo(Ra,Rb): #chess rating algorithm
    e1 = pow(10, float(Ra)/400)
    e2 = pow(10, float(Rb)/400)
    k = 10
    z = Rb + k * (0 - e2 / (e1 + e2))

    return int(Rb - z)

def duel_start(p1, p2):

    current_players[p1].in_duel = True
    current_players[p2].in_duel = True
    network.send_cmd("svsay " + current_players[p1].name + "^7[^3" + str(current_players[p1].mmr) + "^7]" + "  VS. " + current_players[p2].name + "^7[^3" + str(current_players[p2].mmr) + "^7]")
    
def get_index(name , list):
    try:
        index = [ x.name for x in list ].index(name)
        return index
    except:
        print("wtf")

def duel_end(id, current_players):
    p1 = id
    p2 = 0
    for x in current_players:
        if current_players[p1].opponent == x.name:
            break
        p2+=1
    
    current_players[p1].opponent = "%%#" #using this as an "empty" opponent since oone in-game can have "%" character in their name (game restriction)
    current_players[p1].in_duel = False
    difference = elo(current_players[p2].mmr, current_players[p1].mmr)
    current_players[p1].mmr -= difference

    current_players[p2].opponent = "%%#"
    current_players[p2].in_duel = False
    old_mmr2 = current_players[p2].mmr
    current_players[p2].mmr += difference
    print(difference)

    network.send_cmd("svsay [" + current_players[p2].name +"^7(^2+" + str(difference) + "^7)"+ " has won the duel against " + current_players[p1].name+ "^7(^1-" + str(difference) + "^7)")
    

def print_player(pid, current_players = [Player()]):
    try:
        print("[NAME: " + current_players[pid].name + "]" + "[ID: " + str(current_players[pid].id) + "]" + "[OPPONENT: " + current_players[pid].opponent + "]")
    except:
        print("error printing")
def print_list(current_players = [Player()]):
    index = 0
    for client in current_players:
        print_player(index ,current_players)
        index+=1

def search_id2(id, array):
    index = 0
    for x in array:
        if id == x.id:
            print("INDEX: " + str(index))
            return index
        index+=1
    print("Client with ID: " + str(id) + " not found, please reconnect")
    return -1


def search_ip(ip, array):
    index = 0
    for x in array:
        if ip == x.id:

            return index
        index+=1
    return -1

def search_id(id, array):
        for x in array:
            if id == x.id:
                return x


def search_name2(name, array):
    index = 0
    try:
        print("Searching with: " + name)
    except:
        print("tried printing search index")
    for x in array:
        try:
            print("Comparing to: " + x.name)
        except:
            ("tried printing seach-ee")
        if name == x.name:
            print("INDEX: " + str(index))
            return index
        index+=1
    print("Client with that name is not found: " + name)
    return -1
        

def challenge_to_duel(current_players , pid, line2 = ""):
    p1 = pid
    p2 = 0
    it = 0
    flag = 0
    try:
        print("THIS NAME" + current_players[pid].name)
    except:
        print(1)

    for x in current_players:

        if flag > 1:
           network.send_cmd("There are too many players matching that argument.")
           p1 = pid
           p2 = 0
           it = 0
           flag = 0
           return
        if remove_colorcode(line2.lower()) in remove_colorcode(x.name.lower()):
            p2 = it
            flag+=1
        it+=1
    print(p1 , p2, it, flag)
    if flag == 0:
        network.send_cmd("No players match that argument.")
        return

    print("point1")
    print(p1, p2)
    if flag == 1:
        try:
            print(current_players[p2].name)
        except:
            print(2)
        current_players[p1].opponent = current_players[p2].name
        print("point2")
        if current_players[p2].opponent == current_players[p1].name:
            if not current_players[p2].in_duel:
                print("point3")
                if not current_players[p1].in_duel:
                    print("point4")
                    duel_start(p1,p2)
                    del(p1,p2,it,flag)




    




            