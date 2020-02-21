import MMR
import network
import player
import string
import random
import filewatch
Player = player.Player
import threading
import pickle

#This controlflow module is used for processing each line from log.log.  I'm using this log file as an API to interface with the game, filewatch module is input, network module is output
#This log file was not designed to be used as such, so spaghetti code and excessive commenting is required in this module, as the logs are inconsistent and just generally not designed with these scripts in mind, probably evident by the fact that noone has even attempted this
#Due to those issues, going to be a lot of weird one-time conditionals, but i will try my best to document what they do, and why they're in there.
#The main thread of this module (for now) continiously reads the log file, and starts a new thread to process each line separately to avoid skipping a line

#log line examples:
#  0:20 ClientConnect: 0 (IP: 192.168.0.177:29071)
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
get_line = filewatch.get_line1

#MMR duel management methods
current_players = MMR.current_players   #list of successfuly initialized players
searchby_name = MMR.search_name2        #takes a name string and a list as arguments, searches list for a player and returns his index in the list, so that the player can be manipulated
searchby_id = MMR.search_id2            #same as searchby_name, only takes the in-game playerID to find the index
searchby_ip = MMR.search_ip             #idk why this is in here
duel_end = MMR.duel_end                 #used to manage MMR when one player that's in an active duel dies


queue = []          #this script's main thread continiously reads the log.log file, and puts new lines into this queue. Each time controlflow is called, a new thread is started to process the line, and pops the line out of the queue
player_queue = []   #when event_clientconnect is called it puts a player into this list, and the script waits for an Userinfo event to get the necessary data to initialize the player into current_players
playerlist = []     #list used for saving players that are not ingame

#with open("players.txt", "a+") as f: #WORK IN PROGRESS, the idea is at some point to save the players from playerlist to a file, not needed for now as it's in early testing stages
    #f.close()


#while 1:            #WORK IN PROGRESS, as stated in the above comment
    #dude = Player()
    #try:
        #dude.mmr = pickle.load(f)
        #dude.ip = pickle.load(f)
        #dude.aliases = pickle.load(f)
        #playerlist.append(dude)
    #except:
        #print("Loaded players..")
        #break



def say_dummies(pid, current_players): # [TESTING PURPOSES] Creates fake players, "dummies", that you can initiate duels with. 
    #dummies.id will be a random number greater than 32 (id limit ingame, so no real player would be able to have such an id)
    #The opponent of these dummies will be the name of the person that initiated the !dummies command

    current_players.append(Player(random.randrange(33, 99), "fake_ip" + str(2) ,2000,"^1thruman",current_players[pid].name,True,False,None))
    current_players.append(Player(random.randrange(33, 99), "fake_ip" + str(3) ,1000,"Cr^2ooked",current_players[pid].name,True,False,None))
    current_players.append(Player(random.randrange(33, 99), "fake_ip" + str(5) ,1500,"fonzie",current_players[pid].name,True,False,None))
    current_players.append(Player(random.randrange(33, 99), "fake_ip" + str(6) ,1500,"^bogey",current_players[pid].name,True,False,None))
   
    MMR.print_list(current_players)

def say_elo(event_content,name,current_players): #custom !elo command that prints out the player's ELO
    pid = searchby_name(name, current_players) #this searchby_name method returns -1 if no players are found in a given list
    if pid != -1:
        network.send_cmd("svsay " + name + "^7's ELO: [^3" + str(current_players[pid].mmr) + "^7]")

        #Cleanup
        del(pid)
        return True
    else:
        return True

def say_duel(event_content, name, current_players): #custom "!duel [OPPONENT]" chat command, searches the current_players list for an opponent, duel is only started when two players have a matching opponent
    pid = searchby_name(name, current_players)
    if pid == -1:
        network.send_cmd("Client with \"" + str(name) + "\" name is not initialized, please reconnect.")
        #cleanup
        del(pid)
        return False
    try:
        query = event_content.split("!duel ",1)[1]  #Splits the chat event_content so you can get the name to search with
    except:
        print("Error processing [DUEL] chat command.")

    if not current_players[pid].in_duel:
        print("Challenging to duel..")
        MMR.challenge_to_duel(current_players, pid, query)

        #cleanup
        del(name,pid,query)
        return True

    else:
        print("Challenger already in a duel.")

        #cleanup
        del(name,pid,query)
        return False


def event_say(event, event_content, current_players): # executes if line is a "Say:" event, and processes it further using other methods
    if "say:" in event:
     
        name = event_content.split(": ",1)[0]
        MMR.print_list(current_players)

        if "Server" in name:                          #if some wise guy decides to name himself "Server", returns so it doesn't process his chat commands
            return
        pid = searchby_name(name, current_players)    #returns -1 if no player is found
        if pid == -1:
            return False

        chat = event_content.split(": ",1)[1]         #initiates the content of the chat event

        #CUSTOM CHAT COMMANDS
        if chat == "!dummies":
            say_dummies(pid, current_players)

            #CLEANUP
            del(name, chat)
            return True
            
        if chat.startswith("!duel "):
            say_duel(event_content , name, current_players)

            del(name, chat)    
            return True
        if chat.startswith("!elo"):
            say_elo(event_content,name,current_players)
            return True

    else:
        return False
def event_initgame(event):                          #resets duels for all players when the round ends
    if "InitGame:" in event:
        for x in current_players:
            print("Resetting duels")
            x.in_duel = False
            x.opponent = "%%#"
            return True
    else:
        return False

def event_kill(event, event_content, current_players):
    if "Kill:" in event:
        pid = int(event_content[2])
        print("Death id: " , pid)

        dead_player = searchby_id(pid, current_players)
        if dead_player == -1:
            #network.send_cmd("Client not initialized, please reconnect.")
            print("Client not initialized, please reconnect.")
            return False
        if current_players[dead_player].in_duel:
            duel_end(dead_player, current_players)

    else:
        return False

def event_disconnect(event, event_content, current_players):
    global f
    if "ClientD" in event:
        pid = int(event_content[0])
        print("Disconnected id: : " , pid)

        pindex = searchby_id(pid, current_players)
        if pindex == -1:
            #network.send_cmd("Client not initialized, please reconnect.")
            print("Uninitialized client disconnected ID: ", pindex)
            return False
        if current_players[pindex].in_duel:
            duel_end(pindex, current_players)
        print("Removing player..")

        for x in playerlist:
            if x.ip == current_players[pindex].ip:
                x.mmr = current_players[pindex].mmr
                current_players.pop(pindex)
                return

        playerlist.append(current_players[pindex])
        current_players.pop(pindex)
        print("REMOVING AND SAVING PLAYER...\n")

        MMR.print_player(id, current_players)
    else:
        return False
def event_userinfo(event, event_content, current_players = [Player()], player_queue = [Player()], playerlist = [Player()]): #finally initializes the client from the queue
    if "Userinfo" in event:
        print("Userinfo...")
        pid = int(event_content[0])
        pindex = searchby_id(pid, player_queue)
        for x in current_players:                       #since there is no "Changed name to" event, i'm using userinfo to manage changed names in-game
            if x.id == pid:
                x.name = event_content.split("\\",2)[1]
                print("Appending name..")
                return True
        print(pindex,"\n")
        if pindex != -1:
            print("found player in queue\n")
            #name = player_queue[pindex].name
            
            name = event_content.split("\\",2)[1]

            if name == "Server":
                network.send_cmd("kick " + name)

            try:                                        #if player is existing in playerlist, load that client into current_players
                for x in playerlist:
                   if x.ip == player_queue[pindex].ip:
                        current_players.append(Player(pid, x.ip ,x.mmr,name,"%%#",None,False,None))
                        print("loaded existing player")
                        player_queue.pop(pindex)
                        MMR.print_player(pid, current_players)
                        return
            except:
                print("Player not found in playerlist, creating new...")
            current_players.append(Player(pid,player_queue[pindex].ip,1500,name,"%%#",True,False,None))
            playerlist.append(Player(pid,player_queue[pindex].ip,1500,name,"%%#",True,False,None))
            player_queue.pop(pindex)
            print("New player created!")
            MMR.print_player(pindex, current_players)
            return True
        else:
            print("Player not found in queue: ", pid)
            return True
    else:
        return False



def event_clientconnect(event, event_content, player_queue = [Player()]): #adds players to the connection queue
    
    if "ClientConnect" in event:
        print("Client connecting")
        id = int(event_content[0])
        try:
            for x in current_players:
                if id == x.id:
                    print("Client with that ID already initialized.")
                    return False
        except:
            print("Initializing player...PID: ",id)
        ip = event_content.split("IP: ", 1)[1][:-1]
        print(ip)
        print("adding player to queue", id, ip)
        player_queue.append(Player(id,ip,None,None,"%%#",False,False,None))

    else :
        return False

def test(line):
             new_line = line
             timestamp = new_line.lstrip().split(" ",1)[0]
             event = new_line.lstrip().split(" ",2)[1]
             try:
                event_content = new_line.lstrip().split(": ",1)[1]#initialize event_content
             except:
                print("Error processing line: " + new_line)
                
                return


             if event_clientconnect(event,event_content,player_queue):
                 return
             if event_disconnect(event,event_content,current_players):
                 return
             if event_say(event,event_content,current_players):
                 return
             if event_kill(event,event_content,current_players):
                 return
             if event_userinfo(event, event_content, current_players,player_queue):
                 return

mypath1 = 'D:/Program Files (x86)/Steam/steamapps/common/Jedi Academy/GameData/MBII/'
new_line = ""
def file_read(queue):
     
        global new_line
        str1 = filewatch.get_line1()
        #new_line = line
        if new_line != str1: #if new line is actually a new line, not using timestamp because the logs don't provide units smaller than a second
             new_line = str1
             print(new_line)
             queue.append(new_line)
             return True
        else:
             return False



network.check_connection()


while True:
    if not file_read(queue):
        continue
    
    try:
        p1 = queue[0]
    except:
        
        p1 = ""
        continue
    if p1:
        t = threading.Thread(target=test, args = (p1,))
        t.start()
        t.join()
        print(p1)
        queue.pop(0)


     



     


