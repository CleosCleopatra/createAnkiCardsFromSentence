import tkinter as tk

#Create a Tkinter
root = tk()
#Create box to enter sentence
tk.Label(root, text="Enter sentence:  ").grid(row= 0, column = 0)
sentence = tk.Entry(root)
sentence.grid(row=0, column = 1)
#Create a screen
root.mainloop()
#make a popup screen
#Next button and exit buttons
#Put in a box where you can put the whole sentence
#Add a number above each word 
#Enter the number of the word you want to translate
#A box popsup with the translation, you can write in it 
#and change stuff
#Three example sentences popup, you cna press more sentences
#to get other example sentences or choose to use the 
#sentence you have already entered or choose to write 
#your own sentence (it will automatically translate it
#but you can change the translation if you want)