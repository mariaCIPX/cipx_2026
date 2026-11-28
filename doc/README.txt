=====================================
     TRADITIONAL MAHJONG GAME
=====================================
-------------------
1. PROJECT OVERVIEW
-------------------
This project is a two-player Mahjong-style game developed in Python.

The game supports two types of players:
-- HUMAN_player (Manual): The human player enters starting tiles and selects game actions.
-- COMPUTER_player (Automatic): The computer automatically handles tiles and makes game decisions.

The project demonstrates Python programming concepts, including:
-- Lists and data structures
-- Functions and modular programming
-- Loops and conditional statements
-- User input and output
-- Game logic and validation
-- Unit testing and debugging
-------------------
2. GAME COMPONENTS
-------------------
The game uses "Dot" tiles.

There are 36 tiles in total:
-- Tile values range from d1 to d9.
-- Each tile value has four copies.
-- Each tile is represented as a string, such as d1, d5, or d9.
-------------------
3. STARTING A GAME
-------------------
When a new game starts:
   1. Display the GAME START banner.
   2. Initialize the game and prepare the starting hands.
   3. Automatically deal the starting tiles.
   4. Display the Initial Player Status, including:
      -- Number of tiles remaining
      -- Human player's hand
      -- Computer player's hand
      -- Both players' discard lists
      -- Both players' Pung/Chow/Pair/Re-arrange/Draw tile lists
   5. Ask the player:
         Computer play first? (y/n):
   7. Begin the game with the selected starting player.
-------------------
4. GAME INSTRUCTIONS
-------------------
DRAWING TILES
-- The active player draws one tile during a turn.
-- The game displays the player's hand after drawing.

DISCARDING TILES
-- The player selects a tile to discard.
-- The discarded tile is removed from the player's hand and added to the discard list.

RE-ARRANGING TILES
-- The human player can select the Re-arrange option to organize the tiles.
-- Re-arranging must not change the number or identity of the tiles.

WINNING THE GAME
   A player wins when their five tiles form one of the following combinations:

   Option 1: Pair + Chow
   -- Pair: Two identical tiles.
   -- Chow: Three consecutive tiles.
      Example: d8, d8 + d7, d8, d9.

   Option 2: Pung + Pair
   -- Pung: Three identical tiles.
   -- Pair: Two identical tiles.
      Example: d5, d5, d5 + d8, d8.
The game automatically verifies whether the player's hand meets a valid winning combination.
----------------------------------------------
5. COMPUTER PLAYER – AUTOMATIC DECISION-MAKING
----------------------------------------------
The computer player uses an automatic decision-making algorithm to manage its tiles and play the game without human input.

The algorithm handles the following actions:
-- Automatic Drawing: Draws a tile from the remaining tiles.
-- Automatic Discarding: Evaluates its current hand and selects a tile to discard.
-- COMPUTER player is able to calculate the probability to win
-- Winning Detection: Checks whether its hand meets a valid winning combination.
-- Automatic Winning Decision: Determines when to declare a win based on the game rules.
-- Game State Management: Updates its hand, discard list, and relevant tile combinations after each action.
This allows the computer to play independently while following the same game rules as the human player.
-----------------------
6. WINNER VERIFICATION
-----------------------
When a player wins, the game displays:
-- The winning player's name.
-- The winner verification section.
-- The winner's final hand.
-- The opponent's current hand.
This information helps verify the winning condition and the final game state.
-----------------
7. MAIN GAME MENU
-----------------
After a game finishes, the main menu provides the following choices:
-- Continue Playing
-- Exit Game
-- Help

The player can select an option to continue playing, exit the game, or view the game instructions.
----------------
8. PROJECT FILES
----------------
The project consists of two Python scripts:

Main Game Script  (mini_mahjong.py)
-- Implements the Mahjong game.
-- Initializes the game and starting tiles.
-- Controls human and computer player turns.
-- Handles drawing, discarding, and re-arranging tiles.
-- Checks winning combinations.
-- Verifies winners and displays game results.

Test Script
-- Contains unit tests for the Mahjong game.
-- Tests tile combinations and winning conditions.
-- Tests important game functions and expected results.
-- Helps identify errors and verify game behavior.
-----------------------
9. HOW TO RUN THE GAME
-----------------------
Requirements:
-- Python 3 installed on your computer.

Steps:
1. Open a terminal or command prompt.
2. Navigate to the project folder.
3. Run the main game script using Python.
4. HOW TO RUN THE TEST CASES
Run the unit tests using Python's unittest framework.
-----------------------
Testing results is to verify the implementation work as expected.
-----------------------
