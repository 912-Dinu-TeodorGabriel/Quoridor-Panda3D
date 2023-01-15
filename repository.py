from domain import *
import sys
#make me a class repository for the app from services
class repos:
    def __init__(self):
        self.walls = 6
        self.winner = False
        self.squares = [None for i in range(64)]
        self.pieces = [None for i in range(64)]
        self.pieces[3] = Pawn(3, 'WHITE')
        self.pieces[3].obj.setPos(LPoint3((3 % 8) - 3.5, int(3 // 8) - 3.5, 0))
        self.pieces[60] = Pawn(60, 'PIECEBLACK')
        self.pieces[60].obj.setPos(LPoint3((60 % 8) - 3.5, int(60 // 8) - 3.5, 0))
        self.last_black_pos = 60
        self.last_white_pos = 3
        self.prev_black_pos = 60
        self.prev_white_pos = 3
        self.mat = [[1 for i in range(8)] for j in range(8)]
        self.b_walls = 6
        self.recoil_wall_b = 0
        self.recoil_wall_w = 0
        self.last_wall_w = 0
        self.last_wall_b = 0
        self.undo_history = []

    def _read(self):
        #reads a text file
        try:
            f = open("save.txt", "r")
            for i in range(8):
                line = f.readline()
                line = line.split()
                for j in range(8):
                    self.mat[i][j] = int(line[j])
            self.b_walls = int(f.readline())
            self.walls = int(f.readline())
            self.last_black_pos = int(f.readline())
            self.last_white_pos = int(f.readline())
            self.recoil_wall_b = int(f.readline())
            self.recoil_wall_w = int(f.readline())
            self.last_wall_w = int(f.readline())
            self.last_wall_b = int(f.readline())
            self.prev_black_pos = int(f.readline())
            self.prev_white_pos = int(f.readline())
            self.winner = f.readline()
            if self.winner == 'True':
                self.winner = True
            else:
                self.winner = False
            aux_w = self.pieces[3]
            aux_b = self.pieces[60]
            for i in range(64):
                local = f.readline()
                if 'Pawn' in local:
                    local = local[4:]
                    if 'WHITE' in local:    
                        self.pieces[i] = aux_w
                        self.pieces[3] = self.pieces[i]
                        self.pieces[i].obj.setPos(LPoint3((i % 8) - 3.5, int(i // 8) - 3.5, 0))
                    else:
                        self.pieces[i] = aux_b
                        self.pieces[60] = self.pieces[i]
                        self.pieces[i].obj.setPos(LPoint3((i % 8) - 3.5, int(i // 8) - 3.5, 0))
                elif 'Wall' in local:
                    local = local[4:]
                    self.pieces[i] = Wall(i,local)
                    self.pieces[i].obj.setPos(LPoint3((i % 8) - 3, int(i // 8) - 3.5, 0))
            #for undo history
            while line:
                line = f.readline()
                if line:
                    self.undo_history.append(int(line))
                
        except:
            print("New game.Error file not found.")
        else:
            print("Game loaded.")

    def _write(self):
        #writes a text file
        with(open("save.txt", "w")) as f:
            for i in range(8):
                for j in range(8):
                    f.write(str(self.mat[i][j]) + " ")
                f.write("\n")
            f.write(str(self.b_walls) + "\n")
            f.write(str(self.walls) + "\n")
            f.write(str(self.last_black_pos) + "\n")
            f.write(str(self.last_white_pos) + "\n")
            f.write(str(self.recoil_wall_b) + "\n")
            f.write(str(self.recoil_wall_w) + "\n")
            f.write(str(self.last_wall_w) + "\n")
            f.write(str(self.last_wall_b) + "\n")
            f.write(str(self.prev_black_pos) + "\n")
            f.write(str(self.prev_white_pos) + "\n")
            f.write(str(self.winner) + "\n")
            for i in range(64):
                if self.pieces[i]:
                    if self.pieces[i].is_wall == 1:
                        f.write('Wall' + "\n")
                    elif self.pieces[i].is_pawn == 1:
                        if self.last_black_pos == i:
                            f.write('Pawn' + "PIECEBLACK" + "\n")
                        elif self.last_white_pos == i:
                            f.write('Pawn' + "WHITE" + "\n")
                else:
                    f.write('None' + '\n')
            #for undo history
            for i in range(len(self.undo_history)):
                f.write(str(self.undo_history[i]) + "\n")
                

    def add_pawn(self, square, color):
        if self.pieces[square] == None:
            self.pieces[square] = Pawn(square, color)
    def add_wall(self, square, color):
        if self.pieces[square] == None:
            self.pieces[square] = Wall(square, color)
    def remove_object(self, square):
        self.pieces[square].obj.removeNode()
        self.pieces[square] = None
        
    def restart(self):
        self.walls = 6
        self.winner = False

        aux1 = self.pieces[self.last_white_pos]
        self.pieces[self.last_white_pos] = self.pieces[3]
        self.pieces[3] = aux1
        self.pieces[3].obj.setPos(LPoint3((3 % 8) - 3.5, int(3 // 8) - 3.5, 0))

        aux2 = self.pieces[self.last_black_pos]
        self.pieces[self.last_black_pos] = self.pieces[60]
        self.pieces[60] = aux2
        self.pieces[60].obj.setPos(LPoint3((60 % 8) - 3.5, int(60 // 8) - 3.5, 0))
        for index in range (len(self.pieces)):
            if self.pieces[index] != None and self.pieces[index].is_wall:
                self.pieces[index].obj.removeNode()
                self.pieces[index] = None
                

        self.last_black_pos = 60
        self.prev_black_pos = 60
        self.last_white_pos = 3
        self.prev_white_pos = 3
        self.mat = [[1 for i in range(8)] for j in range(8)]
        self.b_walls = 6
        self.recoil_wall_b = 0
        self.recoil_wall_w = 0
        self.last_wall_w = 0
        self.last_wall_b = 0
        self.undo_history = []

    def undo(self):
        if self.winner == 'black':
            self.pieces[self.last_black_pos].obj.removeNode()
            self.pieces[self.last_black_pos] = None
        if len(self.undo_history): 
            for i in range (len(self.undo_history)):
                if i%2 :
                    print(i,"black", self.undo_history[i])
                else:
                    print(i,"white", self.undo_history[i])
            print("\n")
            change = 0
            print(self.undo_history[-1][4:6], self.undo_history[-1][6:])
            if len(self.undo_history)>=3 and self.undo_history[-1][:4] == self.undo_history[-2][:4] and self.undo_history[-1][4:6] == self.undo_history[-3][4:6] and self.undo_history[-1][6:8] == self.undo_history[-2][6:8]:
                self.undo_history.pop()
            elif len(self.undo_history)%2:
                change = 1
                _last = self.undo_history[-1]
                pos = (int(_last[4]) - int('0'))* 10 + int(_last[5]) - int('0')
                if self.pieces[pos]:
                    self.pieces[pos].obj.removeNode()
                if self.pieces[self.last_white_pos]:
                    self.pieces[self.last_white_pos].obj.removeNode()
                    self.pieces[self.last_white_pos] = None
                self.pieces[pos] = Pawn(pos, "WHITE")
                self.pieces[pos].obj.setPos(LPoint3((pos % 8) - 3.5, int(pos // 8) - 3.5, 0))
                self.prev_white_pos = (int(_last[6]) - int('0'))*10 + int(_last[7]) - int('0')
                self.last_white_pos = pos
                self.winner = False
                self.undo_history.pop()
                
            _last = self.undo_history[-2]
            if _last[:4] == 'wall':
                self.last_wall_b = (int(_last[5]) - int('0')) * 10 + int(_last[6]) - int('0')
                _last = (int(_last[4]) - int('0'))* 10 + int(_last[5]) - int('0')
                if self.pieces[_last]:
                    self.pieces[_last].obj.removeNode()
                    self.pieces[_last] = None
                self.walls += 1
                self.mat[_last//8][_last%8] = 1
                self.recoil_wall_w = 0 
                
            elif _last[:4] == "move":
                pos = (int(_last[4]) - int('0'))* 10 + int(_last[5]) - int('0')
                if self.pieces[pos]:
                    self.pieces[pos].obj.removeNode()
                if self.pieces[self.last_white_pos]:
                    self.pieces[self.last_white_pos].obj.removeNode()
                    self.pieces[self.last_white_pos] = None
                self.pieces[pos] = Pawn(pos, "WHITE")
                self.pieces[pos].obj.setPos(LPoint3((pos % 8) - 3.5, int(pos // 8) - 3.5, 0))
                self.prev_white_pos = (int(_last[6]) - int('0'))*10 + int(_last[7]) - int('0')
                self.last_white_pos = pos
                self.winner = False
                
            _last = self.undo_history[-1]
            if _last[:4] == 'wall':
                self.last_wall_b = (int(_last[5]) - int('0')) * 10 + int(_last[6]) - int('0')
                _last = (int(_last[4]) - int('0'))* 10 + int(_last[5]) - int('0')
                if self.pieces[_last]:
                    self.pieces[_last].obj.removeNode()
                    self.pieces[_last] = None
                self.b_walls += 1
                self.mat[_last//8][_last%8] = 1
                self.recoil_wall_b = 0
                
                
            elif _last[:4] == "move":
                pos = (int(_last[4]) - int('0'))* 10 + int(_last[5]) - int('0')
                if self.pieces[pos]:
                    self.pieces[pos].obj.removeNode()
                if self.pieces[self.last_black_pos] and change == 0:
                    self.pieces[self.last_black_pos].obj.removeNode()
                    self.pieces[self.last_black_pos] = None
                self.pieces[pos] = Pawn(pos, "BLACK")
                self.pieces[pos].obj.setPos(LPoint3((pos % 8) - 3.5, int(pos // 8) - 3.5, 0))
                self.prev_white_pos = (int(_last[6]) - int('0'))*10 + int(_last[7]) - int('0')
                self.last_black_pos = pos
                self.winner = False
            
            self.undo_history.pop()
            self.undo_history.pop()
        else:
            print("No undo moves avaliable")