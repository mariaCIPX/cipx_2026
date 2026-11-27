    MAHJONG GAME
********************
1. Project Overview
This project is a two-player Mahjong-style game developed in Python.
HUMAN_player is MANUAL: The player enters his starting tiles and choose the actions.
COMPUTER_player is AUTOMATIC: the system automatically make decisions to handle the tiles.

The project is designed to demonstrate Python programming concepts, including:
-- Lists and data structures
-- Functions and modular programming
-- (for, while) Loops and conditional statements
-- User input and output
-- Game logic and validation
-- Testing and debugging
********************
2. Game Components
The game uses Dot tiles.
There are 36 tiles in total:
- Tile values range from d1 to d9.
- Each tile value has four copies.
- Each tile is represented as a string, such as d1, d5, or d9.
********************
3. Starting a Game
When a new game starts:
1. Display the GAME START banner.
2. Automatically initialize and deal the starting tiles.
3. Display the Initial Player Status, including:
   - Number of tiles remaining
   - Human player's hand
   - Computer player's hand
   - Both players' discard lists
   - Both players' Pung/Chow/Pair/Re-arrange/Draw tile lists
4. Ask the player:
   Computer play first? (y/n):
5. The selected player begins the game.
********************
4. Game Instructions
Drawing Tiles
During a turn, the active player draws one tile.
The game displays the player's hand after the draw.

Discarding Tiles
After drawing, a player can discard a tile.
The discarded tile is removed from the player's hand and added to the discard list.

Re-arranging Tiles
The human player can select the re-arrange option to organize the tiles in their hand.
Re-arranging tiles must not change the number or identity of the tiles.

Winning the Game
A player wins when the five tiles in their hand form one of the following valid combinations:

Option 1: Pair + Chow
- One Pair: two identical tiles.
- One Chow: three consecutive tiles.
Example:
- Pair: d8, d8
- Chow: d7, d8, d9

Option 2: Pung + Pair
- One Pung: three identical tiles.
- One Pair: two identical tiles.
Example:
- Pung: d5, d5, d5
- Pair: d8, d8
The game checks whether the player's hand satisfies a valid winning combination.
********************
5. Winner Verification
When a player wins, the game displays:
- The winning player's name.
- The < Verify player block ... > section.
- The winner's final hand.
- The opponent's current hand.
This verification output helps confirm the final game state before returning to the game menu.
********************
6. Main Game Menu
After a game finishes, the menu provides the following choices:
- Continue playing game
- Exit game
- Help
The user can select an option to continue, exit, or view the game instructions.
********************
7. Project Files
The project consists of the following Python files:

play.py
- Contains the main Mahjong game.
- Initializes the game and player hands.
- Controls player turns.
- Handles drawing, discarding, and re-arranging tiles.
- Checks winning combinations.
- Displays game status and results.

testcases.py
- Contains test cases for the Mahjong game.
- Tests tile combinations and winning conditions.
- Tests important game functions and expected results.
- Helps identify errors and verify game behavior.
********************
8. How to Run the Game
Make sure Python is installed on your computer.
Place play.py and testcases.py in the same project folder.
Open a terminal or command prompt and navigate to the project folder.
Run the game:  python play.py
********************
9. How to Run the Test Cases
Run the test cases using:
      python -m unittest -v testcases.py
The test results help verify whether the implemented game functions behave as expected.
********************
10. Project Objective
The objective of this project is to develop a playable two-player Mahjong-style game using Python.
The project combines game design, logical problem-solving, data structures, and software testing to create an interactive program.
