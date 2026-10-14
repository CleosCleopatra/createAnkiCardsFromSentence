import tkinter as tk
from tkinter import ttk
from google.cloud import translate_v3
from google.api_core.client_options import ClientOptions
import google.auth
import requests
import pandas as pd
import config
import customtkinter

df = pd.read_csv(config.csv_file, sep="\t", names = ["Serbian_id", "Serbian", "English_id", "English"])

source_lang = 'sr'
target_lang = 'en'

letter_dict = {"1": "č", "2": "ć", "3": "đ", "4": "š", "5": "ž"}

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


class toggleButton:
    def __init__(self, parent, text, num_button, command = None):
        print("togglebutton run")
        self.value = False
        self.command = command

        if not num_button:
            self.button = customtkinter.CTkButton(
                parent,
                text = text,
                font = ("Segoe UI", 10),
                fg_color = "#f4f4f4",
                text_color = "#222222",
                corner_radius = 7,
                cursor = "hand2",
                command = self.toggle,
                width = 30
            )
        else: 
            self.button = customtkinter.CTkButton(
                parent,
                text = text,
                font = ("Segoe UI", 10),
                fg_color = "#f4f4f4",
                text_color = "#222222",
                corner_radius = 2,
                cursor = "hand2",
                command = self.toggle,
                width = 5,
                height = 5
            )

    def get_button(self):
        print("get button run")
        return self.button

    def toggle(self):
        print("toggle run")
        self.value = not self.value
        self.update_colour()

        if self.command:
            self.command(self.value)

    def get(self):
        print("get run")
        return self.value

    def set(self, value):
        print("set run")
        self.value = value
        self.update_colour()

    def update_colour(self):
        print("update colour")
        if self.value:
            self.button.configure(
                fg_color="#2f71eb",
                text_color = "white")
        else: 
            self.button.configure(
                fg_color="#f4f4f4",
                text_color = "#222222"
            )
    

class sentence_class:
    def __init__(self, sentence, sentence_index, english_sentence):
        self.sentence = sentence
        self.sentence_index = sentence_index
        self.chosen = False
        self.english_sentence = english_sentence
        
    def change_chosen(self):
        print("change chosen")
        self.chosen = not self.chosen
    def get_chosen(self):
        print("get chosen")
        return self.chosen
    def get_serbian(self):
        print("get serbian")
        return self.sentence
    def get_english(self):
        print("get english")
        return self.english_sentence
    def get_index(self):
        print("get index")
        return self.sentence_index
    


class ankiWord:
    def __init__(self, word, width, height, input_sentence, input_translation, current):
        print("ankiword init")
        self.word = word
        self.width = width
        self.height = height
        self.clicked = False
        self.widget = tk.Frame(current, bg = "lightblue", width = self.width - 20, height = 30)
        self.screen_generated = False

        self.translation = self.translate(word)
        sentence_examples = self.find_all_examples(word)
        self.sentences = []
        if sentence_examples is not None:
            for i in range(sentence_examples.shape[0]):
                example = sentence_examples.iloc[i]
                new_sentence = sentence_class(example["Serbian"], i, example["English"])
                self.sentences.append(new_sentence)

        self.input_sentence = sentence_class(input_sentence, len(self.sentences), input_translation)

        self.word_index_to_show = 0
        self.chosen_sentence = None
        self.chosen_sentence_english = None

        self.select_sentence_buttons = []

    def more_sentences(self):
        print("more sentence")
        self.word_index_to_show = (self.word_index_to_show + 3) % len(self.sentences)

    def choose_sentence(self, sentence):
        print("choose sentences")
        print("here")
        #Changes chosen sentence to whatever we have pressed
        #Saves its pronuncation

    
    def add_word(self):
        print("add word")
        print("add_word")
        if self.chosen_sentence:
            print("True")
            #saves audio files 
            word_sound = self.speak_text(self.word, self.word)
            print(f"word sound is {word_sound} with type {type(word_sound)}")
            sentence_sound = self.speak_text(self.chosen_sentence.get_serbian(), f"{self.word}_sentence")
            #Create audio paths
            print(f"serbian {self.chosen_sentence.get_serbian()}, english {self.chosen_sentence.get_english()}")
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
                                "Sentence Serbian": self.chosen_sentence.get_serbian(),
                                "Sentence English": self.chosen_sentence.get_english(),
                                "Past tense": "",
                                "Future tense": "",
                                "Conjugate": "",
                                "P/I": "",
                                "present": "",
                                "Pronuncation": "",
                                "Sentence pronuncation": ""
                            },
                            "audio": [{
                                "path": word_sound,
                                "filename": f"{self.word}.mp3",
                                "fields": ["Pronuncation"]
                            },
                            {
                                "path": sentence_sound,
                                "filename": f"{self.word}_sentence.mp3",
                                "fields": ["Sentence pronuncation"]
                            }]
                        }
                    }
                }
            )


    def remove_screen_for_ind_word(self):
        print("remove screen for ind word")
        self.widget.pack_forget()

    def sentences_list(self):
        print("sentences list")
        if len(self.sentences) > 0:
            indexes = [self.word_index_to_show, (self.word_index_to_show + 1) % len(self.sentences), 
                   (self.word_index_to_show + 2) %len(self.sentences)]
            return indexes
        return []

    def select_sentence(self, index, state):
        print(f"state is {state}, index is {index}")
        print("select sentence")
        if len(self.sentences) == 0:
            if index == 3:
                self.chosen_sentence = self.input_sentence
            elif index == 4:
                self.chosen_sentence = self.own_example_sentence
            else: 
                return
        else:
            if index <= 2:
                self.chosen_sentence = self.sentences[(self.word_index_to_show + index) % len(self.sentences)]
            elif index == 3:
                self.chosen_sentence = self.input_sentence
            else: 
                self.chosen_sentence = self.own_example_sentence
        self.chosen_sentence_serbian = self.chosen_sentence.get_serbian()
        self.chosen_sentence_english = self.chosen_sentence.get_english()

        for ind, buttons in enumerate(self.select_sentence_buttons):
            print(f"ind is {ind}, index is {index}")
            if ind != index:
                buttons.set(False)



            

    def adding_translation_to_written_sentence(self, event, frame):
        print("adding translation to written sentence")
        sentence = self.own_example_sentence_box.get()
        translated = self.translate(sentence)
        sentence_translated = tk.Label(frame, text = translated,
                                                font = ("Helvetica", 12), fg = "black")
        sentence_translated.grid(row = 4 * 2 + 1, column = 2)
        print(f"sentence is {sentence}")
        self.own_example_sentence = sentence_class(sentence, len(self.sentences) + 1, translated)





    def creates_screen_for_ind_word(self):
        print("creates screen for ind word")
        if not self.screen_generated:
            #Shows the words translation
            word_translation = tk.Label(
                self.widget, text = self.translate(self.word),
                font = ("Helvetica", 16, "bold"), fg = "black"
            )
            word_translation.pack(padx = 15, pady= 3)
            self.screen_generated = True 

            #Shows three sentences and their translation with a button next to each
            indexes_to_show = self.sentences_list()

            frame2 = tk.Frame(
                self.widget, 
                bg = "red")
            frame2.pack(
                fill = "both",
                expand = True
            )

            if len(indexes_to_show) > 0:
                for index in indexes_to_show:
                    button = toggleButton(frame2, text = index, num_button= True,
                                   command = lambda state, val = index: self.select_sentence(val, state))
                    button.button.grid(row = int(index)*2, column = 0, rowspan = 2, pady = (20,0))

                    sentence = tk.Label(
                        frame2, 
                        text = self.sentences[int(index)].get_serbian(),
                        font = ("Helvetica", 12), 
                        fg = "black",
                        bg = "white",
                        wraplength=self.width - 100,
                        justify = "left"
                    )

                    sentence_english = tk.Label(
                        frame2, 
                        text = self.sentences[int(index)].get_english(),
                        font = ("Helvetica", 12), 
                        fg = "black",
                        bg = "white",
                        wraplength=self.width - 100,
                        justify = "left"
                    )
                    sentence.grid(row = int(index)*2, column = 2, pady = (20,0))
                    sentence_english.grid(row = int(index)*2 + 1, column = 2)
                    self.select_sentence_buttons.append(button)
            #add the input question
            button = toggleButton(frame2, text = len(indexes_to_show), num_button= True,
                               command = lambda state, val = len(indexes_to_show): self.select_sentence(val, state))
            button.button.grid(row = 3 * 2, column = 0, rowspan= 2, pady = (20, 0))
            self.select_sentence_buttons.append(button)

            sentence = tk.Label(
                frame2, 
                text = self.input_sentence.get_serbian(), 
                font = ("Helvetica", 12), 
                fg = "black",
                bg = "white",
                wraplength = self.width - 100,
                justify = "left"
            )

            sentence_english = tk.Label(
                frame2, 
                text = self.input_sentence.get_english(), 
                font = ("Helvetica", 12), 
                fg= "black",
                bg = "white",
                wraplength=self.width -100,
                justify = "left"
            )

            sentence.grid(row = 3 * 2, column = 2, pady = (20,0))
            sentence_english.grid(row = 3 * 2 + 1, column = 2)

            #make it possible to enter your own question
            button = toggleButton(frame2, text = len(indexes_to_show) + 1, num_button= True,
                               command = lambda state, val = (len(indexes_to_show) + 1): self.select_sentence(val, state))
            button.button.grid(row = 4 * 2, column = 0, rowspan = 2, pady = (20,0))
            self.select_sentence_buttons.append(button)

            self.own_example_sentence_box = tk.Entry(frame2)
            self.own_example_sentence = self.own_example_sentence_box.get()
            self.own_example_sentence_box.grid(row = 4 * 2, column = 2, pady = (20,0))
            self.own_example_sentence_box.bind("<Return>", 
                                           lambda event: self.adding_translation_to_written_sentence(event, frame2))

                

            
        self.widget.pack()
        
        
        #Shows three sentences and their translation and have a button next to each of them (in frame 2)
        #add the input sentence with a button
        #add an input box with a button

        #add a more sentences button 

        #Create an add button

        return self.widget

    def return_clicked(self):
        print("return clicked")
        """
        returns whether the word has been clicked
        """
        return self.clicked

    def get_clicked(self):
        print("get clicked")
        """
        Changes whether word is clicked or not
        """
        self.clicked = not self.clicked


    def translate(self, to_translate):
        print("translate")
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

        translation = response.translations[0].translated_text

        return translation

    def speak_text(self, to_speak, name):
        print("speak text")
        print(f"to speak is {to_speak}")
        input_text = texttospeech.SynthesisInput(text = to_speak)
        voice = texttospeech.VoiceSelectionParams(language_code = "sr-RS")
        audio_config = texttospeech.AudioConfig(
            audio_encoding = texttospeech.AudioEncoding.MP3
        )

        response = client_speech.synthesize_speech(
            input = input_text,
            voice = voice,
            audio_config = audio_config
        )

        where = config.first_part + name + ".mp3"
        with open(where, "wb") as out:
            out.write(response.audio_content)

        return where

    def find_all_examples(self, word):
        print("find all examples")
        sentences = df[df["Serbian"].str.contains(word, case = False, na = False)]
        self.sentence_shown = 0
        return sentences 

    def translation_choice(self):
        print("translation choice")
        print("hello")
        


#Creating class
class AnkiAdder: 
    def __init__(self, root):
        print("anki adder init")
        """
        Initalisation of Anki Adder
        Inputs: 
            root: the screen
        """
        #initalisation of screen
        self.root = root
        self.root.title("Anki adder")
        self.width = 900
        self.height = 600
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        #Variable
        self.current_word_screen = 0
        self.chosen_words = []
        self.word_buttons = []
        self.word_screens = {}

        #Create the screen
        self.setup_styles()
        self.basic_screen()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 15, "bold"),
            foreground = "#222222",
        )

        style.configure(
            "Subtitle.TLabel",
            font = ("Segoe UI", 10),
            background = "#f5f5f5",
            foreground = "#777777"
        )

        style.configure(
            "Action.TButton",
            font = ("Segoe UI", 10, "bold"),
            padding = (15,8)
        )


    def translate(self, to_translate):
            print("translate")
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
    
            translation = response.translations[0].translated_text
    
            return translation
    
    def resetting(self):
        for word in self.chosen_words:
            word.remove_screen_for_ind_word()
        #Clear the enter sentence box
        self.sentence_entry_box.delete(0, tk.END)
        #Clear the words
        self.current_word_screen = 0
        self.chosen_words = []
        self.word_buttons = []
        #Clear the sentences
        #Remove the screen

        self.num_words_selected = 0
        self.word_area.destroy()
        self.word_area.pack(fill = "both", expand = True, padx = 15, pady = 2)

    def basic_screen(self):
        print("basic screen")
        """
        Creates the screen
        """

        self.main_frame = tk.Frame(
            self.root,
            bg = "#fbfbfc"
        )

        self.main_frame.pack(
            fill = "both",
            expand = True,
            padx = 5,
            pady = 5
        )

        self.top_menu = tk.Frame(
            self.main_frame,
            highlightthickness = 2,
            highlightbackground = "#e4ebf3",
            bg=self.main_frame.cget("bg")
        )

        self.top_menu.pack(
            pady = (0, 5),
            fill='x'
        )

        tk.Label(
            self.top_menu,
            text = "Anki Adder",
            font=("Segoe UI", 15),
            bg = self.main_frame.cget("bg")
        ).pack(side = "left", pady=(5,5), padx = (15))

        tk.Label(self.main_frame,
                    text = "č:1, ć:2, đ: 3, š: 4, ž: 5",
                    font = ("Segoe UI", 15, "bold")).pack(padx = 2)

        self.sentence_card = customtkinter.CTkFrame(
            self.main_frame,
            fg_color = "#f4f7fb",
            border_width = 1,
            border_color = "#e4ebf3"
        )

        self.sentence_card.pack(
            fill = "x",
            pady=(7,7),
            padx =15
        )

        #Enter sentence

        tk.Label(
            self.sentence_card,
            text = "SENTENCE",
            font = ("Segoe UI", 5, "bold"),
            bg= self.sentence_card.cget("fg_color"),
            fg = "#445e82"
        ).pack(
            anchor = "w",
            padx = 15,
            pady=(5,3)
        )

        self.sentence_entry = " "

        self.sentence_entry_box = tk.Entry(
            self.sentence_card,
            font = ("Segoe UI", 16),
            relief = "flat",
            bg = self.sentence_card.cget("fg_color"),
            bd = 0
        )
        
        self.sentence_entry_box.pack(
            fill = "x",
            padx = 15,
            pady = (0,1)
        )


        self.translated_label_box = tk.Entry(
            self.sentence_card,
            font = ("Segoe UI", 16),
            bg = self.sentence_card.cget("fg_color"),
            fg = "#8698b6",
            relief = "flat",
            bd = "0"
        )

        """
        self.translated_label =tk.Label(
            self.sentence_card,
            text = translate,
            font = ("Segoe UI", 10),
            bg= self.sentence_card.cget("fg_color"),
            fg = "#8698b6"
                )
        """
        self.translated_label_box.pack(
                    anchor = "w",
                    padx = 15,
                    pady=(1,3),
                    fill = "x"
                )


        
        self.num_words_selected = 0

        self.sentence_entry_box.bind(
            "<Return>",
            self.enter_sentence
        )

        #word area

        #####################

        self.word_selection_area = tk.Frame(
            self.main_frame,
            bg = self.main_frame.cget("bg")
        )

        self.word_selection_area.pack(
            fill = "both",
            pady = (0,10)
        )

        self.select_words_label = tk.Label(
            self.word_selection_area,
            text = "WORDS IN SENTENCE",
            font = ("Segoe UI", 10, "bold"),
            fg = "#5e7395",
            bg = self.word_selection_area.cget("bg")
        )

        self.select_words_label.pack(side = "left", padx = 7, pady=(5,3))

        self.word_buttons_frame = tk.Frame(
            self.word_selection_area,
            bg = self.word_selection_area.cget("bg")
        )

        self.word_buttons_frame.pack(
            fill = "x"
        )

        #Creates word choice
        self.word_area = customtkinter.CTkFrame(
            self.main_frame,
            corner_radius=6,
            fg_color = "#fcfcfd",
            border_width= 1,
            border_color="#e8eef5"
        )

        self.word_area.pack(fill = "both",
                            expand = True,
                            padx = 15,
                            pady = 2
                            )

        self.navigation_frame = tk.Frame(
            self.main_frame, 
            bg = "#a91b1b"
        )

        self.navigation_frame.pack(
            pady = 5
        )

        self.left_button = tk.Button(
            self.navigation_frame,
            text = "←",
            font = ("Segoe UI", 14),
            bg = "yellow",
            fg = "#333333",
            activebackground="#068604",
            relief = "flat",
            bd = 0,
            padx = 18,
            pady = 5,
            cursor = "hand2",
            command = lambda: self.switch_screen(-1)
        )

        self.left_button.pack(side = "left", padx = 5)

        self.right_button = tk.Button(
            self.navigation_frame,
            text="→",
            font=("Segoe UI", 14),
            bg="green",
            fg="#333333",
            activebackground="#33cc68",
            relief="flat",
            bd=0,
            padx=18,
            pady=5,
            cursor="hand2",
            command=lambda: self.switch_screen(1)
        )
        self.right_button.pack(side="left", padx=5)

        self.button_frame = tk.Frame(
            self.main_frame,
            bg = "#a51483"
        )
        self.button_frame.pack(
            side = "bottom",
            fill = "x",
            pady = 10
        )
        

        #function to add or delete 
        self.add_button = tk.Button(
            self.button_frame,
            text = "Add to Anki",
            font = ("Segoe UI", 10, "bold"),
            bg = "#3006AC",
            fg = "white",
            activebackground= "#ae9a13",
            activeforeground="white",
            relief = "flat",
            bd = 0, 
            padx = 25,
            pady = 9,
            cursor = "hand2",
            command = self.adding_anki
        )
        
        self.add_button.pack(side = "left", padx =5)

        self.reset_button = tk.Button(
            self.button_frame, 
            text = "Reset",
            font = ("Segoe UI", 10),
            bg = "yellow",
            fg = "#555555",
            activebackground="#640101",
            relief = "flat",
            bd = 0,
            padx = 20,
            pady = 9,
            cursor = "hand2",
            command = self.resetting
        )

        self.reset_button.pack(side = "left", padx = 5)

    def make_translated_text(self):
        sentence = self.sentence_entry_box.get().strip()

        print(sentence)
        for i in range(len(sentence)): 
            print(sentence[i])
            if sentence[i] in letter_dict.keys:
                sentence[i] = letter_dict[sentence[i]]

        if not sentence: 
            self.translated_label_box.delete(0, tk.END)
            return
        translate = self.translate(self.sentence_entry)
        self.translated_label_box.delete(0, tk.END)
        self.translated_label_box.insert(0, translate)


    def adding_anki(self):
        print("adding anki")
        print("adding")
        print(f"chosen words are {self.chosen_words}, with {(len(self.chosen_words))}")

        if len(self.chosen_words) > 0:
            print("this is true")    
            self.chosen_words[self.current_word_screen].add_word()

    def select_word(self, i, state): 
        print("select word")
        """
        Adds or removes a word from the chosen list. Changes the clicked value
        for the word to True/False and changes colour of button
        Input: 
            i: the index of the word we are adding
        """   
        """
        word = self.chosen_words[i]
        word.get_clicked()

        if self.chosen_words[i].return_clicked():
             colour = 'red'
             self.num_words_selected += 1
             self.chosen_words[i].creates_screen_for_ind_word()
             self.current_word_screen = i
        else: 
            colour = 'white'
            self.chosen_words[i].get_clicked()
            self.num_words_selected -= 1
            self.chosen_words[i].remove_screen_for_ind_word()
        self.word_buttons[i].config(bg = colour)
        """
        print("wordd")
        if state:
            #if self.current_word_screen != i:
            #    self.chosen_words[self.current_word_screen].remove_screen_for_ind_word()
            print("add word")
            self.num_words_selected += 1
            screen = self.chosen_words[i].creates_screen_for_ind_word()
            self.word_screens[i] = screen
            self.current_word_screen = i
            self.show_frame(i)


        else: 
            print("remove word")
            self.num_words_selected -= 1
            print(f"chosen words is {self.chosen_words[i]}")
            self.chosen_words[i].remove_screen_for_ind_word()
        



    def create_word_selection_screen(self):
        print("create word selection screen")
        """
        Creates the buttons for selecting word in sentence
        """ 
        input_translation = self.translated_label_box.get()    
        if input_translation == "":
            input_translation = self.translate(self.sentence_entry)
        for i, word in enumerate(self.words_in_sentence):

            self.chosen_words.append(ankiWord(word, self.width, self.height, self.sentence_entry, input_translation, self.word_area))

            button_for_word = toggleButton(self.word_buttons_frame, text = word, num_button=False,
                                  command = lambda state, i = i: self.select_word(i, state))

            self.word_buttons.append(button_for_word)
            button_for_word.button.grid(row = 0, column = i, padx = 5, pady = 8)

        self.translated_label_box.delete(0, tk.END)
        self.translated_label_box.insert(0, input_translation)
        #####################################

    def enter_sentence(self, event):
        print("enter sentence")
        """
        Triggered when we enter a sentence.
        Triggers create_word_selection_screen
        """
        sentence = self.sentence_entry_box.get().strip()
    
        print(f"sentence: {sentence}")
        for number in letter_dict.keys():
            sentence = sentence.replace(str(number), letter_dict[number]) 
        print(f"sentence: {sentence}")

        self.sentence_entry = sentence

        self.sentence_entry_box.delete(0, tk.END)
        self.sentence_entry_box.insert(0, sentence)

        

        if not self.sentence_entry:
            return
        translated = self.translate(self.sentence_entry)

        self.words_in_sentence = self.sentence_entry.split(" ")

        self.chosen_words = []
        self.word_buttons = []
        self.word_screens = {}
        self.current_word_screen = 0
        self.num_words_selected = 0

        for widget in self.word_buttons_frame.winfo_children():
            widget.destroy()

        if self.word_area.winfo_exists():
            for widget in self.word_area.winfo_children():
                widget.destroy()

        self.create_word_selection_screen()

    def show_frame(self, index):
        for screen in self.word_screens.values():
            screen.pack_forget()

        if index in self.word_screens:
            self.word_screens[index].pack(
                fill = "both",
                expand = True,
                padx = 15,
                pady = 10
            )
    
    def switch_screen(self, change):
        print("switch screen")
        if self.num_words_selected == 0:
            return

        selected_indexes = [
            i for i, button in enumerate(self.word_buttons)
            if button.get()
        ]

        if not selected_indexes:
            return

        current_position = selected_indexes.index(
            self.current_word_screen
        )

        new_position = (
            current_position + change
        ) % len(selected_indexes)

        self.current_word_screen = (selected_indexes[new_position])
        self.show_frame(self.current_word_screen)
        

        
        


root = customtkinter.CTk()
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