# AXT210078-OS-PROJECT-3
AYUSHA TIMALSENA
AXT210078
OS project 3

FILES INCLUDED 
1. main.py (btree): the main program with all the code for the project. Provided the inference wher ethe user can manage and interact with the index file though commands like create, open, insert, search, load, print, extract and quit. It also handles user input errors. 
2. devlog.md: file containg my thoughts, plans, reflection, and progress 
3. input.csv: input file to test my code 

REQUIREMENTS 
- python version 3.x is used 

HOW TO 
- to run the program, open up the directory containing all the files and execute "python3 main.py"
- once the program starts, you will be presented with the menu with the commands like:"CREATE, OPEN, INSERT, SEARCH, LOAD, PRINT, EXTRACT, QUIT"
- enter the desired command (not case sensitive)
- the create command creates a new index file for the Btree
- the open command opens an existing index file anf validates the file formate before opening 
- the insert command prompts for a key-value pair to insert into the Btree and it also handles not inserting duplicate keys 
- the search command searches for the key in the Btree and displays the assoicated value if the key is found or an error if the key is not found 
- the load command reads the key-value pairs from a file (input.csv) and inserts them to the Btree
- the print command displays all the key-value pairs in the Btree
- the extract comamnd saves the btree to a specific file
- the quit command exits the program and closes any open index file 
