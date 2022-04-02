from tkinter import filedialog

Filename = filedialog.askopenfilename(title="Open File (rapidSTORM Malk format)")
f = open(Filename, "r") # Open the file read only
g = open(Filename[:-4]+"_new.txt", "w") # Open a copy of the file in write mode

for line in f: # Loop through file
    if line.strip():
        g.write("\t".join(line.split()[0:4]) + "\n") # Remove appropriate lines

f.close()
g.close() # Close files

