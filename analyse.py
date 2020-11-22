import numpy as np
import json

file_name = 'btc_usd.json'

# Дескриптор для вывода счёта в долларах
class Value:
    def __set__(self, obj, value):
        obj.b += value

    def __get__(self, obj, obj_type):
        return obj.b * obj.close[-1] + obj.dv


class FinAns:
    bv = Value()

    def __init__(self, dollar_amount):
        self.dv = dollar_amount
        self.wav = None
        self.sav = None
        self.close = None
        self.b = 0

    # Получение взвешенной средней, скользящей средней и цены закрытия
    def get_av(self, sva_value):
        with open(file_name, 'r', encoding='utf-8') as f:
            fdata = json.loads(f.read())
        wav = np.array([x['weightedAverage'] for x in fdata])
        close = np.array([x['close'] for x in fdata])
        lst = []
        s = wav[0]
        for i in range(len(wav)):
            if i % sva_value == 0:
                s = wav[i]
                lst.append(s)
            else:
                lst.append((wav[i] + s) / 2)
        sav = np.array(lst)
        self.wav = wav
        self.sav = sav
        self.close = close

    """
    Процедура торгов. Проводиться по прицнипу: продажа, если 
    скользящее среднее пересекает взвешенное среднее сверху вних;
    покупка, если наоборот.
    Можно рассмотреть три варианта работы с капиталом:
    а) Покупка конкретного количества акций при ограниченном числе долларов
    б) Покупка любого количества акций при ограниченном числе долларов
    в) Покупка конкретного количества акций при неограниченном числе долларов 
    В данном случае рассмотрен вариант а
    """
    def analyse(self, num_of_bit):
        sup = True
        for i in range(len(self.wav)):
            if self.wav[i] > self.sav[i]:
                if sup:
                    if self.dv > num_of_bit*(self.close[i]):
                        self.dv -= num_of_bit*(self.close[i])
                        self.b += num_of_bit
                    else:
                        self.b += self.close[i] / self.dv
                        self.dv = 0
                sup = False

            elif self.wav[i] < self.sav[i]:
                if not sup and self.b > 0:
                    if self.b < num_of_bit:
                        self.dv += self.b * (self.close[i])
                        self.b = 0
                    else:
                        self.b -= num_of_bit
                        self.dv += num_of_bit * (self.close[i])
                    sup = True
                else:
                    continue


dollar = 1000
a = FinAns(dollar)
a.get_av(10)
a.analyse(1)
print(f'Заработано:{(a.bv - dollar):.2f}\nВ процентах:{int(abs(dollar - a.bv) * 100/dollar)}')
