import tkinter as tk
from tkinter import ttk


#Creating class
class AnkiAdder: 
    def __init__(self, root):
        self.root = root
        self.root.title("Anki adder")
        self.height = 300
        self.width = 400
        self.root.geometry(f"{self.width}x{self.height}")

        #Variable
        self.sentence = ""
        self.words = []
        self.word_choosen = ""
        self.translation = ""
        self.sentence_1 = ""
        self.sentence_2 = ""
        self.sentence_3 = ""
        self.entered_sentence = ""
        self.choosen_sentence = ""

        self.next = False
        self.exit = False

        self.num_columns = 5

        #Enter sentence label
        self.sentence_label = tk.Label(
            root, text = "Enter sentence",
            font = ("Helvetica", 16, "bold"), fg = "black"
        )
        self.sentence_label.pack(padx = 15, pady= 10)

        self.sentence_var = tk.Entry(root)
        self.sentence_var.pack(padx = 10)

        self.sentence_var.bind("<Return>", self.enter_sentence)

        #Label with sentence:
        sentence_word_label = tk.Label(
            root, text = "Sentence",
            font = ("Helvetica", 16, "bold"), fg = "black"
        )
        sentence_word_label.pack(padx = 10, pady=10)

        self.frame = tk.Frame(root, bg = "lightblue", width = self.width - 20, height = 30)

    def enter_sentence(self, event):
        self.frame.destroy()
        self.frame = tk.Frame(root, bg = "lightblue", width = self.width - 20, height = 30)
        self.words = self.sentence_var.get().split(" ")

        num_words = len(self.words)
        dist_between_words = (self.width - 20) / num_words
        print(self.words)
        
        self.frame.pack(padx = 10, pady = 10)
        for i, word in enumerate(self.words):
            current_position = dist_between_words*i + 10
            print(f"Current word = {word}, current position = {current_position}")
            label = tk.Label(self.frame, text = word)
            label.grid(row = 0, column = i*2, padx = 10, pady = 10)
            num_label = tk.Label(self.frame, text = i)
            num_label.grid(row = 1, column = i*2, padx = 10)

        


root = tk.Tk()
ttk.Style().theme_use("clam")
app = AnkiAdder(root)
root.mainloop()









#Create a screen

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