import string

class Player(object):
    """__init__() functions as the class constructor"""
    def __init__(self, id = None, ip= None,mmr = None, name= None, opponent = None, initialized = None, in_duel = None, aliases = None):
        self.id = id
        self.ip = ip
        self.name = name
        self.initialized = initialized
        self.in_duel = in_duel
        self.aliases = aliases
        self.mmr = mmr
        self.opponent = opponent
     


