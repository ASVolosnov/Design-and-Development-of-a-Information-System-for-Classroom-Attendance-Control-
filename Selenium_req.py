from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import win32com.client
import pyperclip
import netifaces
#Подключаем необходимые модули

#Функция поиска списка mac адресов в сети роутера
def wifi_mac_ip():
    #указываем путь к гугл драйверу, для возможности общения с роутером
    driver = webdriver.Chrome(executable_path=r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\chromedriver.exe')
    #Указываем ip адрес роутера
    url = "http://tplinkwifi.net"
    driver.get(url)
    #заполняем поля регистрации и делаем вызов нужного компонента web сайта
    login = driver.find_element_by_id('userName')
    login.send_keys("Artem")
    passwd = driver.find_element_by_id('pcPassword')
    passwd.send_keys("as12as12as12")
    logBtn = driver.find_element_by_id('loginBtn')
    logBtn.click()
    #обращаемся к внешнему элементу отвечающего за левой меню
    ll = driver.find_element_by_xpath('//*[@id="frame1"]')
    ll.click()
    #делаем вызовы кликов для вывода на экран необходимой информации
    action = webdriver.common.action_chains.ActionChains(driver)
    #все вызовы кликов, должны происхоить относительно элемента ll
    action.move_to_element_with_offset(ll, 10, 100)
    action.click()
    action.perform()
    action.move_to_element_with_offset(ll, 10, 230)
    action.click()
    action.perform()
    #находим внешний элемент отвечающий за тело отображаемой информации
    vv = driver.find_element_by_xpath('//*[@id="frame2"]')
    #находим необходимую позицию и делаем вызов клика и удержания
    action.move_to_element_with_offset(vv,30,150)
    action.click_and_hold(on_element=None)
    #передвигаем позицию максимально вниз
    action.move_to_element_with_offset(vv,500,500)
    #делаем вызов CTR + C
    shell = win32com.client.Dispatch('WScript.Shell')
    shell.SendKeys('^c')
    #совершаем такой же вызов для web интерфейса
    action.send_keys(Keys.CONTROL, 'c')
    action.perform()
    #выводим содержимого в буфере
    text = pyperclip.paste()
    #возвращаем полученный список (список содержит и иную инфомрацию)
    return text



def my_mac(text):
    #делаем шрифт передаваемого текста малым, что бы не было несоответствий
    text = text.lower()
    list_serv = []
    index = 0
    save_num =0
    #делаем вызов получения mac адресов для каждой созданной связи устройства
    for i in range(0,len(netifaces.interfaces())):
       list_serv.append(netifaces.ifaddresses(netifaces.interfaces()[i])[netifaces.AF_LINK][0]['addr'])
    #ишем в полученном списке совпадения mac адреса и запоминаем
    for i in range(0,len(list_serv)):
        # если находится вхождение подстроки то возвращается позция начала иначе -1
        index = text.find(list_serv[i])
        if index >0:
            save_num = i
            break
    #функций возвращает mac адреса в сети роутера
    return list_serv[save_num]

#функция проверки наличия передаваемого mac адреса в сети роутера
def valid_mac(text,mac):
     # text содержит в себе список роутеров сети
     test_mac = my_mac(text)
     index = text.find(test_mac)
     # возвращает ложь либо истину
     if index < 0:
         return False
     else:
         return True
