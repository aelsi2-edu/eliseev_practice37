from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty, StringProperty, BooleanProperty
from kivy.config import Config
from multiprocessing import Queue, Process
import pyttsx3
import os

QUESTIONS = [ 
    ("Какая у вас плотность?", ["< 100 кг/м³", "100-500 кг/м³", "500-1000 кг/м³", "> 1000 кг/м³"],
    "https://forsport.pro/image/cache/data/TOVAR/Originfit/girya-medved-800x800.jpg"),
    ("Какой ваш объем?", ["< 10 л", "10-50 л", "50-90 л", "> 90 л"],
    "https://cdn.fxyz.ru/img/formulas/sphere_sector_volume.png"),
    ("Каково ваше отношение к специальной операции России на Украине?", ["Положительное", "Патриотичное", "Готов идти воевать", "УРА РАСИЯ"],
    "https://klike.net/uploads/posts/2020-08/1597736699_1.jpg"),
    ("Какой ваш вес? (по вашим ощущениям)", ["40-60 кг", "60-80 кг", "80-100 кг", "> 100 кг"],
    "https://celebheightage.com/wp-content/uploads/2021/01/Nikocado-Avocado-150x150_c.jpg"),
    ("Вы едите на ночь?", ["Никогда", "Иногда", "Часто", "Каждый день"],
    "https://thumbs.dreamstime.com/t/open-refrigerator-lights-inside-clear-d-scene-46047877.jpg"),
    ("Какая из этих игр вам больше нравится?", ["Celeste", "osu!", "League of Legends", "Genshin Impact"],
    "https://www.simply-ergonomic.co.uk/wp-content/uploads/bodybilt-double-bench-192x192.jpg"),
]


def speech_loop(input_queue):
    tts_engine = pyttsx3.init()
    while True:
        if input_queue.empty():
            continue
        string = input_queue.get()
        tts_engine.say(string)
        tts_engine.runAndWait()

Builder.load_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Measurer.kv"))

class QuestionScreen(Screen):
    def reset_checkboxes(self):
        for id in reversed(self.ids):
            if isinstance(self.ids[id], CheckBox):
                self.ids[id].active = False

class ResultScreen(Screen):
    pass

class MeasurerApp(App):
    question_text = StringProperty()
    image_source = StringProperty()
    option_0_text = StringProperty()
    option_1_text = StringProperty()
    option_2_text = StringProperty()
    option_3_text = StringProperty()   
    next_enabled = BooleanProperty(False)
    
    result = NumericProperty()
    
    __question_index : int = 0
    __selected_index : int = None
    __selected_indices : [int] = []
    
    __speech_queue : Queue = None
    
    def __init__(self, speech_queue):
        super().__init__()
        self.__speech_queue = speech_queue
    
    def build(self):
        sm = ScreenManager()
        sm.add_widget(QuestionScreen(name="question"))
        sm.add_widget(ResultScreen(name="result"))
        return sm
    
    def on_start(self, **kwargs):
        self.__load_question(self.__question_index)
    
    def on_next_click(self):
        if (self.__question_index == len(QUESTIONS) - 1):
            
            self.__show_results()
            return
        self.__question_index += 1
        self.__selected_indices.append(self.__selected_index)
        self.__load_question(self.__question_index)
    
    def on_select(self, index, value):
        if value == True:
            self.__selected_index = index
            self.next_enabled = True
        else:
            self.__selected_index = None
            self.next_enabled = False
        
    def on_deselect(self):
        self.__selected_index = None
        self.next_enabled = False
        pass
        
    def __load_question(self, index):
        self.__reset_checkboxes()
        question, options, image = QUESTIONS[index]
        self.question_text = question
        self.option_0_text = options[0]
        self.option_1_text = options[1]
        self.option_2_text = options[2]
        self.option_3_text = options[3]
        self.image_source = image
        self.__speech_queue.put(question)
    
    def __reset_checkboxes(self):
        self.root.screens[0].reset_checkboxes()
        
    def __show_results(self):
        self.result = 30
        for index in self.__selected_indices:
            self.result += (index + 1) * 4
        self.root.current = "result"
        self.__speech_queue.put("Поздравляем! Ваш вес составляет " + str(self.result) + " килограммов.")

if __name__ == "__main__":
    queue = Queue()
    process = Process(target=speech_loop, args=(queue,), daemon=True)
    process.start()
    Config.set('graphics', 'width', '300')
    Config.set('graphics', 'height', '533')
    Config.set('graphics', 'resizable', '0')
    MeasurerApp(queue).run()