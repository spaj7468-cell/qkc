# -*- coding: utf-8 -*-
"""Английский язык, 1–11 классы. Богатая вариативность."""
import random
from build_bank import build_choice, build_input, build_tf
from gen_common import pairs_items

LEVEL = {1: "p", 2: "p", 3: "p", 4: "p", 5: "m", 6: "m", 7: "t", 8: "t", 9: "s", 10: "s", 11: "s"}

VOCAB = {
"p": [("кошка", "cat"), ("собака", "dog"), ("дом", "house"), ("стол", "table"), ("стул", "chair"), ("книга", "book"),
      ("ручка", "pen"), ("карандаш", "pencil"), ("школа", "school"), ("учитель", "teacher"), ("друг", "friend"),
      ("мама", "mother"), ("папа", "father"), ("брат", "brother"), ("сестра", "sister"), ("бабушка", "grandmother"),
      ("дедушка", "grandfather"), ("молоко", "milk"), ("хлеб", "bread"), ("яблоко", "apple"), ("банан", "banana"),
      ("вода", "water"), ("сок", "juice"), ("сыр", "cheese"), ("яйцо", "egg"), ("рыба", "fish"), ("птица", "bird"),
      ("лошадь", "horse"), ("корова", "cow"), ("медведь", "bear"), ("лиса", "fox"), ("заяц", "hare"),
      ("солнце", "sun"), ("луна", "moon"), ("звезда", "star"), ("небо", "sky"), ("дерево", "tree"),
      ("цветок", "flower"), ("трава", "grass"), ("зима", "winter"), ("весна", "spring"), ("лето", "summer"),
      ("осень", "autumn"), ("снег", "snow"), ("дождь", "rain"), ("красный", "red"), ("синий", "blue"),
      ("зелёный", "green"), ("жёлтый", "yellow"), ("чёрный", "black"), ("белый", "white"), ("один", "one"),
      ("два", "two"), ("три", "three"), ("четыре", "four"), ("пять", "five"), ("шесть", "six"), ("семь", "seven"),
      ("восемь", "eight"), ("девять", "nine"), ("десять", "ten"), ("играть", "play"), ("читать", "read"),
      ("писать", "write"), ("бегать", "run"), ("прыгать", "jump"), ("петь", "sing"), ("танцевать", "dance"),
      ("рисовать", "draw"), ("спать", "sleep"), ("есть", "eat"), ("пить", "drink"), ("большой", "big"),
      ("маленький", "small"), ("хороший", "good"), ("плохой", "bad"), ("быстрый", "fast"), ("медленный", "slow"),
      ("новый", "new"), ("старый", "old"), ("тёплый", "warm"), ("холодный", "cold"), ("рука", "hand"),
      ("голова", "head"), ("глаз", "eye"), ("нос", "nose"), ("рот", "mouth"), ("ухо", "ear"), ("нога", "leg")],
"m": [("город", "city"), ("деревня", "village"), ("улица", "street"), ("магазин", "shop"), ("библиотека", "library"),
      ("больница", "hospital"), ("музей", "museum"), ("театр", "theatre"), ("парк", "park"), ("вокзал", "station"),
      ("аэропорт", "airport"), ("поезд", "train"), ("автобус", "bus"), ("автомобиль", "car"), ("велосипед", "bicycle"),
      ("корабль", "ship"), ("самолёт", "plane"), ("дорога", "road"), ("мост", "bridge"), ("река", "river"),
      ("море", "sea"), ("озеро", "lake"), ("гора", "mountain"), ("лес", "forest"), ("поле", "field"),
      ("погода", "weather"), ("ветер", "wind"), ("облако", "cloud"), ("гроза", "storm"), ("туман", "fog"),
      ("профессия", "job"), ("врач", "doctor"), ("медсестра", "nurse"), ("инженер", "engineer"), ("пилот", "pilot"),
      ("повар", "cook"), ("фермер", "farmer"), ("художник", "artist"), ("певец", "singer"), ("учёный", "scientist"),
      ("полицейский", "policeman"), ("пожарный", "fireman"), ("спортсмен", "sportsman"), ("ученик", "pupil"),
      ("студент", "student"), ("предмет", "subject"), ("урок", "lesson"), ("домашнее задание", "homework"),
      ("оценка", "mark"), ("класс", "classroom"), ("доска", "blackboard"), ("парта", "desk"), ("окно", "window"),
      ("дверь", "door"), ("стена", "wall"), ("пол", "floor"), ("потолок", "ceiling"), ("семья", "family"),
      ("родители", "parents"), ("дети", "children"), ("сын", "son"), ("дочь", "daughter"), ("муж", "husband"),
      ("жена", "wife"), ("дядя", "uncle"), ("тётя", "aunt"), ("двоюродный брат", "cousin"), ("племянник", "nephew"),
      ("одежда", "clothes"), ("пальто", "coat"), ("платье", "dress"), ("юбка", "skirt"), ("брюки", "trousers"),
      ("рубашка", "shirt"), ("свитер", "sweater"), ("обувь", "shoes"), ("шапка", "hat"), ("перчатки", "gloves"),
      ("завтрак", "breakfast"), ("обед", "lunch"), ("ужин", "dinner"), ("блюдо", "dish"), ("суп", "soup"),
      ("салат", "salad"), ("мясо", "meat"), ("овощи", "vegetables"), ("фрукты", "fruit"), ("десерт", "dessert")],
"t": [("окружающая среда", "environment"), ("загрязнение", "pollution"), ("природа", "nature"), ("общество", "society"),
      ("развитие", "development"), ("исследование", "research"), ("открытие", "discovery"), ("изобретение", "invention"),
      ("технология", "technology"), ("устройство", "device"), ("программа", "program"), ("компьютер", "computer"),
      ("интернет", "internet"), ("сообщение", "message"), ("письмо", "letter"), ("посылка", "parcel"),
      ("путешествие", "journey"), ("поездка", "trip"), ("отпуск", "holiday"), ("билет", "ticket"),
      ("паспорт", "passport"), ("багаж", "luggage"), ("гостиница", "hotel"), ("достопримечательность", "sight"),
      ("памятник", "monument"), ("галерея", "gallery"), ("выставка", "exhibition"), ("представление", "performance"),
      ("зритель", "spectator"), ("аудитория", "audience"), ("успех", "success"), ("неудача", "failure"),
      ("опыт", "experience"), ("знание", "knowledge"), ("умение", "skill"), ("навык", "ability"),
      ("решение", "decision"), ("выбор", "choice"), ("возможность", "opportunity"), ("цель", "goal"),
      ("мечта", "dream"), ("план", "plan"), ("будущее", "future"), ("прошлое", "past"), ("настоящее", "present"),
      ("здоровье", "health"), ("болезнь", "illness"), ("лекарство", "medicine"), ("привычка", "habit"),
      ("характер", "character"), ("внешность", "appearance"), ("поведение", "behaviour"), ("отношение", "attitude"),
      ("дружба", "friendship"), ("взаимопонимание", "understanding"), ("ссора", "quarrel"), ("соглашение", "agreement"),
      ("новость", "news"), ("газета", "newspaper"), ("журнал", "magazine"), ("статья", "article"),
      ("заголовок", "headline"), ("реклама", "advertisement"), ("объявление", "announcement"),
      ("магазин", "shop"), ("цена", "price"), ("скидка", "discount"), ("продажа", "sale"), ("покупка", "purchase"),
      ("деньги", "money"), ("счёт", "bill"), ("кошелёк", "wallet"), ("банк", "bank"), ("работа", "work"),
      ("карьера", "career"), ("собеседование", "interview"), ("зарплата", "salary"), ("команда", "team"),
      ("руководитель", "manager"), ("сотрудник", "employee"), ("компания", "company")],
"s": [("устойчивое развитие", "sustainable development"), ("глобальное потепление", "global warming"),
      ("биоразнообразие", "biodiversity"), ("ископаемое топливо", "fossil fuel"), ("возобновляемая энергия", "renewable energy"),
      ("население", "population"), ("миграция", "migration"), ("урбанизация", "urbanisation"), ("бедность", "poverty"),
      ("неравенство", "inequality"), ("гражданство", "citizenship"), ("избиратель", "voter"),
      ("правительство", "government"), ("парламент", "parliament"), ("закон", "law"), ("права человека", "human rights"),
      ("свобода слова", "freedom of speech"), ("экономика", "economy"), ("инфляция", "inflation"),
      ("безработица", "unemployment"), ("инвестиции", "investment"), ("прибыль", "profit"), ("убыток", "loss"),
      ("предприниматель", "entrepreneur"), ("конкуренция", "competition"), ("спрос", "demand"),
      ("предложение", "supply"), ("рынок", "market"), ("торговля", "trade"), ("экспорт", "export"),
      ("импорт", "import"), ("валюта", "currency"), ("налог", "tax"), ("бюджет", "budget"),
      ("наука", "science"), ("физика", "physics"), ("химия", "chemistry"), ("биология", "biology"),
      ("математика", "mathematics"), ("литература", "literature"), ("философия", "philosophy"),
      ("психология", "psychology"), ("социология", "sociology"), ("история", "history"),
      ("география", "geography"), ("искусство", "art"), ("культура", "culture"), ("традиция", "tradition"),
      ("наследие", "heritage"), ("язык", "language"), ("перевод", "translation"), ("словарь", "dictionary"),
      ("текст", "text"), ("абзац", "paragraph"), ("предложение", "sentence"), ("слово", "word"),
      ("значение", "meaning"), ("произношение", "pronunciation"), ("грамматика", "grammar"),
      ("правило", "rule"), ("исключение", "exception"), ("упражнение", "exercise"), ("экзамен", "exam"),
      ("результат", "result"), ("оценка", "grade"), ("университет", "university"), ("колледж", "college"),
      ("степень", "degree"), ("лекция", "lecture"), ("семинар", "seminar"), ("исследователь", "researcher"),
      ("гипотеза", "hypothesis"), ("эксперимент", "experiment"), ("данные", "data"), ("анализ", "analysis"),
      ("вывод", "conclusion"), ("доклад", "report"), ("презентация", "presentation")]
}

IRREGULAR = {
"p": [("be", "was/were", "been", "быть"), ("go", "went", "gone", "идти"), ("do", "did", "done", "делать"),
      ("have", "had", "had", "иметь"), ("see", "saw", "seen", "видеть"), ("come", "came", "come", "приходить"),
      ("get", "got", "got", "получать"), ("make", "made", "made", "делать, создавать"), ("take", "took", "taken", "брать"),
      ("eat", "ate", "eaten", "есть"), ("drink", "drank", "drunk", "пить"), ("run", "ran", "run", "бежать"),
      ("swim", "swam", "swum", "плавать"), ("sing", "sang", "sung", "петь"), ("read", "read", "read", "читать"),
      ("write", "wrote", "written", "писать"), ("sleep", "slept", "slept", "спать"), ("give", "gave", "given", "давать"),
      ("find", "found", "found", "находить"), ("say", "said", "said", "сказать")],
"m": [("begin", "began", "begun", "начинать"), ("break", "broke", "broken", "ломать"), ("bring", "brought", "brought", "приносить"),
      ("buy", "bought", "bought", "покупать"), ("catch", "caught", "caught", "ловить"), ("choose", "chose", "chosen", "выбирать"),
      ("cut", "cut", "cut", "резать"), ("draw", "drew", "drawn", "рисовать"), ("drive", "drove", "driven", "водить"),
      ("fall", "fell", "fallen", "падать"), ("feel", "felt", "felt", "чувствовать"), ("fly", "flew", "flown", "летать"),
      ("forget", "forgot", "forgotten", "забывать"), ("grow", "grew", "grown", "расти"), ("hear", "heard", "heard", "слышать"),
      ("keep", "kept", "kept", "хранить"), ("know", "knew", "known", "знать"), ("leave", "left", "left", "покидать"),
      ("lose", "lost", "lost", "терять"), ("meet", "met", "met", "встречать"), ("pay", "paid", "paid", "платить"),
      ("put", "put", "put", "класть"), ("ride", "rode", "ridden", "ездить верхом"), ("sell", "sold", "sold", "продавать"),
      ("send", "sent", "sent", "посылать"), ("show", "showed", "shown", "показывать"), ("sit", "sat", "sat", "сидеть"),
      ("speak", "spoke", "spoken", "говорить"), ("spend", "spent", "spent", "тратить"), ("stand", "stood", "stood", "стоять"),
      ("teach", "taught", "taught", "учить"), ("tell", "told", "told", "рассказывать"), ("think", "thought", "thought", "думать"),
      ("understand", "understood", "understood", "понимать"), ("wear", "wore", "worn", "носить"),
      ("win", "won", "won", "выигрывать"), ("build", "built", "built", "строить")],
"t": [("arise", "arose", "arisen", "возникать"), ("bear", "bore", "born", "нести, рождать"), ("beat", "beat", "beaten", "бить"),
      ("become", "became", "become", "становиться"), ("bite", "bit", "bitten", "кусать"), ("blow", "blew", "blown", "дуть"),
      ("cost", "cost", "cost", "стоить"), ("dig", "dug", "dug", "копать"), ("feed", "fed", "fed", "кормить"),
      ("fight", "fought", "fought", "сражаться"), ("forgive", "forgave", "forgiven", "прощать"),
      ("freeze", "froze", "frozen", "замерзать"), ("hang", "hung", "hung", "вешать"), ("hide", "hid", "hidden", "прятать"),
      ("hit", "hit", "hit", "ударять"), ("hurt", "hurt", "hurt", "причинять боль"), ("lend", "lent", "lent", "одалживать"),
      ("lie", "lay", "lain", "лежать"), ("mean", "meant", "meant", "означать"), ("mistake", "mistook", "mistaken", "ошибаться"),
      ("prove", "proved", "proven", "доказывать"), ("rise", "rose", "risen", "подниматься"),
      ("seek", "sought", "sought", "искать"), ("shake", "shook", "shaken", "трясти"), ("shine", "shone", "shone", "сиять"),
      ("shoot", "shot", "shot", "стрелять"), ("shut", "shut", "shut", "закрывать"), ("sink", "sank", "sunk", "тонуть"),
      ("steal", "stole", "stolen", "красть"), ("sweep", "swept", "swept", "мести"), ("swim", "swam", "swum", "плавать"),
      ("throw", "threw", "thrown", "бросать"), ("wake", "woke", "woken", "просыпаться"),
      ("withdraw", "withdrew", "withdrawn", "отзывать"), ("spoil", "spoilt", "spoilt", "портить")],
"s": [("overcome", "overcame", "overcome", "преодолевать"), ("undertake", "undertook", "undertaken", "предпринимать"),
      ("undergo", "underwent", "undergone", "подвергаться"), ("withstand", "withstood", "withstood", "выдерживать"),
      ("foresee", "foresaw", "foreseen", "предвидеть"), ("forbid", "forbade", "forbidden", "запрещать"),
      ("outweigh", "outweighed", "outweighed", "перевешивать"), ("withhold", "withheld", "withheld", "удерживать"),
      ("arise", "arose", "arisen", "возникать"), ("bet", "bet", "bet", "держать пари"),
      ("broadcast", "broadcast", "broadcast", "транслировать"), ("deal", "dealt", "dealt", "иметь дело"),
      ("flee", "fled", "fled", "спасаться бегством"), ("forbear", "forbore", "forborne", "воздерживаться"),
      ("grind", "ground", "ground", "молоть"), ("kneel", "knelt", "knelt", "становиться на колени"),
      ("lead", "led", "led", "вести"), ("light", "lit", "lit", "освещать"), ("quit", "quit", "quit", "покидать"),
      ("sew", "sewed", "sewn", "шить"), ("slay", "slew", "slain", "убивать"), ("sow", "sowed", "sown", "сеять"),
      ("spring", "sprang", "sprung", "прыгать"), ("sting", "stung", "stung", "жалить"),
      ("stride", "strode", "stridden", "шагать"), ("strive", "strove", "striven", "стремиться"),
      ("swear", "swore", "sworn", "клясться"), ("tear", "tore", "torn", "рвать"), ("weave", "wove", "woven", "ткать"),
      ("weep", "wept", "wept", "плакать")]
}

REGULAR = {
"p": ["play", "work", "help", "ask", "call", "watch", "clean", "open", "close", "like", "love", "want", "need", "start", "finish"],
"m": ["study", "carry", "try", "stop", "plan", "live", "arrive", "travel", "listen", "answer", "visit", "cook", "wash", "play", "use"],
"t": ["decide", "explain", "improve", "mention", "notice", "organise", "prepare", "produce", "protect", "realise",
      "recommend", "reduce", "replace", "require", "suggest", "support", "translate", "compare", "increase", "describe"],
"s": ["analyse", "evaluate", "determine", "establish", "indicate", "investigate", "maintain", "obtain", "participate",
      "recognise", "regulate", "represent", "reveal", "specify", "sustain", "transform", "vary", "witness", "accomplish", "contribute"]
}

COMPAR = {
"p": [("big", "bigger", "biggest"), ("small", "smaller", "smallest"), ("tall", "taller", "tallest"),
      ("short", "shorter", "shortest"), ("fast", "faster", "fastest"), ("slow", "slower", "slowest"),
      ("good", "better", "best"), ("bad", "worse", "worst"), ("long", "longer", "longest"),
      ("cold", "colder", "coldest"), ("hot", "hotter", "hottest"), ("new", "newer", "newest"),
      ("old", "older", "oldest"), ("happy", "happier", "happiest"), ("easy", "easier", "easiest")],
"m": [("beautiful", "more beautiful", "most beautiful"), ("interesting", "more interesting", "most interesting"),
      ("dangerous", "more dangerous", "most dangerous"), ("expensive", "more expensive", "most expensive"),
      ("comfortable", "more comfortable", "most comfortable"), ("popular", "more popular", "most popular"),
      ("difficult", "more difficult", "most difficult"), ("important", "more important", "most important"),
      ("heavy", "heavier", "heaviest"), ("busy", "busier", "busiest"), ("noisy", "noisier", "noisiest"),
      ("friendly", "friendlier", "friendliest"), ("careful", "more careful", "most careful"),
      ("far", "further", "furthest"), ("little", "less", "least")],
"t": [("successful", "more successful", "most successful"), ("effective", "more effective", "most effective"),
      ("significant", "more significant", "most significant"), ("reliable", "more reliable", "most reliable"),
      ("efficient", "more efficient", "most efficient"), ("appropriate", "more appropriate", "most appropriate"),
      ("sensitive", "more sensitive", "most sensitive"), ("creative", "more creative", "most creative"),
      ("powerful", "more powerful", "most powerful"), ("valuable", "more valuable", "most valuable"),
      ("narrow", "narrower", "narrowest"), ("clever", "cleverer", "cleverest"), ("quiet", "quieter", "quietest"),
      ("simple", "simpler", "simplest"), ("gentle", "gentler", "gentlest")],
"s": [("sophisticated", "more sophisticated", "most sophisticated"), ("comprehensive", "more comprehensive", "most comprehensive"),
      ("controversial", "more controversial", "most controversial"), ("inevitable", "more inevitable", "most inevitable"),
      ("substantial", "more substantial", "most substantial"), ("prevalent", "more prevalent", "most prevalent"),
      ("intricate", "more intricate", "most intricate"), ("detrimental", "more detrimental", "most detrimental"),
      ("advantageous", "more advantageous", "most advantageous"), ("versatile", "more versatile", "most versatile"),
      ("thorough", "more thorough", "most thorough"), ("profound", "more profound", "most profound"),
      ("adequate", "more adequate", "most adequate"), ("feasible", "more feasible", "most feasible"),
      ("legitimate", "more legitimate", "most legitimate")]
}

PLURAL = {
"p": [("book", "books"), ("cat", "cats"), ("pen", "pens"), ("dog", "dogs"), ("table", "tables"), ("box", "boxes"),
      ("bus", "buses"), ("dish", "dishes"), ("baby", "babies"), ("toy", "toys"), ("child", "children"),
      ("man", "men"), ("woman", "women"), ("foot", "feet"), ("tooth", "teeth"), ("mouse", "mice"),
      ("sheep", "sheep"), ("fish", "fish"), ("leaf", "leaves"), ("knife", "knives")],
"m": [("city", "cities"), ("country", "countries"), ("story", "stories"), ("family", "families"), ("day", "days"),
      ("key", "keys"), ("boy", "boys"), ("class", "classes"), ("glass", "glasses"), ("watch", "watches"),
      ("sandwich", "sandwiches"), ("potato", "potatoes"), ("tomato", "tomatoes"), ("photo", "photos"),
      ("piano", "pianos"), ("hero", "heroes"), ("shelf", "shelves"), ("half", "halves"), ("wife", "wives"),
      ("life", "lives"), ("goose", "geese"), ("ox", "oxen"), ("person", "people"), ("deer", "deer")],
"t": [("analysis", "analyses"), ("crisis", "crises"), ("basis", "bases"), ("thesis", "theses"), ("phenomenon", "phenomena"),
      ("criterion", "criteria"), ("datum", "data"), ("medium", "media"), ("index", "indices"), ("appendix", "appendices"),
      ("formula", "formulae"), ("bureau", "bureaux"), ("axis", "axes"), ("hypothesis", "hypotheses"),
      ("oasis", "oases"), ("emphasis", "emphases"), ("alumnus", "alumni"), ("syllabus", "syllabi"),
      ("stimulus", "stimuli"), ("radius", "radii"), ("curriculum", "curricula"), ("memorandum", "memoranda")],
"s": [("paradigm", "paradigms"), ("corpus", "corpora"), ("stratum", "strata"), ("vertex", "vertices"),
      ("matrix", "matrices"), ("cortex", "cortices"), ("bacterium", "bacteria"), ("erratum", "errata"),
      ("millennium", "millennia"), ("symposium", "symposia"), ("referendum", "referenda"), ("spectrum", "spectra"),
      ("cactus", "cacti"), ("focus", "foci"), ("fungus", "fungi"), ("nucleus", "nuclei"), ("terminus", "termini"),
      ("antenna", "antennae"), ("vertebra", "vertebrae"), ("persona", "personae"), ("schema", "schemata"),
      ("dogma", "dogmata")]
}

GRAMMAR = {
"p": [("I … a pupil.", "am", ["am", "is", "are", "be"], "С подлежащим I используется am.", "to be"),
      ("He … my brother.", "is", ["is", "am", "are", "be"], "He/She/It → is.", "to be"),
      ("We … friends.", "are", ["are", "is", "am", "be"], "We/You/They → are.", "to be"),
      ("There … a cat on the sofa.", "is", ["is", "are", "be", "am"], "Единственное число → there is.", "there is/are"),
      ("There … five books on the shelf.", "are", ["are", "is", "be", "was"], "Множественное число → there are.", "there is/are"),
      ("She … to school every day.", "goes", ["goes", "go", "going", "gone"], "Present Simple, 3-е лицо ед. ч. → -s/-es.", "Present Simple"),
      ("They … football on Sundays.", "play", ["play", "plays", "playing", "played"], "Present Simple, they → без изменений.", "Present Simple"),
      ("My mum … delicious cakes.", "cooks", ["cooks", "cook", "cooking", "cooked"], "Present Simple, 3-е лицо ед. ч.", "Present Simple"),
      ("Look! The baby … .", "is sleeping", ["is sleeping", "sleeps", "sleep", "slept"], "Present Continuous: действие сейчас.", "Present Continuous"),
      ("I … my homework now.", "am doing", ["am doing", "do", "does", "did"], "Present Continuous с now.", "Present Continuous"),
      ("We … TV at the moment.", "are watching", ["are watching", "watch", "watches", "watched"], "Present Continuous, at the moment.", "Present Continuous"),
      ("Yesterday I … to the park.", "went", ["went", "go", "goes", "going"], "Past Simple: yesterday → вторая форма.", "Past Simple"),
      ("She … a nice dress last Sunday.", "wore", ["wore", "wear", "wears", "wearing"], "Past Simple от wear → wore.", "Past Simple"),
      ("… you like ice cream?", "Do", ["Do", "Does", "Did", "Are"], "Вопрос в Present Simple с you → Do.", "Questions"),
      ("… he play the piano?", "Does", ["Does", "Do", "Is", "Has"], "Вопрос в Present Simple с he → Does.", "Questions"),
      ("I … got a new bike.", "have", ["have", "has", "am", "had"], "have got / has got.", "have got"),
      ("She … got long hair.", "has", ["has", "have", "is", "had"], "She/He/It → has got.", "have got"),
      ("This is … apple.", "an", ["an", "a", "the", "—"], "Перед гласным звуком → an.", "Articles"),
      ("I can see … cat in the garden.", "a", ["a", "an", "the", "—"], "Перед согласным звуком → a.", "Articles"),
      ("… sun is bright today.", "The", ["The", "A", "An", "—"], "Единственный в своём роде предмет → the.", "Articles"),
      ("I get up … seven o'clock.", "at", ["at", "in", "on", "to"], "С точным временем → at.", "Prepositions"),
      ("My birthday is … June.", "in", ["in", "at", "on", "to"], "С месяцами и годами → in.", "Prepositions"),
      ("We have lessons … Monday.", "on", ["on", "in", "at", "to"], "С днями недели → on.", "Prepositions"),
      ("The book is … the table.", "on", ["on", "in", "at", "to"], "На поверхности → on.", "Prepositions"),
      ("There are many toys … the box.", "in", ["in", "on", "at", "under"], "Внутри → in.", "Prepositions"),
      ("I … swim very well.", "can", ["can", "am", "do", "does"], "Способность → can + инфинитив.", "Modals"),
      ("You … do your homework.", "must", ["must", "can", "may", "needn't"], "Обязанность → must.", "Modals"),
      ("… I go out, please?", "May", ["May", "Must", "Should", "Would"], "Просьба о разрешении → May.", "Modals"),
      ("My sister is … than me.", "older", ["older", "old", "oldest", "more old"], "Сравнительная степень → -er.", "Comparatives"),
      ("This is the … book I have read.", "best", ["best", "good", "better", "most good"], "Превосходная степень от good → best.", "Superlatives")],
"m": [("I have lived here … 2015.", "since", ["since", "for", "from", "during"], "since + точка во времени.", "Present Perfect"),
      ("She has worked here … five years.", "for", ["for", "since", "at", "by"], "for + период.", "Present Perfect"),
      ("Have you ever … to London?", "been", ["been", "be", "being", "was"], "Present Perfect: have/has + V3.", "Present Perfect"),
      ("He … just finished his project.", "has", ["has", "have", "is", "was"], "He → has.", "Present Perfect"),
      ("By the time we came, he … .", "had left", ["had left", "has left", "left", "leaves"], "Past Perfect: действие до другого в прошлом.", "Past Perfect"),
      ("She said that she … tired.", "was", ["was", "is", "were", "be"], "Согласование времён в косвенной речи.", "Reported Speech"),
      ("He told me that he … the film already.", "had seen", ["had seen", "has seen", "sees", "will see"], "Backshift: Present Perfect → Past Perfect.", "Reported Speech"),
      ("The letter … yesterday.", "was sent", ["was sent", "is sent", "sent", "has sent"], "Passive Voice, Past: was + V3.", "Passive Voice"),
      ("English … all over the world.", "is spoken", ["is spoken", "speaks", "spoke", "is speaking"], "Passive Voice, Present.", "Passive Voice"),
      ("The house … in 1900.", "was built", ["was built", "is built", "built", "has built"], "Passive Voice с указанием времени в прошлом.", "Passive Voice"),
      ("If it rains, we … at home.", "will stay", ["will stay", "stay", "would stay", "stayed"], "First Conditional: If + Present, will + V.", "Conditionals"),
      ("If I … rich, I would travel.", "were", ["were", "am", "will be", "be"], "Second Conditional: If + Past, would + V.", "Conditionals"),
      ("If he had studied, he … the test.", "would have passed", ["would have passed", "will pass", "passes", "would pass"], "Third Conditional.", "Conditionals"),
      ("I enjoy … books.", "reading", ["reading", "read", "to read", "reads"], "После enjoy → герундий.", "Gerund"),
      ("She decided … a doctor.", "to become", ["to become", "becoming", "become", "became"], "После decide → инфинитив с to.", "Infinitive"),
      ("He wants … English better.", "to learn", ["to learn", "learning", "learn", "learned"], "После want → to + V.", "Infinitive"),
      ("I look forward … you.", "to seeing", ["to seeing", "to see", "seeing", "see"], "look forward to + V-ing.", "Gerund"),
      ("Would you mind … the window?", "opening", ["opening", "to open", "open", "opened"], "После mind → герундий.", "Gerund"),
      ("He stopped … a cigarette.", "to have", ["to have", "having", "have", "had"], "stop + to V — остановиться, чтобы сделать.", "Infinitive"),
      ("This book is … interesting than that one.", "more", ["more", "most", "much", "many"], "Сравнение длинных прилагательных → more.", "Comparatives"),
      ("She is the … student in our class.", "best", ["best", "better", "good", "most"], "Превосходная степень от good.", "Superlatives"),
      ("Mount Everest is the … mountain in the world.", "highest", ["highest", "higher", "high", "most high"], "Превосходная степень: the + -est.", "Superlatives"),
      ("I have … homework today.", "much", ["much", "many", "a lot", "few"], "Homework — неисчисляемое → much.", "Quantifiers"),
      ("There are … students in the hall.", "many", ["many", "much", "a little", "much of"], "Students — исчисляемое → many.", "Quantifiers"),
      ("He gave me … advice.", "some", ["some", "many", "a few", "these"], "Advice — неисчисляемое → some.", "Quantifiers"),
      ("Whose bag is this? — It's … .", "mine", ["mine", "my", "I", "me"], "Абсолютная форма притяжательного местоимения.", "Pronouns"),
      ("I did it … .", "myself", ["myself", "me", "my", "mine"], "Возвратное местоимение.", "Pronouns"),
      ("You … finish the work, … you?", "mustn't", ["mustn't", "don't", "aren't", "haven't"], "Разделительный вопрос к must → mustn't.", "Question tags"),
      ("She is a doctor, … ?", "isn't she", ["isn't she", "doesn't she", "is she", "won't she"], "Разделительный вопрос: утверждение → отрицание.", "Question tags"),
      ("He doesn't like fish, … ?", "does he", ["does he", "doesn't he", "is he", "did he"], "Отрицание → утвердительный «хвостик».", "Question tags")],
"t": [("Hardly … I arrived when it started to rain.", "had", ["had", "have", "did", "was"], "Инверсия после hardly: had + подлежащее.", "Inversion"),
      ("Not only … he sing, but he also dances.", "does", ["does", "do", "is", "has"], "Инверсия после Not only.", "Inversion"),
      ("Never … such a beautiful sunset.", "have I seen", ["have I seen", "I have seen", "I saw", "did I saw"], "Инверсия после never.", "Inversion"),
      ("It was Tom … broke the window.", "who", ["who", "which", "what", "whom"], "Усилительная конструкция It was … who.", "Cleft sentences"),
      ("The film, … was directed by Spielberg, won an Oscar.", "which", ["which", "who", "whom", "what"], "Относительное местоимение для предметов.", "Relative clauses"),
      ("The man … car was stolen called the police.", "whose", ["whose", "who", "which", "that"], "Притяжательное относительное местоимение.", "Relative clauses"),
      ("I wish I … more free time.", "had", ["had", "have", "will have", "would have"], "I wish + Past — сожаление о настоящем.", "Wish"),
      ("If only he … me earlier!", "had told", ["had told", "told", "tells", "would tell"], "If only + Past Perfect — сожаление о прошлом.", "Wish"),
      ("You … have told me about it!", "should", ["should", "would", "could have", "might"], "should have + V3 — упрёк.", "Modals"),
      ("He … be at home: his car is outside.", "must", ["must", "can't", "needn't", "shouldn't"], "Уверенное предположение → must.", "Modals"),
      ("That … be true — it sounds impossible.", "can't", ["can't", "mustn't", "needn't", "shouldn't"], "Невозможность → can't.", "Modals"),
      ("You … pay for the tickets: they are free.", "needn't", ["needn't", "mustn't", "can't", "shouldn't"], "Отсутствие необходимости → needn't.", "Modals"),
      ("I'm not used … up so early.", "to getting", ["to getting", "to get", "get", "getting"], "be used to + V-ing.", "Used to"),
      ("He used … football, but now he doesn't.", "to play", ["to play", "playing", "play", "played"], "used to + инфинитив (привычка в прошлом).", "Used to"),
      ("By next year I … my course.", "will have finished", ["will have finished", "will finish", "finish", "am finishing"], "Future Perfect.", "Future forms"),
      ("This time tomorrow we … on the beach.", "will be lying", ["will be lying", "lie", "will lie", "are lying"], "Future Continuous.", "Future forms"),
      ("The train … at 8 a.m. tomorrow.", "leaves", ["leaves", "will leave", "is leaving", "left"], "Расписание → Present Simple.", "Future forms"),
      ("I … you as soon as I arrive.", "will call", ["will call", "call", "am calling", "would call"], "Future Simple в главной части.", "Future forms"),
      ("He denied … the money.", "taking", ["taking", "to take", "take", "took"], "После deny → герундий.", "Gerund"),
      ("She suggested … to the cinema.", "going", ["going", "to go", "go", "went"], "После suggest → герундий.", "Gerund"),
      ("They avoided … about the accident.", "talking", ["talking", "to talk", "talk", "to talking"], "После avoid → герундий.", "Gerund"),
      ("He insisted … paying the bill.", "on", ["on", "in", "at", "for"], "insist on + V-ing.", "Gerund"),
      ("It's no use … about it.", "worrying", ["worrying", "to worry", "worry", "worried"], "It's no use + V-ing.", "Gerund"),
      ("The report … by the time the meeting started.", "had been written", ["had been written", "was written", "has been written", "is written"], "Passive + Past Perfect.", "Passive Voice"),
      ("New rules … next month.", "will be introduced", ["will be introduced", "will introduce", "are introducing", "introduce"], "Passive + Future Simple.", "Passive Voice"),
      ("Someone … my bicycle!", "has stolen", ["has stolen", "stole", "steals", "is stealing"], "Present Perfect с актуальным результатом.", "Present Perfect"),
      ("I … him since we left school.", "haven't seen", ["haven't seen", "didn't see", "don't see", "hadn't seen"], "Present Perfect с since.", "Present Perfect"),
      ("While I … dinner, the phone rang.", "was cooking", ["was cooking", "cooked", "have cooked", "cook"], "Past Continuous для фона действия.", "Past Continuous"),
      ("We … for two hours when the bus finally arrived.", "had been waiting", ["had been waiting", "waited", "have waited", "are waiting"], "Past Perfect Continuous.", "Past Perfect Continuous"),
      ("The more you practise, the … you become.", "better", ["better", "best", "good", "more good"], "Конструкция the + сравн. ст., the + сравн. ст.", "Comparatives")],
"s": [("Scarcely … the bell rung when the students rushed out.", "had", ["had", "has", "did", "was"], "Инверсия после scarcely.", "Inversion"),
      ("Only after much discussion … a decision.", "did they reach", ["did they reach", "they reached", "they did reach", "reached they"], "Инверсия после only after.", "Inversion"),
      ("So loud … that nobody could sleep.", "was the music", ["was the music", "the music was", "the music", "did the music"], "Инверсия после so + прилагательное.", "Inversion"),
      ("Were I in your position, I … the offer.", "would accept", ["would accept", "will accept", "accept", "accepted"], "Условие без if через инверсию.", "Inversion"),
      ("Had he known the truth, he … differently.", "would have acted", ["would have acted", "will act", "acts", "acted"], "Third Conditional через инверсию.", "Inversion"),
      ("The research, … results were published last year, continues.", "whose", ["whose", "which", "that", "whom"], "Относительное местоимение в формальном стиле.", "Relative clauses"),
      ("He is the person … I spoke to you.", "about whom", ["about whom", "about who", "whom about", "that about"], "Предлог перед whom в формальном стиле.", "Relative clauses"),
      ("Such … the consequences that we had to act at once.", "were", ["were", "was", "is", "are"], "Инверсия после such.", "Inversion"),
      ("Under no circumstances … this information to anyone.", "should you reveal", ["should you reveal", "you should reveal", "you reveal", "reveal you should"], "Инверсия после under no circumstances.", "Inversion"),
      ("Little … that his life was about to change.", "did he know", ["did he know", "he knew", "he did know", "knew he"], "Инверсия после little.", "Inversion"),
      ("It is essential that every student … present.", "be", ["be", "is", "was", "will be"], "Сослагательное наклонение после it is essential that.", "Subjunctive"),
      ("I suggest that the proposal … accepted.", "be", ["be", "is", "was", "will be"], "Сослагательное наклонение после suggest that.", "Subjunctive"),
      ("The data … collected over a decade.", "were", ["were", "was", "is", "been"], "Data — множественное число в формальном стиле.", "Agreement"),
      ("Each of the participants … a certificate.", "received", ["received", "receive", "receiving", "were received"], "Each → единственное число.", "Agreement"),
      ("Neither the manager nor the employees … aware of the risk.", "were", ["were", "was", "is", "been"], "Согласование по ближайшему подлежащему.", "Agreement"),
      ("The number of applicants … risen sharply.", "has", ["has", "have", "are", "were"], "The number of → единственное число.", "Agreement"),
      ("A number of problems … identified.", "were", ["were", "was", "is", "been"], "A number of → множественное число.", "Agreement"),
      ("Despite … hard, he failed the exam.", "working", ["working", "work", "to work", "worked"], "Despite + V-ing.", "Linking words"),
      ("In spite of the rain, the match … .", "went on", ["went on", "goes on", "going on", "to go on"], "In spite of + существительное.", "Linking words"),
      ("He worked hard; … , he passed the exam.", "therefore", ["therefore", "however", "although", "whereas"], "Следствие → therefore.", "Linking words"),
      ("The results were ambiguous; … , further research is needed.", "hence", ["hence", "thus not", "nevertheless not", "whereas"], "Вывод → hence.", "Linking words"),
      ("… being the youngest, she proved the most capable.", "Despite", ["Despite", "Although", "However", "Whereas"], "Despite + V-ing.", "Linking words"),
      ("The theory … widely accepted by the scientific community.", "is", ["is", "are", "were", "been"], "Theory — единственное число.", "Agreement"),
      ("Not until midnight … to bed.", "did he go", ["did he go", "he went", "he did go", "went he"], "Инверсия после not until.", "Inversion"),
      ("He would rather … at home than go out.", "stay", ["stay", "to stay", "staying", "stayed"], "would rather + инфинитив без to.", "Modals"),
      ("I'd rather you … smoke here.", "didn't", ["didn't", "don't", "won't", "not"], "would rather + подлежащее + Past.", "Modals"),
      ("It's high time we … a decision.", "made", ["made", "make", "will make", "making"], "It's high time + Past.", "Subjunctive"),
      ("He behaves as if he … everything.", "knew", ["knew", "knows", "will know", "knowing"], "as if + Past (нереальное).", "Subjunctive"),
      ("The findings suggest that the hypothesis … correct.", "be", ["be", "is", "was", "are"], "Формальный стиль, сослагательное наклонение.", "Subjunctive"),
      ("Were it not … your help, we would have failed.", "for", ["for", "of", "to", "with"], "Were it not for — устойчивая конструкция.", "Inversion")]
}

TOPICS = {
"p": ["Алфавит и звуки", "Семья и друзья", "Школа", "Игрушки", "Животные", "Еда", "Цвета", "Числа", "Время года", "Мой день"],
"m": ["Город и транспорт", "Профессии", "Погода", "Путешествия", "Дом", "Школа и предметы", "Одежда", "Еда и напитки", "Хобби", "Спорт"],
"t": ["Окружающая среда", "Технологии", "СМИ", "Путешествия", "Здоровье", "Образование", "Покупки", "Работа", "Характер человека", "Общество"],
"s": ["Наука и исследования", "Экономика", "Политика и право", "Глобальные проблемы", "Образование", "Культура", "СМИ и реклама", "Технологии будущего", "Карьера", "Общество и личность"]
}


def gen_english(grade, seed=0):
    random.seed(seed)
    lv = LEVEL.get(grade, "s")
    P = []
    A = P.append
    vocab = VOCAB[lv]
    # --- лексика: 4 четверти, круговая раздача тем ---
    quarters = [1, 2, 3, 4]
    random.shuffle(vocab)
    for i, (ru, en) in enumerate(vocab):
        q = quarters[i % 4]
        others_en = [e for _, e in vocab if e != en]
        others_ru = [r for r, _ in vocab if r != ru]
        random.shuffle(others_en); random.shuffle(others_ru)
        A(build_choice(f"Как по-английски будет «{ru}»?", en, others_en[:3], f"«{ru}» — {en}.", "Vocabulary", [q]))
        A(build_choice(f"Как переводится слово «{en}»?", ru, others_ru[:3], f"«{en}» переводится как «{ru}».", "Vocabulary", [q]))
        if i % 2 == 0:
            A(build_tf(f"Верно ли, что «{ru}» переводится как «{en}»?", "Верно", f"Да: {ru} — {en}.", "Vocabulary", [q]))
        else:
            wrong = others_en[0]
            A(build_tf(f"Верно ли, что «{ru}» переводится как «{wrong}»?", "Неверно", f"Неверно: {ru} — {en}.", "Vocabulary", [q]))
    # --- неправильные глаголы ---
    for i, (b, p2, p3, ru) in enumerate(IRREGULAR[lv]):
        q = quarters[(i + 1) % 4]
        others = [x[1] for x in IRREGULAR[lv] if x[0] != b]
        random.shuffle(others)
        A(build_choice(f"Past Simple (V2) от глагола «{b}»:", p2, others[:3], f"{b} — {p2} — {p3}.", "Irregular verbs", [q]))
        others3 = [x[2] for x in IRREGULAR[lv] if x[0] != b]
        random.shuffle(others3)
        A(build_choice(f"Past Participle (V3) от глагола «{b}»:", p3, others3[:3], f"{b} — {p2} — {p3}.", "Irregular verbs", [q]))
        A(build_choice(f"Как переводится глагол «{b}»?", ru, [x[3] for x in IRREGULAR[lv] if x[0] != b][:3],
                       f"«{b}» означает «{ru}».", "Irregular verbs", [q]))
    # --- правильные глаголы ---
    for i, b in enumerate(REGULAR[lv]):
        q = quarters[(i + 2) % 4]
        if b.endswith("e"):
            p2 = b + "d"
        elif b[-1] == "y" and b[-2] not in "aeiou":
            p2 = b[:-1] + "ied"
        elif len(b) >= 3 and b[-1] not in "aeiouwxy" and b[-2] in "aeiou" and b[-3] not in "aeiou":
            p2 = b + b[-1] + "ed"
        else:
            p2 = b + "ed"
        wrongs = [b + "ed" if p2 != b + "ed" else b + "d", b + "ing", b, b[:-1] + "ied" if not b.endswith("y") else b + "ed"]
        A(build_choice(f"Past Simple от правильного глагола «{b}»:", p2, wrongs, f"Правильные глаголы образуют Past Simple добавлением -ed: {p2}.", "Regular verbs", [q]))
    # --- степени сравнения ---
    for i, (a, c, s) in enumerate(COMPAR[lv]):
        q = quarters[(i + 3) % 4]
        others = [x[1] for x in COMPAR[lv] if x[0] != a]
        random.shuffle(others)
        A(build_choice(f"Сравнительная степень от «{a}»:", c, others[:3], f"{a} → {c} → {s}.", "Comparatives", [q]))
        others_s = [x[2] for x in COMPAR[lv] if x[0] != a]
        random.shuffle(others_s)
        A(build_choice(f"Превосходная степень от «{a}»:", s, others_s[:3], f"{a} → {c} → {s}.", "Superlatives", [q]))
    # --- множественное число ---
    for i, (s1, p1) in enumerate(PLURAL[lv]):
        q = quarters[i % 4]
        others = [x[1] for x in PLURAL[lv] if x[0] != s1]
        random.shuffle(others)
        A(build_choice(f"Множественное число от «{s1}»:", p1, others[:3], f"{s1} → {p1}.", "Plurals", [q]))
        others2 = [x[0] for x in PLURAL[lv] if x[1] != p1]
        random.shuffle(others2)
        A(build_choice(f"Единственное число к форме «{p1}»:", s1, others2[:3], f"{s1} → {p1}.", "Plurals", [q]))
    # --- грамматика ---
    for i, (sent, correct, wrongs, exp, topic) in enumerate(GRAMMAR[lv]):
        q = quarters[i % 4]
        A(build_choice(sent, correct, wrongs, exp, topic, [q]))
    # --- тематика и страноведение ---
    for i, t in enumerate(TOPICS[lv]):
        q = quarters[i % 4]
        A(build_choice(f"Какая тема относится к лексическому блоку «{t}»?", "см. варианты", ["см. варианты"], "", "", [q])) if False else None
    # страноведение по уровням
    COUNTRIES = {
        "p": [("the UK", "Великобритания"), ("London", "столица Великобритании"), ("the USA", "США"),
              ("Washington", "столица США"), ("Christmas", "Рождество"), ("Halloween", "праздник 31 октября"),
              ("Big Ben", "знаменитая башня с часами в Лондоне"), ("the Queen", "королева"),
              ("tea", "напиток, который англичане пьют пять раз в день"), ("double-decker bus", "двухэтажный автобус")],
        "m": [("Scotland", "часть Великобритании со своей культурой"), ("Wales", "часть Великобритании с валлийским языком"),
              ("Ireland", "остров, часть которого — независимое государство"), ("Australia", "страна-континент"),
              ("Canada", "страна с двумя государственными языками"), ("New Zealand", "страна, где живут киви"),
              ("Thanksgiving", "американский праздник урожая"), ("the White House", "резиденция президента США"),
              ("Buckingham Palace", "резиденция британского монарха"), ("Stonehenge", "древний памятник в Англии")],
        "t": [("the Commonwealth", "содружество стран во главе с британским монархом"),
              ("Westminster Abbey", "место коронации британских монархов"),
              ("the Houses of Parliament", "здание парламента в Лондоне"),
              ("Oxford", "старейший университет Великобритании"), ("Cambridge", "университетский город в Англии"),
              ("Silicon Valley", "центр IT-индустрии в США"), ("Wall Street", "центр финансовой жизни Нью-Йорка"),
              ("the Statue of Liberty", "символ США в Нью-Йорке"), ("the Thames", "река в Лондоне"),
              ("Loch Ness", "озеро в Шотландии")],
        "s": [("the Magna Carta", "Великая хартия вольностей 1215 года"),
              ("the Bill of Rights", "Билль о правах 1689 года в Англии"),
              ("the Declaration of Independence", "Декларация независимости США 1776 года"),
              ("the Industrial Revolution", "промышленный переворот, начавшийся в Британии"),
              ("the British Empire", "крупнейшая колониальная империя в истории"),
              ("the Commonwealth of Nations", "объединение 56 государств"),
              ("the European Union", "политико-экономический союз европейских стран"),
              ("the United Nations", "международная организация, основанная в 1945 году"),
              ("the Renaissance", "эпоха Возрождения"), ("the Enlightenment", "эпоха Просвещения")]
    }
    for i, (en, ru) in enumerate(COUNTRIES[lv]):
        q = quarters[i % 4]
        A(build_choice(f"Что означает «{en}»?", ru, [x[1] for x in COUNTRIES[lv] if x[0] != en][:3],
                       f"«{en}» — {ru}.", "Culture", [q]))
        A(build_tf(f"Верно ли, что «{en}» означает «{ru}»?", "Верно", f"Да: {en} — {ru}.", "Culture", [q]))
    # --- орфография/фонетика ---
    SPELL = {
        "p": [("beautiful", "b-e-a-u-t-i-f-u-l"), ("because", "b-e-c-a-u-s-e"), ("friend", "f-r-i-e-n-d"),
              ("school", "s-c-h-o-o-l"), ("house", "h-o-u-s-e"), ("family", "f-a-m-i-l-y"),
              ("teacher", "t-e-a-c-h-e-r"), ("window", "w-i-n-d-o-w")],
        "m": [("necessary", "две c и одна s"), ("separate", "par в середине"), ("different", "две f"),
              ("interesting", "три слога -ing"), ("beginning", "две n в конце"), ("tomorrow", "одна r, две o"),
              ("foreign", "ei после for"), ("environment", "n перед ment")],
        "t": [("accommodation", "две c и две m"), ("occurrence", "две c и две r"), ("embarrass", "две r и две s"),
              ("definitely", "без a в середине"), ("government", "n после govern"), ("restaurant", "au в середине"),
              ("independent", "ent на конце"), ("rhythm", "без гласных, кроме y")],
        "s": [("conscience", "sci в середине"), ("bureaucracy", "eau"), ("maintenance", "без a после ten"),
              ("privilege", "без d"), ("consensus", "одна c"), ("millennium", "две n и две l"),
              ("occasionally", "cc и одно s"), ("supersede", "sede, а не cede")]
    }
    for i, (w, hint) in enumerate(SPELL[lv]):
        q = quarters[i % 4]
        letters = list(w)
        if len(letters) > 3:
            idx = random.randint(1, len(letters) - 2)
            masked = "".join(letters[:idx]) + "_" + "".join(letters[idx + 1:])
            A(build_input(f"Вставь пропущенную букву в слове: {masked}", letters[idx],
                          f"Правильное написание: {w}. Подсказка: {hint}.", "Spelling", [q]))
            A(build_choice(f"Выбери правильное написание слова:", w,
                           [w[:idx] + chr((ord(letters[idx]) - 97 + 3) % 26 + 97) + w[idx + 1:],
                            w[:idx] + "_" + w[idx + 1:], w[:max(idx - 1, 0)] + w[idx:], w + w[-1]],
                           f"Верно: {w} ({hint}).", "Spelling", [q]))
    return P
