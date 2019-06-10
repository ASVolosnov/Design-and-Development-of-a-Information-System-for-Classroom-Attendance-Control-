from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
import hashlib
import json
import datetime
from kivy.config import Config
import Selenium_req
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
import pickle
#импортируем необходиые модули
#задаем размеры экрана
Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', 800)
Config.set('graphics', 'height', 500)

#Базовый класс реализующий структуру работы Blockchain для одного из предметов
class Screen1(Screen):
    #функция обновления текста на виджете Label
    def lbl_update(self):
        self.lbl.text = self.formula
    #конструктор класса
    def __init__(self, **kwargs):
        super(Screen1, self).__init__(**kwargs)
        self.chain = [] # вся цепочка
        self.formula = "" # переменная для записи передаваемого текста
        self.nam = "Mathematical analis" #  название предмета
        self.File_name = "blockchain.dat" # название файла где хранитьяс цепочка
        self.now = datetime.datetime.now() # возвращает текущее время в now
        self.user_name = "" # имя пользователя
        self.img = Image(source = 'Main.jpg', size_hint= (None, None), size= (800, 600))
        #открываем файл
        with open(self.File_name, "rb") as file:
            self.chain = pickle.load(file)

        #задем необходимые контейнеры для сборки виджетов экрана
        bl = BoxLayout(orientation = 'vertical', size_hint = (1, .6 ))# обычная коробка виджетов вертикальная или горизонтальная
        gl = GridLayout(cols = 5, spacing = 3, size_hint = (1,.6))# коробка виджетов в виде матриццы
        self.lbl = Label(text = "0", font_size = 20, halign ="center" , valign = "top",  size_hint = (1, .4), text_size = (800, 320))
        #виджет отображающий информацию
        bl.add_widget(self.lbl)
        #заполняем кнопками
        gl.add_widget(Button(text = "Посмотреть журнал", on_press = self.full_chain))
        gl.add_widget(Button(text = "     посмотреть \nпоследний блок", on_press = self.last_block))
        gl.add_widget(Button(text = "отметиться", on_press = self.add_block))
        gl.add_widget(Button(text="ввести пользователя", on_press=self.clk))
        gl.add_widget(Button(text="Закончить предмет", on_press=self.finish_add_gen))

        #заполняем экран
        bl.add_widget(gl)
        self.add_widget(bl)

    #функция заполнения имени пользователя
    def callback(self,value):
        self.user_name = value

    #функция вызова всплывающего окна для заполнения данных пользователя
    def clk(self,obj):
        #формирируем вид всплывающего окна
        box = BoxLayout(orientation='vertical')
        my_int = TextInput(multiline=False)
        box.add_widget(my_int)
        but1 = Button(text="вернуться")
        but2 = Button(text="OK")
        box.add_widget(but1)
        box.add_widget(but2)
        #открываем всплывающее окно
        popup = Popup(content=box)
        popup.open()
        #указываем события нажатия кнопок
        but2.bind(on_press=lambda *a: self.callback(my_int.text))#передаем текст в user_name
        but1.bind(on_press=popup.dismiss)# закрываем всплыающее окно
        return False

    #функция возврата содержимого в цепочки на экран
    def full_chain(self, instance):
        self.formula = ""
        #в цепочке ищем и выводим только имя и время регистрации
        for i in range (0,len(self.chain)):
            self.formula = self.formula + str(self.chain[i]['user_name'])+ " "+ str(self.chain[i]['timestamp']) + "\n"
        self.lbl_update()
    #функция возвращает последний вычисленный блок цепочки ()
    def last_block(self, instance):
        self.formula = str(self.chain[-1])
        self.lbl_update()

    #функция хеширования передаваемой информации, возвращает хеш
    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    #функция проверки верности передаваемого пруфа
    def valid_proof(self, mac,logi):
        #проверяем наличие mac адреса в списке всех пользователей
        check = Selenium_req.valid_mac(logi,mac)
        return check

    #функция вычисления доказательства
    def proof_of_work(self):
        #получаем список текущих mac адресов
        logi = Selenium_req.wifi_mac_ip().lower()
        #получаем mac адрес текущего устройства в форме доказательства
        proof = Selenium_req.my_mac(logi)
        #проверяем его наличие
        valid = self.valid_proof(proof,logi)
        if valid == True:
            return proof
        else:
            return False

    #функция добалвения нового вычисленного блока
    def add_block(self, instance):
        if self.user_name != '':
            #вычисляем mac адрес
            a = self.proof_of_work()
            #формирируем и добавляем блок
            if a != False:
                block = {
                    'user_name': self.user_name,
                    'index': len(self.chain),
                    'timestamp': str(self.now),
                    'proof': a,
                    'previous_hash': self.hash(self.chain[-1]),
                }
                self.chain.append(block)
                #перезаписываем цепочку в файл
                with open(self.File_name, "wb") as file:
                    pickle.dump(self.chain, file)
            else:
                return False
        else:
            return False

    #функция проверки цепочки
    def valid_chain(self, instance):
        #проверка осуществляется путем проверки правильности вычисленных хешей
        for i in range(1,len(self.chain)):
            if self.chain[i]['previous_hash'] != self.hash(self.chain[i-1]):
                self.formula = "False"
                self.lbl_update()
                return False
        self.formula = "True"
        self.lbl_update()
        return True

    #функция добавления законченного предмета в основную цепь
    def finish_add_gen(self,instance):
        #первым делом необходимо посчитать Merkl root
        list_merkle = []
        #вычисляем хеш каждого блока и записываем в списко list_merkle
        for i in range(0,len(self.chain)):
            list_merkle.append(self.hash(self.chain[i]))
        #иттерационо вычисляем хеши двух парных предыдущих сум хешей
        while len(list_merkle) >1:
            #если нечетное количество хешей в списке допляем список последним хешем
            if len(list_merkle) % 2 != 0:
                list_merkle.append(list_merkle[-1])
            #вычисляем хеш суммы двух соседних хешей списка
            for i in range(0,len(list_merkle),2):
                list_merkle[i] = self.hash(list_merkle[i] + list_merkle[i+1])
            #после каждой итерации сокращаем спсок, убирая старые хеши
            for i in range(0,int(len(list_merkle)/2)):
                    del list_merkle[i+1]
        cash = []
        #считываем файл с списком всех завершенных предметов
        with open("GenBlockchain.dat", "rb") as file:
            cash = pickle.load(file)
        Bl = []
        #формируем блок с описание самогоо предмета
        Gen = {
            'name': self.nam,
            'timestamp':str(self.now),
            'len': len(self.chain),
            'merkle_root': list_merkle[0],
            'previous_hash': self.hash(cash[-1][0]),
        }
        #добавляем в блок описание предмета
        Bl.append(Gen)
        #добавляем в блок цепь отметок за все время
        Bl.append(self.chain)
        #полуенный блок добавляем ко всем другим завершенным предметам
        cash.append(Bl)
        # перезаписываем новую цепь
        with open("GenBlockchain.dat", "wb") as file:
            pickle.dump(cash, file)
    pass

#класс наследующий построение Screen1 для построения нового предмета программировние
class Screen3(Screen1):
    def __init__(self, **kwargs):
        super(Screen3, self).__init__(**kwargs)
        self.File_name = "blockchain1.dat"
        self.nam = "Programming"
        #открываем файл для цепочки по программированию
        with open(self.File_name, "rb") as file:
            self.chain = pickle.load(file)

#класс наследующий построение Screen1 для построения нового предмета наука о данных
class Screen4(Screen1):
    def __init__(self, **kwargs):
        super(Screen4, self).__init__(**kwargs)
        self.File_name = "blockchain2.dat"
        self.nam = "Data sciences"
        #открываем файл для цепочки науки о данных
        with open(self.File_name, "rb") as file:
            self.chain = pickle.load(file)

#класс для построения и взаимодействия с цепью всех завершенных предметов
class Screen5(Screen):
    #мметод обновления текста на экране
    def lbl_update(self):
        self.lbl.text = self.formula
    #констурктор для формирования вида окна
    def __init__(self, **kwargs):
        super(Screen5, self).__init__(**kwargs)
        self.cash = [] #здесь храниться цепочка
        self.formula = ""#текст для виджета отображения текста
        self.subj_name = ""#название предмета

        bl = BoxLayout(orientation='vertical', size_hint=(1, .6))
        gl = GridLayout(cols=3, spacing=3, size_hint=(1, .6))
        self.lbl = Label(text="0", font_size=20, halign="center", valign="top", size_hint=(1, .4), text_size=(800, 500))
        bl.add_widget(self.lbl)

        #кнопка для просмотра последнего добавленного предмета
        gl.add_widget(Button(text="       посмотреть \nпоследний предмет", on_press=self.last_block))
        #кнопка поиска введенного предмета
        gl.add_widget(Button(text="     найти \n   предмет", on_press=self.find_block))
        #всплывающее окно с вводом искомого предмета
        gl.add_widget(Button(text="                  задайте \nпоиск по названию предмета", on_press=self.clk))

        bl.add_widget(gl)
        self.add_widget(bl)

    #функция сохранения вводимого названия предмета для поиска
    def callback(self,value):
        self.subj_name = value

    #функция всплывающего окна
    def clk(self,obj):
        box = BoxLayout(orientation='vertical')
        my_int = TextInput(multiline=False)
        box.add_widget(my_int)
        but1 = Button(text="вернуться")
        but2 = Button(text="OK")
        box.add_widget(but1)
        box.add_widget(but2)

        # value = lambda *a:self.callback(my_int.text)
        # print(value)

        popup = Popup(content=box)

        popup.open()
        but2.bind(on_press=lambda *a: self.callback(my_int.text))
        but1.bind(on_press=popup.dismiss)
        return False
    #функция поиска введнного предмета
    def find_block(self,instance):
        #открываем файл для чтения
        with open("GenBlockchain.dat", "rb") as file:
            self.cash = pickle.load(file)
        flag = True
        #алгоритм поиска
        for j in range(2,len(self.cash)):
            #условие поиска имени предмета совпадающее с введеным навзванием
            if self.cash[j][0]['name'] == self.subj_name:
                #записываем описание этого предмета
                self.formula = self.formula + str(self.cash[j][0]['name']) + " " + str(self.cash[j][0]['timestamp']) + "\n"
                #записываем содержимое о посещениях
                for i in range(0, len(self.cash[j][1])):
                    self.formula = self.formula + str(self.cash[j][1][i]['user_name']) + " " + str(self.cash[j][1][i]['timestamp']) + "\n"
                self.lbl_update()
                self.formula = ""
                flag = False
                return 1
        if flag == True:
            self.formula = "Не найдено"
            self.lbl_update()
            self.formula = ""

    #фнкция отображения последнего добавленного предмета
    def last_block(self, instance):
        #открыываем файл для чтения
        with open("GenBlockchain.dat", "rb") as file:
            self.cash = pickle.load(file)
        self.formula =""
        #записываем описание предмета
        self.formula = self.formula+ str(self.cash[-1][0]['name']) + " "+ str(self.cash[-1][0]['timestamp']) + "\n"
        #записываем все отметки этого предмета
        for i in range(0, len(self.cash[-1][1])):
            self.formula = self.formula+ str(self.cash[-1][1][i]['user_name']) +" " +str(self.cash[-1][1][i]['timestamp']) + "\n"
        self.lbl_update()

#класс окна главного меню
class Screen2(Screen):
    pass

#классреализации взаимодействия окон
class ScreenManagement(ScreenManager):
    pass

#путь к файлу содержащий внешнее описание приложения
presentation = Builder.load_file("style.kv")

#класс реализующий запуск работы самого приложения
class MyApp(App):
    def build(self):
        return presentation

if __name__ == "__main__":
    MyApp().run()





