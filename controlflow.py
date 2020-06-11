import MMR
import network
import player
import string
import random
import filewatch
import threading
import pickle
import re
import socket
import json
import ftplib
import multiprocessing
import subprocess
import shlex
import sys
import os
#ClientConnect: 0 (IP: 192.168.0.177:29070)
#ClientConnect: 1 (IP: 192.168.0.123123:29070)

#broadcast: "NAME1 @@@PDUELACCEPT NAME2"
#KILL : 0 1 123123 GOT KILLED BY WHATEVER





#This controlflow module is used for processing each line from start.sh stdout.  I'm using this stdout as an API to interface with the game.
#This log file was not designed to be used as such, so spaghetti code and excessive commenting is required in this module, as the stdout lines are inconsistent and just generally not designed with these scripts in mind, probably evident by the fact that noone has even attempted this
#Due to those issues, going to be a lot of weird one-time conditionals, but i will try my best to document what they do, and why they're in there.
#The main thread of this module (for now) continiously reads stdout, and starts a new thread to process each line separately to avoid skipping necessary data

#stdout examples:
#  ClientConnect: (J^4|^7P ^4b^7lake_^4w^7on) ID: 2 (IP: 178.220.143.189:29070)
#  1:32 say: J^4|^7Y ^4b^7lake_^4w^7on: !dummies
#  1:55 Kill: 0 0 7: J^4|^7Y ^4b^7lake_^4w^7on killed J^4|^7Y ^4b^7lake_^4w^7on by MOD_SUICIDE
#  1:41 ClientUserinfoChanged: 0 n\J^4|^7Y ^4b^7lake_^4w^7on\t\3\model\kreia/

#There's a few general rules of thumb in this script:

#timestamp string is the timestamp at the beggining of each log line
#event is a string usually right after the timpestamp, i presume its purpose is to describe the actual purpose of the log line, and im using it as such
#event_content is the actual content after the "event" instance
#pindex is an index of the player class in the actual list
#pid is the ingame playerID. that id is not a GUID, but rather a temporary id to signify which slot in the server is occupied by the player. (MAX IS 32)




#input method
#get_line = filewatch.get_line1

#MMR duel management methods
current_players = MMR.current_players   #list of successfuly initialized players
searchby_name = MMR.search_name2        #takes a name string and a list as arguments, searches list for a player and returns his index in the list, so that the player can be manipulated
searchby_id = MMR.search_id2            #same as searchby_name, only takes the in-game playerID to find the index
searchby_ip = MMR.search_ip             #same as searchby_name, except that it searches for the index with the ip
duel_end = MMR.duel_end                 #used to manage MMR when one player that's in an active duel dies

player_queue = []   #when event_clientconnect is called it puts a player into this list, and the script waits for an Userinfo event to get the necessary data to initialize the player into current_players
playerlist = []     #list used for saving players that are not ingame
Player = player.Player #imports the player class from the player.py module. It's in a separate file because as i was writing this, i thought that the class would need to have a whole lot of methods to it. That obviously isn't the case now,but this is all still unfinished.
                        




def say_dummies(pid, current_players): # [TESTING PURPOSES] Creates fake players, "dummies", that you can initiate duels with. 
    #dummies.id will be a random number greater than 32 (id limit ingame, so no real player would be able to have such an id)
    #The opponent of these dummies will be the name of the person that initiated the !dummies command

    current_players.append(Player(random.randrange(33, 99), "fake_ip" + str(2) ,2000,"^1thruman",current_players[pid].name,True,False,None,0,0))
    current_players.append(Player(random.randrange(33, 99), "fake_ip" + str(3) ,1000,"Cr^2ooked",current_players[pid].name,True,False,None,0,0))
    current_players.append(Player(random.randrange(33, 99), "fake_ip" + str(5) ,1500,"fonzie",current_players[pid].name,True,False,None,0,0))
    current_players.append(Player(random.randrange(33, 99), "fake_ip" + str(6) ,1500,"^bogey",current_players[pid].name,True,False,None,0,0))

    playerlist.append(Player(random.randrange(33, 99), "fake_ip" + str(2) ,2000,"^1thruman",playerlist[pid].name,True,False,None,0,0))
    playerlist.append(Player(random.randrange(33, 99), "fake_ip" + str(3) ,1000,"Cr^2ooked",playerlist[pid].name,True,False,None,0,0))
    playerlist.append(Player(random.randrange(33, 99), "fake_ip" + str(5) ,1500,"fonzie",playerlist[pid].name,True,False,None,0,0))
    playerlist.append(Player(random.randrange(33, 99), "fake_ip" + str(6) ,1500,"^bogey",current_players[pid].name,True,False,None,0,0))
   
    MMR.print_list(current_players)

def say_elo(event_content,name,current_players): #custom !elo command that prints out the player's ELO points in-game
    pindex = searchby_name(name, current_players) #this searchby_name method returns -1 if no players are found in a given list
    #say [NAME] : CHAT
    if pindex != -1:
        network.send_cmd("svsay " + name + "^7's ELO: [^3" + str(current_players[pindex].mmr) + "^7]")

        #Cleanup
        del(pindex)
        return True
    else: #!ELO
        return True
def printplayer(index, list): #[TESTING PURPOSES] prints out a player in stdout
    print("[NAME: " + list[index].name + "]" + "[ID: " + str(list[index].id) + "]" + "[IP: " + list[index].ip + "]" + "[ELO: " + str(list[index].mmr) + "]")

def printlist(list):          #[TESTING PURPOSES] prints out a playerlist in stdout
    for x in list:
        print("[NAME: " + str(x.name) + "]" + "[ID: " + str(x.id) + "]" + "[IP: " + str(x.ip) + "]" + "[ELO: " + str(x.mmr) + "]")

def say_print():              #[TESTING PURPOSES] used to execute the printlist() function from the in-game chat
    print("LIST")
    printlist(playerlist)

def say_duel(event_content, name, current_players): #custom "!duel [OPPONENT]" chat command, searches the current_players list for an opponent, duel is only started when two players have a matching opponent, this is obsolete now.
    pindex = searchby_name(name, current_players)
    if pindex == -1:
        network.send_cmd("Client with \"" + str(name) + "\" name is not initialized, please reconnect.")
        #cleanup
        del(pindex)
        return False
    try:
        query = event_content.split("!duel ",1)[1]  #Splits the chat event_content so you can get the name to search with
    except:
        print("Error processing [DUEL] chat command.")

    if not current_players[pindex].in_duel:
        print("Challenging to duel..")
        MMR.challenge_to_duel(current_players, pindex, query)

        #cleanup
        del(name,pindex,query)
        return True

    else:
        print("Challenger already in a duel.")

        #cleanup
        del(name,pindex,query)
        return False

def say_chill(i):          #custom !chill command, disables ranked dueling for the player that executes the command.
    current_players[i].chill = not current_players[i].chill
    if current_players[i].chill:
        network.send_cmd("svsay %s's ranked mode: ^1OFF" %(current_players[i].name))
    else:
        network.send_cmd("svsay %s's ranked mode: ^2ON" %(current_players[i].name))


def event_say(event, event_content): # executes if line is a "Say:" event, and processes it further using other methods
    if "say" in event:
        print("say before:")
        print(event_content)
        event_content = event_content.replace("\"", "")
        print("SAY NOW: ")
        print(event_content)
        name = event_content.split(": ",1)[0]

        if "Server" in name:                          #if some wise guy decides to name himself "Server", returns so it doesn't process his chat commands
            return
        pindex = searchby_name(name, current_players)    #returns -1 if no player is found
        if pindex == -1:
            return False

        chat = event_content.split(": ",1)[1]         #initiates the content of the chat event

        #CUSTOM CHAT COMMANDS
        if chat == "!dummies":
            say_dummies(pindex, current_players)

            #CLEANUP
            del(name, chat)
            return True
        if chat.startswith("!chill"):
            say_chill(pindex)
        if chat.startswith("!printl"):
            say_print()
            return True
        if chat.startswith("!elo"):
            say_elo(event_content,name,current_players)
            return True

    else:
        return False
def event_kill(event, event_content, current_players): #executes when the "kill" event is triggered in-game
    if "Kill" in event:
        pid = int(event_content.split(" ",2)[1])       #grabs the id from the event line

        print("Death id: " , pid)

        dead_player = searchby_id(pid, current_players)#searches for the player with that ID in the playerlist, returns -1 if no player is found
        if dead_player == -1:
            print("Client not initialized, please reconnect.", pid)
            return False
        if current_players[dead_player].in_duel:       #checks if the person is in an active duel, and if he is executes the duel management function
            duel_end(dead_player, current_players)

    else:
        return False

def event_disconnect(event, event_content, current_players): #executes when the "kill" event is triggered in-game
    if "ClientD" in event:
        pid = int(event_content.split(" ",1)[0])  #grabs the player ID
        print("Disconnected id: : " , pid)

        pindex = searchby_id(pid, current_players)#searches for the player with that ID, returns -1 if no player is found
        print("PINDEX: " + str(pindex))
        if pindex == -1:
            #network.send_cmd("Client not initialized, please reconnect.")
            print("Uninitialized client disconnected ID: ", pindex)
            return False
        if current_players[pindex].in_duel:
            duel_end(pindex, current_players)

        print("Removing player..")

        if x.guid != "0":                      #will be triggered if the player is using OpenJK, and will attempt to save the player through his OpenJK GUID
            for x in playerlist:
                if x.guid == current_players[pindex].guid:
                    x.mmr = current_players[pindex].mmr
                    x.name = current_players[pindex].name
                    x.wins = current_players[pindex].wins
                    x.losses = current_players[pindex].losses
                    x.guid = current_players[pindex].guid
                    current_players.pop(pindex)
                    queue_index = searchby_id(pid,player_queue)
                    if queue_index != -1:
                        player_queue.pop(queue_index)
                    return True



        for x in playerlist:                #if the client is a JAMP user, it will attempt to save the player through his IP.
            if x.ip == current_players[pindex].ip:
                x.mmr = current_players[pindex].mmr
                x.name = current_players[pindex].name
                x.wins = current_players[pindex].wins
                x.losses = current_players[pindex].losses
                x.guid = current_players[pindex].guid
                current_players.pop(pindex)
                queue_index = searchby_id(pid,player_queue)
                if queue_index != -1:
                    player_queue.pop(queue_index)
                return True

        MMR.print_player(pindex, current_players)
        print("REMOVING AND SAVING PLAYER...\n")

        playerlist.append(current_players[pindex])#if this is a new player, it will simply append the playerlist with that player
        current_players.pop(pindex)

        queue_index = searchby_id(pid,player_queue)#cleanup
        if queue_index != -1:
            player_queue.pop(queue_index)
        return True
    else:
        return False
def event_userinfo(event, event_content): #finally initializes the client from the queue, now obsolete as i am using the "Player" event for the OpenJK GUID integration.
    if "Userinfo" in event:
        print("Userinfo...")
        #CLIENTUSERINFO CHANGED: 1  NAME, CLASS, COLOR, TEAM
        pid = int(event_content.split(" ",1)[0])
        pindex = searchby_id(pid, player_queue)
        if pindex != -1:
            print("found player in queue\n")
            try:
                name = event_content.split("\\",2)[1]
            except:
                print("error processing userinfo.")
                return True
        else:
            print("Player not found in queue: ", pid)
            return True


        for x in current_players:                       #since there is no "Changed name to" event, i'm using userinfo to manage changed names in-game
            if x.id == pid:
                print("Client ", x.id, " already initialized.")
                return
                return True

        if name == "Server":
            network.send_cmd("kick " + name)
            return True
        try:                                        #if player is existing in playerlist, load that client into current_players
            for x in playerlist:
                if x.ip == player_queue[pindex].ip:
                    print(x.mmr,"\n")
                    current_players.append(Player(pid, x.ip ,x.mmr,name,"%%#",None,False,None,x.wins,x.losses))
                    print("loaded existing player")
                    player_queue.pop(pindex)
                    return True
        except:
            print("Player not found in playerlist, creating new...")
        current_players.append(Player(pid,player_queue[pindex].ip, 1500, name, "%%#",True,False,None,0,0))
        playerlist.append(Player(pid,player_queue[pindex].ip, 1500,name,"%%#",True,False,None,0,0))
        player_queue.pop(pindex)
        print("New player created!")
        del(pid,pindex,event,event_content, name)
        return True
    else:
        del(event,event_content)
        return False

def event_shutdown(event):                          #shutdown event, triggered on new rounds in-game. If you're modifying this script, it is recommended that you use this method for all your cleanups, maintenance etc.
    if "shutdown" in event.lower():
        print(">>>>>ROUND END<<<<<<<<<")
        for x in current_players:                  #saves each players to the playerlist each round. It has to be this way since the server "reconnects" everyone each round. (Meaning that the clientconnect event is triggered for everyone each round) 
            print("Resetting duels")
            x.in_duel = False
            x.opponent = "%%#"
            for y in playerlist:
                if x.ip == y.ip:
                    y.name = x.name
                    y.mmr = x.mmr
                    y.losses = x.losses
                    y.wins = x.wins
                    y.guid = x.guid
                    print("SAVING THIS DUDE TO PLAYERLIST: ", y.name,y.mmr)
        flush_list()
        player_queue.clear()
        current_players.clear()
        return True
    else:
        return False

def loadby_ip(ip, pid, name, guid):          #loads the player in by ip
    for x in playerlist:
        if ip == x.ip:
            current_players.append(Player(pid,ip,x.mmr,name,"##%",None,None,None,x.wins,x.losses,guid,False))
            print("Loaded existing player.")
            #printlist(current_players)
            return
    print("Existing player not found, creating new..")
    current_players.append(Player(pid,ip,1500,name,"##%",None,None,None,0,0,guid, False))
    playerlist.append(Player(None,ip,1500,name,"##%",None,None,None,0,0,guid,False))

def loadby_guid(ip, pid, name, guid):        #loads the player in by GUID for OpenJK users.
    if guid != "0":
        for x in playerlist:
            if guid == x.guid:
                current_players.append(Player(pid,ip,x.mmr,name,"##%",None,None,None,x.wins,x.losses,guid,False))
                print("Loaded player by GUID, [NAME: %s] [IP: %s] [GUID: %s]" %(name,ip,guid))  
                return True
    else:
        return False



def event_player(event, event_content):      #This is your player initialization method, grabs a player from the queue list (more on that in event_clientconnect() ). Attaches all the necessary data for duel management into the player class.
    if event.startswith("Player"):
            pid = int(event.split(" ",2)[1]) #Grabs the player ID from the event, returns -1 if no player is found
            if searchby_id(pid, current_players) != -1:
                print("Player with", pid, "id already intialized.")
                return True

            queue_i = searchby_id(pid, player_queue) #grabs the player from the queue using the Already saved ID
            if queue_i == -1:
                print("Player not found in queue, returning...")
                return True
            ip = player_queue[queue_i].ip
            player_queue.pop(queue_i)

            try:
                name = event_content.split("\\name\\",1)[1].split("\\",1)[0] #grabs the name
            except:
                print("Error in loading name from event_player, exiting..")
                return

            try:
                guid = event_content.split("\\ja_guid\\",1)[1].split("\\",1)[0] #attempts to grab the GUID if the client is using OpenJK
            except:
                guid = "0"
            print("Loading player with info: [IP: %s][PID: %s][NAME: %s]" %( ip, pid, name))
            if loadby_guid(ip,pid,name,guid):
                return True
                
            loadby_ip(ip,pid,name,guid)             #If the client is a JAMP user, it will load the player through IP
            return True
    else:
        return False

def event_broadcast(event,event_content):           #There's two useful things in the broadcast event. Player changing names, and the private duels are triggered through it.
    if "broadcast" in event:
        templine = event_content.strip().split("print ",1)[1][0:-3] #the broadcast event is formatted differently from all the others, containing 2 event descriptions as seen above
        if "@@@PLDUELACCEPT" in templine:           #Private duels
            print("Starting duel..")
            try:
                name1 = templine.split(" @@@PLDUELACCEPT ",1)[0][1:].strip()
                name2 = templine.split(" @@@PLDUELACCEPT ",1)[1].strip().split("\\",1)[0][:-1]
            except:
                print("Error getting the names, returning...")
                return True

            pindex1 = searchby_name(name1, current_players)
            pindex2 = searchby_name(name2, current_players)


            if pindex1 < 0 or pindex2 < 0:
                print("One or more players not found in current playerlist, returning..",name1,name2)
                return True
            if current_players[pindex1].chill or current_players[pindex2].chill:
                network.send_cmd("svtell %s ^3Unranked duel." %(current_players[pindex1].id))
                network.send_cmd("svtell %s ^3Unranked duel." %(current_players[pindex2].id))
                return True

            if not current_players[pindex1].in_duel:
                if not current_players[pindex2].in_duel:
                    current_players[pindex1].opponent = name2
                    current_players[pindex2].opponent = name1
                    MMR.duel_start_broadcast(pindex1, pindex2, current_players)
                    return True
            return True

        if "@@@PLRENAME" in templine: #Players changing names.
            try:
                name1 = templine.split(" @@@PLRENAME ",1)[0][1:-2].split("\\n",1)[0]
                name2 = templine.split(" @@@PLRENAME ",1)[1].strip()
                pindex = searchby_name(name1, current_players)
                current_players[pindex].name = name2
                print("success in changing name, [%s][%s]" %(name1, name2))
                return True
            except:
                print("Error in name change, returning..")
                return True
    return False

def event_clientconnect(event, event_content, player_queue): #adds players to the connection queue
    
    if "ClientConnect" in event:
        print("Client connecting..")

        pid = int(event_content.split("ID: ",1)[1].split(" ",1)[0]) #grabs the ID
        
        #ClientConnect: (J^4|^7P ^4b^7lake_^4w^7on) ID: 2 (IP: 178.220.143.189:29070)
        try:
            for x in current_players:
                if pid == x.id:
                    print("Client with that ID already initialized.")
                    return False
        except:
            print("Initializing player...PID: ",pid)
        ip = event_content.split("IP: ", 1)[1].split(":",1)[0]
        print(ip)

        print("Adding player to queue: [PID: %s] [IP: %s]" %(pid, ip))
        player_queue.append(Player(pid,ip,None,None,"%%#",False,False,None))

    else :
        return False


def test(new_line):                   #This is the "funnel" of the script. Checks each line for events and calls the appropriate functions.

            try:                #formatting
                event = new_line.lstrip().split(":",1)[0]
                try:
                    event_content = new_line.split(":",1)[1].lstrip()
                except:
                    event_content = ""
            except Exception as e:
                print("Error in initial processing: ", e)
                print(new_line)
                return

            if event.isdigit():       #For some reason, every "say" event starts with the playerIDs, this is the best workaround that i could think of.
                try:
                    event = event_content.lstrip().split(": ",1)[0]
                    event_content = event_content.lstrip().split(": ",1)[1].replace("\"", "") 
                except Exception as e:
                    print("Error in processing say event: ", e)
                    print(new_line)
                    return

            #funneling
            if event_shutdown(event):
                return
            if event_player(event, event_content):
                return
            if event_broadcast(event,event_content):
                return
            if event_clientconnect(event,event_content,player_queue):
                return
            if event_disconnect(event,event_content,current_players):
                return
            if event_say(event,event_content):
                return
            if event_kill(event,event_content,current_players):
                return
            if event_userinfo(event, event_content):
                return

mypath1 = 'D:/Program Files (x86)/Steam/steamapps/common/Jedi Academy/GameData/MBII/'
new_line = ""

def load_list():        #loads the players from players.json
    #try:
        with open("players.json","r+") as f:
            file_list = json.load(f)
            count = 0
            for clients in file_list:
                temp = Player(None,clients['ip'],clients['mmr'],clients['name'],None,None,None,None,clients['wins'],clients['losses'])
                playerlist.append(temp)
                print(temp.name, temp.id,temp.ip,temp.mmr)
                count = count + 1
            print("Loaded",count,"players!")
            f.close()


#this is a function that i have used to upload the playerlist json file to the personal leaderboard that i had owned. I am keeping this in here in case someone might find it useful
def upload_file(SERVER = "ftp server hostname", USER = "ftp username", FILE = "path to the file that you will be uploading", UPLOAD_AS = "name of the file you want to upload it as", PASS = "ftp password"):
    with open("path to the file you want to upload","rb+") as f:
        session = ftplib.FTP(SERVER, USER, PASS)
        session.cwd("folder on the server where you want your file to be")
        session.storbinary(UPLOAD_AS, f)
        session.quit()
        f.close()
        print("Saved the json file to the remote server.")


def flush_list(): #Saves the playerlist to the json file.

    with open("players.json","w+") as f:
        json.dump(playerlist, f,default=lambda o: o.__dict__,sort_keys=True,indent=4)
        print("saving playerlist for me")
        f.close()
    del(data)


#The initial loading of players upon starting the dedicated server.
print("Loading players..")
try:
    load_list()
except:
    print("Error loading list.")
printlist(playerlist)

def check_line(line):       #checks if the line in stoud is a line of interest. Improves performance of the script
    if line.startswith("Pl"):
        return True
    if line.startswith("Shut"):
        return True
    if line.startswith("ClientConne"):
        return True
    if line.startswith("ClientDisconn"):
        return True
    if line.startswith("Kill"):
        return True
    if "say:" in line[0:10]:
        return True
    if line.startswith("ClientUser"):
        return True
    if line.startswith("broadca"):
        return True
    return False


def run_command(command):

    # Execute command
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    # Read stdout and print each new line
    sys.stdout.flush()
    for line1 in iter(p.stderr.readline, b''):
        # Print line
        sys.stdout.flush()
        line1 = line1.decode('utf-8',errors='replace')
        print(">>> " + line1.rstrip())


        # Look for the string 'Render done' in the stdout output
        if check_line(line1.rstrip()):

            # Flushes the stdout to prevent pipe overflow.
            sys.stdout.flush()

            # Execute something
            t = threading.Thread(target=test,args=(line1,))
            t.start()
            t.join()
            
run_command("sh start.sh")


     



     


