# Quoridor-Panda3D
<h3>Before compile</h3>
You must have Panda3D installed ( pip install Panda3D ), for more informations about the framework on https://www.panda3d.org/
<h3>Game Rules</h3>

Each player in turn, chooses to move his pawn or to put up one of his fences. When he has run out of fences, the player must move his pawn.
At the beginning the board is empty. Choose and place your pawn in the center of the first line of your side of the board, your opponent takes another pawn and places it in the center of the first line of his side of the board (the one facing yours). Then take 6 fences each.
The white moves first.

The pawns are moved one square at a time, horizontally or vertically, forwards or backwards, never diagonally (fig.2).

![game2](https://user-images.githubusercontent.com/115081686/212549703-31d09830-2a14-4fd2-85eb-94b3e3bff45c.jpg)

The pawns must bypass the fences (fig.3). If, while you move, you face your opponent's pawn you can jump over.

![game3](https://user-images.githubusercontent.com/115081686/212549747-ff4a6ff3-1b22-4318-8bdd-272a6ff50374.jpg)

The original game was made to put 2 square fance(fig.4), this particular one is a 8x8 table with 1 square fance.

By placing fences, you force your opponent to move around it and increase the number of moves they need to make. But be careful, you are not allowed to lock up to lock up your opponents pawn, it must always be able to reach it's goal by at least one square (fig.5).

![game5](https://user-images.githubusercontent.com/115081686/212549777-8de8ae07-5ad5-48f9-8376-fb19b229a9c1.jpg)

<h3>Face To Face</h3>

When two pawns face each other on neighboring squares which are not separated by a fence, the player whose turn it is can swap the opponent's pawn with his own(fig.6).

![game6](https://user-images.githubusercontent.com/115081686/212549996-f79ff537-0b23-4883-ad4d-570fbc0099e8.jpg)


<h3>End of the Game</h3>

The first player who reaches one of the 8 squares opposite his base line is the winner (fig. 7).

![game7](https://user-images.githubusercontent.com/115081686/212550026-e11bb4b8-f93d-48f8-9b61-652d4cce9ddb.jpg)
  
<h3>General info about game</h3>
  
![img1](https://user-images.githubusercontent.com/115081686/212552057-eb8f3654-d48a-4313-88b3-fc4a512d0891.jpg)

<h3>Updates</h3>

<h1>Version 1.1</h1>
~bug fix : when the black wins the undo didn't work properly

~new : you can visualize the wall block until you place it
<h1>Version 1.0</h1>
~RELEASE~
