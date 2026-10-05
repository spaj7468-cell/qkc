# -*- coding: utf-8 -*-
"""
OuRi — генератор банка вопросов.
Строгая разбивка: класс (1-11) -> предмет -> четверть -> вопросы.
"""
import random, json, os, sys, re

MIN_PER_QUARTER = 42
TARGET_PER_QUARTER = 48
MAX_PASSES = 40


class Item:
    __slots__ = ("text", "typ", "options", "answer", "exp", "topic", "q", "unit")

    def __init__(self, text, typ="choice", options=None, answer=None, exp="", topic="", q=None, unit=None):
        self.text = text
        self.typ = typ
        self.options = options
        self.answer = answer
        self.exp = exp
        self.topic = topic
        self.q = q
        self.unit = unit


def build_choice(text, correct, wrongs, exp="", topic="", q=None, shuffle=True, unit=None):
    wrongs = [w for w in wrongs if str(w) != "" and str(w) != str(correct)]
    seen, ws = set(), []
    for w in wrongs:
        k = str(w)
        if k not in seen:
            seen.add(k)
            ws.append(w)
    opts = [str(correct)] + [str(w) for w in ws[:3]]
    if shuffle:
        random.shuffle(opts)
    return Item(text, "choice", opts, str(correct), exp, topic, q, unit)


def build_input(text, answer, exp="", topic="", q=None, unit=None):
    return Item(text, "input", None, str(answer), exp, topic, q, unit)


def build_tf(text, answer, exp="", topic="", q=None):
    return Item(text, "tf", ["Верно", "Неверно"], str(answer), exp, topic, q)


def uniq(items):
    seen, out = set(), []
    for it in items:
        key = (it.text, it.typ, str(it.answer))
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


# ============================================================ МАТЕМАТИКА (алгебра/геометрия)
def gen_math(grade, seed=0):
    random.seed(seed)
    P = []
    A = P.append

    def num(n):
        return str(n).replace(".", ",")

    # ---------- 1 класс ----------
    if grade == 1:
        for _ in range(30):
            a, b = random.randint(1, 9), random.randint(1, 10)
            if a + b > 20:
                b = 20 - a
            A(build_input(f"Вычисли: {a} + {b} = ?", a + b, f"{a} + {b} = {a+b}. Считаем по единицам или десятками.", "Сложение и вычитание", [1, 2]))
            A(build_input(f"Вычисли: {a+b} − {b} = ?", a, f"{a+b} − {b} = {a}.", "Сложение и вычитание", [3, 4]))
        for _ in range(14):
            a = random.randint(1, 18); b = random.randint(1, 18)
            A(build_choice(f"Сравни: {a} ☐ {b}. Какой знак нужно поставить?", ">" if a > b else ("<" if a < b else "="),
                           [">", "<", "=", "≠"], f"Чем правее число на числовом луче, тем оно больше: {a} {'>' if a>b else '<'} {b}.", "Сравнение чисел", [1, 2]))
        for _ in range(10):
            n = random.randint(11, 19)
            A(build_choice(f"Сколько десятков и единиц в числе {n}?", f"1 десяток {n-10} единиц",
                           [f"1 десяток {n-10} единиц", f"{n-10} десятков 1 единица", f"{n} десятков", f"1 десяток {10-n%10 if n%10 else 10} единиц"],
                           f"{n} = 10 + {n-10}, значит 1 десяток и {n-10} единиц.", "Нумерация", [1, 2]))
        for _ in range(10):
            n = random.randint(2, 18)
            A(build_choice(f"Какое число идёт при счёте сразу за числом {n}?", n + 1, [n + 1, n - 1, n + 2, n + 10],
                           f"За числом {n} следует {n+1}.", "Нумерация", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 9); b = random.randint(1, 10 - a)
            A(build_choice(f"У Ани {a + b} конфет. {b} она отдала брату. Сколько конфет осталось?", a,
                           [a, b, a + b, a + b + 1], f"{a+b} − {b} = {a}.", "Задачи", [3, 4]))
        for _ in range(12):
            a = random.randint(1, 8); b = random.randint(1, 8)
            A(build_choice(f"В одной коробке {a} карандашей, в другой {b}. Сколько всего карандашей?", a + b,
                           [a + b, a * b, abs(a - b), a + b + 2], f"{a} + {b} = {a+b}.", "Задачи", [1, 2]))
        for _ in range(10):
            side = random.randint(2, 9)
            A(build_choice(f"У квадрата сторона {side} см. Чему равен его периметр?", f"{side*4} см",
                           [f"{side*4} см", f"{side*2} см", f"{side*side} см", f"{side+4} см"],
                           f"Периметр квадрата P = 4 · a = 4 · {side} = {side*4} см.", "Геометрия", [3, 4]))
        for _ in range(8):
            items = [("яблоко", "яблок"), ("груша", "груш"), ("кукла", "кукол"), ("машина", "машин")][random.randint(0, 3)]
            n = random.randint(3, 9)
            A(build_choice(f"На столе {n} {items[1]}, а в вазе на 2 больше. Сколько в вазе?", n + 2,
                           [n + 2, n - 2, n * 2, n + 3], f"{n} + 2 = {n+2}. «На 2 больше» — значит прибавить 2.", "Задачи", [3, 4]))
        for _ in range(8):
            a = random.randint(10, 19); b = random.randint(1, 9)
            A(build_choice(f"Вычисли: {a} − {b}", a - b, [a - b, a + b, a - b + 1, a - b - 1], f"{a} − {b} = {a-b}.", "Сложение и вычитание", [3, 4]))
        for _ in range(8):
            a = random.randint(1, 9)
            A(build_choice(f"Какое число на {a} больше, чем 10?", 10 + a, [10 + a, 10 - a if 10 - a > 0 else 10 + a + 1, a, 10 * a],
                           f"10 + {a} = {10+a}.", "Сложение и вычитание", [1, 2]))
        return P

    # ---------- 2 класс ----------
    if grade == 2:
        for _ in range(26):
            a = random.randint(10, 80); b = random.randint(5, 19)
            if a + b > 100:
                b = 100 - a
            A(build_input(f"Вычисли: {a} + {b}", a + b, f"{a} + {b} = {a+b}.", "Сложение и вычитание", [1, 2]))
            A(build_input(f"Вычисли: {a+b} − {b}", a, f"{a+b} − {b} = {a}.", "Сложение и вычитание", [1, 2]))
        for _ in range(18):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_input(f"Вычисли: {a} · {b}", a * b, f"{a} · {b} = {a*b} (таблица умножения).", "Таблица умножения", [3, 4]))
            A(build_input(f"Вычисли: {a*b} : {a}", b, f"{a*b} : {a} = {b}, так как {a} · {b} = {a*b}.", "Таблица умножения", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_choice(f"Во сколько раз {a*b} больше, чем {b}?", a, [a, b, a * b, a + b], f"{a*b} : {b} = {a}. «Во сколько раз больше» — значит разделить.", "Таблица умножения", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 9); n = random.randint(2, 6)
            A(build_choice(f"Одна тетрадь стоит {a} руб. Сколько стоят {n} такие тетради?", a * n, [a * n, a + n, a * n + a, n], f"{a} · {n} = {a*n} руб.", "Задачи", [3, 4]))
        for _ in range(10):
            n = random.randint(2, 9)
            A(build_choice(f"Найди 1/2 от числа {n*2}.", n, [n, n * 2, 2, n * 4], f"{n*2} : 2 = {n}.", "Доли", [3, 4]))
        for _ in range(10):
            v = random.choice([(1, "м", 100, "см"), (1, "дм", 10, "см"), (1, "см", 10, "мм"), (1, "м", 10, "дм")])
            n = random.randint(2, 9)
            A(build_choice(f"Сколько сантиметров в {n} {v[0] if v[0]!=1 else ''}{'метр' if v[1]=='м' else ('дециметр' if v[1]=='дм' else 'сантимметр')}"
                           f"{'ах' if n>4 else ('е' if n>1 else '')}?" if v[1] != "см" else f"Сколько миллиметров в {n} см?",
                           n * v[2], [n * v[2], n * v[2] + v[2], n, v[2]], f"1 {v[1]} = {v[2]} {v[3]}, значит {n} {v[1]} = {n*v[2]} {v[3]}.", "Величины", [1, 2]))
        for _ in range(8):
            A(build_choice("Сколько минут в одном часе?", "60", ["60", "100", "30", "24"], "1 ч = 60 мин.", "Величины", [1, 2]))
        for _ in range(8):
            a, b = random.randint(3, 12), random.randint(3, 12)
            A(build_choice(f"Прямоугольник со сторонами {a} см и {b} см. Найди периметр.", f"{2*(a+b)} см",
                           [f"{2*(a+b)} см", f"{a*b} см", f"{a+b} см", f"{2*(a+b)+1} см"], f"P = 2·(a+b) = 2·({a}+{b}) = {2*(a+b)} см.", "Геометрия", [3, 4]))
        for _ in range(8):
            a, b = random.randint(2, 9), random.randint(2, 9)
            A(build_choice(f"Найди площадь прямоугольника со сторонами {a} см и {b} см.", f"{a*b} см²", [f"{a*b} см²", f"{2*(a+b)} см²", f"{a+b} см²", f"{a*b*2} см²"],
                           f"S = a · b = {a} · {b} = {a*b} см².", "Геометрия", [3, 4]))
        for _ in range(10):
            a = random.randint(21, 89); b = random.randint(11, 60)
            A(build_choice(f"Сравни: {a} ☐ {b}", ">" if a > b else "<", [">", "<", "=", "≠"], f"{a} {'больше' if a>b else 'меньше'} {b}.", "Сравнение чисел", [1, 2]))
        for _ in range(8):
            n = random.randint(30, 90)
            A(build_choice(f"Какое число на 10 меньше, чем {n}?", n - 10, [n - 10, n + 10, n - 1, n / 10], f"{n} − 10 = {n-10}.", "Нумерация", [1, 2]))
        for _ in range(8):
            x = random.randint(2, 9); s = random.randint(10, 40)
            A(build_input(f"Реши уравнение: x + {x} = {s + x}. x = ?", s, f"x = {s+x} − {x} = {s}.", "Уравнения", [3, 4]))
        return P

    # ---------- 3 класс ----------
    if grade == 3:
        for _ in range(22):
            a = random.randint(100, 800); b = random.randint(20, 199)
            if a + b > 1000:
                b = 1000 - a
            A(build_input(f"Вычисли: {a} + {b}", a + b, f"{a} + {b} = {a+b}.", "Сложение и вычитание", [1, 2]))
            A(build_input(f"Вычисли: {a+b} − {b}", a, f"{a+b} − {b} = {a}.", "Сложение и вычитание", [1, 2]))
        for _ in range(18):
            a = random.randint(11, 99); b = random.randint(2, 9)
            A(build_input(f"Вычисли: {a} · {b}", a * b, f"{a} · {b} = {a*b}. Умножаем поразрядно.", "Умножение и деление", [1, 2]))
            A(build_input(f"Вычисли: {a*b} : {a}", b, f"{a*b} : {a} = {b}.", "Умножение и деление", [1, 2]))
        for _ in range(14):
            a = random.randint(2, 12); b = random.randint(2, 12)
            A(build_choice(f"Найди значение выражения: {a} · {b} + {a}", a * b + a, [a * b + a, a * (b + 1) + 1, a * b - a, a * b + b],
                           f"Сначала умножение: {a}·{b} = {a*b}, затем прибавляем {a}: {a*b}+{a} = {a*b+a}.", "Порядок действий", [3, 4]))
        for _ in range(12):
            n = random.randint(2, 9); k = random.randint(2, 9)
            A(build_choice(f"Найди 1/{n} от числа {n*k}.", k, [k, n * k, n, n * k * n], f"{n*k} : {n} = {k}.", "Доли", [3, 4]))
        for _ in range(12):
            v = random.randint(40, 90); t = random.randint(2, 5)
            A(build_choice(f"Поезд едет со скоростью {v} км/ч. Какое расстояние он проедет за {t} ч?", f"{v*t} км",
                           [f"{v*t} км", f"{v//t} км", f"{v+t} км", f"{v*t*2} км"], f"S = v · t = {v} · {t} = {v*t} км.", "Задачи на движение", [3, 4]))
        for _ in range(10):
            t = random.choice([2, 3, 4, 5]); s = t * random.randint(10, 60)
            A(build_input(f"Расстояние {s} км прошли за {t} ч. Какова скорость (км/ч)?", s // t, f"v = S : t = {s} : {t} = {s//t} км/ч.", "Задачи на движение", [3, 4]))
        for _ in range(10):
            a, b = random.randint(3, 15), random.randint(3, 15)
            A(build_choice(f"Периметр прямоугольника со сторонами {a} см и {b} см равен:", f"{2*(a+b)} см", [f"{2*(a+b)} см", f"{a*b} см", f"{a+b} см", f"{4*a} см"],
                           f"P = 2·({a}+{b}) = {2*(a+b)} см.", "Геометрия", [3, 4]))
        for _ in range(10):
            a, b = random.randint(3, 14), random.randint(3, 14)
            A(build_choice(f"Площадь прямоугольника {a} см × {b} см равна:", f"{a*b} см²", [f"{a*b} см²", f"{2*(a+b)} см²", f"{a+b} см²", f"{a*b//2} см²"],
                           f"S = {a} · {b} = {a*b} см².", "Геометрия", [3, 4]))
        for _ in range(10):
            a = random.randint(2, 20)
            A(build_choice(f"Площадь квадрата со стороной {a} см равна:", f"{a*a} см²", [f"{a*a} см²", f"{4*a} см²", f"{2*a} см²", f"{a*a*2} см²"],
                           f"S = a² = {a}² = {a*a} см².", "Геометрия", [3, 4]))
        for _ in range(10):
            kg = random.randint(2, 9)
            A(build_choice(f"Сколько килограммов в {kg} т?", kg * 1000, [kg * 1000, kg * 100, kg * 10, kg], f"1 т = 1000 кг, значит {kg} т = {kg*1000} кг.", "Величины", [1, 2]))
        for _ in range(8):
            A(build_choice("Сколько месяцев в трёх годах?", "36", ["36", "30", "12", "48"], "1 год = 12 месяцев, 3 · 12 = 36.", "Величины", [1, 2]))
        for _ in range(12):
            x = random.randint(3, 40); k = random.randint(2, 9)
            A(build_input(f"Реши уравнение: x · {k} = {x*k}. x = ?", x, f"x = {x*k} : {k} = {x}.", "Уравнения", [3, 4]))
            A(build_input(f"Реши уравнение: x : {k} = {x}. x = ?", x * k, f"x = {x} · {k} = {x*k}.", "Уравнения", [3, 4]))
        for _ in range(10):
            a = random.randint(2, 6); b = random.randint(2, 6); c = random.randint(2, 9)
            A(build_choice(f"Вычисли: ({a} + {b}) · {c}", (a + b) * c, [(a + b) * c, a + b * c, a * b + c, (a + b) * c + 1],
                           f"Сначала действие в скобках: {a}+{b} = {a+b}, затем {a+b}·{c} = {(a+b)*c}.", "Порядок действий", [1, 2]))
        return P

    # ---------- 4 класс ----------
    if grade == 4:
        for _ in range(18):
            a = random.randint(1000, 8000); b = random.randint(100, 1999)
            A(build_input(f"Вычисли: {a} + {b}", a + b, f"{a} + {b} = {a+b}.", "Сложение и вычитание", [1, 2]))
            A(build_input(f"Вычисли: {a+b} − {b}", a, f"{a+b} − {b} = {a}.", "Сложение и вычитание", [1, 2]))
        for _ in range(16):
            a = random.randint(12, 250); b = random.randint(3, 9)
            A(build_input(f"Вычисли: {a} · {b}", a * b, f"{a} · {b} = {a*b}.", "Умножение и деление", [1, 2]))
            A(build_input(f"Вычисли: {a*b} : {a}", b, f"{a*b} : {a} = {b}.", "Умножение и деление", [1, 2]))
        for _ in range(14):
            a = random.randint(2, 9); b = random.randint(2, 9); c = random.randint(2, 9)
            A(build_choice(f"Найди значение: {a} · {b} + {c} · {b}", (a + c) * b, [(a + c) * b, a * b + c, (a + c) * b + b, a * (b + c)],
                           f"{a}·{b} = {a*b}, {c}·{b} = {c*b}, сумма = {(a+c)*b}. (Распределительное свойство: ({a}+{c})·{b}.)", "Порядок действий", [3, 4]))
        for _ in range(14):
            n, d = random.randint(1, 7), random.randint(2, 9)
            if n >= d:
                n = d - 1
            A(build_choice(f"Какая дробь больше: {n}/{d} или 1?", f"{n}/{d} меньше 1" if n < d else f"{n}/{d} больше 1",
                           [f"{n}/{d} меньше 1", f"{n}/{d} больше 1", "дроби равны", "сравнить нельзя"],
                           f"Правильная дробь (числитель меньше знаменателя) всегда меньше 1.", "Дроби", [3, 4]))
        for _ in range(14):
            d = random.randint(2, 10); n1 = random.randint(1, d - 1); n2 = random.randint(1, d - n1)
            A(build_choice(f"Вычисли: {n1}/{d} + {n2}/{d}", f"{n1+n2}/{d}", [f"{n1+n2}/{d}", f"{n1+n2}/{2*d}", f"{n1*n2}/{d}", f"{n1+n2+1}/{d}"],
                           f"При одинаковых знаменателях складываем числители: ({n1}+{n2})/{d} = {n1+n2}/{d}.", "Дроби", [3, 4]))
        for _ in range(12):
            whole = random.randint(2, 20) * 10
            A(build_choice(f"Найди 1/10 от числа {whole}.", whole // 10, [whole // 10, whole * 10, whole // 2, whole], f"{whole} : 10 = {whole//10}.", "Дроби", [1, 2]))
        for _ in range(12):
            v1 = random.randint(40, 90); v2 = random.randint(30, 80); t = random.randint(2, 5)
            A(build_choice(f"Два поезда выехали навстречу друг другу со скоростями {v1} км/ч и {v2} км/ч. Какое расстояние будет между ними через {t} ч, если изначально оно равно 0?",
                           f"{(v1+v2)*t} км", [f"{(v1+v2)*t} км", f"{(v1-v2)*t} км", f"{v1*v2*t} км", f"{v1+v2+t} км"],
                           f"Скорость сближения {v1}+{v2} = {v1+v2} км/ч; за {t} ч: {(v1+v2)}·{t} = {(v1+v2)*t} км.", "Задачи на движение", [3, 4]))
        for _ in range(12):
            v = random.randint(30, 90); t = random.randint(2, 6); s = v * t
            A(build_input(f"Расстояние {s} км автомобиль проехал за {t} ч. Какова его скорость (км/ч)?", v, f"v = S : t = {s} : {t} = {v} км/ч.", "Задачи на движение", [3, 4]))
        for _ in range(10):
            a, b = random.randint(4, 25), random.randint(4, 25)
            A(build_choice(f"Площадь прямоугольника {a} м × {b} м равна:", f"{a*b} м²", [f"{a*b} м²", f"{2*(a+b)} м²", f"{a+b} м²", f"{a*b*10} м²"], f"S = {a}·{b} = {a*b} м².", "Геометрия", [1, 2]))
        for _ in range(10):
            a = random.randint(3, 12); h = random.randint(3, 12)
            A(build_choice(f"Найди площадь треугольника с основанием {a*2} см и высотой {h} см.", f"{a*h*2//2*2//2} см²" if False else f"{(a*2*h)//2} см²",
                           [f"{(a*2*h)//2} см²", f"{a*2*h} см²", f"{(a*2+h)} см²", f"{(a*2*h)//2+1} см²"], f"S = (a·h)/2 = ({a*2}·{h})/2 = {(a*2*h)//2} см².", "Геометрия", [3, 4]))
        for _ in range(10):
            n = random.choice([100, 1000, 10])
            v = random.randint(3, 97)
            A(build_choice(f"Вычисли: {v} · {n}", v * n, [v * n, v * n // 10, v + n, v * n * 10], f"При умножении на {n} приписываем нужное число нулей: {v*n}.", "Умножение и деление", [1, 2]))
        for _ in range(12):
            x = random.randint(4, 60); k = random.randint(3, 12)
            A(build_input(f"Реши уравнение: {k} · x = {x*k}. x = ?", x, f"x = {x*k} : {k} = {x}.", "Уравнения", [3, 4]))
        for _ in range(10):
            a = random.randint(1, 9); b = random.randint(1, 9)
            A(build_choice(f"Представь число {a*10+b} в виде суммы разрядных слагаемых.", f"{a*10} + {b}", [f"{a*10} + {b}", f"{a} + {b}", f"{a*100} + {b}", f"{b*10} + {a}"],
                           f"{a*10+b} = {a} дес. + {b} ед. = {a*10} + {b}.", "Нумерация", [1, 2]))
        for _ in range(10):
            n = random.randint(1000, 99999)
            A(build_choice(f"Округли число {n} до сотен.", str(round(n, -2)).replace(".0", ""),
                           [str(round(n, -2)), str(round(n, -1)), str(round(n, -3)), str(n + 100)],
                           f"Смотрим на десятки: {n} ≈ {round(n,-2)}.", "Округление", [1, 2]))
        return P

    # ---------- 5 класс ----------
    if grade == 5:
        for _ in range(18):
            k = random.randint(2, 9); a = random.randint(1, 9); b = random.randint(1, 9)
            A(build_choice(f"Сократи дробь {a*k}/{b*k}", f"{a}/{b}", [f"{a}/{b}", f"{a*k}/{b}", f"{a}/{b*k}", f"{a+1}/{b}"],
                           f"Делим числитель и знаменатель на {k}: {a*k}/{b*k} = {a}/{b}.", "Обыкновенные дроби", [1, 2]))
        for _ in range(18):
            d1 = random.randint(2, 9); d2 = d1 * random.choice([2, 3])
            n = random.randint(1, d1 - 1)
            A(build_choice(f"Приведи дробь {n}/{d1} к знаменателю {d2}. Какой будет числитель?", n * (d2 // d1),
                           [n * (d2 // d1), n, n + d2 // d1, d2 // d1], f"Дополнительный множитель {d2}:{d1} = {d2//d1}; числитель {n}·{d2//d1} = {n*(d2//d1)}.", "Обыкновенные дроби", [1, 2]))
        for _ in range(16):
            a = random.randint(1, 9); b = random.randint(1, 9); d = random.randint(10, 20)
            A(build_choice(f"Вычисли: {a}/{d} + {b}/{d}", f"{a+b}/{d}", [f"{a+b}/{d}", f"{a+b}/{2*d}", f"{a*b}/{d}", f"{a+b}/{d+1}"],
                           f"Знаменатели равны — складываем числители.", "Обыкновенные дроби", [3, 4]))
        for _ in range(14):
            whole = random.randint(2, 20); pct = random.choice([10, 20, 25, 50])
            A(build_choice(f"Найди {pct}% от числа {whole*10}.", whole * 10 * pct // 100, [whole * 10 * pct // 100, whole * 10 // pct, whole * pct, whole * 10 + pct],
                           f"{whole*10} · {pct}/100 = {whole*10*pct//100}.", "Проценты", [3, 4]))
        for _ in range(14):
            pct = random.choice([10, 25, 50, 5]); v = (100 // pct) * random.randint(1, 20)
            A(build_input(f"Товар стоит {v} руб. Скидка {pct}%. Сколько рублей составляет скидка?", v * pct // 100, f"Скидка = {v} · {pct}/100 = {v*pct//100} руб.", "Проценты", [3, 4]))
        for _ in range(12):
            a = random.randint(3, 20); b = random.randint(3, 20)
            nod = 1
            for i in range(min(a, b), 0, -1):
                if a % i == 0 and b % i == 0:
                    nod = i; break
            A(build_choice(f"Найди НОД({a}, {b}).", nod, [nod, a * b, max(a, b), nod + 1], f"Наибольший общий делитель {a} и {b} равен {nod}.", "Делимость", [1, 2]))
        for _ in range(12):
            a = random.randint(2, 12); b = random.randint(2, 12)
            nok = a * b // (lambda x, y: [i for i in range(min(x, y), 0, -1) if x % i == 0 and y % i == 0][0])(a, b)
            A(build_choice(f"Найди НОК({a}, {b}).", nok, [nok, a * b, max(a, b), min(a, b)], f"Наименьшее общее кратное {a} и {b} равно {nok}.", "Делимость", [1, 2]))
        for _ in range(12):
            n = random.randint(101, 999)
            A(build_choice(f"Делится ли число {n} на 3 без остатка?", "Да" if n % 3 == 0 else "Нет", ["Да", "Нет", "Делится на 9", "Не определить"],
                           f"Сумма цифр: {'+'.join(list(str(n)))} = {sum(int(c) for c in str(n))}. Если она делится на 3, то и число делится.", "Делимость", [1, 2]))
        for _ in range(12):
            n = random.randint(10, 200)
            A(build_choice(f"Число {n} — простое или составное?", "Простое" if all(n % i for i in range(2, int(n**0.5) + 1)) and n > 1 else "Составное",
                           ["Простое", "Составное", "Ни то ни другое", "Чётное простое"], "Простое число делится только на 1 и на само себя.", "Делимость", [3, 4]))
        for _ in range(14):
            x = random.randint(2, 40); a = random.randint(2, 60)
            A(build_input(f"Реши уравнение: x + {a} = {x + a}. x = ?", x, f"x = {x+a} − {a} = {x}.", "Уравнения", [1, 2]))
            A(build_input(f"Реши уравнение: {a} · x = {a*x}. x = ?", x, f"x = {a*x} : {a} = {x}.", "Уравнения", [1, 2]))
        for _ in range(12):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_choice(f"Найди площадь прямоугольника {a} см × {b} см.", f"{a*b} см²", [f"{a*b} см²", f"{2*(a+b)} см²", f"{a+b} см²", f"{a*b*2} см²"], f"S = a·b = {a*b} см².", "Геометрия", [3, 4]))
        for _ in range(10):
            r = random.randint(2, 20)
            A(build_choice(f"Найди диаметр окружности, если её радиус {r} см.", f"{2*r} см", [f"{2*r} см", f"{r} см", f"{r+2} см", f"{r*3} см"], "d = 2r.", "Геометрия", [3, 4]))
        for _ in range(10):
            v = random.randint(3, 12)
            A(build_choice(f"Найди объём куба с ребром {v} см.", f"{v**3} см³", [f"{v**3} см³", f"{6*v*v} см³", f"{v*3} см³", f"{4*v**3} см³"], f"V = a³ = {v}³ = {v**3} см³.", "Геометрия", [3, 4]))
        for _ in range(10):
            a = random.randint(2, 12); b = random.randint(2, 12); c = random.randint(2, 12)
            A(build_choice(f"Объём прямоугольного параллелепипеда {a}×{b}×{c} см равен:", f"{a*b*c} см³", [f"{a*b*c} см³", f"{a+b+c} см³", f"{2*(a*b+b*c+a*c)} см³", f"{a*b*c*2} см³"], f"V = a·b·c = {a*b*c} см³.", "Геометрия", [3, 4]))
        for _ in range(10):
            x = random.randint(-9, 9); y = random.randint(-9, 9)
            A(build_choice(f"Вычисли: ({x}) + ({y})", x + y, [x + y, abs(x) + abs(y), x - y, -(x + y)], "Сложение чисел с разными знаками: модуль большего минус модуль меньшего, знак большего.", "Отрицательные числа", [3, 4]))
        for _ in range(10):
            n = random.randint(2, 12); k = random.choice([2, 3])
            A(build_choice(f"Возведи в степень: {n}^{k}", n ** k, [n ** k, n * k, n ** (k + 1), n ** k + k], f"{n}^{k} = {'·'.join([str(n)]*k)} = {n**k}.", "Степень", [1, 2]))
        for _ in range(10):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_choice(f"Отношение {a*3} к {b*3} равно:", f"{a}:{b}", [f"{a}:{b}", f"{a*3}:{b}", f"{a}:{b*3}", f"{a*b}:3"], f"Сокращаем на 3: {a*3}:{b*3} = {a}:{b}.", "Отношения", [1, 2]))
        return P

    # ---------- 6 класс ----------
    if grade == 6:
        for _ in range(16):
            a = random.randint(1, 9); b = random.randint(1, 9); c = random.randint(1, 9); d = random.randint(1, 9)
            A(build_choice(f"Вычисли: {a}/{b} · {c}/{d}", f"{a*c}/{b*d}", [f"{a*c}/{b*d}", f"{a+c}/{b+d}", f"{a*c}/{b+d}", f"{a*d}/{b*c}"],
                           f"Умножение дробей: числитель на числитель, знаменатель на знаменатель. {a*c}/{b*d}" + (" (дробь можно сократить)." if (b * d) % (a * c) == 0 or True else ""), "Дроби", [1, 2]))
        for _ in range(16):
            a = random.randint(2, 8); b = random.randint(2, 8); c = random.randint(2, 8); d = random.randint(2, 8)
            numr, denr = a * d, b * c
            g = 1
            for i in range(min(numr, denr), 0, -1):
                if numr % i == 0 and denr % i == 0:
                    g = i; break
            A(build_choice(f"Вычисли: {a}/{b} : {c}/{d}", f"{numr//g}/{denr//g}" if g != denr else f"{numr//g}/{denr//g}",
                           [f"{numr//g}/{denr//g}" if denr // g != 1 else str(numr // g), f"{a*c}/{b*d}", f"{a+d}/{b+c}", f"{numr}/{denr}"],
                           f"{a}/{b} : {c}/{d} = {a}/{b} · {d}/{c} = {numr}/{denr} = {numr//g}/{denr//g}.", "Дроби", [1, 2]))
        for _ in range(14):
            pct = random.choice([5, 10, 20, 25, 50]); whole = (100 // pct) * random.randint(1, 10)
            A(build_input(f"Найди {pct}% от {whole}.", whole * pct // 100, f"{whole} · {pct}/100 = {whole*pct//100}.", "Проценты", [1, 2]))
        for _ in range(14):
            part = random.randint(2, 40); pct = random.choice([10, 20, 25, 50])
            whole = part * 100 // pct
            A(build_choice(f"{part} — это {pct}% некоторого числа. Найди это число.", whole, [whole, part * pct // 100, part + pct, whole // 2],
                           f"Число = {part} : {pct}/100 = {whole}.", "Проценты", [1, 2]))
        for _ in range(14):
            a, b, c = random.randint(2, 9), random.randint(2, 9), random.randint(2, 20)
            A(build_choice(f"Пропорция {a}/{b} = x/{b*c}. Найди x.", a * c, [a * c, a * b, c, a + c], f"x = {a} · {b*c} : {b} = {a*c}.", "Пропорции", [3, 4]))
        for _ in range(14):
            x = random.randint(-20, 20); a = random.randint(2, 9); b = random.randint(2, 40)
            A(build_input(f"Реши уравнение: {a}·x − {b} = {a*x - b}. x = ?", x, f"{a}·x = {a*x-b} + {b} = {a*x}; x = {a*x} : {a} = {x}.", "Уравнения", [3, 4]))
        for _ in range(12):
            x = random.randint(-15, 15)
            A(build_choice(f"Модуль числа |{x}| равен:", abs(x), [abs(x), x, -abs(x), x * x], "Модуль — расстояние от нуля, всегда неотрицателен.", "Отрицательные числа", [1, 2]))
        for _ in range(14):
            a = random.randint(-12, 12); b = random.randint(-12, 12)
            A(build_choice(f"Вычисли: ({a}) · ({b})", a * b, [a * b, abs(a * b), -abs(a * b) if a * b > 0 else abs(a * b), a + b],
                           "Минус на минус даёт плюс; плюс на минус — минус.", "Отрицательные числа", [1, 2]))
        for _ in range(12):
            a = random.randint(-15, 15); b = random.randint(-15, 15)
            A(build_choice(f"Вычисли: ({a}) − ({b})", a - b, [a - b, a + b, b - a, abs(a - b)], f"({a}) − ({b}) = {a} + ({-b}) = {a-b}.", "Отрицательные числа", [3, 4]))
        for _ in range(12):
            x1, y1 = random.randint(-6, 6), random.randint(-6, 6)
            A(build_choice(f"В какой четверти координатной плоскости находится точка ({x1}; {y1})?" if x1 and y1 else f"В какой четверти находится точка ({x1 or 3}; {y1 or 4})?",
                           ["I", "II", "III", "IV"][ (0 if (x1 or 3) > 0 and (y1 or 4) > 0 else 1 if (x1 or 3) < 0 and (y1 or 4) > 0 else 2 if (x1 or 3) < 0 and (y1 or 4) < 0 else 3) ],
                           ["I", "II", "III", "IV"], "I: x>0,y>0; II: x<0,y>0; III: x<0,y<0; IV: x>0,y<0.", "Координаты", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 12); n = random.choice([2, 3])
            A(build_choice(f"Вычисли: {a}^{n}", a ** n, [a ** n, a * n, a ** (n + 1), a ** n * 2], f"{a}^{n} = {a**n}.", "Степень", [1, 2]))
        for _ in range(10):
            r = random.randint(1, 15)
            A(build_choice(f"Длина окружности радиуса {r} см (π ≈ 3,14) равна примерно:", f"{round(2*3.14*r,2)} см".replace(".", ","),
                           [f"{round(2*3.14*r,2)} см".replace(".", ","), f"{round(3.14*r*r,2)} см".replace(".", ","), f"{2*r} см", f"{round(3.14*r,2)} см".replace(".", ",")],
                           f"C = 2πr = 2 · 3,14 · {r} = {round(2*3.14*r,2)} см.", "Геометрия", [3, 4]))
        for _ in range(10):
            n = random.randint(10, 999)
            A(build_choice(f"Округли {n} до десятков.", str(round(n, -1)), [str(round(n, -1)), str(round(n, -2)), str(n), str(round(n, -1) + 10)],
                           f"Смотрим на единицы: {n} ≈ {round(n,-1)}.", "Округление", [1, 2]))
        for _ in range(10):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_choice(f"Раскрой скобки: {a}·(x + {b})", f"{a}x + {a*b}", [f"{a}x + {a*b}", f"{a}x + {b}", f"{a+b}x", f"{a}x · {b}"],
                           f"Распределительное свойство: {a}·x + {a}·{b} = {a}x + {a*b}.", "Выражения", [3, 4]))
        return P

    # ---------- 7 класс: алгебра + геометрия ----------
    if grade == 7:
        for _ in range(14):
            a = random.randint(2, 9); b = random.randint(2, 9); n = random.choice([2, 3])
            A(build_choice(f"Упрости: (a^{n})^{n} · a^{b} при a ≠ 0" if False else f"Упрости: x^{a} · x^{b}", f"x^{a+b}",
                           [f"x^{a+b}", f"x^{a*b}", f"x^{a}+x^{b}", f"2x^{a+b}"], f"При умножении степеней с одинаковым основанием показатели складываются: {a}+{b} = {a+b}.", "Степень", [1, 2]))
        for _ in range(14):
            a = random.randint(4, 15); b = random.randint(1, a - 2)
            A(build_choice(f"Упрости: x^{a} : x^{b}", f"x^{a-b}", [f"x^{a-b}", f"x^{a+b}", f"x^{a//b if b else a}", f"x^{a*b}"], f"Показатели вычитаются: {a}−{b} = {a-b}.", "Степень", [1, 2]))
        for _ in range(14):
            a = random.randint(2, 12); b = random.randint(2, 12)
            A(build_choice(f"Раскрой скобки: (x + {a})(x + {b})", f"x² + {a+b}x + {a*b}", [f"x² + {a+b}x + {a*b}", f"x² + {a*b}x + {a+b}", f"x² + {a}x + {b}", f"x² − {a+b}x + {a*b}"],
                           f"По формуле (x+p)(x+q) = x² + (p+q)x + pq.", "Многочлены", [1, 2]))
        for _ in range(14):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_choice(f"Раскрой скобки: ({a}x + {b})² ", f"{a*a}x² + {2*a*b}x + {b*b}", [f"{a*a}x² + {2*a*b}x + {b*b}", f"{a*a}x² + {b*b}", f"{a}x² + {2*a*b}x + {b}x", f"{a*a}x² + {a*b}x + {b*b}"],
                           f"(p+q)² = p² + 2pq + q².", "Формулы сокращённого умножения", [3, 4]))
        for _ in range(14):
            a = random.randint(2, 12); b = random.randint(2, 12)
            A(build_choice(f"Разложи на множители: {a*a}x² − {b*b}", f"({a}x − {b})({a}x + {b})", [f"({a}x − {b})({a}x + {b})", f"({a}x − {b})²", f"{a*a}(x² − {b*b})", f"({a}x + {b})²"],
                           f"a² − b² = (a − b)(a + b).", "Формулы сокращённого умножения", [3, 4]))
        for _ in range(14):
            a = random.randint(2, 9); b = random.randint(2, 12); c = random.randint(1, 9)
            A(build_input(f"Реши уравнение: {a}x + {b} = {a*c + b}. x = ?", c, f"{a}x = {a*c+b} − {b} = {a*c}; x = {a*c} : {a} = {c}.", "Линейные уравнения", [1, 2]))
        for _ in range(12):
            k = random.choice([-3, -2, -1, 1, 2, 3]); b = random.randint(-6, 6)
            A(build_choice(f"Функция y = {k}x {'+' if b>=0 else '−'} {abs(b)}. Чему равен её свободный член (значение y при x = 0)?", b, [b, k, k + b, 0],
                           f"При x = 0: y = {b}. Это точка пересечения с осью Oy.", "Линейная функция", [3, 4]))
        for _ in range(12):
            k1 = random.choice([-2, -1, 2, 3]); k2 = random.choice([-2, -1, 2, 3])
            while k2 == k1:
                k2 = random.choice([-2, -1, 2, 3])
            A(build_choice(f"Пересекаются ли графики y = {k1}x + 1 и y = {k2}x + 5?", "Да, в одной точке", ["Да, в одной точке", "Нет, параллельны", "Совпадают", "Не определить"],
                           "Угловые коэффициенты различны — графики пересекаются в одной точке.", "Линейная функция", [3, 4]))
        for _ in range(12):
            a = random.randint(25, 90); b = random.randint(25, 150 - a)
            A(build_choice(f"Два угла треугольника равны {a}° и {b}°. Найди третий угол.", 180 - a - b, [180 - a - b, 180 - a, 90 - b, a + b],
                           f"Сумма углов треугольника 180°: 180 − {a} − {b} = {180-a-b}°.", "Геометрия: треугольник", [1, 2]))
        for _ in range(14):
            a = random.randint(20, 100); b = random.randint(20, 159 - a)
            A(build_choice(f"Два угла треугольника равны {a}° и {b}°. Найди третий угол.", 180 - a - b, [180 - a - b, 180 - a, 90 - b, a + b],
                           f"180° − {a}° − {b}° = {180-a-b}°.", "Геометрия: треугольник", [1, 2]))
        for _ in range(12):
            a = random.randint(30, 80)
            A(build_choice(f"Смежный с углом {a}° равен:", 180 - a, [180 - a, 90 - a, a, 360 - a], f"Смежные углы в сумме дают 180°: 180 − {a} = {180-a}°.", "Геометрия: углы", [3, 4]))
        for _ in range(12):
            a = random.randint(20, 70)
            A(build_choice(f"Вертикальный угол к углу {a}° равен:", a, [a, 180 - a, 90 - a, 2 * a], "Вертикальные углы равны.", "Геометрия: углы", [3, 4]))
        for _ in range(12):
            a = random.randint(3, 12); b = random.randint(3, 12)
            while a == b:
                b = random.randint(3, 12)
            A(build_choice(f"В равнобедренном треугольнике боковая сторона {a} см, основание {b} см. Найди периметр.", f"{2*a+b} см", [f"{2*a+b} см", f"{a+2*b} см", f"{a*b} см", f"{2*(a+b)} см"],
                           f"P = {a} + {a} + {b} = {2*a+b} см.", "Геометрия: треугольник", [3, 4]))
        for _ in range(12):
            x = random.randint(-9, 9); n = random.randint(2, 20)
            A(build_choice(f"Реши неравенство: x + {n} > {x + n}. Множество решений:", f"x > {x}", [f"x > {x}", f"x < {x}", f"x ≥ {x}", f"x ≠ {x}"],
                           f"Переносим {n}: x > {x+n} − {n} = {x}.", "Неравенства", [3, 4]))
        for _ in range(10):
            a = random.randint(2, 6); b = random.randint(2, 9)
            A(build_choice(f"Упрости одночлен: {a}x · {b}x²", f"{a*b}x³", [f"{a*b}x³", f"{a*b}x²", f"{a+b}x³", f"{a*b}x"], f"Коэффициенты перемножаем, показатели складываем: {a}·{b} = {a*b}, x·x² = x³.", "Одночлены", [1, 2]))
        for _ in range(10):
            n = random.randint(2, 8); k = random.randint(2, 5)
            A(build_choice(f"Возведи в степень: ({n}x)^{k}", f"{n**k}x^{k}", [f"{n**k}x^{k}", f"{n*k}x^{k}", f"{n**k}x", f"{n}x^{k}"], f"({n}x)^{k} = {n}^{k}·x^{k} = {n**k}x^{k}.", "Степень", [3, 4]))
        return P

    # ---------- 8 класс ----------
    if grade == 8:
        for _ in range(14):
            b = random.randint(-15, 15); c = random.randint(-20, 20)
            x1 = random.randint(-6, 6); x2 = random.randint(-6, 6)
            bb = -(x1 + x2); cc = x1 * x2
            A(build_choice(f"Реши уравнение: x² {'+' if bb>=0 else '−'} {abs(bb)}x {'+' if cc>=0 else '−'} {abs(cc)} = 0",
                           f"{min(x1,x2)}; {max(x1,x2)}", [f"{min(x1,x2)}; {max(x1,x2)}", f"{x1}", "нет корней", f"{max(x1,x2)}; {min(x1,x2)+1}"],
                           f"По теореме Виета: сумма корней {x1+x2}, произведение {cc}. Корни {x1} и {x2}.", "Квадратные уравнения", [1, 2]))
        for _ in range(14):
            a = random.choice([1, 2]); b = random.randint(-9, 9); c = random.randint(-9, 9)
            D = b * b - 4 * a * c
            if D < 0:
                A(build_choice(f"Сколько корней у уравнения {a}x² {'+' if b>=0 else '−'} {abs(b)}x {'+' if c>=0 else '−'} {abs(c)} = 0?", "ни одного",
                               ["ни одного", "один", "два", "бесконечно много"], f"D = b² − 4ac = {b*b} − {4*a*c} = {D} < 0 — корней нет.", "Квадратные уравнения", [1, 2]))
            else:
                A(build_input(f"Найди дискриминант уравнения {a}x² {'+' if b>=0 else '−'} {abs(b)}x {'+' if c>=0 else '−'} {abs(c)} = 0.", D,
                              f"D = b² − 4ac = ({b})² − 4·{a}·({c}) = {D}.", "Квадратные уравнения", [1, 2]))
        for _ in range(12):
            n = random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144])
            A(build_choice(f"Вычисли: √{n}", int(n ** 0.5), [int(n ** 0.5), n // 2, int(n ** 0.5) + 1, n], f"√{n} = {int(n**0.5)}, так как {int(n**0.5)}² = {n}.", "Квадратные корни", [1, 2]))
        for _ in range(12):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_choice(f"Упрости: √{a*a*b*b}", a * b, [a * b, a * a * b * b, a + b, a * b * 2], f"√(a²b²) = |ab| = {a*b}.", "Квадратные корни", [1, 2]))
        for _ in range(12):
            a = random.randint(2, 12); b = random.randint(2, 12)
            A(build_choice(f"Вычисли: √{a*a} · √{b*b}", a * b, [a * b, a + b, a * a * b * b, abs(a - b)], f"√{a*a} = {a}, √{b*b} = {b}, произведение {a*b}.", "Квадратные корни", [3, 4]))
        for _ in range(12):
            a = random.randint(3, 12); b = random.randint(3, 12)
            A(build_choice(f"Упрости дробь: ({a}x)/( {b}x² )" if False else f"Сократи дробь: ({a*b}x²)/({b}x)", f"{a}x", [f"{a}x", f"{a}x²", f"{a*b}x", f"{a}/{b}"],
                           f"({a*b}x²)/({b}x) = {a}x.", "Рациональные дроби", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_choice(f"Сложи дроби: 1/{a} + 1/{b}", f"{a+b}/{a*b}", [f"{a+b}/{a*b}", f"2/{a+b}", f"1/{a+b}", f"{a*b}/{a+b}"],
                           f"Общий знаменатель {a*b}: {b}/{a*b} + {a}/{a*b} = {a+b}/{a*b}.", "Рациональные дроби", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 9)
            A(build_choice(f"Квадратный трёхчлен x² − {2*a}x + {a*a} разлагается как:", f"(x − {a})²", [f"(x − {a})²", f"(x + {a})²", f"(x − {a})(x + {a})", f"(x − {a*a})²"],
                           f"Это полный квадрат: x² − 2·{a}·x + {a}² = (x − {a})².", "Формулы сокращённого умножения", [1, 2]))
        TRIPLES = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41), (12, 16, 20)]
        for _ in range(12):
            a, b, c = random.choice(TRIPLES)
            if random.random() < 0.5:
                a, b = b, a
            A(build_input(f"Катеты прямоугольного треугольника {a} см и {b} см. Найди гипотенузу (см).", c, f"c = √(a²+b²) = √({a*a}+{b*b}) = √{a*a+b*b} = {c} см.", "Теорема Пифагора", [1, 2]))
        for _ in range(12):
            a, b, c = random.choice(TRIPLES)
            if random.random() < 0.5:
                A(build_input(f"Гипотенуза {c} см, один катет {a} см. Найди второй катет (см).", b, f"b = √(c² − a²) = √({c*c} − {a*a}) = √{b*b} = {b} см.", "Теорема Пифагора", [1, 2]))
            else:
                A(build_choice(f"Гипотенуза {c} см, катет {a} см. Чему равен квадрат второго катета?", b * b, [b * b, b * b + a * a, c * c, c - a],
                               f"b² = c² − a² = {c*c} − {a*a} = {b*b}.", "Теорема Пифагора", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 12)
            A(build_choice(f"Площадь квадрата {a*a} см². Чему равна его сторона?", f"{a} см", [f"{a} см", f"{a*a} см", f"{4*a} см", f"{a//2} см"], f"a = √{a*a} = {a} см.", "Четырёхугольники", [3, 4]))
        for _ in range(12):
            a = random.randint(3, 15); h = random.randint(3, 15)
            A(build_choice(f"Площадь параллелограмма с основанием {a} см и высотой {h} см равна:", f"{a*h} см²", [f"{a*h} см²", f"{a*h//2} см²", f"{2*(a+h)} см²", f"{a+h} см²"],
                           f"S = a · h = {a} · {h} = {a*h} см².", "Площади фигур", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 10); b = random.randint(2, 10); h = random.randint(2, 10)
            A(build_choice(f"Площадь трапеции с основаниями {a} см и {b} см и высотой {h} см равна:", f"{(a+b)*h/2:g} см²".replace(".", ","),
                           [f"{(a+b)*h/2:g} см²".replace(".", ","), f"{(a+b)*h:g} см²".replace(".", ","), f"{a*b*h:g} см²", f"{(a+b)+h:g} см²"],
                           f"S = ((a+b)/2)·h = (({a}+{b})/2)·{h} = {(a+b)*h/2:g} см².", "Площади фигур", [3, 4]))
        for _ in range(12):
            x = random.randint(-8, 8); k = random.choice([-3, -2, 2, 3])
            A(build_choice(f"Реши неравенство: {k}x > {k*x - abs(k)}" if False else f"При каком условии верно неравенство {k}x > {k*x+1}?",
                           f"x {'<' if k<0 else '>'} {x + 1/k:g}".replace(".", ","), [f"x {'<' if k<0 else '>'} {x + 1/k:g}".replace(".", ","), f"x > {x}", f"x < {x}", "решений нет"],
                           f"Делим на {k}" + (" (отрицательное число — знак неравенства меняется)." if k < 0 else "."), "Неравенства", [3, 4]))
        for _ in range(10):
            n = random.randint(2, 6); a = random.randint(2, 9)
            A(build_choice(f"Упрости: (x^{n})^{a}", f"x^{n*a}", [f"x^{n*a}", f"x^{n+a}", f"x^{n}·{a}", f"{a}x^{n}"], f"При возведении степени в степень показатели перемножаются: {n}·{a} = {n*a}.", "Степень", [1, 2]))
        return P

    # ---------- 9 класс ----------
    if grade == 9:
        import math as _m
        for _ in range(16):
            a = random.choice([1, 1, 2]); b = random.randint(-8, 8); c = random.randint(-8, 8)
            D = b * b - 4 * a * c
            if D >= 0:
                x1 = (-b + _m.sqrt(D)) / (2 * a); x2 = (-b - _m.sqrt(D)) / (2 * a)
                nice = D == int(_m.isqrt(D)) ** 2
                if nice:
                    A(build_choice(f"Реши уравнение: {a if a!=1 else ''}x² {'+' if b>=0 else '−'} {abs(b) if b else ''}x {'+' if c>=0 else '−'} {abs(c)} = 0".replace("x² +  x", "x² + 0x"),
                                   f"{min(x1,x2):g}; {max(x1,x2):g}".replace(".", ","),
                                   [f"{min(x1,x2):g}; {max(x1,x2):g}".replace(".", ","), f"{-b/a:g}".replace(".", ","), "нет корней", f"{max(x1,x2):g}".replace(".", ",")],
                                   f"D = {D}; x = (−b ± √D)/2a = ({-b} ± {int(_m.isqrt(D))})/{2*a}.", "Квадратные уравнения", [1, 2]))
        for _ in range(14):
            a = random.randint(1, 5); b = random.randint(-6, 6)
            A(build_choice(f"Найди координату x вершины параболы y = {a}x² {'+' if b>=0 else '−'} {abs(b)}x + 2.", f"{-b/(2*a):g}".replace(".", ","),
                           [f"{-b/(2*a):g}".replace(".", ","), f"{b/(2*a):g}".replace(".", ","), f"{-b/a:g}".replace(".", ","), f"{2*a:g}"],
                           f"x₀ = −b/(2a) = {-b}/(2·{a}) = {-b/(2*a):g}.", "Квадратичная функция", [1, 2]))
        for _ in range(12):
            a = random.choice([-2, -1, 1, 2, 3])
            A(build_choice(f"Куда направлены ветви параболы y = {a}x² + 1?", "вверх" if a > 0 else "вниз", ["вверх", "вниз", "вправо", "влево"],
                           "При a > 0 ветви вверх, при a < 0 — вниз.", "Квадратичная функция", [1, 2]))
        for _ in range(14):
            b1 = random.randint(-6, 6); q = random.choice([2, 3, -2])
            A(build_choice(f"Геометрическая прогрессия: b₁ = {b1}, q = {q}. Найди b₃.", b1 * q * q, [b1 * q * q, b1 * q, b1 + 2 * q, b1 * q * q * q],
                           f"b₃ = b₁·q² = {b1}·{q*q} = {b1*q*q}.", "Прогрессии", [3, 4]))
        for _ in range(14):
            a1 = random.randint(-5, 10); d = random.randint(-4, 6)
            n = random.randint(5, 15)
            A(build_input(f"Арифметическая прогрессия: a₁ = {a1}, d = {d}. Найди a{n}.", a1 + d * (n - 1),
                          f"aₙ = a₁ + d(n−1) = {a1} + ({d})·{n-1} = {a1 + d*(n-1)}.", "Прогрессии", [3, 4]))
        for _ in range(12):
            a1 = random.randint(1, 6); d = random.randint(1, 5); n = random.randint(4, 10)
            S = n * (2 * a1 + d * (n - 1)) // 2
            A(build_input(f"Найди сумму первых {n} членов арифметической прогрессии, если a₁ = {a1}, d = {d}.", S,
                          f"Sₙ = (2a₁ + d(n−1))·n/2 = (2·{a1} + {d}·{n-1})·{n}/2 = {S}.", "Прогрессии", [3, 4]))
        for _ in range(12):
            n = random.randint(3, 9)
            A(build_choice(f"Сколько существует двузначных чисел, составленных из цифр 1..{n} (с повторениями)?", n * n, [n * n, n * (n - 1), n + n, n ** 3],
                           f"По правилу произведения: {n}·{n} = {n*n}.", "Комбинаторика", [3, 4]))
        for _ in range(12):
            n = random.randint(4, 9); k = random.randint(2, 3)
            import math as _m
            C = _m.comb(n, k)
            A(build_choice(f"Вычисли C({n}, {k}) — число сочетаний из {n} по {k}.", C, [C, n * k, _m.perm(n, k), C + 1],
                           f"C({n},{k}) = {n}!/({k}!·{n-k}!) = {C}.", "Комбинаторика", [3, 4]))
        for _ in range(12):
            n = random.randint(4, 10)
            A(build_choice(f"Сколькими способами можно рассадить {n} человек на {n} стульев?", _m.factorial(n),
                           [str(_m.factorial(n)), str(n * n), str(n), str(2 ** n)], f"Это перестановки: P({n}) = {n}! = {_m.factorial(n)}.", "Комбинаторика", [3, 4]))
        for _ in range(14):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_choice(f"В прямоугольном треугольнике катеты {a} и {b}. Найди квадрат гипотенузы.", a * a + b * b, [a * a + b * b, (a + b) ** 2, a * b, a * a - b * b],
                           f"c² = a² + b² = {a*a} + {b*b} = {a*a+b*b}.", "Геометрия: треугольник", [1, 2]))
        for _ in range(14):
            a = random.randint(2, 10)
            A(build_choice(f"Средняя линия треугольника параллельна стороне, равной {a*2} см. Чему равна средняя линия?", f"{a} см", [f"{a} см", f"{a*2} см", f"{a*4} см", f"{a//2} см"],
                           "Средняя линия равна половине параллельной ей стороны.", "Геометрия: треугольник", [1, 2]))
        for _ in range(12):
            r = random.randint(2, 10)
            A(build_choice(f"Площадь круга радиуса {r} (π ≈ 3,14) равна примерно:", f"{round(3.14*r*r,2)} см²".replace(".", ","),
                           [f"{round(3.14*r*r,2)} см²".replace(".", ","), f"{round(2*3.14*r,2)} см²".replace(".", ","), f"{r*r} см²", f"{round(3.14*r,2)} см²".replace(".", ",")],
                           f"S = πr² = 3,14 · {r*r} = {round(3.14*r*r,2)} см².", "Геометрия: окружность", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 8); b = random.randint(2, 8)
            A(build_choice(f"Векторы a⃗({a}; {b}) и b⃗({b}; {a}). Чему равно их скалярное произведение?", 2 * a * b, [2 * a * b, a * a + b * b, a + b, 0],
                           f"a⃗·b⃗ = {a}·{b} + {b}·{a} = {2*a*b}.", "Векторы", [3, 4]))
        for _ in range(12):
            n = random.randint(3, 8)
            A(build_choice(f"Сумма внутренних углов выпуклого {n}-угольника равна:", f"{180*(n-2)}°", [f"{180*(n-2)}°", f"{180*n}°", f"{360*(n-2)}°", f"{90*n}°"],
                           f"S = 180°·(n − 2) = 180°·{n-2} = {180*(n-2)}°.", "Геометрия: многоугольники", [1, 2]))
        for _ in range(10):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_choice(f"Упрости: √({a*a}·{b})", f"{a}√{b}", [f"{a}√{b}", f"{a*b}", f"{a*a}√{b}", f"√{a}·{b}"], f"√({a*a}·{b}) = {a}√{b}.", "Квадратные корни", [1, 2]))
        for _ in range(10):
            y = random.randint(2, 9); k = random.randint(2, 6)
            A(build_choice(f"Функция y = {k}/x. Найди y при x = {y}.", f"{k/y:g}".replace(".", ","), [f"{k/y:g}".replace(".", ","), f"{k*y}", f"{y/k:g}".replace(".", ","), f"{k+y}"],
                           f"y = {k}/{y} = {k/y:g}.", "Функции", [3, 4]))
        return P

    # ---------- 10 класс ----------
    if grade == 10:
        import math as _m
        for _ in range(14):
            x = random.randint(2, 9); n = random.choice([2, 3, 4])
            A(build_input(f"Вычисли: sin²{x}°… " if False else f"Найди значение: 2·sin30°·cos60° (в десятичной дроби).", 0.5,
                          "sin30° = 0,5; cos60° = 0,5; 2·0,5·0,5 = 0,5.", "Тригонометрия", [1, 2]))
            break
        for _ in range(16):
            val = random.choice([("sin30°", "0,5"), ("cos60°", "0,5"), ("sin90°", "1"), ("cos0°", "1"), ("tg45°", "1"),
                                 ("sin0°", "0"), ("cos90°", "0"), ("sin45°", "√2/2"), ("cos45°", "√2/2"), ("sin60°", "√3/2"),
                                 ("cos30°", "√3/2"), ("tg30°", "√3/3"), ("ctg45°", "1"), ("sin180°", "0"), ("cos180°", "−1")])
            others = [v for k, v in [("sin30°", "0,5"), ("cos60°", "0,5"), ("sin90°", "1"), ("cos0°", "1"), ("tg45°", "1"),
                                     ("sin0°", "0"), ("cos90°", "0"), ("sin45°", "√2/2"), ("cos45°", "√2/2"), ("sin60°", "√3/2"),
                                     ("cos30°", "√3/2"), ("tg30°", "√3/3"), ("ctg45°", "1"), ("sin180°", "0"), ("cos180°", "−1")] if k != val[0]]
            random.shuffle(others)
            A(build_choice(f"Найди значение выражения {val[0]}.", val[1], [val[1]] + others[:3], "Значение из таблицы тригонометрических функций.", "Тригонометрия", [1, 2]))
        for _ in range(14):
            a = random.randint(2, 9)
            A(build_choice(f"Упрости: sin²x + cos²x + {a}", a + 1, [a + 1, a, a * 2, a - 1], "Основное тригонометрическое тождество: sin²x + cos²x = 1.", "Тригонометрия", [1, 2]))
        for _ in range(14):
            k = random.choice([-2, -1, 1, 2, 3]); b = random.randint(1, 5)
            A(build_choice(f"Найди период функции y = {k}·sin({b}x).", f"{2*_m.pi/b:g}π".replace(".", ",") if b != 1 else "2π",
                           [f"2π/{b}", "2π", f"π/{b}", f"{2*b}π"], f"Период sin(kx) равен 2π/|k| = 2π/{b}.", "Тригонометрия", [3, 4]))
        for _ in range(16):
            n = random.randint(2, 6)
            A(build_choice(f"Найди производную функции f(x) = x^{n}.", f"{n}x^{n-1}", [f"{n}x^{n-1}", f"x^{n+1}/{n+1}", f"{n}x^{n}", f"{n-1}x^{n}"],
                           f"(xⁿ)′ = n·xⁿ⁻¹ = {n}x^{n-1}.", "Производная", [1, 2]))
        for _ in range(16):
            a = random.randint(2, 9); n = random.randint(2, 5)
            A(build_choice(f"Найди производную: f(x) = {a}x^{n}.", f"{a*n}x^{n-1}", [f"{a*n}x^{n-1}", f"{a}x^{n-1}", f"{a*n}x^{n}", f"{a+n}x^{n-1}"],
                           f"(Cxⁿ)′ = C·n·xⁿ⁻¹ = {a}·{n}·x^{n-1} = {a*n}x^{n-1}.", "Производная", [1, 2]))
        for _ in range(12):
            a = random.randint(2, 6); x0 = random.randint(1, 4)
            A(build_input(f"f(x) = x² + {a}x. Найди f′({x0}).", 2 * x0 + a, f"f′(x) = 2x + {a}; f′({x0}) = 2·{x0} + {a} = {2*x0+a}.", "Производная", [3, 4]))
        for _ in range(12):
            a = random.randint(1, 5)
            A(build_choice(f"Производная функции f(x) = sin({a}x) равна:", f"{a}cos({a}x)", [f"{a}cos({a}x)", f"{a}sin({a}x)", f"−{a}cos({a}x)", f"cos({a}x)/{a}"],
                           f"(sin kx)′ = k·cos kx.", "Производная", [3, 4]))
        for _ in range(12):
            n = random.randint(2, 6)
            A(build_choice(f"Найди первообразную F(x) для f(x) = {n}x^{n-1} (C = 0).", f"x^{n}", [f"x^{n}", f"x^{n+1}", f"{n}x^{n}", f"x^{n-1}/{n-1}"],
                           f"(x^{n})′ = {n}x^{n-1}, значит F(x) = x^{n}.", "Первообразная", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 8)
            A(build_choice(f"Реши уравнение: log₂x = {a}.", 2 ** a, [2 ** a, a * 2, 2 * a, a ** 2], f"x = 2^{a} = {2**a}.", "Логарифмы", [1, 2]))
        for _ in range(12):
            n = random.randint(2, 10)
            A(build_choice(f"Вычисли: log₃{3**n}.", n, [n, 3 * n, 3 ** n, n ** 3], f"log₃3^{n} = {n}.", "Логарифмы", [1, 2]))
        for _ in range(12):
            a = random.randint(2, 6); b = random.randint(2, 6)
            A(build_choice(f"Упрости: log₂{2**a} + log₂{2**b}.", a + b, [a + b, a * b, 2 ** (a + b), a - b], f"log₂2^{a} = {a}, log₂2^{b} = {b}; сумма = {a+b}.", "Логарифмы", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 9); n = random.randint(2, 5)
            one_over = "1/" + str(n)
            A(build_choice(f"Упрости: ({a}^{n})^({one_over})", a, [a, a ** n, n, a * n], f"Показатели перемножаются: n · {one_over} = 1, значит результат {a}.", "Степень", [1, 2]))
        for _ in range(12):
            n = random.randint(3, 8)
            A(build_choice(f"Сколькими способами можно выбрать старосту и его заместителя из {n} человек?", n * (n - 1), [n * (n - 1), n * n, n, _m.factorial(n)],
                           f"Размещения: A({n},2) = {n}·{n-1} = {n*(n-1)}.", "Комбинаторика", [3, 4]))
        for _ in range(12):
            n = random.randint(4, 10); k = random.randint(2, 3)
            A(build_choice(f"Вычисли C({n},{k}).", _m.comb(n, k), [_m.comb(n, k), n * k, _m.comb(n, k - 1), _m.perm(n, k)],
                           f"C({n},{k}) = {n}!/({k}!·{n-k}!) = {_m.comb(n,k)}.", "Комбинаторика", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 8); b = random.randint(2, 8); c = random.randint(2, 12)
            A(build_choice(f"В кубе ребро {a} см. Найди площадь его полной поверхности.", f"{6*a*a} см²", [f"{6*a*a} см²", f"{a*a*a} см²", f"{4*a*a} см²", f"{6*a} см²"],
                           f"S = 6a² = 6·{a*a} = {6*a*a} см².", "Стереометрия", [1, 2]))
        for _ in range(12):
            a = random.randint(2, 7); h = random.randint(3, 12)
            A(build_choice(f"Объём цилиндра с радиусом основания {a} и высотой {h} (π ≈ 3,14) равен примерно:", f"{round(3.14*a*a*h,2)}".replace(".", ","),
                           [f"{round(3.14*a*a*h,2)}".replace(".", ","), f"{round(2*3.14*a*h,2)}".replace(".", ","), f"{a*a*h}", f"{round(3.14*a*h,2)}".replace(".", ",")],
                           f"V = πr²h = 3,14·{a*a}·{h} = {round(3.14*a*a*h,2)}.", "Стереометрия", [3, 4]))
        for _ in range(12):
            r = random.randint(2, 6)
            A(build_choice(f"Объём шара радиуса {r} (π ≈ 3,14) равен примерно:", f"{round(4/3*3.14*r**3,2)}".replace(".", ","),
                           [f"{round(4/3*3.14*r**3,2)}".replace(".", ","), f"{round(4*3.14*r**2,2)}".replace(".", ","), f"{round(3.14*r**3,2)}".replace(".", ","), f"{round(2*3.14*r,2)}".replace(".", ",")],
                           f"V = (4/3)πr³ = (4/3)·3,14·{r**3} = {round(4/3*3.14*r**3,2)}.", "Стереометрия", [3, 4]))
        for _ in range(10):
            a = random.randint(3, 9); b = random.randint(3, 9)
            A(build_choice(f"В прямоугольном параллелепипеде измерения {a}, {b} и {a+b} см. Найди длину его диагонали.",
                           f"√{a*a+b*b+(a+b)**2} см", [f"√{a*a+b*b+(a+b)**2} см", f"{a+b} см", f"{a*b*(a+b)} см", f"√{a*a+b*b} см"],
                           f"d = √(a²+b²+c²) = √({a*a}+{b*b}+{(a+b)**2}) см.", "Стереометрия", [1, 2]))
        return P

    # ---------- 11 класс ----------
    if grade == 11:
        import math as _m
        for _ in range(16):
            a = random.randint(2, 9); b = random.randint(2, 9)
            A(build_choice(f"Вычисли: log{a}{a**b}.", b, [b, a * b, a ** b, b ** a], f"log{a}{a**b} = {b} по определению логарифма.", "Логарифмы", [1, 2]))
        for _ in range(14):
            a = random.randint(2, 5); b = random.randint(2, 5); c = random.randint(2, 5)
            A(build_choice(f"Упрости: log{a}({b*c}) − log{a}{c}" if False else f"Упрости: log{a}{b} + log{a}{c}.", f"log{a}{b*c}",
                           [f"log{a}{b*c}", f"log{a}{b*c}", f"log{a}{b}/log{a}{c}", f"log{a}{b+c}", f"log{a}{b-c}"],
                           "Сумма логарифмов с одинаковым основанием = логарифм произведения.", "Логарифмы", [1, 2]))
        for _ in range(14):
            n = random.randint(2, 6); a = random.randint(2, 6)
            A(build_choice(f"Найди производную f(x) = {a}·x^{n} + 3x.", f"{a*n}x^{n-1} + 3", [f"{a*n}x^{n-1} + 3", f"{a*n}x^{n} + 3", f"{a}x^{n-1} + 3x", f"{a*n+3}x^{n-1}"],
                           f"Производная суммы: ({a}x^{n})′ + (3x)′ = {a*n}x^{n-1} + 3.", "Производная", [1, 2]))
        for _ in range(14):
            a = random.randint(2, 6)
            A(build_choice(f"Производная функции f(x) = e^({a}x) равна:", f"{a}e^({a}x)", [f"{a}e^({a}x)", f"e^({a}x)", f"{a}x·e^({a}x−1)", f"e^({a}x)/{a}"],
                           "(e^{kx})′ = k·e^{kx}.", "Производная", [1, 2]))
        for _ in range(12):
            a = random.randint(1, 5); x0 = random.randint(-3, 3)
            A(build_input(f"f(x) = x³ − {a}x. Найди f′({x0}).", 3 * x0 * x0 - a, f"f′(x) = 3x² − {a}; f′({x0}) = 3·{x0*x0} − {a} = {3*x0*x0-a}.", "Производная", [3, 4]))
        for _ in range(12):
            a = random.randint(1, 4)
            A(build_choice(f"Найди точки экстремума функции f(x) = x² − {2*a}x.", f"x = {a}", [f"x = {a}", f"x = {2*a}", f"x = 0", f"x = −{a}"],
                           f"f′(x) = 2x − {2*a} = 0 → x = {a}. Это точка минимума.", "Применение производной", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 8)
            A(build_input(f"Найди определённый интеграл ∫₀^{a} 2x dx.", a * a, f"∫2x dx = x²; подставляем: {a}² − 0² = {a*a}.", "Интеграл", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 6)
            A(build_input(f"Вычисли ∫₀^{a} 3x² dx.", a ** 3, f"∫3x² dx = x³; {a}³ − 0 = {a**3}.", "Интеграл", [3, 4]))
        for _ in range(12):
            n = random.randint(3, 9); k = random.randint(2, 4)
            A(build_choice(f"Вычисли C({n},{k}).", _m.comb(n, k), [_m.comb(n, k), _m.perm(n, k), n * k, _m.comb(n, k) + n],
                           f"C({n},{k}) = {n}!/({k}!·{n-k}!) = {_m.comb(n,k)}.", "Комбинаторика", [1, 2]))
        for _ in range(12):
            n = random.randint(3, 7)
            A(build_choice(f"Сколько различных слов (перестановок) можно составить из букв слова «КНИГА»?" if n == 5 else f"Сколько перестановок из {n} различных элементов?",
                           _m.factorial(5) if n == 5 else _m.factorial(n), [str(_m.factorial(5) if n == 5 else _m.factorial(n)), str(n * n), str(2 ** n), str(n)],
                           f"P(n) = n! = {_m.factorial(5) if n==5 else _m.factorial(n)}.", "Комбинаторика", [1, 2]))
        for _ in range(12):
            p = random.choice([0.2, 0.25, 0.5, 0.1]); n = random.randint(2, 6)
            A(build_choice(f"Вероятность события {p:g}. Какова вероятность противоположного события?".replace(".", ","), f"{1-p:g}".replace(".", ","),
                           [f"{1-p:g}".replace(".", ","), f"{p:g}".replace(".", ","), "1", "0"], f"P(A̅) = 1 − P(A) = 1 − {p:g} = {1-p:g}.".replace(".", ","), "Вероятность", [1, 2]))
        for _ in range(12):
            fav = random.choice([2, 5, 8]); tot = fav * random.choice([5, 10, 20])
            A(build_choice(f"В коробке {tot} шаров, из них {fav} белых. Какова вероятность вытащить белый шар (обыкновенной дробью)?", f"{fav}/{tot}",
                           [f"{fav}/{tot}", f"{tot}/{fav}", f"{fav}/{tot-fav}", f"{tot-fav}/{tot}"], f"P = {fav}/{tot}.", "Вероятность", [1, 2]))
        for _ in range(14):
            k = random.randint(2, 7); a = random.randint(2, 5)
            A(build_input(f"Реши уравнение: {a}^x = {a**k}. x = ?", k, f"Представим {a**k} как {a}^{k}; значит x = {k}.", "Показательные уравнения", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 8); b = random.randint(2, 8); h = random.randint(3, 12)
            A(build_choice(f"Объём прямой призмы с площадью основания {a*b} см² и высотой {h} см равен:", f"{a*b*h} см³", [f"{a*b*h} см³", f"{a*b+h} см³", f"{a*b*h//2} см³", f"{2*(a*b+h)} см³"],
                           f"V = S·h = {a*b}·{h} = {a*b*h} см³.", "Стереометрия", [1, 2]))
        for _ in range(12):
            r = random.randint(2, 8); h = random.randint(3, 15)
            A(build_choice(f"Объём конуса с радиусом {r} и высотой {h} (π ≈ 3,14) равен примерно:", f"{round(3.14*r*r*h/3,2)}".replace(".", ","),
                           [f"{round(3.14*r*r*h/3,2)}".replace(".", ","), f"{round(3.14*r*r*h,2)}".replace(".", ","), f"{round(2*3.14*r*h,2)}".replace(".", ","), f"{round(3.14*r*h,2)}".replace(".", ",")],
                           f"V = (1/3)πr²h = (1/3)·3,14·{r*r}·{h} = {round(3.14*r*r*h/3,2)}.", "Стереометрия", [1, 2]))
        for _ in range(12):
            r = random.randint(2, 9); h = random.randint(4, 20)
            A(build_choice(f"Площадь боковой поверхности цилиндра с радиусом {r} и высотой {h} (π ≈ 3,14) равна примерно:", f"{round(2*3.14*r*h,2)}".replace(".", ","),
                           [f"{round(2*3.14*r*h,2)}".replace(".", ","), f"{round(3.14*r*r*h,2)}".replace(".", ","), f"{round(3.14*r*h,2)}".replace(".", ","), f"{2*r*h}"],
                           f"Sбок = 2πrh = 2·3,14·{r}·{h} = {round(2*3.14*r*h,2)}.", "Стереометрия", [3, 4]))
        for _ in range(12):
            a = random.randint(2, 7); n = random.randint(2, 5)
            A(build_choice(f"Упрости: (√{a})^{2*n}" if False else f"Упрости: {a}^{1/2} · {a}^{1/2}.", a, [a, a ** 2, 2 * a, a ** 0.5], f"{a}^(1/2+1/2) = {a}¹ = {a}.", "Степень", [3, 4]))
        for _ in range(12):
            x = random.randint(2, 9)
            A(build_choice(f"Найди область определения функции y = √(x − {x}).", f"x ≥ {x}", [f"x ≥ {x}", f"x > {x}", f"x ≤ {x}", f"x ∈ R"],
                           "Подкоренное выражение неотрицательно: x − a ≥ 0.", "Функции", [3, 4]))
        for _ in range(10):
            a = random.randint(1, 6); b = random.randint(1, 6)
            A(build_choice(f"Найди ∫₀^{a}(2x + {b}) dx при a = {a}, b = {b}.", a * a + b * a, [a * a + b * a, a * a, 2 * a + b, a * b],
                           f"∫(2x+{b})dx = x² + {b}x; подставляем {a}: {a*a} + {b*a} = {a*a + b*a}.", "Интеграл", [1, 2]))
        return P

    return P


# ============================================================ ФИЗИКА (параметрические задачи)
def gen_physics(grade, seed=0):
    random.seed(seed)
    P = []
    A = P.append
    if grade == 7:
        for _ in range(16):
            t = random.randint(2, 20); s = t * random.randint(2, 25)
            A(build_input(f"Пешеход прошёл {s} м за {t} с. Какова его скорость (м/с)?", s // t, f"v = S/t = {s}/{t} = {s//t} м/с.", "Скорость", [1, 2]))
        for _ in range(14):
            v = random.randint(2, 20); t = random.randint(2, 10)
            A(build_choice(f"Тело движется со скоростью {v} м/с. Какой путь оно пройдёт за {t} с?", f"{v*t} м", [f"{v*t} м", f"{v//t} м", f"{v+t} м", f"{v*t*2} м"], f"S = v·t = {v}·{t} = {v*t} м.", "Скорость", [1, 2]))
        for _ in range(14):
            V = random.choice([2, 4, 5, 10, 20, 25]); m = V * random.randint(10, 60)
            A(build_input(f"Масса тела {m} кг, объём {V} м³. Найди плотность (кг/м³).", m // V, f"ρ = m/V = {m}/{V} = {m//V} кг/м³.", "Плотность", [1, 2]))
        for _ in range(12):
            rho = random.choice([800, 1000, 1200, 2700]); V = random.randint(2, 9)
            A(build_choice(f"Плотность вещества {rho} кг/м³. Какова масса {V} м³ этого вещества?", f"{rho*V} кг", [f"{rho*V} кг", f"{rho//V} кг", f"{rho+V} кг", f"{rho*V//10} кг"], f"m = ρV = {rho}·{V} = {rho*V} кг.", "Плотность", [3, 4]))
        for _ in range(14):
            m = random.randint(1, 20); g = 10
            A(build_choice(f"Чему равна сила тяжести, действующая на тело массой {m} кг (g = 10 Н/кг)?", f"{m*g} Н", [f"{m*g} Н", f"{m} Н", f"{m*g*10} Н", f"{m/g:g} Н".replace(".", ",")], f"F = mg = {m}·10 = {m*g} Н.", "Сила тяжести", [3, 4]))
        for _ in range(12):
            S = random.choice([2, 4, 5, 10]); F = S * random.randint(5, 40)
            A(build_input(f"Сила {F} Н действует перпендикулярно площадке {S} м². Найди давление (Па).", F // S, f"p = F/S = {F}/{S} = {F//S} Па.", "Давление", [3, 4]))
        for _ in range(12):
            F = random.randint(5, 100); s = random.randint(2, 20)
            A(build_choice(f"Сила {F} Н переместила тело на {s} м по направлению силы. Какая работа совершена?", f"{F*s} Дж", [f"{F*s} Дж", f"{F+s} Дж", f"{F//s} Дж", f"{F*s*2} Дж"], f"A = F·S = {F}·{s} = {F*s} Дж.", "Работа и мощность", [3, 4]))
        for _ in range(12):
            t = random.choice([2, 4, 5, 10, 20]); A_ = t * random.randint(50, 200)
            A(build_input(f"Работа {A_} Дж совершена за {t} с. Найди мощность (Вт).", A_ // t, f"N = A/t = {A_}/{t} = {A_//t} Вт.", "Работа и мощность", [3, 4]))
        for _ in range(10):
            m = random.randint(1, 20); h = random.randint(2, 20)
            A(build_choice(f"Тело массой {m} кг поднято на высоту {h} м. Какова его потенциальная энергия (g = 10 Н/кг)?", f"{m*10*h} Дж", [f"{m*10*h} Дж", f"{m*h} Дж", f"{m*10*h//2} Дж", f"{m+h} Дж"], f"Ep = mgh = {m}·10·{h} = {m*10*h} Дж.", "Энергия", [3, 4]))
        for _ in range(10):
            m = random.randint(1, 10); v = random.randint(2, 10)
            A(build_choice(f"Кинетическая энергия тела массой {m} кг, движущегося со скоростью {v} м/с, равна:", f"{m*v*v//2} Дж" if (m*v*v) % 2 == 0 else f"{m*v*v/2:g} Дж".replace(".", ","),
                           [f"{m*v*v/2:g} Дж".replace(".", ","), f"{m*v} Дж", f"{m*v*v} Дж", f"{m*v*2} Дж"], f"Ek = mv²/2 = {m}·{v*v}/2 = {m*v*v/2:g} Дж.", "Энергия", [3, 4]))
        for _ in range(10):
            a = random.randint(2, 10); b = random.randint(2, 10)
            A(build_choice(f"Рычаг в равновесии: плечо силы F₁ = {a*10} Н равно {b} см. Какое плечо у силы {a*10*2} Н?", f"{b/2:g} см".replace(".", ","),
                           [f"{b/2:g} см".replace(".", ","), f"{b*2} см", f"{b} см", f"{b+a} см"], f"Условие равновесия: F₁l₁ = F₂l₂ → l₂ = {a*10}·{b}/{a*10*2} = {b/2:g} см.", "Простые механизмы", [3, 4]))
        for _ in range(10):
            A(build_choice("Единица измерения силы в СИ:", "ньютон (Н)", ["ньютон (Н)", "паскаль (Па)", "джоуль (Дж)", "килограмм (кг)"], "1 Н = 1 кг·м/с².", "Основы", [1, 2]))
        for _ in range(8):
            A(build_choice("Прибор для измерения силы:", "динамометр", ["динамометр", "барометр", "мензурка", "спидометр"], "Динамометр измеряет силу (обычно в ньютонах).", "Основы", [1, 2]))
        return P
    if grade == 8:
        for _ in range(14):
            m = random.randint(1, 10); dt = random.randint(5, 60)
            c = random.choice([4200, 500, 900, 2100])
            A(build_input(f"Какое количество теплоты нужно, чтобы нагреть {m} кг вещества (c = {c} Дж/(кг·°C)) на {dt} °C? (в Дж)", c * m * dt, f"Q = cmΔt = {c}·{m}·{dt} = {c*m*dt} Дж.", "Тепловые явления", [1, 2]))
        for _ in range(12):
            m = random.randint(1, 5)
            lam = random.choice([330000, 2300000, 84000])
            A(build_choice(f"Удельная теплота плавления {lam} Дж/кг. Сколько теплоты нужно для плавления {m} кг вещества?", f"{lam*m} Дж", [f"{lam*m} Дж", f"{lam//m} Дж", f"{lam+m} Дж", f"{lam*m//1000} Дж"], f"Q = λm = {lam}·{m} = {lam*m} Дж.", "Тепловые явления", [1, 2]))
        for _ in range(12):
            I = random.randint(1, 10); U = random.randint(2, 40)
            A(build_choice(f"Сила тока {I} А, напряжение {U} В. Чему равно сопротивление участка?", f"{U//I} Ом" if U % I == 0 else f"{U/I:g} Ом".replace(".", ","),
                           [f"{U/I:g} Ом".replace(".", ","), f"{I*U} Ом", f"{U+I} Ом", f"{I/U:g} Ом".replace(".", ",")], f"Закон Ома: R = U/I = {U}/{I} = {U/I:g} Ом.", "Электричество", [3, 4]))
        for _ in range(14):
            R = random.choice([2, 4, 5, 10, 20]); I = random.randint(1, 5)
            A(build_choice(f"Сопротивление {R} Ом, сила тока {I} А. Чему равно напряжение?", f"{R*I} В", [f"{R*I} В", f"{R//I} В", f"{R+I} В", f"{R*I*10} В"], f"U = IR = {I}·{R} = {R*I} В.", "Электричество", [3, 4]))
        for _ in range(12):
            r1 = random.randint(2, 20); r2 = random.randint(2, 20)
            A(build_choice(f"Два резистора {r1} Ом и {r2} Ом соединены последовательно. Общее сопротивление:", f"{r1+r2} Ом", [f"{r1+r2} Ом", f"{r1*r2//(r1+r2)} Ом", f"{r1*r2} Ом", f"{max(r1,r2)} Ом"], "При последовательном соединении R = R₁ + R₂.", "Электричество", [3, 4]))
        for _ in range(12):
            r1 = random.choice([2, 4, 6, 8, 10]); r2 = r1 * random.choice([1, 2])
            R = r1 * r2 / (r1 + r2)
            A(build_choice(f"Два резистора {r1} Ом и {r2} Ом соединены параллельно. Общее сопротивление:", f"{R:g} Ом".replace(".", ","),
                           [f"{R:g} Ом".replace(".", ","), f"{r1+r2} Ом", f"{r1*r2} Ом", f"{R*2:g} Ом".replace(".", ",")], f"1/R = 1/R₁ + 1/R₂ → R = {r1}·{r2}/({r1}+{r2}) = {R:g} Ом.", "Электричество", [3, 4]))
        for _ in range(12):
            U = random.randint(2, 20); I = random.randint(1, 10); t = random.choice([2, 5, 10])
            A(build_choice(f"Мощность потребителя при U = {U} В и I = {I} А равна:", f"{U*I} Вт", [f"{U*I} Вт", f"{U//I} Вт", f"{U+I} Вт", f"{U*I*t} Вт"], f"P = UI = {U}·{I} = {U*I} Вт.", "Электричество", [3, 4]))
        for _ in range(10):
            Pw = random.randint(100, 2000); t = random.randint(1, 10)
            A(build_choice(f"Электроприбор мощностью {Pw} Вт работал {t} ч. Сколько кВт·ч израсходовано?", f"{Pw*t/1000:g}".replace(".", ","),
                           [f"{Pw*t/1000:g}".replace(".", ","), f"{Pw*t}", f"{Pw//t}", f"{Pw*t/100:g}".replace(".", ",")], f"A = P·t = {Pw} Вт · {t} ч = {Pw*t} Вт·ч = {Pw*t/1000:g} кВт·ч.", "Электричество", [3, 4]))
        for _ in range(10):
            I = random.randint(1, 5); R = random.choice([2, 5, 10, 20]); t = random.choice([2, 5, 10])
            A(build_choice(f"Какое количество теплоты выделится в проводнике сопротивлением {R} Ом при токе {I} А за {t} с?", f"{I*I*R*t} Дж", [f"{I*I*R*t} Дж", f"{I*R*t} Дж", f"{I*I*R} Дж", f"{I+R+t} Дж"], f"Закон Джоуля–Ленца: Q = I²Rt = {I*I}·{R}·{t} = {I*I*R*t} Дж.", "Электричество", [3, 4]))
        for _ in range(8):
            A(build_choice("Как называется процесс передачи тепла без переноса вещества (через неподвижную среду)?", "теплопроводность",
                           ["теплопроводность", "конвекция", "излучение", "испарение"], "Теплопроводность — передача энергии от частицы к частице.", "Тепловые явления", [1, 2]))
        for _ in range(8):
            A(build_choice("Единица измерения количества теплоты:", "джоуль (Дж)", ["джоуль (Дж)", "ватт (Вт)", "ньютон (Н)", "паскаль (Па)"], "Q измеряется в джоулях.", "Тепловые явления", [1, 2]))
        return P
    if grade == 9:
        for _ in range(14):
            v0 = random.randint(0, 20); a = random.randint(1, 5); t = random.randint(2, 10)
            A(build_input(f"Тело движется с начальной скоростью {v0} м/с и ускорением {a} м/с². Какой будет скорость через {t} с (м/с)?", v0 + a * t, f"v = v₀ + at = {v0} + {a}·{t} = {v0+a*t} м/с.", "Кинематика", [1, 2]))
        for _ in range(14):
            a = random.randint(1, 5); t = random.randint(2, 10)
            A(build_choice(f"Тело начинает движение из покоя с ускорением {a} м/с². Какой путь оно пройдёт за {t} с?", f"{a*t*t//2} м" if (a*t*t) % 2 == 0 else f"{a*t*t/2:g} м".replace(".", ","),
                           [f"{a*t*t/2:g} м".replace(".", ","), f"{a*t} м", f"{a*t*t} м", f"{a+t*t} м"], f"S = at²/2 = {a}·{t*t}/2 = {a*t*t/2:g} м.", "Кинематика", [1, 2]))
        for _ in range(12):
            m = random.randint(1, 10); a = random.randint(1, 8)
            A(build_choice(f"Какая сила сообщает телу массой {m} кг ускорение {a} м/с²?", f"{m*a} Н", [f"{m*a} Н", f"{m//a} Н", f"{m+a} Н", f"{m*a*10} Н"], f"F = ma = {m}·{a} = {m*a} Н (второй закон Ньютона).", "Динамика", [1, 2]))
        for _ in range(12):
            m = random.choice([2, 4, 5, 10]); F = m * random.randint(5, 20)
            A(build_input(f"Сила {F} Н действует на тело массой {m} кг. Найди ускорение (м/с²).", F // m, f"a = F/m = {F}/{m} = {F//m} м/с².", "Динамика", [1, 2]))
        for _ in range(12):
            m = random.randint(1, 10); v = random.randint(2, 15)
            A(build_choice(f"Импульс тела массой {m} кг, движущегося со скоростью {v} м/с:", f"{m*v} кг·м/с", [f"{m*v} кг·м/с", f"{m*v//2} кг·м/с", f"{m+v} кг·м/с", f"{m*v*v} кг·м/с"], f"p = mv = {m}·{v} = {m*v} кг·м/с.", "Импульс", [3, 4]))
        for _ in range(10):
            m = random.randint(1, 5); v = random.randint(2, 8)
            A(build_choice(f"Тело массой {m} кг и скоростью {v} м/с останавливается. Какую работу совершила сила трения?", f"−{m*v*v//2} Дж" if (m*v*v) % 2 == 0 else f"−{m*v*v/2:g} Дж".replace(".", ","),
                           [f"−{m*v*v/2:g} Дж".replace(".", ","), f"{m*v*v/2:g} Дж".replace(".", ","), f"{m*v} Дж", f"0 Дж"], f"A = ΔEk = 0 − mv²/2 = −{m*v*v/2:g} Дж.", "Энергия", [3, 4]))
        for _ in range(10):
            R = random.choice([1, 2, 4, 5, 10]); U = random.randint(2, 12)
            A(build_choice(f"Сопротивление {R} Ом, напряжение {U} В. Чему равна сила тока?", f"{U/R:g} А".replace(".", ","), [f"{U/R:g} А".replace(".", ","), f"{U*R} А", f"{R/U:g} А".replace(".", ","), f"{U+R} А"], f"I = U/R = {U}/{R} = {U/R:g} А.", "Электричество", [1, 2]))
        for _ in range(10):
            A(build_choice("Что показывает сила тока?", "сколько заряда проходит через поперечное сечение проводника за 1 с",
                           ["сколько заряда проходит через поперечное сечение проводника за 1 с", "напряжение на участке", "сопротивление проводника", "мощность цепи"],
                           "I = q/t, единица — ампер (А).", "Электричество", [1, 2]))
        for _ in range(10):
            T = random.randint(2, 10)
            A(build_choice(f"Период колебаний {T} с. Чему равна частота?", f"{1/T:g} Гц".replace(".", ","), [f"{1/T:g} Гц".replace(".", ","), f"{T} Гц", f"{2*T} Гц", f"{T*T} Гц"], f"ν = 1/T = 1/{T} = {1/T:g} Гц.", "Колебания и волны", [3, 4]))
        for _ in range(10):
            v, nu = random.choice([(340, 17), (340, 20), (300, 15), (1500, 25), (330, 11), (300, 10), (1500, 50), (340, 4)])
            A(build_input(f"Скорость волны {v} м/с, частота {nu} Гц. Найди длину волны (м).", v // nu, f"λ = v/ν = {v}/{nu} = {v//nu} м.", "Колебания и волны", [3, 4]))
        for _ in range(10):
            m1 = random.randint(1, 5); v1 = random.randint(2, 10); m2 = m1 * 2
            A(build_choice(f"Тело массой {m1} кг со скоростью {v1} м/с сталкивается с покоящимся телом массой {m2} кг, они движутся вместе. Какова их общая скорость?",
                           f"{m1*v1/(m1+m2):g} м/с".replace(".", ","), [f"{m1*v1/(m1+m2):g} м/с".replace(".", ","), f"{v1} м/с", f"{m1*v1} м/с", f"{v1/2:g} м/с".replace(".", ",")],
                           f"Закон сохранения импульса: v = m₁v₁/(m₁+m₂) = {m1}·{v1}/{m1+m2} = {m1*v1/(m1+m2):g} м/с.", "Импульс", [3, 4]))
        return P
    if grade in (10, 11):
        import math as _m
        q1 = 1 if grade == 10 else 3
        q2 = 2 if grade == 10 else 4
        for _ in range(14):
            v0 = random.randint(5, 30); a = random.randint(1, 4); t = random.randint(2, 10)
            A(build_choice(f"Скорость тела изменяется по закону v = {v0} + {a}t. Какой путь пройдёт тело за {t} с?", f"{v0*t + a*t*t//2} м",
                           [f"{v0*t + a*t*t//2} м", f"{v0*t} м", f"{a*t*t} м", f"{v0*t + a*t} м"], f"S = v₀t + at²/2 = {v0}·{t} + {a}·{t*t}/2 = {v0*t + a*t*t//2} м.", "Кинематика", [1, 2]))
        for _ in range(14):
            m = random.randint(1, 10); g = 10; h = random.randint(2, 20)
            A(build_choice(f"Тело массой {m} кг падает с высоты {h} м. Какова его кинетическая энергия у поверхности (g = 10 Н/кг)?", f"{m*g*h} Дж",
                           [f"{m*g*h} Дж", f"{m*g*h//2} Дж", f"{m*h} Дж", f"{m*g} Дж"], f"По закону сохранения энергии Ek = Ep = mgh = {m*g*h} Дж.", "Энергия", [1, 2]))
        for _ in range(12):
            k = random.randint(50, 500); x = random.choice([0.02, 0.05, 0.1])
            A(build_choice(f"Жёсткость пружины {k} Н/м, удлинение {str(x).replace('.',',')} м. Чему равна сила упругости?", f"{k*x:g} Н".replace(".", ","),
                           [f"{k*x:g} Н".replace(".", ","), f"{k//x:g} Н".replace(".", ","), f"{k+x} Н", f"{k*x*2:g} Н".replace(".", ",")], f"F = kx = {k}·{x} = {k*x:g} Н (закон Гука).", "Динамика", [1, 2]))
        for _ in range(12):
            mu = random.choice([0.1, 0.2, 0.5]); m = random.randint(2, 20)
            A(build_choice(f"Коэффициент трения {str(mu).replace('.',',')}, масса тела {m} кг (g = 10 Н/кг). Чему равна сила трения скольжения?", f"{mu*m*10:g} Н".replace(".", ","),
                           [f"{mu*m*10:g} Н".replace(".", ","), f"{m*10:g} Н", f"{mu*m:g} Н".replace(".", ","), f"{mu*10:g} Н".replace(".", ",")], f"Fтр = μN = μmg = {mu}·{m}·10 = {mu*m*10:g} Н.", "Динамика", [3, 4]))
        for _ in range(12):
            v = random.randint(5, 30); R = random.choice([10, 20, 50, 100])
            A(build_choice(f"Тело движется по окружности радиуса {R} м со скоростью {v} м/с. Чему равно центростремительное ускорение?", f"{v*v/R:g} м/с²".replace(".", ","),
                           [f"{v*v/R:g} м/с²".replace(".", ","), f"{v/R:g} м/с²".replace(".", ","), f"{v*R:g} м/с²".replace(".", ","), f"{v*v*R:g} м/с²".replace(".", ",")],
                           f"a = v²/R = {v*v}/{R} = {v*v/R:g} м/с².", "Движение по окружности", [3, 4]))
        for _ in range(12):
            m1 = random.randint(1, 9); m2 = random.randint(1, 9); r = random.randint(1, 5)
            A(build_choice(f"Два тела массами {m1} кг и {m2} кг находятся на расстоянии {r} м. Во сколько раз увеличится сила притяжения, если расстояние уменьшить в 2 раза?", "в 4 раза",
                           ["в 4 раза", "в 2 раза", "не изменится", "в 8 раз"], f"F ~ 1/r²: при уменьшении r вдвое сила возрастает в 2² = 4 раза.", "Гравитация", [3, 4]))
        for _ in range(12):
            T = random.choice([2, 4, 5, 10]); A_ = random.randint(2, 20)
            A(build_choice(f"Амплитуда колебаний {A_} см, период {T} с. Какой путь пройдёт тело за один период?", f"{4*A_} см", [f"{4*A_} см", f"{A_} см", f"{2*A_} см", f"{A_*T} см"],
                           "За период тело проходит 4 амплитуды.", "Колебания", [1, 2]))
        for _ in range(12):
            l = random.choice([0.25, 1, 4])
            T = 2 * _m.pi * _m.sqrt(l / 9.8)
            A(build_choice(f"Чему примерно равен период математического маятника длиной {str(l).replace('.',',')} м (g ≈ 9,8 м/с²)?", f"{T:.2f} с".replace(".", ","),
                           [f"{T:.2f} с".replace(".", ","), f"{2*T:.2f} с".replace(".", ","), f"{T/2:.2f} с".replace(".", ","), f"{l} с".replace(".", ",")],
                           f"T = 2π√(l/g) = 2π√({l}/9,8) ≈ {T:.2f} с.", "Колебания", [1, 2]))
        for _ in range(10):
            p = random.randint(100, 400) * 1000; V = random.randint(1, 5); T = random.choice([200, 300, 400])
            nu = random.randint(1, 5)
            A(build_input(f"Сколько молекул в {nu} моль газа (NA = 6·10²³ моль⁻¹)? Ответ запиши как число ×10²³, например 12.", nu * 6, f"N = ν·NA = {nu}·6·10²³ = {nu*6}·10²³.", "МКТ", [1, 2]))
        for _ in range(10):
            nu = random.randint(1, 4); T = random.choice([200, 300, 400]); R = 8.31
            A(build_choice(f"Давление идеального газа при ν = {nu} моль, T = {T} К и V = 1 м³ (R = 8,31 Дж/(моль·К)) примерно равно:", f"{round(nu*R*T/1000,1)} кПа".replace(".", ","),
                           [f"{round(nu*R*T/1000,1)} кПа".replace(".", ","), f"{round(nu*R*T,1)} Па".replace(".", ","), f"{round(nu*T,1)} кПа".replace(".", ","), f"{round(R*T,1)} кПа".replace(".", ",")],
                           f"Уравнение Менделеева–Клапейрона: p = νRT/V = {nu}·8,31·{T}/1 = {round(nu*R*T)} Па = {round(nu*R*T/1000,1)} кПа.", "МКТ", [3, 4]))
        for _ in range(10):
            q = random.randint(1, 9); E = random.randint(2, 20)
            A(build_choice(f"На заряд {q}·10⁻⁶ Кл в электрическом поле действует сила {q*E}·10⁻⁶ Н. Чему равна напряжённость поля?", f"{E} Н/Кл", [f"{E} Н/Кл", f"{q*E} Н/Кл", f"{E//q} Н/Кл", f"{q+E} Н/Кл"], f"E = F/q = {q*E}·10⁻⁶/{q}·10⁻⁶ = {E} Н/Кл.", "Электростатика", [3, 4]))
        for _ in range(10):
            C = random.randint(2, 20); U = random.randint(2, 20)
            A(build_choice(f"Ёмкость конденсатора {C} мкФ, напряжение {U} В. Чему равен заряд конденсатора?", f"{C*U} мкКл", [f"{C*U} мкКл", f"{C//U} мкКл", f"{C+U} мкКл", f"{C*U*2} мкКл"], f"q = CU = {C}·{U} = {C*U} мкКл.", "Электростатика", [3, 4]))
        for _ in range(10):
            A(build_choice("Как формулируется закон сохранения механической энергии?", "в замкнутой системе, где действуют только консервативные силы, полная механическая энергия постоянна",
                           ["в замкнутой системе, где действуют только консервативные силы, полная механическая энергия постоянна", "энергия всегда уменьшается", "кинетическая энергия постоянна", "потенциальная энергия равна нулю"],
                           "Ek + Ep = const при отсутствии диссипативных сил.", "Энергия", [1, 2]))
        return P
    return P


# ============================================================ ХИМИЯ (расчётные задачи)
def gen_chem(grade, seed=0):
    random.seed(seed)
    P = []
    A = P.append
    MR = {"H2O": 18, "CO2": 44, "NaCl": 58.5, "HCl": 36.5, "H2SO4": 98, "NaOH": 40, "CaCO3": 100, "O2": 32, "N2": 28,
          "CH4": 16, "C2H6": 30, "CuO": 80, "Fe2O3": 160, "KOH": 56, "HNO3": 63, "NH3": 17, "SO2": 64, "MgO": 40, "CaO": 56}
    if grade == 8:
        for _ in range(18):
            f = random.choice(list(MR.keys()))
            A(build_choice(f"Вычисли относительную молекулярную массу Mr({f}).", str(MR[f]).replace(".", ","),
                           [str(MR[f]).replace(".", ","), str(MR[f] * 2).replace(".", ","), str(round(MR[f] / 2, 1)).replace(".", ","), str(MR[f] + 1).replace(".", ",")],
                           f"Mr складывается из атомных масс: Mr({f}) = {str(MR[f]).replace('.', ',')}.", "Атом и молекула", [1, 2]))
        for _ in range(14):
            n = random.randint(1, 5); f = random.choice(["H2O", "CO2", "NaCl", "O2", "CH4", "NaOH"])
            A(build_choice(f"Чему равна масса {n} моль {f}?", f"{n*MR[f]:g} г".replace(".", ","), [f"{n*MR[f]:g} г".replace(".", ","), f"{MR[f]/n:g} г".replace(".", ","), f"{n+MR[f]:g} г", f"{n*MR[f]*2:g} г".replace(".", ",")],
                           f"m = n·M = {n} · {MR[f]} = {n*MR[f]:g} г.", "Количество вещества", [1, 2]))
        for _ in range(14):
            m = random.choice([18, 36, 44, 88, 9, 58.5, 117, 40, 80])
            f = random.choice(["H2O", "CO2", "NaCl", "NaOH", "CuO"])
            n = round(m / MR[f], 2)
            A(build_choice(f"Сколько моль составляет {str(m).replace('.',',')} г {f}?", f"{n:g} моль".replace(".", ","),
                           [f"{n:g} моль".replace(".", ","), f"{m*MR[f]:g} моль".replace(".", ","), f"{m+MR[f]:g} моль", f"{MR[f]/m:g} моль".replace(".", ",")],
                           f"n = m/M = {m}/{MR[f]} = {n:g} моль.", "Количество вещества", [1, 2]))
        for _ in range(12):
            n = random.randint(1, 4)
            A(build_choice(f"Сколько молекул содержится в {n} моль вещества (NA = 6·10²³)?", f"{6*n}·10²³", [f"{6*n}·10²³", f"{6/n}·10²³".replace(".", ","), f"{n}·10²³", f"{6*n}·10²⁴"],
                           f"N = n·NA = {n}·6·10²³ = {6*n}·10²³.", "Количество вещества", [3, 4]))
        for _ in range(12):
            n = random.randint(1, 5)
            A(build_choice(f"Какой объём (н.у.) занимают {n} моль газа?", f"{22.4*n:g} л".replace(".", ","), [f"{22.4*n:g} л".replace(".", ","), f"{22.4/n:g} л".replace(".", ","), f"{n} л", f"{24*n} л".replace(".", ",")],
                           f"V = n·Vm = {n} · 22,4 = {22.4*n:g} л (Vm = 22,4 л/моль при н.у.).", "Количество вещества", [3, 4]))
        for _ in range(12):
            m_salt = random.randint(5, 50); m_water = random.randint(50, 250)
            w = round(m_salt / (m_salt + m_water) * 100, 1)
            A(build_choice(f"В {m_water} г воды растворили {m_salt} г соли. Какова массовая доля соли в растворе (%)?", f"{w:g}".replace(".", ","),
                           [f"{w:g}".replace(".", ","), f"{m_salt/m_water*100:.1f}".replace(".", ","), f"{m_salt}", f"{m_salt+m_water}"],
                           f"w = m(в-ва)/m(р-ра) = {m_salt}/({m_salt}+{m_water}) = {m_salt}/{m_salt+m_water} ≈ {w:g}%.", "Растворы", [3, 4]))
        for _ in range(12):
            m_r = random.choice([100, 200, 500]); pct = random.choice([5, 10, 20, 25])
            A(build_input(f"Сколько граммов соли нужно, чтобы приготовить {m_r} г {pct}% раствора?", m_r * pct // 100, f"m = {m_r} · {pct}/100 = {m_r*pct//100} г.", "Растворы", [3, 4]))
        for _ in range(10):
            A(build_choice("Заряд ядра атома определяется:", "числом протонов", ["числом протонов", "числом нейтронов", "числом нейтронов и протонов", "атомной массой"],
                           "Заряд ядра = номер элемента = число протонов.", "Строение атома", [1, 2]))
        for _ in range(10):
            Z = random.choice([3, 6, 8, 11, 12, 17, 19, 20])
            A(build_choice(f"Сколько электронов в атоме с зарядом ядра +{Z}?", Z, [Z, Z * 2, Z - 1, Z + 1], "В нейтральном атоме число электронов равно заряду ядра.", "Строение атома", [1, 2]))
        for _ in range(10):
            A(build_choice("Химическая связь между атомами с большой разностью электроотрицательностей (например, Na и Cl):", "ионная", ["ионная", "ковалентная неполярная", "металлическая", "водородная"],
                           "При большой разности ЭО происходит полный переход электрона — связь ионная.", "Химическая связь", [3, 4]))
        for _ in range(10):
            A(build_choice("Связь в молекуле Cl₂:", "ковалентная неполярная", ["ковалентная неполярная", "ковалентная полярная", "ионная", "металлическая"],
                           "Атомы одинаковы, общая электронная пара не смещена.", "Химическая связь", [3, 4]))
        # --- расчёты: молярная масса, количество вещества, объём, валентность ---
        M8 = {"H₂O": 18, "CO₂": 44, "NaCl": 58.5, "HCl": 36.5, "H₂SO₄": 98, "NaOH": 40, "CaCO₃": 100,
              "O₂": 32, "N₂": 28, "CH₄": 16, "CuO": 80, "Fe₂O₃": 160, "KOH": 56, "HNO₃": 63, "NH₃": 17,
              "SO₂": 64, "MgO": 40, "CaO": 56, "H₂": 2, "Cl₂": 71, "Al₂O₃": 102, "KCl": 74.5, "CuSO₄": 160,
              "H₃PO₄": 98, "Na₂CO₃": 106, "Ca(OH)₂": 74, "FeS": 88, "ZnO": 81}
        for i, (f, mr) in enumerate(M8.items()):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x for x in M8.values() if x != mr]
            random.shuffle(w)
            A(build_choice(f"Вычисли относительную молекулярную массу Mr({f}).", f"{mr:g}".replace(".", ","),
                           [f"{x:g}".replace(".", ",") for x in w[:3]],
                           f"Mr({f}) = {mr:g} (сумма атомных масс с учётом индексов).".replace(".", ","), "Атом и молекула", q))
        for _ in range(14):
            f = random.choice(list(M8.keys())); n = random.randint(1, 6)
            A(build_input(f"Чему равна масса {n} моль вещества {f} (г)?", round(n * M8[f], 1),
                          f"m = n·M = {n} · {M8[f]:g} = {round(n*M8[f],1)} г.", "Количество вещества", [1, 2]))
        for _ in range(14):
            f = random.choice(list(M8.keys())); n = random.randint(1, 6)
            A(build_input(f"Сколько молекул (в единицах 10²³) содержится в {n} моль вещества (NA = 6·10²³)?", 6 * n,
                          f"N = n·NA = {n}·6·10²³ = {6*n}·10²³ молекул.", "Количество вещества", [1, 2]))
        for _ in range(14):
            n = random.randint(1, 6)
            A(build_input(f"Какой объём (н. у.) занимают {n} моль газа (л)?", round(22.4 * n, 1),
                          f"V = n·Vm = {n} · 22,4 = {round(22.4*n,1)} л.", "Количество вещества", [3, 4]))
        VAL = [("HCl", "Cl", "I"), ("H₂O", "O", "II"), ("NH₃", "N", "III"), ("CH₄", "C", "IV"),
               ("CO₂", "C", "IV"), ("SO₃", "S", "VI"), ("H₂S", "S", "II"), ("NaCl", "Cl", "I"),
               ("CaO", "Ca", "II"), ("Al₂O₃", "Al", "III"), ("Fe₂O₃", "Fe", "III"), ("N₂O₅", "N", "V"),
               ("P₂O₅", "P", "V"), ("SiO₂", "Si", "IV"), ("MgO", "Mg", "II"), ("K₂O", "K", "I")]
        for i, (f, el, v) in enumerate(VAL):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x for x in ["I", "II", "III", "IV", "V", "VI", "VII"] if x != v]
            random.shuffle(w)
            A(build_choice(f"Определи валентность элемента {el} в соединении {f} (валентность H = I, O = II).", v, w[:3],
                           f"В {f} валентность {el} равна {v}.", "Валентность", q))
        EQ8 = [("2H₂ + O₂ = 2H₂O", "2"), ("CaCO₃ = CaO + CO₂", "1"), ("Zn + 2HCl = ZnCl₂ + H₂", "2"),
               ("2KClO₃ = 2KCl + 3O₂", "3"), ("N₂ + 3H₂ = 2NH₃", "3"), ("CuO + H₂ = Cu + H₂O", "1"),
               ("2Mg + O₂ = 2MgO", "1"), ("Fe + S = FeS", "1"), ("CaO + H₂O = Ca(OH)₂", "1"), ("SO₃ + H₂O = H₂SO₄", "1")]
        for i, (eq, koef) in enumerate(EQ8):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            A(build_choice(f"В уравнении {eq} коэффициент перед вторым реагентом равен:", koef,
                           [x for x in ["1", "2", "3", "4", "5"] if x != koef],
                           f"Уравнение {eq}: искомый коэффициент равен {koef}.", "Химические уравнения", q))
        PHEN = [("горение свечи", "химическое"), ("таяние льда", "физическое"), ("ржавление железа", "химическое"),
                ("испарение воды", "физическое"), ("скисание молока", "химическое"), ("плавление металла", "физическое"),
                ("гниение листьев", "химическое"), ("растворение сахара в воде", "физическое"),
                ("фотосинтез", "химическое"), ("дробление камня", "физическое"),
                ("горение древесины", "химическое"), ("замерзание воды", "физическое")]
        for i, (ph, kind) in enumerate(PHEN):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            A(build_choice(f"Явление «{ph}» — это …", kind + " явление", [x + " явление" for x in ["химическое", "физическое"] if x != kind],
                           f"{ph} — {kind} явление" + (" (образуются новые вещества)." if kind == "химическое" else " (состав вещества не меняется)."),
                           "Физические и химические явления", q))
        LAB = [("пробирка", "тонкостенный сосуд для небольших объёмов реакций"),
               ("колба", "сосуд для смешивания и нагревания жидкостей"),
               ("мензурка", "цилиндр для измерения объёма жидкости"),
               ("воронка", "приспособление для переливания и фильтрования"),
               ("спиртовка", "прибор для нагревания"),
               ("шпатель", "ложечка для взятия твёрдых веществ"),
               ("фильтр", "бумага для отделения осадка от жидкости"),
               ("штатив", "приспособление для закрепления посуды")]
        for i, (t, d) in enumerate(LAB):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x[1] for x in LAB if x[0] != t]
            random.shuffle(w)
            A(build_choice(f"Что такое {t} в химической лаборатории?", d, w[:3], f"{t} — {d}.", "Лабораторное оборудование", q))
        A(build_choice("Чистое вещество — это …", "вещество, состоящее из частиц одного вида",
                       ["вещество, состоящее из частиц одного вида", "смесь нескольких веществ", "любая жидкость", "только металлы"],
                       "Пример: дистиллированная вода.", "Вещества и смеси", [1, 2]))
        A(build_choice("Смесь — это …", "сочетание двух и более веществ", ["сочетание двух и более веществ",
                       "одно вещество", "атом одного элемента", "молекула воды"], "Примеры: воздух, молоко, почва.", "Вещества и смеси", [1, 2]))
        A(build_choice("Какой способ разделения подходит для смеси песка и воды?", "фильтрование", ["фильтрование",
                       "выпаривание", "действие магнитом", "перегонка"], "Песок остаётся на фильтре.", "Вещества и смеси", [3, 4]))
        A(build_choice("Как разделить смесь железных опилок и серы?", "магнитом", ["магнитом", "фильтрованием",
                       "выпариванием", "отстаиванием"], "Железо притягивается магнитом.", "Вещества и смеси", [3, 4]))
        A(build_choice("Как из раствора соли получить соль?", "выпариванием", ["выпариванием", "фильтрованием",
                       "магнитом", "отстаиванием"], "Вода испаряется, соль остаётся.", "Вещества и смеси", [3, 4]))
        return P
    if grade == 9:
        for _ in range(14):
            eq = random.choice([("2H₂ + O₂ = 2H₂O", "2", "соединения"), ("CaCO₃ = CaO + CO₂", "1", "разложения"),
                                ("Zn + 2HCl = ZnCl₂ + H₂", "1", "замещения"), ("NaOH + HCl = NaCl + H₂O", "1", "обмена"),
                                ("2KClO₃ = 2KCl + 3O₂", "2", "разложения"), ("N₂ + 3H₂ = 2NH₃", "3", "соединения"),
                                ("CuO + H₂ = Cu + H₂O", "1", "замещения"), ("AgNO₃ + NaCl = AgCl + NaNO₃", "1", "обмена")])
            A(build_choice(f"К какому типу относится реакция: {eq[0]}?", f"реакция {eq[2]}", [f"реакция {eq[2]}", "реакция соединения", "реакция разложения", "реакция обмена"],
                           f"Тип реакции — {eq[2]}.", "Классификация реакций", [1, 2]))
        for _ in range(12):
            A(build_choice("Коэффициент перед кислородом в уравнении 2H₂ + O₂ = 2H₂O равен:", "1", ["1", "2", "3", "4"], "Уравнение уже уравновешено: 2H₂ + 1O₂ = 2H₂O.", "Классификация реакций", [1, 2]))
        for _ in range(14):
            m = random.choice([2, 4, 6, 8])
            A(build_input(f"Сколько моль воды образуется при сгорании {m} моль водорода (2H₂ + O₂ = 2H₂O)?", m, f"По уравнению из 2 моль H₂ получается 2 моль H₂O, значит из {m} моль — {m} моль.", "Расчёты по уравнениям", [1, 2]))
        for _ in range(12):
            n = random.randint(1, 4)
            A(build_choice(f"Какой объём CO₂ (н.у.) выделится при разложении {n} моль CaCO₃ (CaCO₃ = CaO + CO₂)?", f"{22.4*n:g} л".replace(".", ","),
                           [f"{22.4*n:g} л".replace(".", ","), f"{22.4/n:g} л".replace(".", ","), f"{n} л", f"{44*n} л"],
                           f"1 моль CaCO₃ → 1 моль CO₂; V = {n}·22,4 = {22.4*n:g} л.", "Расчёты по уравнениям", [3, 4]))
        for _ in range(12):
            A(build_choice("Оксид, который реагирует и с кислотами, и со щелочами, называется:", "амфотерным", ["амфотерным", "кислотным", "основным", "несолеобразующим"],
                           "Примеры амфотерных оксидов: ZnO, Al₂O₃.", "Оксиды, кислоты, основания", [1, 2]))
        for _ in range(12):
            f = random.choice([("HCl", "кислота"), ("NaOH", "основание"), ("NaCl", "соль"), ("H₂SO₄", "кислота"), ("KOH", "основание"), ("CaCO₃", "соль"), ("CuO", "основный оксид"), ("SO₃", "кислотный оксид")])
            A(build_choice(f"К какому классу относится вещество {f[0]}?", f[1], ["кислота", "основание", "соль", "оксид"], f"{f[0]} — это {f[1]}.", "Оксиды, кислоты, основания", [1, 2]))
        for _ in range(12):
            A(build_choice("Раствор, в котором [H⁺] > [OH⁻], имеет среду:", "кислую", ["кислую", "щелочную", "нейтральную", "не определить"], "Лакмус в такой среде краснеет.", "Электролиты", [3, 4]))
        for _ in range(12):
            A(build_choice("Какой ион образуется при диссоциации кислот?", "H⁺", ["H⁺", "OH⁻", "Cl⁻", "Na⁺"], "Кислоты диссоциируют с образованием катионов водорода.", "Электролиты", [3, 4]))
        for _ in range(12):
            m = random.choice([100, 200, 500, 400]); pct = random.choice([10, 20, 5, 25])
            A(build_input(f"Сколько граммов вещества содержится в {m} г {pct}% раствора?", m * pct // 100, f"m(в-ва) = m(р-ра)·w = {m}·{pct}/100 = {m*pct//100} г.", "Растворы", [3, 4]))
        for _ in range(10):
            el = random.choice([("Li", "+1"), ("Mg", "+2"), ("Al", "+3"), ("S в H₂S", "−2"), ("N в NH₃", "−3"), ("C в CO₂", "+4")])
            A(build_choice(f"Степень окисления {el[0]}:", el[1], ["+1", "+2", "+3", "−2", "+4", "−3", "0"], f"Степень окисления {el[0]} равна {el[1]}.", "ОВР", [3, 4]))
        # --- расчёты и факты 9 класса ---
        M9 = {"NaCl": 58.5, "HCl": 36.5, "H₂SO₄": 98, "NaOH": 40, "CaCO₃": 100, "KOH": 56, "HNO₃": 63,
              "CuSO₄": 160, "Na₂CO₃": 106, "Ca(OH)₂": 74, "FeCl₃": 162.5, "ZnSO₄": 161, "Al₂(SO₄)₃": 342,
              "BaCl₂": 208, "AgNO₃": 170, "MgO": 40, "SO₂": 64, "NH₃": 17}
        for i, (f, mr) in enumerate(M9.items()):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x for x in M9.values() if x != mr]
            random.shuffle(w)
            A(build_choice(f"Молярная масса вещества {f} (г/моль):", f"{mr:g}".replace(".", ","),
                           [f"{x:g}".replace(".", ",") for x in w[:3]], f"M({f}) = {mr:g} г/моль.", "Расчёты", q))
        for _ in range(12):
            f = random.choice(list(M9.keys())); n = random.randint(1, 4)
            A(build_input(f"Вычисли массу {n} моль {f} (г).", round(n * M9[f], 1),
                          f"m = n·M = {n} · {M9[f]:g} = {round(n*M9[f],1)} г.", "Расчёты", [1, 2]))
        for _ in range(12):
            m_r = random.choice([50, 100, 150, 200, 250, 400, 500]); w_ = random.choice([2, 5, 10, 20, 25, 40])
            A(build_input(f"Сколько граммов вещества нужно для приготовления {m_r} г {w_}%-ного раствора?", m_r * w_ // 100,
                          f"m = {m_r} · {w_}/100 = {m_r*w_//100} г.", "Растворы", [1, 2]))
        for _ in range(12):
            n = random.randint(1, 6)
            A(build_input(f"Объём (н. у.) {n} моль газа (л):", round(22.4 * n, 1), f"V = n·22,4 = {round(22.4*n,1)} л.", "Расчёты", [3, 4]))
        EQ9 = [("2Na + 2H₂O = 2NaOH + H₂", "замещения"), ("CaO + H₂O = Ca(OH)₂", "соединения"),
               ("2H₂O₂ = 2H₂O + O₂", "разложения"), ("HCl + NaOH = NaCl + H₂O", "обмена"),
               ("CuSO₄ + Fe = FeSO₄ + Cu", "замещения"), ("CaCO₃ = CaO + CO₂", "разложения"),
               ("Na₂O + CO₂ = Na₂CO₃", "соединения"), ("AgNO₃ + NaCl = AgCl + NaNO₃", "обмена"),
               ("Zn + 2HCl = ZnCl₂ + H₂", "замещения"), ("2Al + 3Cl₂ = 2AlCl₃", "соединения"),
               ("Cu(OH)₂ = CuO + H₂O", "разложения"), ("BaCl₂ + Na₂SO₄ = BaSO₄ + 2NaCl", "обмена"),
               ("Fe₂O₃ + 3H₂ = 2Fe + 3H₂O", "замещения"), ("SO₃ + H₂O = H₂SO₄", "соединения"),
               ("K₂O + 2HNO₃ = 2KNO₃ + H₂O", "обмена"), ("2KClO₃ = 2KCl + 3O₂", "разложения")]
        for i, (eq, typ) in enumerate(EQ9):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x for x in ["соединения", "разложения", "замещения", "обмена"] if x != typ]
            A(build_choice(f"К какому типу относится реакция {eq}?", f"реакция {typ}", [f"реакция {x}" for x in w],
                           f"Это реакция {typ}.", "Классификация реакций", q))
        ACT = [("цинк в растворе CuSO₄", "вытеснит медь"), ("медь в растворе ZnSO₄", "не вытеснит цинк"),
               ("железо в растворе CuSO₄", "вытеснит медь"), ("цинк в соляной кислоте", "выделит водород"),
               ("медь в соляной кислоте", "не реагирует"), ("магний в растворе FeCl₂", "вытеснит железо"),
               ("серебро в растворе CuSO₄", "не вытеснит медь"), ("алюминий в растворе AgNO₃", "вытеснит серебро"),
               ("натрий в воде", "бурно реагирует с выделением водорода"), ("золото в соляной кислоте", "не реагирует")]
        for i, (sit, res) in enumerate(ACT):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x[1] for x in ACT if x[1] != res]
            random.shuffle(w)
            A(build_choice(f"Что произойдёт: {sit}?", res, list(dict.fromkeys(w))[:3],
                           f"По ряду активности металлов: {sit} — {res}.", "Ряд активности металлов", q))
        ION = [("Ba²⁺ и SO₄²⁻", "BaSO₄ (белый осадок)"), ("Ag⁺ и Cl⁻", "AgCl (белый творожистый осадок)"),
               ("H⁺ и OH⁻", "H₂O (реакция нейтрализации)"), ("Ca²⁺ и CO₃²⁻", "CaCO₃ (белый осадок)"),
               ("H⁺ и CO₃²⁻", "CO₂ и H₂O (выделение газа)"), ("Fe³⁺ и OH⁻", "Fe(OH)₃ (бурый осадок)"),
               ("Cu²⁺ и OH⁻", "Cu(OH)₂ (голубой осадок)"), ("Mg²⁺ и OH⁻", "Mg(OH)₂ (белый осадок)"),
               ("Na⁺ и Cl⁻", "реакция обмена не идёт"), ("K⁺ и NO₃⁻", "реакция обмена не идёт")]
        for i, (ions, res) in enumerate(ION):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x[1] for x in ION if x[0] != ions]
            random.shuffle(w)
            A(build_choice(f"Что образуется при смешивании растворов, содержащих ионы {ions}?", res,
                           list(dict.fromkeys(w))[:3], f"Ионное уравнение даёт {res}.", "Ионные уравнения", q))
        EL9 = [("кислород", "газ, поддерживающий горение и дыхание"), ("водород", "самый лёгкий газ, горит"),
               ("хлор", "жёлто-зелёный ядовитый газ"), ("сера", "жёлтый порошок, горит синим пламенем"),
               ("фосфор", "бывает белым и красным"), ("азот", "инертный газ, 78% воздуха"),
               ("углерод", "образует алмаз, графит и фуллерены"), ("кремний", "полупроводник, основа песка"),
               ("железо", "магнитный металл, ржавеет на воздухе"), ("алюминий", "лёгкий металл с защитной плёнкой"),
               ("натрий", "мягкий щелочной металл, хранится под керосином"), ("кальций", "щелочноземельный металл"),
               ("медь", "красноватый пластичный металл, проводник"), ("ртуть", "жидкий металл при комнатной температуре")]
        for i, (el, d) in enumerate(EL9):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x[1] for x in EL9 if x[0] != el]
            random.shuffle(w)
            A(build_choice(f"Что верно для простого вещества «{el}»?", d, w[:3], f"{el}: {d}.", "Вещества и их свойства", q))
            w2 = [x[0] for x in EL9 if x[1] != d]
            random.shuffle(w2)
            A(build_choice(f"О каком веществе сказано: «{d}»?", el, w2[:3], f"Это {el}.", "Вещества и их свойства", q))
        CLS = [("HCl", "кислота"), ("H₂SO₄", "кислота"), ("NaOH", "основание (щёлочь)"), ("Ca(OH)₂", "основание (щёлочь)"),
               ("Cu(OH)₂", "нерастворимое основание"), ("NaCl", "соль"), ("CaCO₃", "соль"), ("K₂SO₄", "соль"),
               ("CO₂", "кислотный оксид"), ("SO₃", "кислотный оксид"), ("CaO", "основный оксид"), ("Na₂O", "основный оксид"),
               ("Al₂O₃", "амфотерный оксид"), ("ZnO", "амфотерный оксид"), ("CO", "несолеобразующий оксид")]
        for i, (f, c) in enumerate(CLS):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x[1] for x in CLS if x[1] != c]
            A(build_choice(f"К какому классу относится вещество {f}?", c, list(dict.fromkeys(w))[:3],
                           f"{f} — {c}.", "Классы неорганических веществ", q))
        IND = [("лакмус в кислоте", "краснеет"), ("лакмус в щёлочи", "синеет"), ("фенолфталеин в щёлочи", "становится малиновым"),
               ("фенолфталеин в кислоте", "остаётся бесцветным"), ("метилоранж в кислоте", "краснеет"),
               ("метилоранж в щёлочи", "желтеет"), ("лакмус в нейтральной среде", "остаётся фиолетовым")]
        for i, (sit, res) in enumerate(IND):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x[1] for x in IND if x[0] != sit]
            random.shuffle(w)
            A(build_choice(f"Что произойдёт: {sit}?", res, list(dict.fromkeys(w))[:3],
                           f"Индикатор: {sit} — {res}.", "Индикаторы", q))
        A(build_choice("Электролит — это вещество, раствор или расплав которого …", "проводит электрический ток",
                       ["проводит электрический ток", "не проводит ток", "всегда твёрдое", "является газом"],
                       "Электролиты диссоциируют на ионы.", "Электролиты", [1, 2]))
        A(build_choice("Какое вещество НЕ является электролитом?", "спирт", ["спирт", "поваренная соль", "соляная кислота", "щёлочь"],
                       "Раствор спирта не проводит ток.", "Электролиты", [1, 2]))
        A(build_choice("Диссоциация — это …", "распад электролита на ионы в растворе", ["распад электролита на ионы в растворе",
                       "соединение ионов", "испарение воды", "реакция обмена"], "Процесс обратим для слабых электролитов.", "Электролиты", [3, 4]))
        return P
    if grade == 10:
        form = [("CH₄", "метан", "алкан"), ("C₂H₆", "этан", "алкан"), ("C₃H₈", "пропан", "алкан"), ("C₄H₁₀", "бутан", "алкан"),
                ("C₂H₄", "этен", "алкен"), ("C₃H₆", "пропен", "алкен"), ("C₂H₂", "этин", "алкин"), ("C₃H₄", "пропин", "алкин"),
                ("C₆H₆", "бензол", "арен"), ("CH₃OH", "метанол", "спирт"), ("C₂H₅OH", "этанол", "спирт")]
        for _ in range(20):
            f, name, cls = random.choice(form)
            A(build_choice(f"К какому классу относится органическое вещество {f}?", cls, ["алкан", "алкен", "алкин", "арен", "спирт"], f"{f} — {name}, класс: {cls}.", "Классы органических веществ", [1, 2]))
        for _ in range(14):
            n = random.randint(1, 8)
            A(build_choice(f"Общая формула алканов CₙH₂ₙ₊₂. Сколько атомов водорода в алкане с n = {n}?", 2 * n + 2, [2 * n + 2, 2 * n, 2 * n - 2, n + 2], f"2·{n} + 2 = {2*n+2}.", "Углеводороды", [1, 2]))
        for _ in range(14):
            n = random.randint(2, 8)
            A(build_choice(f"Сколько атомов водорода в алкене CₙH₂ₙ при n = {n}?", 2 * n, [2 * n, 2 * n + 2, 2 * n - 2, n], f"Общая формула алкенов CₙH₂ₙ → 2·{n} = {2*n}.", "Углеводороды", [1, 2]))
        for _ in range(12):
            A(build_choice("Гомолог — это вещество, которое отличается от данного на:", "одну или несколько групп CH₂", ["одну или несколько групп CH₂", "одну двойную связь", "один атом водорода", "функциональную группу"],
                           "Гомологи имеют одинаковое строение и отличаются на группу CH₂.", "Гомологи и изомеры", [1, 2]))
        for _ in range(12):
            A(build_choice("Изомеры — это вещества с:", "одинаковой формулой, но разным строением", ["одинаковой формулой, но разным строением", "разной формулой", "одинаковым строением", "одинаковой молярной массой и строением"],
                           "Изомеры: одинаковый состав — разное строение и свойства.", "Гомологи и изомеры", [1, 2]))
        for _ in range(12):
            n = random.choice([4, 5, 6])
            A(build_choice(f"Сколько структурных изомеров (без учёта циклических) у алкана C{n}H{2*n+2}?", {4: 2, 5: 3, 6: 5}[n], [{4: 2, 5: 3, 6: 5}[n], 1, n, 2 * n],
                           f"Для C{n}H{2*n+2} число изомеров — {[4,5,6] and {4:2,5:3,6:5}[n]}.", "Гомологи и изомеры", [3, 4]))
        for _ in range(12):
            A(build_choice("Реакция присоединения водорода к этилену называется:", "гидрирование", ["гидрирование", "дегидрирование", "полимеризация", "замещение"],
                           "C₂H₄ + H₂ → C₂H₆ — гидрирование.", "Химические свойства", [3, 4]))
        for _ in range(12):
            A(build_choice("Качественная реакция на непредельные углеводороды (двойная связь):", "обесцвечивание бромной воды", ["обесцвечивание бромной воды", "реакция с натрием", "горение", "взаимодействие с кислотами"],
                           "Бромная вода обесцвечивается при реакции с алкенами и алкинами.", "Химические свойства", [3, 4]))
        for _ in range(12):
            n = random.randint(1, 6)
            A(build_choice(f"Молярная масса алкана C{n}H{2*n+2} (C = 12, H = 1) равна:", 14 * n + 2, [14 * n + 2, 12 * n, 14 * n, 12 * n + 2], f"M = 12·{n} + 1·{2*n+2} = {14*n+2} г/моль.", "Расчёты", [1, 2]))
        for _ in range(10):
            m = random.choice([16, 30, 44, 58])
            A(build_input(f"Сколько моль составляет {m} г метана… " if False else f"Сколько моль составляет {m} г вещества с M = {m} г/моль?", 1, f"n = m/M = {m}/{m} = 1 моль.", "Расчёты", [1, 2]))
        for _ in range(10):
            A(build_choice("Функциональная группа спиртов:", "−OH", ["−OH", "−COOH", "−NH₂", "−CHO"], "Гидроксильная группа −OH определяет свойства спиртов.", "Кислородсодержащие", [3, 4]))
        for _ in range(10):
            A(build_choice("Функциональная группа карбоновых кислот:", "−COOH", ["−COOH", "−OH", "−CHO", "−CO−"], "Карбоксильная группа −COOH.", "Кислородсодержащие", [3, 4]))
        # --- органика: номенклатура, формулы, молярные массы, горение, изомеры ---
        ALK = ["метан", "этан", "пропан", "бутан", "пентан", "гексан", "гептан", "октан", "нонан", "декан"]
        ALK_names = [(n, i + 1) for i, n in enumerate(ALK)]
        for _ in range(22):
            n = random.randint(1, 10)
            name = ALK[n - 1]
            formula = f"C{n}H{2*n+2}"
            wrong_f = [f"C{n}H{2*n}", f"C{n}H{2*n-2}", f"C{n+1}H{2*n+4}"]
            wrong_n = [x for x in ALK if x != name]
            random.shuffle(wrong_n)
            A(build_choice(f"Как называется алкан с формулой {formula}?", name, wrong_n[:3],
                           f"Алканы: {'; '.join(f'C{i+1} — {ALK[i]}' for i in range(max(0,n-1), min(10,n+2)))}. Формула {formula} — это {name}.",
                           "Углеводороды · номенклатура", [1, 2]))
            A(build_choice(f"Какова формула алкана «{name}»?", formula, wrong_f,
                           f"Общая формула алканов CₙH₂ₙ₊₂; при n = {n}: {formula}.", "Углеводороды · номенклатура", [1, 2]))
            A(build_input(f"Вычисли молярную массу алкана {formula} (C = 12, H = 1). Ответ в г/моль.", 12 * n + (2 * n + 2),
                           f"M = 12·{n} + 1·{2*n+2} = {12*n} + {2*n+2} = {12*n + 2*n + 2} г/моль.", "Углеводороды · расчёты", [1, 2]))
            A(build_choice(f"Сколько атомов водорода в молекуле {formula}?", 2 * n + 2, [2 * n, 2 * n - 2, n + 2, 2 * n + 4],
                           f"Индекс у водорода: {2*n+2}.", "Углеводороды · строение", [3, 4]))
            A(build_choice(f"Сколько атомов углерода в молекуле алкана «{name}»?", n, [n + 1, n - 1 if n > 1 else 2, 2 * n, 10],
                           f"Приставка «{name.split('ан')[0]}-» соответствует {n} атомам углерода.", "Углеводороды · строение", [3, 4]))
        for _ in range(14):
            n = random.randint(2, 8)
            A(build_choice(f"Формула алкена с {n} атомами углерода:", f"C{n}H{2*n}", [f"C{n}H{2*n}", f"C{n}H{2*n+2}", f"C{n}H{2*n-2}", f"C{n}H{n}"],
                           f"Алкены: CₙH₂ₙ (одна двойная связь). При n = {n}: C{n}H{2*n}.", "Углеводороды · классы", [1, 2]))
            A(build_choice(f"Формула алкина с {n} атомами углерода:", f"C{n}H{2*n-2}", [f"C{n}H{2*n-2}", f"C{n}H{2*n}", f"C{n}H{2*n+2}", f"C{n}H{2*n-4}"],
                           f"Алкины: CₙH₂ₙ₋₂ (одна тройная связь). При n = {n}: C{n}H{2*n-2}.", "Углеводороды · классы", [3, 4]))
            A(build_choice(f"По формуле C{n}H{2*n} определите класс углеводорода:", "алкен", ["алкен", "алкан", "алкин", "арен"],
                           "CₙH₂ₙ — общая формула алкенов.", "Углеводороды · классы", [3, 4]))
        for _ in range(14):
            n = random.randint(1, 6)
            o2 = (3 * n + 1) / 2
            o2s = f"{o2:g}".replace(".", ",")
            A(build_choice(f"Сколько моль кислорода потребуется для полного сгорания 1 моль алкана C{n}H{2*n+2}?", o2s,
                           [o2s, f"{n:g}", f"{(3*n):g}", f"{(n+1)/1:g}".replace(".", ",")],
                           f"C{n}H{2*n+2} + {o2s}O₂ → {n}CO₂ + {n+1}H₂O. Коэффициент при O₂ = (3·{n}+1)/2 = {o2s}.",
                           "Горение углеводородов", [3, 4]))
            A(build_input(f"Сколько моль CO₂ образуется при полном сгорании 1 моль алкана C{n}H{2*n+2}?", n,
                          f"По уравнению C{n}H{2*n+2} + O₂ → {n}CO₂ + {n+1}H₂O образуется {n} моль CO₂.", "Горение углеводородов", [3, 4]))
            A(build_input(f"Сколько моль воды образуется при полном сгорании 1 моль алкана C{n}H{2*n+2}?", n + 1,
                          f"Водорода {2*n+2} атома → воды ({2*n+2})/2 = {n+1} моль.", "Горение углеводородов", [3, 4]))
        ISO = [(4, 2), (5, 3), (6, 5), (7, 9), (8, 18)]
        for n, cnt in ISO:
            A(build_choice(f"Сколько структурных изомеров имеет алкан C{n}H{2*n+2} (без учёта пространственных)?", cnt,
                           [cnt, cnt + 1, cnt - 1, n], f"Для C{n}H{2*n+2} известно {cnt} структурных изомера(ов).",
                           "Изомерия", [1, 2]))
        for _ in range(10):
            n = random.randint(2, 6)
            A(build_choice(f"Гомологом пропана C3H8 является …", f"C{n+3}H{2*(n+3)+2}", [f"C{n+3}H{2*(n+3)+2}", "C3H6", "C3H4", "C6H6"],
                           f"Гомологи отличаются на группу CH₂: C3H8 → C{3+1}H{2*4+2} → …", "Гомологи", [1, 2]))
        for _ in range(8):
            A(build_choice("Какую реакцию алкан претерпеть не может?", "реакцию присоединения", ["реакцию присоединения", "горение",
                           "замещение", "крекинг"], "Алканы предельные — двойных связей нет, присоединение невозможно.", "Химические свойства", [3, 4]))
        for _ in range(8):
            A(build_choice("Реакция замещения характерна для …", "алканов (на свету с галогенами)", ["алканов (на свету с галогенами)",
                           "алкенов с бромной водой", "алкинов с водородом", "аренов с кислотами"], "CH₄ + Cl₂ → CH₃Cl + HCl (на свету).", "Химические свойства", [3, 4]))
        for _ in range(8):
            A(build_choice("Полимеризация — это реакция …", "соединения многих молекул мономера в одну большую",
                           ["соединения многих молекул мономера в одну большую", "разложения вещества", "замещения атомов",
                            "обмена между веществами"], "nCH₂=CH₂ → (−CH₂−CH₂−)ₙ.", "Химические свойства", [3, 4]))

        return P
    if grade == 11:
        for _ in range(12):
            A(build_choice("При повышении температуры скорость большинства химических реакций:", "увеличивается", ["увеличивается", "уменьшается", "не изменяется", "сначала уменьшается"],
                           "Правило Вант-Гоффа: при росте температуры на 10 °C скорость возрастает в 2–4 раза.", "Скорость реакции", [1, 2]))
        for _ in range(12):
            g = random.choice([2, 3, 4]); dt = random.choice([10, 20, 30])
            A(build_choice(f"Температурный коэффициент γ = {g}. Во сколько раз возрастёт скорость реакции при повышении температуры на {dt} °C?", g ** (dt // 10),
                           [g ** (dt // 10), g * dt // 10, g, dt // 10], f"v₂/v₁ = γ^(Δt/10) = {g}^{dt//10} = {g**(dt//10)}.", "Скорость реакции", [1, 2]))
        for _ in range(12):
            A(build_choice("Как сместится равновесие N₂ + 3H₂ ⇌ 2NH₃ + Q при повышении давления?", "в сторону продукта (вправо)",
                           ["в сторону продукта (вправо)", "в сторону исходных веществ", "не сместится", "равновесие разрушится"],
                           "При повышении давления равновесие смещается в сторону меньшего числа молей газа: 4 → 2.", "Химическое равновесие", [1, 2]))
        for _ in range(12):
            A(build_choice("Соль, раствор которой имеет щелочную среду:", "Na₂CO₃", ["Na₂CO₃", "NH₄Cl", "KNO₃", "AlCl₃"],
                           "Na₂CO₃ — соль сильного основания и слабой кислоты: гидролиз по аниону, среда щелочная.", "Гидролиз", [3, 4]))
        for _ in range(12):
            A(build_choice("Соль, раствор которой имеет кислую среду:", "NH₄Cl", ["NH₄Cl", "NaCl", "K₂SO₄", "Na₂CO₃"],
                           "NH₄Cl — соль слабое основание + сильная кислота: гидролиз по катиону, среда кислая.", "Гидролиз", [3, 4]))
        for _ in range(12):
            A(build_choice("Раствор соли NaCl (сильная кислота + сильное основание) имеет среду:", "нейтральную", ["нейтральную", "кислую", "щелочную", "зависит от концентрации"], "Гидролиза нет, pH = 7.", "Гидролиз", [3, 4]))
        for _ in range(12):
            A(build_choice("Восстановитель в окислительно-восстановительной реакции:", "отдаёт электроны и окисляется", ["отдаёт электроны и окисляется", "принимает электроны", "не меняет степень окисления", "всегда металл"],
                           "Восстановитель отдаёт электроны, его степень окисления повышается.", "ОВР", [3, 4]))
        for _ in range(12):
            el = random.choice([("S в H₂SO₄", "+6"), ("N в HNO₃", "+5"), ("Cr в K₂Cr₂O₇", "+6"), ("Mn в KMnO₄", "+7"), ("P в H₃PO₄", "+5"), ("Cl в HClO₄", "+7")])
            A(build_choice(f"Степень окисления элемента: {el[0]}.", el[1], ["+1", "+2", "+3", "+4", "+5", "+6", "+7", "−2"], f"Ответ: {el[1]}.", "ОВР", [3, 4]))
        for _ in range(12):
            A(build_choice("На катоде при электролизе водного раствора происходит:", "восстановление катионов", ["восстановление катионов", "окисление анионов", "нейтрализация", "растворение анода"],
                           "Катод — отрицательный электрод, на нём идёт восстановление.", "Электролиз", [3, 4]))
        for _ in range(12):
            A(build_choice("Процесс самопроизвольного разрушения металлов под действием окружающей среды:", "коррозия", ["коррозия", "электролиз", "гидролиз", "пассивация"], "Коррозия — окисление металла.", "Металлы", [1, 2]))
        for _ in range(12):
            A(build_choice("Экзотермическая реакция — это реакция, идущая с:", "выделением теплоты", ["выделением теплоты", "поглощением теплоты", "без теплового эффекта", "образованием газа"], "ΔH < 0.", "Тепловой эффект", [1, 2]))
        # --- гидролиз солей ---
        SALTS = [("Na₂CO₃", "щелочная", "соль сильного основания и слабой кислоты, гидролиз по аниону"),
                 ("K₂CO₃", "щелочная", "сильное основание + слабая кислота, гидролиз по аниону"),
                 ("Na₂SiO₃", "щелочная", "соль сильного основания и слабой кислоты"),
                 ("CH₃COONa", "щелочная", "ацетат натрия, гидролиз по аниону"),
                 ("NH₄Cl", "кислая", "соль слабого основания и сильной кислоты, гидролиз по катиону"),
                 ("AlCl₃", "кислая", "хлорид алюминия, гидролиз по катиону"),
                 ("ZnSO₄", "кислая", "соль слабого основания и сильной кислоты"),
                 ("Fe(NO₃)₃", "кислая", "нитрат железа(III), гидролиз по катиону"),
                 ("NaCl", "нейтральная", "соль сильного основания и сильной кислоты, гидролиза нет"),
                 ("KNO₃", "нейтральная", "сильное основание + сильная кислота"),
                 ("Na₂SO₄", "нейтральная", "соль сильной кислоты и сильного основания"),
                 ("BaCl₂", "нейтральная", "гидролиза практически нет")]
        for i, (s, env, why) in enumerate(SALTS):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            others = [x[1] for x in SALTS if x[0] != s]
            A(build_choice(f"Какая среда в растворе соли {s}?", env, list(dict.fromkeys(others))[:3],
                           f"{s}: {why} → среда {env}.", "Гидролиз солей", q))
            others2 = [x[0] for x in SALTS if x[1] != env]
            random.shuffle(others2)
            A(build_choice(f"Какая соль даёт {env.capitalize() if False else env} среду раствора?", s, others2[:3],
                           f"{s} — {why}.", "Гидролиз солей", q))
        # --- степень окисления (параметрически) ---
        OX = [("H₂SO₄", "S", "+6"), ("HNO₃", "N", "+5"), ("KMnO₄", "Mn", "+7"), ("K₂Cr₂O₇", "Cr", "+6"),
              ("H₃PO₄", "P", "+5"), ("HClO₄", "Cl", "+7"), ("NH₃", "N", "−3"), ("H₂S", "S", "−2"),
              ("CO₂", "C", "+4"), ("SO₃", "S", "+6"), ("Fe₂O₃", "Fe", "+3"), ("MnO₂", "Mn", "+4"),
              ("Na₂SO₃", "S", "+4"), ("KClO₃", "Cl", "+5"), ("PH₃", "P", "−3"), ("CH₄", "C", "−4")]
        opts = ["+1", "+2", "+3", "+4", "+5", "+6", "+7", "−1", "−2", "−3", "−4", "0"]
        for i, (f, el, ox) in enumerate(OX):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x for x in opts if x != ox]
            random.shuffle(w)
            A(build_choice(f"Степень окисления элемента {el} в соединении {f}:", ox, w[:3],
                           f"Сумма степеней окисления равна нулю; {el} здесь {ox}.", "ОВР", q))
        # --- скорость реакции (расчёты) ---
        for _ in range(12):
            g = random.choice([2, 3, 4])
            dt = random.choice([10, 20, 30, 40])
            k = dt // 10
            A(build_input(f"Температурный коэффициент γ = {g}. Во сколько раз возрастёт скорость реакции при нагревании на {dt} °C?",
                          g ** k, f"Правило Вант-Гоффа: v₂/v₁ = γ^(Δt/10) = {g}^{k} = {g**k}.", "Скорость реакции", [1, 2]))
        for _ in range(10):
            v1 = random.choice([0.1, 0.2, 0.5, 1, 2])
            t = random.choice([5, 10, 20])
            A(build_choice(f"За {t} с концентрация вещества изменилась с 0 до {v1:g} моль/л. Какова средняя скорость реакции (моль/(л·с))?".replace(".", ","),
                           f"{v1/t:g}".replace(".", ","), [f"{v1/t:g}".replace(".", ","), f"{v1*t:g}".replace(".", ","),
                           f"{t/v1:g}".replace(".", ","), f"{v1:g}".replace(".", ",")],
                           f"v = ΔC/Δt = {v1:g}/{t} = {v1/t:g} моль/(л·с).".replace(".", ","), "Скорость реакции", [1, 2]))
        # --- химическое равновесие (сценарии) ---
        EQ = [("N₂ + 3H₂ ⇌ 2NH₃ + Q", "повышение давления", "в сторону продукта (вправо)",
               "При росте давления равновесие смещается к меньшему числу молей газа: 4 → 2."),
              ("N₂ + 3H₂ ⇌ 2NH₃ + Q", "повышение температуры", "в сторону исходных веществ (влево)",
               "Реакция экзотермическая: нагрев смещает равновесие влево."),
              ("N₂ + 3H₂ ⇌ 2NH₃ + Q", "увеличение концентрации азота", "в сторону продукта (вправо)",
               "Добавление реагента смещает равновесие вправо."),
              ("2SO₂ + O₂ ⇌ 2SO₃ + Q", "повышение давления", "в сторону продукта (вправо)",
               "3 моля газа → 2 моля: рост давления смещает вправо."),
              ("2SO₂ + O₂ ⇌ 2SO₃ + Q", "понижение температуры", "в сторону продукта (вправо)",
               "Экзотермическая реакция: охлаждение смещает равновесие вправо."),
              ("CO₂(тв) ⇌ CO₂(г) − Q", "повышение температуры", "в сторону газообразного CO₂",
               "Процесс эндотермический, нагрев смещает равновесие вправо."),
              ("H₂ + I₂ ⇌ 2HI", "повышение давления", "не сместится",
               "Число молей газа одинаково с обеих сторон (2 и 2)."),
              ("N₂O₄ ⇌ 2NO₂ − Q", "понижение давления", "в сторону NO₂",
               "Снижение давления смещает равновесие к большему числу молей газа."),
              ("CaCO₃ ⇌ CaO + CO₂ − Q", "повышение температуры", "в сторону продуктов (вправо)",
               "Реакция эндотермическая."),
              ("CaCO₃ ⇌ CaO + CO₂ − Q", "удаление CO₂ из зоны реакции", "в сторону продуктов (вправо)",
               "Уменьшение концентрации продукта смещает равновесие вправо.")]
        for i, (eq, act, res, why) in enumerate(EQ):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x[2] for x in EQ if x[2] != res]
            random.shuffle(w)
            A(build_choice(f"Равновесие {eq}. Куда сместится равновесие, если произвести действие «{act}»?", res,
                           list(dict.fromkeys(w))[:3], why, "Химическое равновесие", q))
        # --- расчёты: масса, количество вещества, объём ---
        M = {"H₂O": 18, "NaCl": 58.5, "CO₂": 44, "NaOH": 40, "HCl": 36.5, "H₂SO₄": 98, "CaCO₃": 100, "KOH": 56,
             "NH₃": 17, "O₂": 32, "CuO": 80, "Fe₂O₃": 160, "MgO": 40, "HNO₃": 63, "SO₂": 64, "CH₄": 16}
        for _ in range(12):
            f = random.choice(list(M.keys()))
            n = random.randint(1, 5)
            A(build_input(f"Вычисли массу {n} моль вещества {f} (г). Ответ округлите до десятых.", round(n * M[f], 1),
                          f"m = n·M = {n} · {M[f]} = {round(n*M[f],1)} г.", "Расчёты по формулам", [1, 2]))
        for _ in range(12):
            n = random.randint(1, 6)
            A(build_input(f"Какой объём (н. у.) занимают {n} моль любого газа (л)?", round(22.4 * n, 1),
                          f"V = n·Vm = {n} · 22,4 = {round(22.4*n,1)} л.", "Расчёты по формулам", [3, 4]))
        for _ in range(12):
            m = random.choice([50, 100, 200, 400, 500])
            w = random.choice([5, 10, 15, 20, 25])
            A(build_input(f"Сколько граммов соли нужно растворить, чтобы получить {m} г {w}%-ного раствора?", m * w // 100,
                          f"m(в-ва) = m(р-ра)·w = {m}·{w}/100 = {m*w//100} г.", "Растворы", [3, 4]))
        for _ in range(10):
            m_salt = random.randint(10, 60); m_water = random.randint(90, 300)
            w = round(m_salt / (m_salt + m_water) * 100, 1)
            A(build_choice(f"В {m_water} г воды растворили {m_salt} г соли. Массовая доля соли (%)?", f"{w:g}".replace(".", ","),
                           [f"{w:g}".replace(".", ","), f"{round(m_salt/m_water*100,1):g}".replace(".", ","),
                            f"{m_salt}", f"{m_salt + m_water}"],
                           f"w = {m_salt}/({m_salt}+{m_water}) · 100% = {w:g}%.".replace(".", ","), "Растворы", [1, 2]))
        # --- периодический закон (факты) ---
        PER = [("литий (Li)", "щелочной металл 2-го периода"), ("натрий (Na)", "щелочной металл 3-го периода"),
               ("магний (Mg)", "щелочноземельный металл 3-го периода"), ("алюминий (Al)", "амфотерный металл 3-го периода"),
               ("хлор (Cl)", "галоген 3-го периода"), ("сера (S)", "неметалл 3-го периода, образует SO₂ и SO₃"),
               ("калий (K)", "щелочной металл 4-го периода"), ("кальций (Ca)", "щелочноземельный металл 4-го периода"),
               ("железо (Fe)", "побочная подгруппа, переходный металл"), ("медь (Cu)", "побочная подгруппа, пластичный металл"),
               ("фтор (F)", "самый активный неметалл-галоген"), ("бром (Br)", "жидкий галоген"),
               ("йод (I)", "галоген, возгоняется, даёт синее окрашивание с крахмалом"),
               ("неон (Ne)", "инертный газ 2-го периода"), ("аргон (Ar)", "инертный газ 3-го периода"),
               ("фосфор (P)", "неметалл, образует белый и красный фосфор"), ("кремний (Si)", "неметалл, основа электроники"),
               ("азот (N)", "неметалл, 78% воздуха"), ("кислород (O)", "газ, поддерживающий горение"),
               ("углерод (C)", "элемент, образующий алмаз и графит")]
        for i, (el, d) in enumerate(PER):
            q = [1, 2] if i % 2 == 0 else [3, 4]
            w = [x[1] for x in PER if x[0] != el]
            random.shuffle(w)
            A(build_choice(f"Что верно для элемента «{el}»?", d, w[:3], f"{el} — {d}.", "Периодический закон", q))
            w2 = [x[0] for x in PER if x[1] != d]
            random.shuffle(w2)
            A(build_choice(f"Какой элемент характеризуется так: «{d}»?", el, w2[:3], f"Это {el}.", "Периодический закон", q))
        # --- строение атома (параметрически) ---
        for _ in range(12):
            z = random.choice([3, 6, 8, 11, 12, 13, 15, 17, 19, 20, 26, 29])
            ar = {3: 7, 6: 12, 8: 16, 11: 23, 12: 24, 13: 27, 15: 31, 17: 35, 19: 39, 20: 40, 26: 56, 29: 64}[z]
            A(build_input(f"Заряд ядра атома +{z}, массовое число {ar}. Сколько нейтронов в ядре?", ar - z,
                          f"N = A − Z = {ar} − {z} = {ar-z}.", "Строение атома", [3, 4]))
            A(build_input(f"Сколько электронов в нейтральном атоме с зарядом ядра +{z}?", z,
                          f"Число электронов равно заряду ядра: {z}.", "Строение атома", [3, 4]))

        for _ in range(10):
            A(build_choice("Катализатор:", "ускоряет реакцию, но не расходуется", ["ускоряет реакцию, но не расходуется", "расходуется в реакции", "замедляет реакцию", "смещает равновесие"],
                           "Катализатор снижает энергию активации и не входит в продукты.", "Скорость реакции", [1, 2]))
        for _ in range(10):
            A(build_choice("С увеличением радиуса атома в главной подгруппе сверху вниз металлические свойства:", "усиливаются", ["усиливаются", "ослабевают", "не изменяются", "исчезают"],
                           "Радиус растёт — электроны внешнего уровня удерживаются слабее.", "Периодический закон", [1, 2]))
        return P
    return P


# ============================================================ ИНФОРМАТИКА
def _js_items(A, band):
    """Модуль «JavaScript» в информатике: band 1 — 7–9 классы, band 2 — 10–11."""
    T = "JavaScript"
    ALLT = ["number", "string", "boolean", "object", "undefined"]
    TYPES = [("42", "number"), ("3.14", "number"), ("'привет'", "string"), ('"мир"', "string"),
             ("true", "boolean"), ("false", "boolean"), ("[1, 2]", "object"), ("undefined", "undefined")]
    if band == 1:
        for _ in range(12):
            v, t = random.choice(TYPES)
            A(build_choice(f"Что выведет в JavaScript: typeof {v}?", t, [x for x in ALLT if x != t],
                           f"typeof {v} → «{t}».", T, [1, 2]))
        for _ in range(12):
            a = [random.randint(1, 9) for _ in range(random.randint(2, 6))]
            A(build_choice(f"Чему равно a.length, если const a = {a};?", len(a), [len(a) + 1, len(a) - 1, a[-1]],
                           f"length — число элементов массива: {len(a)}.", T, [1, 2]))
        for _ in range(10):
            a = [random.randint(1, 9) for _ in range(random.randint(3, 6))]
            A(build_choice(f"Что вернёт a[a.length - 1], если const a = {a};?", a[-1], [a[0], a[1], len(a)],
                           f"a[a.length - 1] — последний элемент: {a[-1]}.", T, [3, 4]))
        for _ in range(10):
            w = random.choice(["код", "скрипт", "функция", "массив", "объект", "строка"])
            A(build_choice(f"Чему равно '{w}'.length в JavaScript?", len(w), [len(w) - 1, len(w) + 1, len(w) * 2],
                           f"length у строки — число символов: {len(w)}.", T, [1, 2]))
        for _ in range(10):
            n = random.randint(1, 9)
            A(build_choice(f"Что выведет console.log({n} + '{n}')?", f"{n}{n}", [n + n, f"{n}{n}{n}", "NaN"],
                           f"Число со строкой даёт склейку строк: «{n}{n}».", T, [3, 4]))
        for _ in range(10):
            n = random.randint(2, 9)
            A(build_choice(f"Сколько раз выполнится тело цикла: for (let i = 0; i < {n}; i++) {{ … }}?", n,
                           [n - 1, n + 1, n * 2], f"i принимает значения 0…{n-1} — всего {n} итераций.", T, [3, 4]))
        for _ in range(12):
            x, y = random.randint(2, 20), random.randint(2, 20)
            A(build_choice(f"Что вернёт вызов sum({x}, {y}), если function sum(a, b) {{ return a + b; }}?", x + y,
                           [x * y, x - y, str(x) + str(y)], f"Функция возвращает сумму: {x} + {y} = {x+y}.", T, [1, 2]))
        for _ in range(8):
            n = random.randint(2, 9)
            A(build_choice(f"Что вернёт f({n}), если const f = (x) => x * 2;?", n * 2, [n + 2, n ** 2, n * 2 + 1],
                           f"Стрелочная функция умножает на 2: {n} · 2 = {n*2}.", T, [3, 4]))
        for _ in range(8):
            a, b = random.randint(2, 30), random.randint(2, 30)
            if b == a:
                b += 1
            A(build_choice(f"Что вернёт Math.max({a}, {b})?", max(a, b), [min(a, b), a + b, abs(a - b)],
                           f"Math.max возвращает большее из чисел: {max(a,b)}.", T, [1, 2]))
        for _ in range(8):
            x = random.randint(1, 9) + 0.5
            A(build_choice(f"Что вернёт Math.floor({x})?", int(x), [int(x) + 1, int(x) - 1, int(x) * 2],
                           f"Math.floor округляет вниз: {int(x)}.", T, [3, 4]))
        A(build_choice("Каким тегом подключают JavaScript к веб-странице?", "<script>", ["<js>", "<code>", "<style>"],
                       "Скрипты помещают в тег <script> (атрибут src — путь к файлу).", T, [1, 2]))
        A(build_choice("Что означает запись // комментарий в JavaScript?", "однострочный комментарий",
                       ["деление нацело", "начало цикла", "ошибка синтаксиса"],
                       "// начинает однострочный комментарий; /* … */ — многострочный.", T, [1, 2]))
        A(build_choice("Что делает console.log(…)?", "выводит значение в консоль",
                       ["показывает всплывающее окно", "записывает значение в файл", "останавливает программу"],
                       "console.log — основной инструмент отладки в JS.", T, [1, 2]))
        A(build_choice("Можно ли присвоить новое значение после const a = 5;?", "нет, будет ошибка",
                       ["да, без ограничений", "да, но только число", "зависит от браузера"],
                       "const объявляет константу: повторное присваивание запрещено.", T, [1, 2]))
        A(build_choice("Что делает document.getElementById('card')?", "находит элемент страницы по id",
                       ["создаёт новый элемент", "удаляет элемент", "меняет тему страницы"],
                       "Метод возвращает элемент с указанным id — основа работы с DOM.", T, [3, 4]))
        A(build_choice("Когда выполнится функция f в btn.addEventListener('click', f);?", "по клику на btn",
                       ["сразу при загрузке страницы", "каждую секунду", "никогда"],
                       "addEventListener подписывает обработчик на событие — здесь click.", T, [3, 4]))
        A(build_tf("5 === '5' в JavaScript — это true.", "Неверно",
                   "Строгое равенство === не приводит типы: число и строка не равны.", T, [3, 4]))
        A(build_tf("JavaScript выполняется только в браузере.", "Неверно",
                   "Есть и серверная среда выполнения — Node.js.", T, [3, 4]))
        return
    # ---- band 2: 10–11 классы ----
    for _ in range(10):
        A(build_choice("Что выведет typeof null в JavaScript?", "object", ["null", "undefined", "number"],
                       "Историческая особенность JS: typeof null → «object».", T, [1, 2]))
    for _ in range(10):
        a = [random.randint(1, 5) for _ in range(4)]
        r = [x * 2 for x in a]
        A(build_choice(f"Что вернёт {a}.map(x => x * 2)?", str(r), [str(a), str([x + 2 for x in a]), str(len(a))],
                       "map создаёт новый массив, применив функцию к каждому элементу.", T, [1, 2]))
    for _ in range(10):
        a = [random.randint(1, 9) for _ in range(6)]
        k = random.randint(3, 6)
        r = [x for x in a if x > k]
        A(build_choice(f"Что вернёт {a}.filter(x => x > {k})?", str(r), [str([x for x in a if x < k]), str(a), str(sum(r))],
                       "filter оставляет элементы, для которых условие истинно.", T, [3, 4]))
    for _ in range(10):
        a = [random.randint(1, 9) for _ in range(4)]
        A(build_choice(f"Что вернёт {a}.reduce((s, x) => s + x, 0)?", sum(a), [max(a), len(a), sum(a) - 1],
                       "reduce сворачивает массив к одному значению: здесь к сумме.", T, [3, 4]))
    for _ in range(8):
        n = random.randint(1, 3)
        A(build_choice(f"Что вернёт ['a', 'b', 'c'].slice(0, {n})?", str(['a', 'b', 'c'][:n]),
                       [str(['a', 'b', 'c'][n:]), str(n), "['c', 'b', 'a']"],
                       f"slice копирует часть массива с 0 до {n} (не включая {n}).", T, [1, 2]))
    A(build_choice("Что вернёт `привет, ${name}`, если const name = 'МИР';?", "привет, МИР",
                   ["привет, ${name}", "привет, name", "привет, {name}"],
                   "Шаблонная строка в обратных кавычках подставляет значение в ${…}.", T, [1, 2]))
    for _ in range(8):
        a = [random.randint(1, 9) for _ in range(3)]
        A(build_choice(f"Что вернёт {a}.join('-')?", "-".join(map(str, a)), ["".join(map(str, a)), str(a), str(len(a))],
                       "join склеивает элементы массива в строку с разделителем.", T, [3, 4]))
    A(build_choice("Что вернёт 'а,б,в'.split(',')?", "массив из трёх строк",
                   ["строку 'а,б,в'", "массив из трёх чисел", "ошибку"],
                   "split разбивает строку по разделителю в массив.", T, [3, 4]))
    for _ in range(8):
        x = random.randint(1, 9)
        A(build_choice(f"Что вернёт [1, 2, 3].includes({x})?", "true" if x in (1, 2, 3) else "false",
                       ["false" if x in (1, 2, 3) else "true", str(x), "undefined"],
                       "includes проверяет, есть ли элемент в массиве.", T, [1, 2]))
    A(build_choice("Что такое Promise в JavaScript?", "объект для асинхронных операций",
                   ["синтаксис цикла", "тип данных для строк", "метод массива"],
                   "Promise представляет результат операции, которая завершится позже.", T, [1, 2]))
    A(build_choice("Что делает оператор await внутри async-функции?", "ждёт выполнения Promise",
                   ["останавливает браузер", "объявляет переменную", "создаёт новый поток"],
                   "await приостанавливает функцию до разрешения Promise.", T, [3, 4]))
    A(build_choice("Что такое Node.js?", "среда выполнения JavaScript вне браузера",
                   ["браузер", "база данных", "язык программирования"],
                   "Node.js запускает JS на сервере и в скриптах разработчика.", T, [1, 2]))
    A(build_choice("Для чего используют npm?", "установка пакетов и управление зависимостями",
                   ["рисование графиков", "проверка орфографии", "сжатие изображений"],
                   "npm — пакетный менеджер экосистемы JavaScript.", T, [1, 2]))
    A(build_choice("Чем let отличается от var?", "let имеет блочную область видимости",
                   ["let нельзя изменить", "let работает только в циклах", "ничем"],
                   "let видна только внутри блока {…}, var — всей функции.", T, [3, 4]))
    A(build_choice("Что такое замыкание в JavaScript?", "функция, запоминающая внешние переменные",
                   ["цикл внутри функции", "ошибка памяти", "способ закрыть вкладку"],
                   "Замыкание сохраняет доступ к переменным внешней функции.", T, [3, 4]))
    A(build_tf("NaN === NaN — это true.", "Неверно", "NaN не равен даже самому себе; используют Number.isNaN().", T, [3, 4]))
    A(build_choice("Что вернёт [...a, ...b], если a = [1] и b = [2]?", "[1, 2]",
                   ["[[1], [2]]", "[2, 1]", "3"],
                   "Оператор распространения (spread) объединяет массивы.", T, [3, 4]))
    A(build_choice("Что вернёт JSON.parse('{\"a\": 1}')?", "объект из JSON-строки",
                   ["строку", "число 1", "ошибку"],
                   "JSON.parse превращает JSON-текст в объект; JSON.stringify — наоборот.", T, [1, 2]))


def gen_info(grade, seed=0):
    random.seed(seed)
    P = []
    A = P.append
    if grade in (5, 6):
        for _ in range(12):
            n = random.randint(2, 20)
            A(build_choice(f"Сколько бит в {n} байтах?", n * 8, [n * 8, n, n * 2, n * 16], f"1 байт = 8 бит, значит {n}·8 = {n*8} бит.", "Информация", [1, 2]))
        for _ in range(12):
            n = random.randint(2, 10)
            A(build_choice(f"Сколько байт в {n} Кбайт (1 Кбайт = 1024 байта)?", n * 1024, [n * 1024, n * 1000, n * 8, n], f"{n} Кбайт = {n}·1024 = {n*1024} байт.", "Информация", [1, 2]))
        for _ in range(12):
            A(build_choice("Устройство для ввода текстовой информации:", "клавиатура", ["клавиатура", "монитор", "принтер", "колонки"], "Клавиатура — устройство ввода.", "Устройства компьютера", [1, 2]))
        for _ in range(10):
            A(build_choice("Где хранится информация после выключения компьютера (постоянно)?", "на жёстком диске", ["на жёстком диске", "в оперативной памяти", "в процессоре", "на экране"], "ОЗУ очищается при выключении, диск — нет.", "Устройства компьютера", [3, 4]))
        for _ in range(10):
            A(build_choice("Что такое алгоритм?", "конечная последовательность точных指令 действий" if False else "конечная последовательность точных действий, приводящая к решению задачи",
                           ["конечная последовательность точных действий, приводящая к решению задачи", "любая программа", "число", "устройство компьютера"], "Алгоритм — понятный и конечный набор шагов.", "Алгоритмы", [3, 4]))
        for _ in range(10):
            A(build_choice("Какой фигурой в блок-схеме обозначается условие (ветвление)?", "ромб", ["ромб", "овал", "прямоугольник", "параллелограмм"], "Ромб — блок условия.", "Алгоритмы", [3, 4]))
        for _ in range(10):
            A(build_choice("Расширение файла .txt означает:", "текстовый файл", ["текстовый файл", "изображение", "звуковой файл", "программу"], ".txt — простой текст.", "Файлы", [1, 2]))
        for _ in range(10):
            A(build_choice("1 Кбайт равен:", "1024 байта", ["1024 байта", "1000 байт", "8 байт", "1024 бит"], "В информатике 1 Кбайт = 2¹⁰ = 1024 байта.", "Информация", [3, 4]))
        for _ in range(10):
            n = random.randint(2, 20)
            A(build_choice(f"Сколько килобайт в {n} Мбайт (1 Мбайт = 1024 Кбайт)?", n * 1024, [n * 1024, n * 1000, n, n * 8],
                           f"{n} Мбайт = {n}·1024 = {n*1024} Кбайт.", "Информация", [1, 2]))
        for _ in range(10):
            n = random.randint(1, 16)
            A(build_choice(f"Сколько бит в {n} Кбайт?", n * 1024 * 8, [n * 1024 * 8, n * 1024, n * 8, n * 1000 * 8],
                           f"{n} Кбайт = {n*1024} байт = {n*1024*8} бит.", "Информация", [3, 4]))
        for _ in range(8):
            n = random.randint(2, 10)
            A(build_choice(f"Сколько различных символов можно закодировать {n} битами?", 2 ** n, [2 ** n, n * 2, n ** 2, 2 * n + 1],
                           f"Каждый бит — 2 варианта, всего 2^{n} = {2**n}.", "Информация", [3, 4]))
        for _ in range(8):
            n = random.randint(3, 9)
            A(build_input(f"Мощность алфавита {2**n} символов. Каков информационный вес одного символа (в битах)?", n,
                          f"N = 2^i → {2**n} = 2^{n}, значит i = {n} бит.", "Информация", [3, 4]))
        for _ in range(8):
            n = random.randint(2, 12); k = random.randint(2, 8)
            A(build_input(f"Сообщение из {n} символов, вес символа {k} бит. Каков объём сообщения (в битах)?", n * k,
                          f"Объём = {n} · {k} = {n*k} бит.", "Информация", [1, 2]))
        P.extend([build_choice("Устройство ввода информации:", a, [a, "монитор", "принтер", "колонки"],
                               f"{a} — устройство ввода.", "Устройства компьютера", [1, 2])
                  for a in ["мышь", "сканер", "микрофон", "веб-камера", "клавиатура", "джойстик"]])
        P.extend([build_choice("Устройство вывода информации:", a, [a, "клавиатура", "сканер", "микрофон"],
                               f"{a} — устройство вывода.", "Устройства компьютера", [1, 2])
                  for a in ["монитор", "принтер", "колонки", "проектор", "наушники"]])
        P.extend([build_choice("Устройство для хранения информации:", a, [a, "принтер", "монитор", "мышь"],
                               f"{a} — устройство хранения данных.", "Устройства компьютера", [3, 4])
                  for a in ["жёсткий диск", "флеш-накопитель", "оптический диск", "SSD-накопитель", "карта памяти"]])
        P.extend([build_choice(f"Файл с расширением {e} — это …", d, [d, "текстовый документ", "изображение", "звуковой файл"],
                               f"Расширение {e} указывает на {d}.", "Файлы", [1, 2])
                  for e, d in [(".jpg", "изображение"), (".png", "изображение"), (".mp3", "звуковой файл"),
                               (".mp4", "видеофайл"), (".docx", "текстовый документ"), (".xlsx", "электронная таблица"),
                               (".pptx", "презентация"), (".pdf", "документ для чтения"), (".zip", "архив"),
                               (".py", "программа на Python"), (".html", "веб-страница")]])
        P.extend([build_choice("Что делает эта программа/устройство: " + d + "?", a, [a, "хранит данные", "печатает текст", "воспроизводит звук"],
                               f"{d} — {a}.", "Информационные технологии", [3, 4])
                  for d, a in [("текстовый редактор", "создаёт и редактирует текстовые документы"),
                               ("графический редактор", "создаёт и обрабатывает рисунки"),
                               ("электронная таблица", "работает с таблицами и вычислениями"),
                               ("браузер", "просматривает веб-страницы"),
                               ("антивирус", "защищает компьютер от вредоносных программ"),
                               ("архиватор", "сжимает файлы для экономии места")]])
        P.extend([build_choice("Алгоритм, в котором действия выполняются одно за другим без условий, называется …", "линейным",
                               ["линейным", "разветвляющимся", "циклическим", "рекурсивным"], "Линейный алгоритм — последовательность шагов.",
                               "Алгоритмы", [1, 2])])
        P.extend([build_choice("Алгоритм с проверкой условия называется …", "разветвляющимся", ["разветвляющимся", "линейным",
                               "циклическим", "вспомогательным"], "Ветвление: если … то … иначе ….", "Алгоритмы", [1, 2])])
        P.extend([build_choice("Алгоритм с повторением действий называется …", "циклическим", ["циклическим", "линейным",
                               "разветвляющимся", "рекурсивным"], "Цикл повторяет действия, пока условие истинно.", "Алгоритмы", [3, 4])])
        P.extend([build_choice("Свойство алгоритма «дискретность» означает, что …", "алгоритм разбит на отдельные шаги",
                               ["алгоритм разбит на отдельные шаги", "алгоритм понятен исполнителю", "алгоритм приводит к результату",
                                "алгоритм применим к разным задачам"], "Дискретность — пошаговость.", "Алгоритмы", [3, 4])])
        P.extend([build_choice("Свойство алгоритма «результативность» означает, что …", "алгоритм завершается получением результата",
                               ["алгоритм завершается получением результата", "он понятен всем", "состоит из шагов", "универсален"],
                               "Алгоритм должен давать результат за конечное число шагов.", "Алгоритмы", [3, 4])])
        P.extend([build_choice("Кто такой исполнитель алгоритма?", "тот, кто выполняет команды алгоритма",
                               ["тот, кто выполняет команды алгоритма", "автор алгоритма", "компьютерная программа", "учитель информатики"],
                               "Исполнитель понимает систему команд (СКИ).", "Алгоритмы", [1, 2])])
        P.extend([build_tf("1 байт равен 8 битам.", "Верно", "Байт — 8 бит.", "Информация", [1, 2])])
        P.extend([build_tf("Оперативная память сохраняет данные после выключения компьютера.", "Неверно",
                           "ОЗУ очищается; данные хранятся на диске.", "Устройства компьютера", [1, 2])])
        P.extend([build_tf("Процессор обрабатывает информацию.", "Верно", "Процессор выполняет команды программы.", "Устройства компьютера", [3, 4])])
        P.extend([build_tf("Принтер — устройство ввода.", "Неверно", "Принтер выводит информацию на бумагу.", "Устройства компьютера", [3, 4])])
        P.extend([build_choice("Что такое информация для человека?", "сведения об окружающем мире",
                               ["сведения об окружающем мире", "только числа", "компьютерные файлы", "электрические сигналы"],
                               "Информация — сведения, уменьшающие неопределённость.", "Информация", [1, 2])])
        P.extend([build_choice("Какой бывает информация по способу восприятия?", "зрительная, звуковая, вкусовая, обонятельная, осязательная",
                               ["зрительная, звуковая, вкусовая, обонятельная, осязательная", "только текстовая",
                                "числовая и графическая", "полезная и вредная"], "Пять видов по органам чувств.", "Информация", [1, 2])])
        P.extend([build_choice("Что такое компьютерная сеть?", "объединение компьютеров для обмена данными",
                               ["объединение компьютеров для обмена данными", "набор программ", "жесткий диск", "принтер и сканер"],
                               "Локальные и глобальные сети.", "Сети", [3, 4])])
        P.extend([build_choice("Глобальная сеть — это …", "Интернет", ["Интернет", "локальная сеть школы", "принтер", "процессор"],
                               "Интернет объединяет сети по всему миру.", "Сети", [3, 4])])
        P.extend([build_choice("Что такое электронная почта?", "служба обмена сообщениями через Интернет",
                               ["служба обмена сообщениями через Интернет", "программа для рисования", "вид памяти", "устройство печати"],
                               "Адрес имеет вид имя@сервер.", "Сети", [3, 4])])
        P.extend([build_choice("Какой символ обязательно есть в адресе электронной почты?", "@", ["@", "#", "&", "*"],
                               "«Собака» разделяет имя пользователя и домен.", "Сети", [3, 4])])
        P.extend([build_choice("Что такое браузер?", "программа для просмотра веб-страниц",
                               ["программа для просмотра веб-страниц", "поисковый робот", "сервер", "язык разметки"],
                               "Примеры: Chrome, Firefox, Safari.", "Сети", [3, 4])])
        P.extend([build_choice("Безопасное поведение в сети включает …", "не сообщать личные данные незнакомцам",
                               ["не сообщать личные данные незнакомцам", "открывать все ссылки", "использовать один пароль везде",
                                "публиковать адрес дома"], "Цифровая гигиена.", "Безопасность", [1, 2])])
        P.extend([build_choice("Надёжный пароль — это …", "длинная смесь букв разного регистра, цифр и символов",
                               ["длинная смесь букв разного регистра, цифр и символов", "дата рождения", "имя питомца", "123456"],
                               "Чем длиннее и разнообразнее, тем надёжнее.", "Безопасность", [1, 2])])

        return P
    if grade in (7, 8, 9):
        for _ in range(14):
            n = random.randint(1, 200)
            A(build_input(f"Переведи десятичное число {n} в двоичную систему. Ответ запиши без пробелов.", bin(n)[2:], f"{n} = {bin(n)[2:]}₂.", "Системы счисления", [1, 2]))
        for _ in range(14):
            b = bin(random.randint(1, 100))[2:]
            A(build_input(f"Переведи двоичное число {b}₂ в десятичную систему.", int(b, 2), f"{b}₂ = {int(b,2)}₁₀.", "Системы счисления", [1, 2]))
        for _ in range(12):
            a = random.randint(0, 1); b = random.randint(0, 1); op = random.choice(["И", "ИЛИ"])
            r = (a and b) if op == "И" else (a or b)
            A(build_choice(f"Вычисли: {a} {op} {b}.", 1 if r else 0, [1 if r else 0, 0 if r else 1, a, b], f"Логическая операция «{op}»: {a} {op} {b} = {1 if r else 0}.", "Логика", [1, 2]))
        for _ in range(12):
            a = random.randint(0, 1)
            A(build_choice(f"Вычисли: НЕ {a}.", 1 - a, [1 - a, a, 0, 1], f"Инверсия: НЕ {a} = {1-a}.", "Логика", [1, 2]))
        for _ in range(12):
            n = random.randint(4, 16)
            A(build_choice(f"Сколько информации несёт сообщение о том, что выпало одно из {2**n} равновероятных событий?", f"{n} бит", [f"{n} бит", f"{2**n} бит", f"{n*2} бит", f"{n//2} бит"], f"N = 2^i → i = {n} бит.", "Информация", [3, 4]))
        for _ in range(12):
            n = random.randint(2, 10); k = random.randint(2, 10)
            A(build_choice(f"Текст из {n*k} символов, алфавит содержит {2**k} символов. Каков объём сообщения в байтах?", n, [n, n * k, n * k // 8, 2 ** k], f"Вес одного символа {k} бит; объём = {n*k}·{k} бит = {n*k*k//8}… = {n} байт при k=8/{k}·{n*k} бит.", "Информация", [3, 4]))
        for _ in range(12):
            n = random.randint(2, 6)
            A(build_choice(f"Сколько существует различных последовательностей из {n} бит?", 2 ** n, [2 ** n, n * 2, n ** 2, 2 * n], f"Каждый разряд — 2 варианта: 2^{n} = {2**n}.", "Информация", [1, 2]))
        for _ in range(10):
            a = random.randint(2, 20); b = random.randint(2, 20)
            A(build_choice(f"Что выведет программа на Python: print({a} % {b})?", a % b, [a % b, a // b, a / b, a * b], "Оператор % возвращает остаток от деления.", "Программирование", [3, 4]))
        for _ in range(10):
            a = random.randint(2, 50); b = random.randint(2, 9)
            A(build_choice(f"Результат выражения {a} // {b} в Python:", a // b, [a // b, a / b, a % b, round(a / b)], "// — целочисленное деление.", "Программирование", [3, 4]))
        for _ in range(10):
            A(build_choice("Какой тип данных в Python хранит целое число?", "int", ["int", "float", "str", "bool"], "int — целые числа.", "Программирование", [1, 2]))
        for _ in range(10):
            A(build_choice("Цикл с известным числом повторений в Python:", "for", ["for", "if", "def", "while… нет"], "for i in range(n) — цикл со счётчиком.", "Программирование", [3, 4]))
        for _ in range(10):
            A(build_choice("Что делает функция len('информатика')?", "возвращает 11", ["возвращает 11", "возвращает 10", "возвращает строку", "ошибку"], "len считает количество символов: в слове «информатика» 11 букв.", "Программирование", [3, 4]))
        _js_items(A, 1)
        return P
    if grade in (10, 11):
        for _ in range(14):
            n = random.randint(100, 4000)
            A(build_input(f"Переведи число {n} в двоичную систему счисления.", bin(n)[2:], f"{n}₁₀ = {bin(n)[2:]}₂.", "Системы счисления", [1, 2]))
        for _ in range(12):
            h = hex(random.randint(10, 255))[2:].upper()
            A(build_input(f"Переведи {h}₁₆ в десятичную систему.", int(h, 16), f"{h}₁₆ = {int(h,16)}₁₀.", "Системы счисления", [1, 2]))
        for _ in range(12):
            n = random.randint(5, 12)
            A(build_choice(f"Сколько различных значений можно закодировать {n} битами?", 2 ** n, [2 ** n, n * 2, n ** 2, 2 * n + 1], f"2^{n} = {2**n}.", "Информация", [1, 2]))
        for _ in range(12):
            px = random.randint(100, 1000); depth = random.choice([8, 16, 24])
            A(build_choice(f"Изображение {px}×{px} пикселей, глубина цвета {depth} бит. Каков объём памяти в байтах?", px * px * depth // 8, [px * px * depth // 8, px * px, px * depth, px * px * depth],
                           f"Объём = {px}·{px}·{depth} бит = {px*px*depth} бит = {px*px*depth//8} байт.", "Информация", [1, 2]))
        for _ in range(12):
            n = random.randint(3, 8)
            A(build_choice(f"Сколько рёбер у полного графа с {n} вершинами?", n * (n - 1) // 2, [n * (n - 1) // 2, n * n, n - 1, n * (n - 1)], f"C({n},2) = {n}·{n-1}/2 = {n*(n-1)//2}.", "Графы", [3, 4]))
        for _ in range(12):
            a = [random.randint(1, 9) for _ in range(4)]
            A(build_choice(f"Что вернёт max({a})?", max(a), [max(a), min(a), sum(a), len(a)], "max возвращает наибольший элемент списка.", "Программирование", [1, 2]))
        for _ in range(12):
            a = [random.randint(1, 20) for _ in range(5)]
            A(build_input(f"Чему равна сумма элементов списка {a}?", sum(a), f"{' + '.join(map(str,a))} = {sum(a)}.", "Программирование", [1, 2]))
        for _ in range(12):
            n = random.randint(1, 8)
            import math as _m
            A(build_input(f"Вычисли факториал {n}!", _m.factorial(n), f"{n}! = {_m.factorial(n)}.", "Алгоритмы", [3, 4]))
        for _ in range(10):
            n = random.randint(5, 20)
            A(build_choice(f"Какова временная сложность бинарного поиска в массиве из {n} элементов?", "O(log n)", ["O(log n)", "O(n)", "O(n²)", "O(1)"], "На каждом шаге область поиска делится пополам.", "Алгоритмы", [3, 4]))
        for _ in range(10):
            A(build_choice("Сложность алгоритма сортировки пузырьком в худшем случае:", "O(n²)", ["O(n²)", "O(n log n)", "O(n)", "O(1)"], "Два вложенных цикла по n.", "Алгоритмы", [3, 4]))
        for _ in range(10):
            A(build_choice("Что выведет print(2 ** 10)?", 1024, [1024, 20, 100, 512], "2¹⁰ = 1024.", "Программирование", [1, 2]))
        for _ in range(10):
            A(build_choice("Какой оператор в Python используется для проверки условия?", "if", ["if", "for", "while", "import"], "if … else — условный оператор.", "Программирование", [1, 2]))
        _js_items(A, 2)
        return P
    return P


# ============================================================ АНГЛИЙСКИЙ ЯЗЫК
def gen_english(grade, seed=0):
    random.seed(seed)
    P = []
    A = P.append
    if grade in (3, 4):
        for _ in range(12):
            n = random.choice(["apple", "cat", "dog", "book", "pen", "table", "egg", "orange", "umbrella", "ice cream"])
            art = "an" if n[0] in "aeiou" else "a"
            A(build_choice(f"Choose the correct article: … {n}", art, ["a", "an", "the", "—"], f"Перед согласным звуком ставим «a», перед гласным — «an».", "Articles", [1, 2]))
        for _ in range(12):
            w = random.choice([("book", "books"), ("cat", "cats"), ("box", "boxes"), ("child", "children"), ("man", "men"), ("toy", "toys"), ("baby", "babies"), ("bus", "buses")])
            A(build_choice(f"What is the plural of «{w[0]}»?", w[1], [w[1], w[0] + "s" if w[1] != w[0] + "s" else w[0] + "es", w[0], w[1] + "s"], "Форма множественного числа.", "Plurals", [1, 2]))
        for _ in range(12):
            s = random.choice([("I", "am"), ("He", "is"), ("She", "is"), ("It", "is"), ("We", "are"), ("They", "are"), ("You", "are")])
            A(build_choice(f"Choose: {s[0]} … a student.", s[1], ["am", "is", "are", "be"], f"{s[0]} + {s[1]} (форма глагола to be).", "to be", [1, 2]))
        for _ in range(12):
            A(build_choice("Translate: «собака»", "dog", ["dog", "cat", "cow", "pig"], "dog — собака.", "Vocabulary", [1, 2]))
        for _ in range(12):
            A(build_choice("Translate: «красный»", "red", ["red", "blue", "green", "black"], "red — красный.", "Vocabulary", [1, 2]))
        for _ in range(10):
            A(build_choice("How many days are there in a week?", "seven", ["seven", "five", "six", "ten"], "В неделе семь дней.", "Numbers", [3, 4]))
        for _ in range(10):
            n = random.choice([("two", 2), ("five", 5), ("ten", 10), ("seven", 7), ("three", 3)])
            A(build_choice(f"What number is «{n[0]}»?", n[1], [n[1], n[1] + 1, n[1] - 1, n[1] * 2], f"{n[0]} = {n[1]}.", "Numbers", [3, 4]))
        for _ in range(10):
            A(build_choice("Choose: I … to school every day.", "go", ["go", "goes", "going", "went"], "С подлежащим I глагол стоит в форме go.", "Present Simple", [3, 4]))
        for _ in range(10):
            A(build_choice("Choose: She … English at school.", "studies", ["studies", "study", "studying", "studys"], "С he/she/it в Present Simple окончание -s/-es: study → studies.", "Present Simple", [3, 4]))
        return P
    if grade in (5, 6):
        for _ in range(14):
            s = random.choice([("He usually … up at 7 o'clock.", "gets", ["gets", "get", "getting", "got"]),
                             ("They … to the cinema every Friday.", "go", ["go", "goes", "going", "went"]),
                             ("My sister … very well.", "sings", ["sings", "sing", "singing", "sang"]),
                             ("We … English every day.", "study", ["study", "studies", "studying", "studied"]),
                             ("The cat … milk.", "likes", ["likes", "like", "liking", "liked"])])
            A(build_choice(s[0], s[1], s[2], "Present Simple: с he/she/it — окончание -s.", "Present Simple", [1, 2]))
        for _ in range(14):
            s = random.choice([("Look! It … now.", "is raining", ["is raining", "rains", "rain", "rained"]),
                             ("She … a book at the moment.", "is reading", ["is reading", "reads", "read", "reading"]),
                             ("They … football now.", "are playing", ["are playing", "plays", "play", "played"])])
            A(build_choice(s[0], s[1], s[2], "Present Continuous: am/is/are + V-ing (действие сейчас).", "Present Continuous", [1, 2]))
        for _ in range(14):
            s = random.choice([("I … to Moscow last summer.", "went", ["went", "go", "goes", "going"]),
                             ("He … his homework yesterday.", "did", ["did", "do", "does", "done"]),
                             ("We … a film two days ago.", "watched", ["watched", "watch", "watches", "watching"])])
            A(build_choice(s[0], s[1], s[2], "Past Simple: вторая форма глагола (правильные — окончание -ed).", "Past Simple", [1, 2]))
        for _ in range(12):
            s = random.choice([("I … never … sushi.", "have … tried", ["have … tried", "has … tried", "did … try", "am … trying"]),
                             ("She … just … home.", "has … come", ["has … come", "have … come", "did … come", "is … coming"])])
            A(build_choice(s[0], s[1], s[2], "Present Perfect: have/has + V3.", "Present Perfect", [3, 4]))
        for _ in range(12):
            s = random.choice([("There … a book on the table.", "is", ["is", "are", "be", "am"]),
                             ("There … many students in the hall.", "are", ["are", "is", "am", "be"])])
            A(build_choice(s[0], s[1], s[2], "There is — единственное число, there are — множественное.", "There is/are", [3, 4]))
        for _ in range(12):
            A(build_choice("Choose the correct preposition: I get up … 7 o'clock.", "at", ["at", "in", "on", "to"], "С точным временем — at.", "Prepositions", [1, 2]))
        for _ in range(12):
            A(build_choice("My birthday is … May.", "in", ["in", "at", "on", "to"], "С месяцами и годами — in.", "Prepositions", [1, 2]))
        for _ in range(12):
            A(build_choice("Translate: «всегда»", "always", ["always", "never", "sometimes", "usually"], "always — всегда (100%).", "Vocabulary", [3, 4]))
        for _ in range(12):
            n = random.randint(2, 9)
            A(build_choice(f"How do you write the number {n} in English?", ["two", "three", "four", "five", "six", "seven", "eight", "nine"][n - 2],
                           ["two", "three", "four", "five", "six", "seven", "eight", "nine"], f"{n} = " + ["two", "three", "four", "five", "six", "seven", "eight", "nine"][n - 2] + ".", "Numbers", [1, 2]))
        return P
    if grade in (7, 8):
        for _ in range(14):
            s = random.choice([("If it rains, we … at home.", "will stay", ["will stay", "stay", "would stay", "stayed"]),
                             ("If I had time, I … you.", "would help", ["would help", "will help", "help", "helped"]),
                             ("If she … tired, she will go to bed.", "is", ["is", "was", "will be", "were"])])
            A(build_choice(s[0], s[1], s[2], "Условные предложения: First Conditional (will), Second Conditional (would + V).", "Conditionals", [1, 2]))
        for _ in range(14):
            s = random.choice([("The letter … yesterday.", "was written", ["was written", "is written", "wrote", "has written"]),
                             ("English … all over the world.", "is spoken", ["is spoken", "speaks", "spoke", "is speaking"]),
                             ("The house … in 1990.", "was built", ["was built", "is built", "built", "has built"])])
            A(build_choice(s[0], s[1], s[2], "Passive Voice: be + V3.", "Passive Voice", [1, 2]))
        for _ in range(14):
            s = random.choice([("He said that he … busy.", "was", ["was", "is", "will be", "be"]),
                             ("She told me that she … the film.", "had seen", ["had seen", "has seen", "sees", "will see"])])
            A(build_choice(s[0], s[1], s[2], "Reported speech: согласование времён (backshift).", "Reported Speech", [3, 4]))
        for _ in range(14):
            s = random.choice([("I enjoy … books.", "reading", ["reading", "read", "to read", "reads"]),
                             ("She decided … a doctor.", "to become", ["to become", "becoming", "become", "became"]),
                             ("He wants … English.", "to learn", ["to learn", "learning", "learn", "learned"])])
            A(build_choice(s[0], s[1], s[2], "После enjoy — герундий (-ing), после decide/want — инфинитив с to.", "Gerund & Infinitive", [3, 4]))
        for _ in range(12):
            s = random.choice([("You … do your homework.", "must", ["must", "can", "may", "needn't"]),
                             ("… I come in?", "May", ["May", "Must", "Should", "Would"]),
                             ("He … swim very well.", "can", ["can", "must", "should", "may"])])
            A(build_choice(s[0], s[1], s[2], "Модальные глаголы: must — долженствование, can — способность, may — разрешение.", "Modals", [1, 2]))
        for _ in range(12):
            s = random.choice([("I have lived here … 2010.", "since", ["since", "for", "from", "during"]),
                             ("She has waited … two hours.", "for", ["for", "since", "at", "by"])])
            A(build_choice(s[0], s[1], s[2], "since + точка во времени, for + период.", "Present Perfect", [3, 4]))
        for _ in range(12):
            A(build_choice("Choose: The book … cover is red is mine.", "whose", ["whose", "who", "which", "that"], "whose — притяжательное относительное местоимение.", "Relative clauses", [3, 4]))
        for _ in range(12):
            A(build_choice("Translate: «достопримечательности»", "sights", ["sights", "rights", "nights", "flights"], "sights — достопримечательности.", "Vocabulary", [1, 2]))
        return P
    if grade in (9, 10, 11):
        for _ in range(14):
            s = random.choice([("By the time we arrived, the film … .", "had started", ["had started", "has started", "started", "starts"]),
                             ("She … dinner when I called.", "was cooking", ["was cooking", "cooked", "has cooked", "cooks"]),
                             ("I … my homework before I went out.", "had finished", ["had finished", "have finished", "finish", "was finishing"])])
            A(build_choice(s[0], s[1], s[2], "Past Perfect — действие, завершённое до другого действия в прошлом.", "Tenses", [1, 2]))
        for _ in range(14):
            s = random.choice([("He … be at home — the lights are off.", "can't", ["can't", "mustn't", "needn't", "shouldn't"]),
                             ("You … pay: it's free.", "needn't", ["needn't", "mustn't", "can't", "shouldn't"]),
                             ("Students … hand in their essays on time.", "must", ["must", "can", "may", "needn't"])])
            A(build_choice(s[0], s[1], s[2], "Модальные глаголы для дедукции и долженствования.", "Modals", [1, 2]))
        for _ in range(14):
            s = random.choice([("If I … you, I would apologise.", "were", ["were", "am", "was being", "will be"]),
                             ("If he had studied, he … the exam.", "would have passed", ["would have passed", "will pass", "passes", "would pass"])])
            A(build_choice(s[0], s[1], s[2], "Second/Third Conditional.", "Conditionals", [1, 2]))
        for _ in range(12):
            A(build_choice("Choose the synonym of «big»:", "enormous", ["enormous", "tiny", "short", "narrow"], "enormous — огромный, синоним big.", "Vocabulary", [3, 4]))
        for _ in range(12):
            A(build_choice("Choose the antonym of «ancient»:", "modern", ["modern", "old", "historical", "antique"], "ancient — древний, антоним modern.", "Vocabulary", [3, 4]))
        for _ in range(12):
            A(build_choice("… having lunch, he went for a walk.", "After", ["After", "Before", "While", "During"], "After + V-ing — «после того как».", "Linking words", [3, 4]))
        for _ in range(12):
            A(build_choice("The results were … : nobody expected them.", "unexpected", ["unexpected", "expecting", "expectedly", "unexpect"], "Прилагательное с отрицательной приставкой un-.", "Word formation", [1, 2]))
        for _ in range(12):
            A(build_choice("Choose the correct form: Neither of the answers … correct.", "is", ["is", "are", "be", "were"], "Neither — единственное число: is.", "Grammar", [1, 2]))
        for _ in range(12):
            A(build_choice("He is used … up early.", "to getting", ["to getting", "to get", "get", "getting"], "be used to + V-ing — «привык к».", "Grammar", [3, 4]))
        for _ in range(10):
            A(build_choice("Which word is a phrasal verb?", "give up", ["give up", "giving", "gave", "giver"], "give up — фразовый глагол (бросать).", "Vocabulary", [1, 2]))
        for _ in range(10):
            A(build_choice("Choose: I look forward … from you.", "to hearing", ["to hearing", "to hear", "hearing", "hear"], "look forward to + V-ing.", "Grammar", [3, 4]))
        return P
    return P


GENS = {}  # заполняется в gen_curated.py
