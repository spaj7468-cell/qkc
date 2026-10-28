# -*- coding: utf-8 -*-
"""США: 14 авторов. Решающий заслон здесь — год первой публикации < 1930."""
from common import A, W

COUNTRY = dict(slug="usa", name="США", label="Американская литература",
               rule="В США с 1 января 2026 года в общественном достоянии всё, "
                    "опубликованное до 1930 года, независимо от года смерти автора. "
                    "Русский перевод — отдельное произведение переводчика, поэтому "
                    "пока не заполнены tr/tr_died, текст не публикуется.")

AUTHORS = [
 A("irving", "Вашингтон Ирвинг", "Washington Irving", 1783, 1859, "романтизм",
   "Первый американский писатель, получивший европейскую известность.", "новелла, рассказ", [
   W("rip-van-winkle", "Рип Ван Винкль", "новелла", 1819, "en", orig="Rip Van Winkle"),
   W("legenda-o-sonnoy-loshchine", "Легенда о Сонной Лощине", "новелла", 1820, "en", orig="The Legend of Sleepy Hollow"),
 ]),

 A("cooper", "Джеймс Фенимор Купер", "James Fenimore Cooper", 1789, 1851, "романтизм",
   "Создатель американского романа о фронтире и цикла о Кожаном Чулке.", "роман", [
   W("pionery", "Пионеры", "роман", 1823, "en", orig="The Pioneers"),
   W("posledniy-iz-mogikan", "Последний из могикан", "роман", 1826, "en", orig="The Last of the Mohicans"),
   W("preriya", "Прерия", "роман", 1827, "en", orig="The Prairie"),
   W("sledopyt", "Следопыт", "роман", 1840, "en", orig="The Pathfinder"),
   W("zveroboy", "Зверобой", "роман", 1841, "en", orig="The Deerslayer"),
 ]),

 A("poe", "Эдгар Аллан По", "Edgar Allan Poe", 1809, 1849, "романтизм",
   "Изобретатель детектива и мастер макабра; умер при невыясненных обстоятельствах в 40 лет.",
   "новелла, рассказ, стихотворение", [
   W("kolodets-i-mayatnik", "Колодец и маятник", "рассказ", 1842, "en", orig="The Pit and the Pendulum"),
   W("padenie-doma-asherov", "Падение дома Ашеров", "рассказ", 1839, "en", orig="The Fall of the House of Usher"),
   W("serdtse-oblichitel", "Сердце-обличитель", "рассказ", 1843, "en", orig="The Tell-Tale Heart"),
   W("maska-krasnoy-smerti", "Маска Красной смерти", "рассказ", 1842, "en", orig="The Masque of the Red Death"),
   W("ubiystvo-na-ulitse-morg", "Убийство на улице Морг", "рассказ", 1841, "en", orig="The Murders in the Rue Morgue"),
   W("tayna-mari-rozhe", "Тайна Мари Роже", "рассказ", 1842, "en", orig="The Mystery of Marie Rogêt"),
   W("poхishchennoe-pismo", "Похищенное письмо", "рассказ", 1844, "en", orig="The Purloined Letter"),
   W("bochonok-amontilyado", "Бочонок амонтильядо", "рассказ", 1846, "en", orig="The Cask of Amontillado"),
   W("chernyy-kot", "Чёрный кот", "рассказ", 1843, "en", orig="The Black Cat"),
   W("lyagushonok", "Лягушонок", "рассказ", 1849, "en", orig="Hop-Frog"),
   W("nizverzhenie-v-maelstrom", "Низвержение в Мальстрём", "рассказ", 1841, "en", orig="A Descent into the Maelström"),
   W("metsengerstein", "Метценгерштейн", "рассказ", 1832, "en", orig="Metzengerstein"),
   W("rukopis-naydennaya-v-butyilke", "Рукопись, найденная в бутылке", "рассказ", 1833, "en", orig="MS. Found in a Bottle"),
   W("annabel-li", "Аннабель Ли", "стихотворение", 1849, "en", orig="Annabel Lee"),
   W("voron", "Ворон", "поэма", 1845, "en", orig="The Raven"),
 ]),

 A("hawthorne", "Натаниэль Готорн", "Nathaniel Hawthorne", 1804, 1864, "романтизм",
   "Потомок судей салемского процесса, всю жизнь писавший о грехе и его наследовании.", "роман, рассказ", [
   W("molodoy-gudman-braun", "Молодой Гудман Браун", "рассказ", 1835, "en", orig="Young Goodman Brown"),
   W("rodinka", "Родимое пятно", "рассказ", 1843, "en", orig="The Birth-Mark"),
   W("alaya-bukva", "Алая буква", "роман", 1850, "en", orig="The Scarlet Letter"),
   W("dom-o-semi-frontonah", "Дом о семи фронтонах", "роман", 1851, "en", orig="The House of the Seven Gables"),
 ]),

 A("thoreau", "Генри Дэвид Торо", "Henry David Thoreau", 1817, 1862, "трансцендентализм",
   "Два года прожил в хижине у Уолденского пруда и описал этот опыт; сидел в тюрьме за неуплату налога.", "очерк, трактат", [
   W("grazhdanskoe-nepovinovenie", "Гражданское неповиновение", "трактат", 1849, "en", orig="Civil Disobedience"),
   W("uolden", "Уолден, или Жизнь в лесу", "очерк", 1854, "en", orig="Walden; or, Life in the Woods"),
   W("progulka", "Прогулка", "очерк", 1862, "en", orig="Walking"),
 ]),

 A("melville", "Герман Мелвилл", "Herman Melville", 1819, 1891, "романтизм",
   "Бывший китобой; при жизни почти забыт, открыт заново только в 1920-е.", "роман, новелла", [
   W("taypi", "Тайпи", "роман", 1846, "en", orig="Typee"),
   W("mobi-dik", "Моби Дик, или Белый Кит", "роман", 1851, "en", orig="Moby-Dick; or, The Whale"),
   W("bartlbi", "Бартлби", "новелла", 1853, "en", orig="Bartleby, the Scrivener"),
   W("benito-sereno", "Бенито Серено", "новелла", 1855, "en", orig="Benito Cereno"),
   W("billy-budd", "Билли Бадд", "новелла", 1919, "en", orig="Billy Budd, Sailor", conf="chk"),
 ]),

 A("whitman", "Уолт Уитмен", "Walt Whitman", 1819, 1892, "поэзия",
   "Выпустил «Листья травы» за свой счёт в 1855; потом всю жизнь дописывал и переиздавал.", "поэма, стихотворение", [
   W("pesnya-o-sebe", "Песня о себе", "поэма", 1855, "en", orig="Song of Myself"),
   W("listya-travy", "Листья травы", "сборник", 1855, "en", orig="Leaves of Grass"),
   W("o-kapitan-moy-kapitan", "О капитан! мой капитан!", "стихотворение", 1865, "en", orig="O Captain! My Captain!"),
   W("kogda-sireni-posledniy-raz-tsvli", "Когда сирень в последний раз цвела", "поэма", 1865, "en", orig="When Lilacs Last in the Dooryard Bloom'd"),
 ]),

 A("dickinson", "Эмили Дикинсон", "Emily Dickinson", 1830, 1886, "поэзия",
   "Почти не выходила из дома; из 1800 стихотворений при жизни напечатала меньше дюжины.", "стихотворение", [
   W("ya-nikto-a-ty", "Я — никто! А ты?", "стихотворение", 1891, "en", orig="I'm Nobody! Who are you?", conf="chk"),
   W("nadezhda-eto-to-s-peryami", "Надежда — это то, что с перьями", "стихотворение", 1891, "en", orig="Hope is the thing with feathers", conf="chk"),
   W("potomu-chto-ne-mogla-ostanovitsya", "Потому что не могла остановиться ради Смерти", "стихотворение", 1890, "en", orig="Because I could not stop for Death", conf="chk"),
 ]),

 A("twain", "Марк Твен", "Mark Twain", 1835, 1910, "реализм",
   "Лоцман на Миссисипи, ставший самым популярным американским писателем своего времени.",
   "роман, рассказ, повесть", [
   W("skachushchaya-lyagushka", "Знаменитая скачущая лягушка из Калавераса", "рассказ", 1865, "en", orig="The Celebrated Jumping Frog of Calaveras County"),
   W("priklyucheniya-toma-soyera", "Приключения Тома Сойера", "роман", 1876, "en", orig="The Adventures of Tom Sawyer"),
   W("prints-i-nishchiy", "Принц и нищий", "роман", 1881, "en", orig="The Prince and the Pauper"),
   W("zhizn-na-missisipi", "Жизнь на Миссисипи", "очерк", 1883, "en", orig="Life on the Mississippi"),
   W("priklyucheniya-gelberri-finna", "Приключения Гекльберри Финна", "роман", 1884, "en", orig="Adventures of Huckleberry Finn"),
   W("yanki-iz-konnektikuta", "Янки из Коннектикута при дворе короля Артура", "роман", 1889, "en", orig="A Connecticut Yankee in King Arthur's Court"),
 ]),

 A("james-h", "Генри Джеймс", "Henry James", 1843, 1916, "реализм",
   "Американец, ставший британцем; изобретатель психологического романа о столкновении двух культур.", "роман, новелла", [
   W("deyzi-miller", "Дейзи Миллер", "новелла", 1878, "en", orig="Daisy Miller"),
   W("portret-ledi", "Портрет леди", "роман", 1881, "en", orig="The Portrait of a Lady"),
   W("povorot-vinta", "Поворот винта", "новелла", 1898, "en", orig="The Turn of the Screw"),
   W("zver-v-dzhunglyah", "Зверь в джунглях", "новелла", 1903, "en", orig="The Beast in the Jungle"),
   W("krylya-golubki", "Крылья голубки", "роман", 1902, "en", orig="The Wings of the Dove"),
 ]),

 A("o-henry", "О. Генри", "O. Henry", 1862, 1910, "реализм",
   "Бывший бухгалтер и беглец от правосудия; мастер финала-неожиданности.", "рассказ", [
   W("dary-volkhvov", "Дары волхвов", "рассказ", 1905, "en", orig="The Gift of the Magi"),
   W("posledniy-list", "Последний лист", "рассказ", 1907, "en", orig="The Last Leaf"),
   W("vozhd-krasnokozhih", "Вождь Краснокожих", "рассказ", 1910, "en", orig="The Ransom of Red Chief"),
   W("dorogi-kotorye-my-vybiraem", "Дороги, которые мы выбираем", "рассказ", 1904, "en", orig="The Roads We Take"),
       ]),

 A("london", "Джек Лондон", "Jack London", 1876, 1916, "реализм",
   "Устричный пират, золотоискатель и моряк; самый высокооплачиваемый писатель Америки 1900-х.",
   "роман, рассказ, повесть", [
   W("syn-volka", "Сын волка", "сборник", 1900, "en", orig="The Son of the Wolf"),
   W("zov-predkov", "Зов предков", "роман", 1903, "en", orig="The Call of the Wild"),
   W("belyy-klyk", "Белый Клык", "роман", 1906, "en", orig="White Fang"),
   W("meksikanets", "Мексиканец", "рассказ", 1911, "en", orig="The Mexican"),
   W("kostyor", "Развести костёр", "рассказ", 1908, "en", orig="To Build a Fire"),
   W("lyubov-k-zhizni", "Любовь к жизни", "рассказ", 1907, "en", orig="Love of Life"),
   W("martin-iden", "Мартин Иден", "роман", 1909, "en", orig="Martin Eden"),
   W("morskoy-volk", "Морской волк", "роман", 1904, "en", orig="The Sea-Wolf"),
   W("zakon-zhizni", "Закон жизни", "рассказ", 1901, "en", orig="The Law of Life"),
 ]),

 A("wharton", "Эдит Уортон", "Edith Wharton", 1862, 1937, "реализм",
   "Первая женщина — лауреат Пулитцеровской премии за роман (1921).", "роман, новелла", [
   W("dom-veselya", "Дом веселья", "роман", 1905, "en", orig="The House of Mirth"),
   W("etan-from", "Этан Фром", "роман", 1911, "en", orig="Ethan Frome"),
   W("vek-nevinnosti", "Век невинности", "роман", 1920, "en", orig="The Age of Innocence"),
    ]),

 A("dreiser", "Теодор Драйзер", "Theodore Dreiser", 1871, 1945, "натурализм",
   "Главный американский натуралист; «Сестру Керри» изъяли из продажи как непристойную.", "роман", [
   W("sestra-kerri", "Сестра Керри", "роман", 1900, "en", orig="Sister Carrie"),
   W("dzhenni-gerkhardt", "Дженни Герхардт", "роман", 1911, "en", orig="Jennie Gerhardt"),
   W("finansist", "Финансист", "роман", 1912, "en", orig="The Financier"),
   W("titan", "Титан", "роман", 1914, "en", orig="The Titan"),
   W("geniy", "Гений", "роман", 1915, "en", orig="The Genius"),
   W("amerikanskaya-tragediya", "Американская трагедия", "роман", 1925, "en", orig="An American Tragedy"),
 ]),
]
