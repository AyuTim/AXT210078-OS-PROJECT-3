# Devlog - Project 3 OS

# 11/26/2024
 Before the Session 
 - After reading over the project, I feel like I can finish impleneting the requirenments on time. I think python would be the easiest language to use since I used it for the past few projects and its the one I have the most experience with so far. It also has built-in support for file and data management that may be helpful for this project.
 Plans for the session 
 - take notes on the project doc (I took notes on a google doc about the requirenments of this project so I can refer back to it)
 - Create the git repo and the dev log 

# 11/27/2024 (forgot to commit during this session)
Thoughts before the sesson:
- breaking the project down helped give an idea of what functions I needed first 
Plans for this session (Things I got done):
- defined the constants and blank_block function 
- created the BtreeNode class 
- created the BTreeHeader class
- wrote comments to get an idea of what each class and functions should have (TO-DO: code the things written in the commets)
Reflection 
- During this session, I was able to sucessfully implement the constants and the BtreeHeader class (still need to test)
- I also went over a general overview of how to structure my code and the genreal algo for it by adding comments. Now I just need to code the implement the logic in the comments and test the code to see if it works. 

# 12/1/2024 (forgot to commit during this sesssion)
Thoughts before the session 
- I will need to just go over my comments and code each of the functions and classes. Today I want to focuse on the Btree class. 
During the session + what I finished: 
- Create the Btree class and coded the file operations and cache managment  
Reflection on this session 
- I completed the file operations and also implemented LRU cache managment 
- I need to test to make sure the disk writes and cache updates work 
- I used OrderedFict to effciently access the node 

# 12/2/2024
Thoughts before the session 
- Coding the insert operation might be complex becasue of node splitting logic (which I was confused with doing when i was writing my comments)
- My plans for this session is to implement the core tree operations like insert (adds keys and splits nodes if needed), search (recursively finds keys and handles errors), print(displays the tree structure), extract (exports the key-value pairs to a file)
During this session 
- Coded the core tree operations like insert, search, load, etc 
Refection for after the session 
- TO-DO: clean up the code and test out some test cases/edge cases + create the read me and look over the project instructions again to make sure all the requirements are met 

# 12/3/2024
Thoughts 
- Realized that my dev log have been kind of short so I should make them more detailed from now on. 
- I need to test the code for edge cases and just test it in gerneal 
- I should change the formating of the output file so I can see the tree struture in a better way to make it easier for me to debug it 
What I did during this session 
- Did some test cases to check my program 
- fixed issues with the search and load function 
- ensured that the search and load functions handle edge cases like empty trees and duplicate keys in the input 
- added test cases for tree hight growth and multiple splits but realized that the layout of my output file makes it harder to tell how the tree looks so decided to change up the look of theoutput file 
Reflection 
- fix the output file for the bTree 
- look over the requirements one more time and make sure i have everything 
- turn the project in 

