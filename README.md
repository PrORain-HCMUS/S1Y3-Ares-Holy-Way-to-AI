# HCMUS CS140003 Ares's Adventure
For better understanding and detailed explanations, our report is [here](doc/Report.pdf).


## Problem Introduction:
According to legend, hidden deep in a faraway kingdom is a gate that leads to mysterious treasure. It’s said that to open the gate, one must solve a maze by moving heavy stones onto secret switches. Though this may sound simple, many have tried and failed, as the maze is very tricky, and moving the large stones through tight spaces is tough. Even a small mistake could trap the challenger in the maze forever.

One day, a young adventurer named Ares decided to face this challenge. He knew that success would need careful planning, paying attention to every move, every details, and never giving up. Your task is to help Ares on his adventure. Using the search algorithms you have learned in the Introduction to Artificial Intelligence course, you must guide him through the challenging maze, finding the path and positioning the stones on the switches to unlock the treasure gate.

![Figure 1: Example of a maze modeled in the 2D world.](images/example/ares_example.png)


Do you have the skills to help Ares conquer the maze and uncover the legendary endless treasure?
Begin the journey and show your intelligence!

## About the Product Ares: Holy Way to AI
As above has been shown, this is simply a paraphrased version of the classic game Sokoban. The difference here is Ares will not only be provided with chances to conquer maps on his own, but also has the assistance of an AI system, which helps him to plan and play action sequences leading to the completion of the stages. 

## Input
### A. Basic Input: 
The first line contains a list of positive integers representing the weight of each stone, in the order they appear on the map, from left to right and top to bottom. The following lines describe the positions of objects on the map according to the following conventions:

- `#` represents a wall.
- `whitespace` represents an empty space with no objects on the map.
- `$` represents a stone.
- `@` represents the player character Ares.
- `.` represents a switch.
- `*` represents a stone that is currently on a switch.
- `+` represents Ares standing on a switch.


### B. Digitized Input

During our time developing this product, we notice that the first type above sometimes gives us a hard time creating a considerable number of inputs. That's why we also spent time consulting from seniors and finally now we can introduce you **digitized input**. This type has a structure consisting of **6 lines** as follows:

1. <code><span style="color: #e83e8c;">nRows, nCols</span></code>: Map size. For example, `10 10` means the map has dimensions of 10 x 10.

2. <code><span style="color: #e83e8c;">nWalls</span></code>: The number of wall blocks surrounding the map, followed by a list of coordinates of wall blocks. For example: `42 10 10 8 10 ...` where `42` is the number of wall blocks, and wall blocks are located at coordinates (10,10), (8,10), ...

3. <code><span style="color: #e83e8c;">nStones</span></code>: The number of stones, followed by a list of coordinates of these stones.

4. <code><span style="color: #e83e8c;">nSwitches</span></code>: The number of switches, followed by a list of coordinates of these switches.

5. <code><span style="color: #e83e8c;">pos</span></code>: The initial position of Ares, for example: `2 6`, meaning Ares is located at coordinates (2,6).

6. <code><span style="color: #e83e8c;">weights</span></code>: The weight of each stone, in the order they appear on the map, from left to right and top to bottom.

For example, this will be the digitized input for the figure above:

```bash
10 10
44 10 10 8 10 4 7 6 10 4 10 2 10 9 1 7 1 5 1 5 2 3 1 7 5 3 2 1 1 9 10 1 2 3 4 1 3 7 10 1 4 1 5 5 10 1 6 3 8 1 7 3 10 1 8 1 9 1 10 10 1 10 2 8 1 10 3 10 4 6 1 10 5 8 3 10 6 4 1 10 7 10 8 8 6 2 1 10 9 
2 3 3 8 7 
2 4 4 6 5 
4 8
12 8
