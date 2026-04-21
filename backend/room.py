import random
from enum import Enum
from Core.board import Board
from Core.engine import Engine


class RoomState(Enum):
    WAITING = "waiting"
    ONGOING = "ongoing"
    FINISHED = "finished"

class Room:
    def __init__(self,roomId = None):
        self.roomId = roomId
        self.participants = {} #{white : websocket1, black : websocket2}
        self.engine = None
        self.state = RoomState.WAITING
        self.temp = []

    def random_assign_colors(self,players):
        self.participants["white"] = random.choice(players)
        players.remove(self.participants["white"])
        self.participants["black"] = players[0]
    
        
    def initiate_game(self):
        board = Board()
        self.engine = Engine(board)


    def add_participants(self, player):
        self.temp.append(player)
        if len(self.temp) == 2:
            self.random_assign_colors(self.temp)
            self.state = RoomState.ONGOING
            self.initiate_game()
            self.temp = []
            return True
        else:
            return False