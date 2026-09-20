import tkinter as tk
from tkinter import ttk
from google.cloud import translate_v3
from google.api_core.client_options import ClientOptions
import google.auth
import pandas as pd
import config

df = pd.read_csv(config.csv_file, sep="\t", names = ["Serbian_id", "Serbian", "English_id", "English"])

source_lang = 'sr'
target_lang = 'en'

letter_dict = {1: "č", 2: "ć", 3: "đ", 4: "š", 5: "ž"}

PROJECT_ID = config.project_id

credentials, credientials_project = google.auth.default()

client = translate_v3.TranslationServiceClient(
    credentials = credentials,
    client_options=ClientOptions(
        quota_project_id=PROJECT_ID
    )
)
parent = f"projects/{PROJECT_ID}/locations/global"

from google.cloud import texttospeech

client_speech = texttospeech.TextToSpeechClient()

class ankiWord:
    def __init__(self, word, width, height, input_sentence, root):
        self.word = word
        self.width = width
        self.height = height
        self.clicked = False
        self.widget = tk.Frame(root, bg = "lightblue", width = self.width - 20, height = 30)
        self.screen_generated = False

        self.translation = self.translate(word)
        self.sentences = self.find_all_examples(word)
        self.sentences_english = []
        if self.sentences is not None:
            for sentence in self.sentences:
                self.sentences_english.append(self.translate(sentence))

        self.input_sentence = input_sentence

        self.translated_input_sentence = self.translate(input_sentence)

        self.word_index_to_show = 0
        self.chosen_sentence = None
        self.chosen_sentence_english = None

    def more_sentences(self):
        self.word_index_to_show = (self.word_index_to_show + 3) % len(self.sentences)

    def choose_sentence(self, sentence):
        print("here")
        #Changes chosen sentence to whatever we have pressed
        #Saves its pronuncation

    
    def add_word(self):
        if self.chosen_sentence:
            #saves audio files 
            self.speak_text(self.word)
            self.speak_text(self.chosen_sentence)
            #Create audio paths
            audio_path = config.first_part + self.word + '.mp3'
            audio_path_sentence = config.first_part + self.chosen_sentence + '.mp3'
            #add them in anki
            response = requests.post(
                config.anki_code,
                json = {
                    "action": "addNote",
                    "version" : 6,
                    "params":{
                        "note": {
                            "deckName": "Serbian course::Serbiska",
                            "modelName": "With Sentences",
                            "fields": {
                                "Front": self.word,
                                "Back": self.translation,
                                "Sentence Serbian": self.chosen_sentence,
                                "Sentence English": self.translated_input_sentence,
                                "Past tense": "",
                                "Future tense": "",
                                "Conjugate": "",
                                "P/I": "",
                                "present": "",
                                "Pronuncation": "",
                                "Sentence pronuncation": ""
                            },
                            "audio": [{
                                "path": audio_path,
                                "filename": f"{self.word}.mp3",
                                "fields": ["Pronuncation"]
                            },
                            {
                                "path": audio_path_sentence,
                                "filename": f"{self.chosen_sentence}.mp3",
                                "fields": ["Sentence pronuncation"]
                            }]
                        }
                    }
                }
            )


    def remove_screen_for_ind_word(self):
        self.widget.pack_forget()

    def sentences_list(self):
        if len(self.sentences_english) > 0:
            indexes = [self.word_index_to_show, (self.word_index_to_show + 1) % len(self.sentences_english), 
                   (self.word_index_to_show + 2) %len(self.sentences_english)]
            return indexes
        return []

    def select_sentence(self, index):
        print("we got here")
        if index <= 2:
            print(f"self sentences {self.word_index_to_show}")
            self.chosen_sentence = self.sentences.iloc[(self.word_index_to_show + index) % len(self.sentences_english)]["Serbian"]
            self.chosen_sentence_english = self.sentences.iloc[(self.word_index_to_show + index) % len(self.sentences_english)]["English"]
        elif index == 3:
            self.chosen_sentence = self.input_sentence
            self.chosen_sentence_english = self.translate(self.input_sentence)
        else: 
            self.chosen_sentences = self.own_example_sentence.get()
            self.chosen_sentence_english = self.translate(self.chosen_sentence)
            

    def adding_translation_to_written_sentence(self, event, frame):
        translated = self.translate(self.own_example_sentence.get())
        sentence_translated = tk.Label(frame, text = translated,
                                                font = ("Helvetica", 12), fg = "black")
        sentence_translated.grid(row = 4 * 2 + 1, column = 2)




    def creates_screen_for_ind_word(self):
        if not self.screen_generated:
            #Shows the words translation
            word_translation = tk.Label(
                self.widget, text = self.translate(self.word),
                font = ("Helvetica", 16, "bold"), fg = "black"
            )
            word_translation.pack(padx = 15, pady= 10)
            self.screen_generated = True

            #Shows three sentences and their translation with a button next to each
            indexes_to_show = self.sentences_list()

            frame2 = tk.Frame(self.widget, bg = "lightblue", width = self.width - 20, height = 30)
            frame2.pack()
            if len(indexes_to_show) > 0:
                for index in indexes_to_show:
                    button = tk.Button(frame2, text = index, 
                                   command = lambda val = index: self.select_sentence(val))
                    button.grid(row = int(index)*2, column = 0, rowspan = 2, pady = (20,0))

                    sentence = tk.Label(frame2, text = self.sentences.iloc[int(index)]["Serbian"],
                                        font = ("Helvetica", 12), fg = "black")
                    sentence_english = tk.Label(frame2, text = self.sentences.iloc[int(index)]["English"],
                                                font = ("Helvetica", 12), fg = "black")
                    sentence.grid(row = int(index)*2, column = 2, pady = (20,0))
                    sentence_english.grid(row = int(index)*2 + 1, column = 2)
            #add the input question
            button = tk.Button(frame2, text = 4, 
                               command = lambda val = 3: self.select_sentence(val))
            button.grid(row = 3 * 2, column = 0, rowspan= 2, pady = (20, 0))

            sentence = tk.Label(frame2, text = self.input_sentence, font = ("Helvetica", 12), fg = "black")
            sentence_english = tk.Label(frame2, text = self.translate(self.input_sentence), 
                                        font = ("Helvetica", 12), fg= "black")
            sentence.grid(row = 3 * 2, column = 2, pady = (20,0))
            sentence_english.grid(row = 3 * 2 + 1, column = 2)

            #make it possible to enter your own question
            button = tk.Button(frame2, text = 5, 
                               command = lambda val = 4: self.select_sentence(val))
            button.grid(row = 4 * 2, column = 0, rowspan = 2, pady = (20,0))

            self.own_example_sentence = tk.Entry(frame2)
            self.own_example_sentence.grid(row = 4 * 2, column = 2, pady = (20,0))
            self.own_example_sentence.bind("<Return>", 
                                           lambda event: self.adding_translation_to_written_sentence(event, frame2))

                

            
        self.widget.pack()
        
        
        #Shows three sentences and their translation and have a button next to each of them (in frame 2)
        #add the input sentence with a button
        #add an input box with a button

        #add a more sentences button 

        #Create an add button

    def return_clicked(self):
        """
        returns whether the word has been clicked
        """
        return self.clicked

    def get_clicked(self):
        """
        Changes whether word is clicked or not
        """
        self.clicked = not self.clicked

    def translate(self, to_translate):
        """
        Translates the something
        """
        mime_type = "text/plain"

        response = client.translate_text(
            contents = [to_translate],
            parent = parent,
            mime_type = mime_type,
            source_language_code = source_lang,
            target_language_code= target_lang
        )

        translation = response.translations[0]

        return translation

    def speak_text(self, to_speak):
        input_text = texttospeech.SynthesisInput(text = to_speak)
        voice = texttospeech.VoiceSelectionParams(language_code = "sr-RS")
        audio_config = texttospeech.AudioConfig(
            audio_encoding = texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input = input_text,
            voice = voice,
            audio_config = audio_config
        )

        with open(config.first_part + to_speak + ".mp3", "wb") as out:
            out.write(response.audio_content)

    def find_all_examples(self, word):
        sentences = df[df["Serbian"].str.contains(word, case = False, na = False)]
        self.sentence_shown = 0
        return sentences 

    def translation_choice(self):
        print("hello")
        


#Creating class
class AnkiAdder: 
    def __init__(self, root):
        """
        Initalisation of Anki Adder
        Inputs: 
            root: the screen
        """
        #initalisation of screen
        self.root = root
        self.root.title("Anki adder")
        self.height = 700
        self.width = 400
        self.root.geometry(f"{self.width}x{self.height}")

        #Variable
        self.current_word_screen = 0
        self.chosen_words = []
        self.word_buttons = []

        #Create the screen
        self.basic_screen()

    def basic_screen(self):
        """
        Creates the screen
        """
        #Creates sentence block
        sentence_label = tk.Label(
            root, text = "Enter sentence",
            font = ("Helvetica", 16, "bold"), fg = "black"
        )
        sentence_label.pack(padx = 15, pady= 10)
        
        self.sentence_entry = tk.Entry(root)
        self.sentence_entry.pack(padx = 10)
        self.num_words_selected = 0
        
        self.sentence_entry.bind("<Return>", self.enter_sentence)


        #Creates word choice
        sentence_word_label = tk.Label(
            root, text = "Sentence",
            font = ("Helvetica", 16, "bold"), fg = "black"
        )
        sentence_word_label.pack(padx = 10, pady=10)
        
        self.frame = tk.Frame(root, bg = "lightblue", width = self.width - 20, height = 30)

        #function to create window with all words
        self.word_screen()

        #function to add or delete 
        print(f"len is {len(self.chosen_words)}")
    
        print("Len")
        add_button = tk.Button(root, text = "Add", command= self.adding_anki)
        add_button.pack(padx = 10, pady = 10)

    def adding_anki(self):
        if len(self.chosen_words) > 0:
            self.chosen_words[self.current_word_screen].add_word

    def select_word(self, i): 
        """
        Adds or removes a word from the chosen list. Changes the clicked value
        for the word to True/False and changes colour of button
        Input: 
            i: the index of the word we are adding
        """    
        if self.chosen_words[i].return_clicked():
             colour = 'red'
             self.chosen_words[i].get_clicked()
             self.num_words_selected += 1
             self.chosen_words[i].creates_screen_for_ind_word()
             self.current_word_screen = i
        else: 
            colour = 'white'
            self.chosen_words[i].get_clicked()
            self.num_words_selected -= 1
            self.chosen_words[i].remove_screen_for_ind_word()
        self.word_buttons[i].config(bg = colour)
        


    def create_word_selection_screen(self):
        """
        Creates the buttons for selecting word in sentence
        """     
        self.frame.pack(padx = 10, pady = 5)
        for i, word in enumerate(self.words_in_sentence):
            self.chosen_words.append(ankiWord(word, self.width, self.height, self.sentence_entry, root))

            button_for_word = tk.Button(self.frame, text = word, bg = "white", 
                                  command = lambda val = i: self.select_word(val))

            self.word_buttons.append(button_for_word)
            button_for_word.grid(row = 1, column = i*2, padx = 10)

    def enter_sentence(self, event):
        """
        Triggered when we enter a sentence.
        Triggers create_word_selection_screen
        """
        self.frame.destroy()
        self.frame = tk.Frame(root, bg = "lightblue", width = self.width - 20, height = 30)
        self.sentence_entry = self.sentence_entry.get()
        self.words_in_sentence = self.sentence_entry.split(" ")
        self.create_word_selection_screen()

    def switch_screen(self, change):
        new_screen = (self.current_word_screen + change) % self.num_words_selected
        self.current_word_screen = new_screen
        self.chosen_words[self.current_word_screen].create_screen_for_ind_word()
        


    def word_screen(self):
        """
        Creates the screen that holds the word screen 
        """
        self.frameInner = tk.Frame(root, bg = "lightblue", width = self.width - 20, height = 30)
        left_button = tk.Button(self.frameInner, text = "←", 
            command= lambda change = -1: 
            self.switch_screen(change))
        
        right_button = tk.Button(self.frameInner, text = "→",
                                 command= lambda change = -1: 
                                             self.switch_screen(change))

        
        


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