# MergeBalls

MergeBalls is a pazzle game made with Python and Panda3D.
Rules are simple. Only need to combine balls with the same color, size and shape continually, until a smiley is finally generated to jump up. When combined, the balls burst into flames, or sparkles. 

![demo](https://github.com/taKana671/MergeBalls/assets/48859041/ec767778-a465-4699-b820-9f2bb64e8871)

# Requirements
* Panda3D 1.10.13

# Environment
* Python 3.11
* Windows11

# Usage
* Execute a command below on your command line.
```
>>>python merge_balls.py
```
* Click [PLAY]button on screen to start game.
* If starting the game, some balls will fall due to gravity. Click one of them, and the balls next to each other with the same color, size and shape will be merged into a bigger new ball.
* Pressing [Esc]key shows a pause screen. To resume the game, click [continue]button. To reboot, click [reset]button. When the game is reset, the theme color of the balls is changed.
* If some of the balls overflow the game cabinet, they blink three times, which means gameover.   
* Pressing [D]key toggles debug mode on and off. You can see collision shapes in the debug mode.
