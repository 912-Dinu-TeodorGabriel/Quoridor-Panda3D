from copy import deepcopy
from collections import deque
from repository import*
import unittest

class services():
    def __init__(self):
        self.repo = repos()

    # A handy little function for getting the proper position for a given square1
    def SquarePos(i):
        return LPoint3((i % 8) - 3.5, int(i // 8) - 3.5, 0)
    
    # Helper function for determining whether a square should be white or black
    # The modulo operations (%) generate the every-other pattern of a chess-board
    def SquareColor(i):
        #gets the color of the square by its position
        if (i + ((i // 8) % 2)) % 2:
            return 0
        else:
            return 1
        
    def swapPieces(self, fr, to):
        #swaps the pieces by their square
        if fr == self.repo.last_black_pos:
            self.repo.last_black_pos = to
        elif to == self.repo.last_black_pos:
            self.repo.last_black_pos = fr
            
        if fr == self.repo.last_white_pos:
            self.repo.last_white_pos = to
        elif to == self.repo.last_white_pos:
            self.repo.last_white_pos = fr
        
        

        temp = self.repo.pieces[fr]
        self.repo.pieces[fr] = self.repo.pieces[to]
        self.repo.pieces[to] = temp
        if self.repo.pieces[fr]:
            self.repo.pieces[fr].square = fr
            self.repo.pieces[fr].obj.setPos(LPoint3((fr % 8) - 3.5, int(fr // 8) - 3.5, 0))
        if self.repo.pieces[to]:
            self.repo.pieces[to].square = to
            self.repo.pieces[to].obj.setPos(LPoint3((to % 8) - 3.5, int(to // 8) - 3.5, 0))
            

            
    def getSquare(self, x,y):
        #gets the coordonates by the square
        return x * 8 + y
            
    def move_white(self, hiSq):
        #it put the wall in the square that was click on
        if self.repo.pieces[hiSq] == None:
            if hiSq < 10 and self.repo.last_wall_w < 10:
                self.repo.undo_history.append("wall0" + str(hiSq) + "0" + str(self.repo.last_wall_w))
            elif hiSq > 10 and self.repo.last_wall_w < 10:
                self.repo.undo_history.append("wall" + str(hiSq) + "0" + str(self.repo.last_wall_w))
            elif hiSq<10 and self.repo.last_wall_w > 10 :
                self.repo.undo_history.append("wall0" + str(hiSq) + str(self.repo.last_wall_w))
            else:
                self.repo.undo_history.append("wall" + str(hiSq) + str(self.repo.last_wall_w))
            self.repo.walls = self.repo.walls - 1
            self.repo.pieces[hiSq] = Wall(hiSq, 'WHITE_WALL')
            x,y,z = services.SquarePos(hiSq)
            self.repo.pieces[hiSq].obj.setPos(LPoint3(x+0.5,y,z))
            self.repo.mat[hiSq//8][hiSq%8] = 0
            self.repo.recoil_wall_w = 1
            self.repo.last_wall_w = hiSq
        
    def move_black(self):
        #decide by the path of the white and the path of the black if black puts a wall
        path_b = []
        path_a = []
        path_w_L = self.find_fastest_path(self.repo.mat, (self.repo.last_white_pos//8, self.repo.last_white_pos%8), (7, 0))
        path_w_R = self.find_fastest_path(self.repo.mat, (self.repo.last_white_pos//8, self.repo.last_white_pos%8), (7, 7))
        path_w_F = self.find_fastest_path(self.repo.mat, (self.repo.last_white_pos//8, self.repo.last_white_pos%8), (7, self.repo.last_white_pos%8))
        for index in range(1,7):
            local = self.find_fastest_path(self.repo.mat, (self.repo.last_white_pos//8, self.repo.last_white_pos%8), (7, index))
            if path_a == []:
                path_a = deepcopy(local)
            if local != [] and len(path_a) > len(local):
                path_a = deepcopy(local)
             
        if len(path_a) > len(path_w_L):
            path_a = path_w_L
        if len(path_a) > len(path_w_R):
            path_a = path_w_R

        sim_matrix = deepcopy(self.repo.mat)
        if self.repo.recoil_wall_w and self.repo.walls:
            if self.repo.walls and self.repo.last_wall_w % 8 == 1:
                sim_matrix[(self.repo.last_wall_w - 1)// 8][0] = 0
            if self.repo.walls and self.repo.last_wall_w % 8 == 6:
                sim_matrix[(self.repo.last_wall_w - 1)// 8][7] = 0  
            if self.repo.last_wall_b % 8 == 1:
                sim_matrix[(self.repo.last_wall_b - 1)// 8][0] = 0
            if self.repo.last_wall_b % 8 == 6:
                sim_matrix[(self.repo.last_wall_b - 1)// 8][7] = 0

        for index in range(8):
            pathlocal_b = self.find_fastest_path(sim_matrix, (self.repo.last_black_pos//8, self.repo.last_black_pos%8), (0, index))
            if path_b == [] and pathlocal_b != []:
                path_b = deepcopy(pathlocal_b)         
            elif len(pathlocal_b) < len(path_b) and pathlocal_b !=[]:
                path_b = deepcopy(pathlocal_b)
                
        if path_b == []:
            for index in range(8):
                pathlocal_b = self.find_fastest_path(self.repo.mat, (self.repo.last_black_pos//8, self.repo.last_black_pos%8), (0, index))
                if path_b == [] and pathlocal_b != []:
                    path_b = deepcopy(pathlocal_b)         
                elif len(pathlocal_b) < len(path_b) and pathlocal_b !=[]:
                    path_b = deepcopy(pathlocal_b)
                 
        if len(path_b) > len(path_a) and self.repo.b_walls and self.repo.recoil_wall_b < 1:#decides if it puts wall or just continue the path       
            if (self.repo.last_white_pos - 1) // 8 == self.repo.last_white_pos // 8 and self.repo.pieces[self.repo.last_white_pos - 1] == None and (self.repo.pieces[self.repo.last_white_pos - 2] == None or self.repo.last_white_pos == 1) and self.repo.last_white_pos + 8 and len(path_w_L) < len(path_w_R) and len(path_w_F) > len(path_w_L) and self.repo.prev_white_pos -1 == self.repo.last_white_pos and self.check_position(self.repo.last_white_pos-1) == 0:
                if self.repo.last_white_pos-1 < 10 and self.repo.last_wall_b < 10:
                    self.repo.undo_history.append("wall0" + str(self.repo.last_white_pos-1) + "0" + str(self.repo.last_wall_b))
                elif self.repo.last_white_pos-1 < 10 and self.repo.last_wall_b >= 10:     
                    self.repo.undo_history.append("wall0" + str(self.repo.last_white_pos-1) + str(self.repo.last_wall_b))
                elif self.repo.last_white_pos-1 >= 10 and self.repo.last_wall_b < 10:
                    self.repo.undo_history.append("wall" + str(self.repo.last_white_pos-1) + "0" + str(self.repo.last_wall_b))
                else:
                    self.repo.undo_history.append("wall" + str(self.repo.last_white_pos-1) + str(self.repo.last_wall_b))
                
                self.repo.pieces[self.repo.last_white_pos-1] = Wall(self.repo.last_white_pos - 1, 'BLACK_WALL')
                self.repo.pieces[self.repo.last_white_pos-1].obj.setPos(LPoint3(((self.repo.last_white_pos-1) % 8) - 3, (self.repo.last_white_pos-1) //8 -3.5 ,0))
                self.repo.mat[(self.repo.last_white_pos-1) // 8][(self.repo.last_white_pos-1) % 8] = 0
                self.repo.b_walls -=1
                self.repo.recoil_wall_b = 1
                self.repo.last_wall_b = self.repo.last_white_pos-1

            elif (self.repo.last_white_pos + 1) // 8 == self.repo.last_white_pos // 8 and self.repo.pieces[self.repo.last_white_pos + 1] == None and (self.repo.pieces[self.repo.last_white_pos + 2] == None or self.repo.last_white_pos == 6) and self.repo.last_white_pos + 8 and len(path_w_L) > len(path_w_R) and len(path_w_F) > len(path_w_R) and self.repo.prev_white_pos + 1 == self.repo.last_white_pos and self.check_position(self.repo.last_white_pos+1) == 0:
                if self.repo.last_white_pos+1 < 10 and self.repo.last_wall_b < 10:
                    self.repo.undo_history.append("wall0" + str(self.repo.last_white_pos+1) + "0" + str(self.repo.last_wall_b))
                elif self.repo.last_white_pos+1 < 10 and self.repo.last_wall_b >= 10:     
                    self.repo.undo_history.append("wall0" + str(self.repo.last_white_pos+1) + str(self.repo.last_wall_b))
                elif self.repo.last_white_pos+1 >= 10 and self.repo.last_wall_b < 10:
                    self.repo.undo_history.append("wall" + str(self.repo.last_white_pos+1) + "0" + str(self.repo.last_wall_b))
                else:
                    self.repo.undo_history.append("wall" + str(self.repo.last_white_pos+1) + str(self.repo.last_wall_b))
                               
                self.repo.pieces[self.repo.last_white_pos+1] = Wall(self.repo.last_white_pos + 1, 'BLACK_WALL')
                self.repo.pieces[self.repo.last_white_pos+1].obj.setPos(LPoint3(((self.repo.last_white_pos+1) % 8) - 3, (self.repo.last_white_pos+1) //8 -3.5 ,0))
                self.repo.mat[(self.repo.last_white_pos+1) // 8][(self.repo.last_white_pos+1) % 8] = 0
                self.repo.b_walls -=1
                self.repo.recoil_wall_b = 1
                self.repo.last_wall_b = self.repo.last_white_pos+1

            elif self.repo.pieces[self.repo.last_white_pos+8] == None and (self.repo.last_white_pos + 8 > 55 or self.repo.pieces[self.repo.last_white_pos + 16]) == None and self.check_position(self.repo.last_white_pos+8) == 0:
                if self.repo.last_black_pos+8 < 10 and self.repo.last_wall_b < 10:
                    self.repo.undo_history.append("wall0" + str(self.repo.last_white_pos+8) + "0" + str(self.repo.last_wall_b))
                elif self.repo.last_white_pos+8 < 10 and self.repo.last_wall_b >= 10:     
                    self.repo.undo_history.append("wall0" + str(self.repo.last_white_pos+8))
                elif self.repo.last_white_pos+8 >= 10 and self.repo.last_wall_b < 10:
                    self.repo.undo_history.append("wall" + str(self.repo.last_white_pos+8) + "0" + str(self.repo.last_wall_b))
                else:
                    self.repo.undo_history.append("wall" + str(self.repo.last_white_pos+8) + str(self.repo.last_wall_b))
                            
                self.repo.pieces[self.repo.last_white_pos+8] = Wall(self.repo.last_white_pos + 8, 'BLACK_WALL')
                self.repo.pieces[self.repo.last_white_pos+8].obj.setPos(LPoint3((self.repo.last_white_pos % 8) - 3, self.repo.last_white_pos //8 -2.5 ,0))
                self.repo.mat[self.repo.last_white_pos // 8 + 1][self.repo.last_white_pos % 8] = 0
                self.repo.b_walls -=1
                self.repo.recoil_wall_b = 1
                self.repo.last_wall_b = self.repo.last_white_pos+8

            else:
                if self.repo.pieces[self.getSquare(path_b[0][0], path_b[0][1])] == None or self.repo.pieces[self.getSquare(path_b[0][0], path_b[0][1])].is_wall == 0:
                    if self.repo.last_black_pos < 10 and self.repo.prev_black_pos < 10:
                        self.repo.undo_history.append("move0" + str(self.repo.last_black_pos)+ "0" + str(self.repo.prev_black_pos))
                    elif self.repo.last_black_pos >= 10 and self.repo.prev_black_pos < 10:
                        self.repo.undo_history.append("move" + str(self.repo.last_black_pos) + "0" + str(self.repo.prev_black_pos))
                    elif self.repo.last_black_pos < 10 and self.repo.prev_black_pos >= 10:
                        self.repo.undo_history.append("move0" + str(self.repo.last_black_pos) + str(self.repo.prev_black_pos))
                    else:
                        self.repo.undo_history.append("move" + str(self.repo.last_black_pos) + str(self.repo.prev_black_pos))
                    self.repo.prev_black_pos = self.repo.last_black_pos
                fr = self.getSquare(path_b[0][0], path_b[0][1])
                if self.repo.pieces[fr]:
                    if fr < 10 and self.repo.prev_white_pos < 10:
                        self.repo.undo_history.append("move0" + str(fr) + "0" + str(self.repo.prev_white_pos))
                    elif fr >= 10 and self.repo.prev_white_pos >= 10:
                        self.repo.undo_history.append("move" + str(fr) + str(self.repo.prev_white_pos))
                    elif fr >= 10 and self.repo.prev_white_pos < 10:
                        self.repo.undo_history.append("move" + str(fr) + "0" + str(self.repo.prev_white_pos))
                    else:
                        self.repo.undo_history.append("move0" + str(fr) + str(self.repo.prev_white_pos))
                    self.swapPieces(self.repo.last_black_pos, fr)          
                if self.repo.last_black_pos < 8:
                    self.repo.winner = 'black'
                    if self.repo.last_white_pos < 10 and self.repo.prev_white_pos < 10:
                        self.repo.undo_history.append("move0" + str(self.repo.last_white_pos) + "0" + str(self.repo.prev_white_pos))
                    elif self.repo.last_white_pos >= 10 and self.repo.prev_white_pos >= 10:
                        self.repo.undo_history.append("move" + str(self.repo.last_white_pos) + str(self.repo.prev_white_pos))
                    elif self.repo.last_white_pos >= 10 and self.repo.prev_white_pos < 10:
                        self.repo.undo_history.append("move" + str(self.repo.last_white_pos) + "0" + str(self.repo.prev_white_pos))
                    else:
                        self.repo.undo_history.append("move0" + str(self.repo.last_white_pos) + str(self.repo.prev_white_pos))
                self.repo.recoil_wall_b = 0
                
                      
        else:
            if self.repo.pieces[self.getSquare(path_b[0][0], path_b[0][1])] == None or self.repo.pieces[self.getSquare(path_b[0][0], path_b[0][1])].is_wall == 0:
                if self.repo.last_black_pos < 10 and self.repo.prev_black_pos < 10:
                    self.repo.undo_history.append("move0" + str(self.repo.last_black_pos)+ "0" + str(self.repo.prev_black_pos))
                elif self.repo.last_black_pos >= 10 and self.repo.prev_black_pos < 10:
                    self.repo.undo_history.append("move" + str(self.repo.last_black_pos) + "0" + str(self.repo.prev_black_pos))
                elif self.repo.last_black_pos < 10 and self.repo.prev_black_pos >= 10:
                    self.repo.undo_history.append("move0" + str(self.repo.last_black_pos) + str(self.repo.prev_black_pos))
                else:
                    self.repo.undo_history.append("move" + str(self.repo.last_black_pos) + str(self.repo.prev_black_pos))  
                self.repo.prev_black_pos = self.repo.last_black_pos
                fr = self.getSquare(path_b[0][0], path_b[0][1])
                if self.repo.pieces[fr]:
                    if fr < 10 and self.repo.prev_white_pos < 10:
                        self.repo.undo_history.append("move0" + str(fr) + "0" + str(self.repo.prev_white_pos))
                    elif fr >= 10 and self.repo.prev_white_pos >= 10:
                        self.repo.undo_history.append("move" + str(fr) + str(self.repo.prev_white_pos))
                    elif fr >= 10 and self.repo.prev_white_pos < 10:
                        self.repo.undo_history.append("move" + str(fr) + "0" + str(self.repo.prev_white_pos))
                    else:
                        self.repo.undo_history.append("move0" + str(fr) + str(self.repo.prev_white_pos))
                self.swapPieces(self.repo.last_black_pos, fr)         
            if self.repo.last_black_pos < 8:
                self.repo.winner = 'black'
                if self.repo.last_white_pos < 10 and self.repo.prev_white_pos < 10:
                    self.repo.undo_history.append("move0" + str(self.repo.last_white_pos) + "0" + str(self.repo.prev_white_pos))
                elif self.repo.last_white_pos >= 10 and self.repo.prev_white_pos >= 10:
                    self.repo.undo_history.append("move" + str(self.repo.last_white_pos) + str(self.repo.prev_white_pos))
                elif self.repo.last_white_pos >= 10 and self.repo.prev_white_pos < 10:
                    self.repo.undo_history.append("move" + str(self.repo.last_white_pos) + "0" + str(self.repo.prev_white_pos))
                else:
                    self.repo.undo_history.append("move0" + str(self.repo.last_white_pos) + str(self.repo.prev_white_pos))
            self.repo.recoil_wall_b = 0
                
    def check_position(self, move):
        #checks if there is a move avaliable if you put a wall there
        self.repo.mat[move//8][move%8] = 0
        ok_w = 0
        ok_b = 0
        for index in range(8):
            path = self.find_fastest_path(self.repo.mat, (self.repo.last_white_pos//8, self.repo.last_white_pos%8), (7, index))
            if path != []:
                ok_w = 1
                break
                   
        for index in range(8):
            path = self.find_fastest_path(self.repo.mat, (self.repo.last_black_pos//8, self.repo.last_black_pos%8), (0, index))
            if path != []:
                ok_b = 1
                break
           
        self.repo.mat[move//8][move%8] = 1
        return ok_w * ok_b == 0

    def find_fastest_path(self, matrix, start, end):
      # Set up a queue to store the next positions to explore
      queue = deque([(start, [])])
      # Keep track of the positions we have already visited
      visited = set()

      while queue:
        # Get the next position to explore and the path taken to get there
        pos, path = queue.popleft()
        # Add the current position to the visited set
        visited.add(pos)

        # Check if we have reached the end
        if pos == end:
          return path

        # Explore the neighbors of this position
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
          # Calculate the position of the neighbor
          x, y = pos[0] + dx, pos[1] + dy
          # Check if the neighbor is within the bounds of the matrix
          # and not an obstacle (0 in this case)
          if 0 <= x < len(matrix) and 0 <= y < len(matrix[0]) and matrix[x][y] != 0:
            # Add the neighbor to the queue and update the path taken
            neighbor = (x, y)
            if neighbor not in visited:
              queue.append((neighbor, path + [neighbor]))
        
      # If we get here, it means that we have not found a path to the end
      return []
  
    def move_on_board(self, fr,to):
        #moves on board the white piece
        if fr < 10 and self.repo.prev_white_pos < 10:
            self.repo.undo_history.append("move0" + str(fr) + "0" + str(self.repo.prev_white_pos))
        elif fr >= 10 and self.repo.prev_white_pos >= 10:
            self.repo.undo_history.append("move" + str(fr) + str(self.repo.prev_white_pos))
        elif fr >= 10 and self.repo.prev_white_pos < 10:
            self.repo.undo_history.append("move" + str(fr) + "0" + str(self.repo.prev_white_pos))
        else:
            self.repo.undo_history.append("move0" + str(fr) + str(self.repo.prev_white_pos))
        if self.repo.pieces[to]:
            if to < 10 and self.repo.prev_black_pos < 10:
                self.repo.undo_history.append("move0" + str(to) + "0" + str(self.repo.prev_black_pos))
            elif to >= 10 and self.repo.prev_black_pos >= 10:
                self.repo.undo_history.append("move" + str(to) + str(self.repo.prev_black_pos))
            elif to >= 10 and self.repo.prev_black_pos < 10:
                self.repo.undo_history.append("move" + str(to) + "0" + str(self.repo.prev_black_pos))
            else:
                self.repo.undo_history.append("move0" + str(to) + str(self.repo.prev_black_pos))
        self.swapPieces(fr,to)
        self.repo.prev_white_pos = fr
        if(to >=56):
            self.repo.winner = "white"
            if self.repo.last_black_pos < 10 and self.repo.prev_black_pos < 10:
                self.repo.undo_history.append("move0" + str(self.repo.last_black_pos)+ "0" + str(self.repo.prev_black_pos))
            elif self.repo.last_black_pos >= 10 and self.repo.prev_black_pos < 10:
                self.repo.undo_history.append("move" + str(self.repo.last_black_pos) + "0" + str(self.repo.prev_black_pos))
            elif self.repo.last_black_pos < 10 and self.repo.prev_black_pos >= 10:
                self.repo.undo_history.append("move0" + str(self.repo.last_black_pos) + str(self.repo.prev_black_pos))
            else:
                self.repo.undo_history.append("move" + str(self.repo.last_black_pos) + str(self.repo.prev_black_pos))  
        else:
            self.move_black()
        
