import requests
import datetime
from datetime import date, time, datetime
from bs4 import BeautifulSoup
import os.path
from termcolor import colored
import sys

def loadPetTable() -> list[dict]:
    pets = list()
    print('Загружаем таблицу питомцев')
    r = requests.get('https://wiki.godville.net/%D0%9F%D0%B8%D1%82%D0%BE%D0%BC%D0%B5%D1%86')
    if(r.status_code != 200):
        print("Не вышло :(")
        return
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find_all('table')[2].find('tbody')
    rows = table.find_all('tr')
     
    for row in rows[3:]:
        cells = row.find_all('td')
        pets.append({'name': cells[0].text, 
                     'level_low': cells[1].next.next_sibling.split('–')[0], #это не минус кстати
                     'level_high': cells[1].next.next_sibling.split('–')[1],
                     'level_low_ark': cells[2].next.next_sibling.split('–')[0],
                     'level_high_ark': cells[2].next.next_sibling.split('–')[1],})
    return pets
    
def writeTableToFile(table, filename):
    with open(filename, 'w') as file:
        file.write(date.today().strftime('%Y-%m-%d') + '\n')
        for pet in table:
            file.write(f'{pet["name"]},{pet["level_low"]},{pet["level_high"]},{pet["level_low_ark"]},{pet["level_high_ark"]}\n')
    
def loadPetTableCached() -> list[dict]:
    if os.path.exists('pettable.txt'):
        with open('pettable.txt', 'r') as file:
            line = file.readline()[:-1]
            save_date = datetime.strptime(line, '%Y-%m-%d').date()
            if save_date == date.today():
                lines = file.readlines()
                pets = list()
                for line in lines:
                    splitted = line.split(',')
                    pets.append({'name': splitted[0],
                                 'level_low': splitted[1],
                                 'level_high': splitted[2],
                                 'level_low_ark': splitted[3],
                                 'level_high_ark': splitted[4][:-1],}) #обрезаем последний \n
                return pets
                                
    table = loadPetTable()
    writeTableToFile(table, 'pettable.txt')
    return table

    
if __name__ == "__main__":
    print('Введите имя героя')
    hero_name = str(input())
    r = requests.get(f'http://godville.net/gods/api/{hero_name}') 
    if r.status_code != 200:
        print("Герой не найден")
        sys.exit()
    data = r.json()
    name = data["name"]
    lvl = int(data["level"])
    ark = False
    if data["ark_completed_at"] != None:
        ark = True

    print(f'Имя: {name}, {lvl} lvl, ковчег:', 'есть' if ark else 'нет')

    print("")
    print("Таблица питомцев")
    print("{:<25} {:<25} {:<25}".format('Название', 'диапазон б.к.', 'диапазон с к.'))

    table = loadPetTableCached()
    for pet in table:
        if ark:
            avaliable = False
            if int(pet["level_low_ark"]) < lvl < int(pet["level_high_ark"]):
                avaliable = True
            print("{:<25} {:<25} {:<25}".format(f'{pet["name"]}', f'{pet["level_low"]}-{pet["level_high"]}', colored(f'{pet["level_low_ark"]}-{pet["level_high_ark"]}', 'green') if avaliable else colored(f'{pet["level_low_ark"]}-{pet["level_high_ark"]}', 'red')))
        else:
            avaliable = False
            if int(pet["level_low"]) < lvl < int(pet["level_high"]):
                avaliable = True
            print("{:<25} {:<25} {:<25}".format(f'{pet["name"]}', colored(f'{pet["level_low"]}-{pet["level_high"]}', 'green') if avaliable else colored(f'{pet["level_low"]}-{pet["level_high"]}', 'red'), f'{pet["level_low_ark"]}-{pet["level_high_ark"]}'))