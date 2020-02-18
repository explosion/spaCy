"""
Example sentences to test spaCy and its language models.

>>> from spacy.lang.de.examples import sentences
>>> docs = nlp.pipe(sentences)
"""

# combined examples from de/en/es/fr/it/nl/pl/pt/ru

sentences = [
    "Die ganze Stadt ist ein Startup: Shenzhen ist das Silicon Valley für Hardware-Firmen",
    "Wie deutsche Startups die Technologie vorantreiben wollen: Künstliche Intelligenz",
    "Trend zum Urlaub in Deutschland beschert Gastwirten mehr Umsatz",
    "Bundesanwaltschaft erhebt Anklage gegen mutmaßlichen Schweizer Spion",
    "San Francisco erwägt Verbot von Lieferrobotern",
    "Autonome Fahrzeuge verlagern Haftpflicht auf Hersteller",
    "Wo bist du?",
    "Was ist die Hauptstadt von Deutschland?",
    "Apple is looking at buying U.K. startup for $1 billion",
    "Autonomous cars shift insurance liability toward manufacturers",
    "San Francisco considers banning sidewalk delivery robots",
    "London is a big city in the United Kingdom.",
    "Where are you?",
    "Who is the president of France?",
    "What is the capital of the United States?",
    "When was Barack Obama born?",
    "Apple está buscando comprar una startup del Reino Unido por mil millones de dólares.",
    "Los coches autónomos delegan la responsabilidad del seguro en sus fabricantes.",
    "San Francisco analiza prohibir los robots delivery.",
    "Londres es una gran ciudad del Reino Unido.",
    "El gato come pescado.",
    "Veo al hombre con el telescopio.",
    "La araña come moscas.",
    "El pingüino incuba en su nido.",
    "Apple cherche à acheter une start-up anglaise pour 1 milliard de dollars",
    "Les voitures autonomes déplacent la responsabilité de l'assurance vers les constructeurs",
    "San Francisco envisage d'interdire les robots coursiers sur les trottoirs",
    "Londres est une grande ville du Royaume-Uni",
    "L’Italie choisit ArcelorMittal pour reprendre la plus grande aciérie d’Europe",
    "Apple lance HomePod parce qu'il se sent menacé par l'Echo d'Amazon",
    "La France ne devrait pas manquer d'électricité cet été, même en cas de canicule",
    "Nouvelles attaques de Trump contre le maire de Londres",
    "Où es-tu ?",
    "Qui est le président de la France ?",
    "Où est la capitale des États-Unis ?",
    "Quand est né Barack Obama ?",
    "Apple vuole comprare una startup del Regno Unito per un miliardo di dollari",
    "Le automobili a guida autonoma spostano la responsabilità assicurativa verso i produttori",
    "San Francisco prevede di bandire i robot di consegna porta a porta",
    "Londra è una grande città del Regno Unito.",
    "Apple overweegt om voor 1 miljard een U.K. startup te kopen",
    "Autonome auto's verschuiven de verzekeringverantwoordelijkheid naar producenten",
    "San Francisco overweegt robots op voetpaden te verbieden",
    "Londen is een grote stad in het Verenigd Koninkrijk",
    "Poczuł przyjemną woń mocnej kawy.",
    "Istnieje wiele dróg oddziaływania substancji psychoaktywnej na układ nerwowy.",
    "Powitał mnie biało-czarny kot, płosząc siedzące na płocie trzy dorodne dudki.",
    "Nowy abonament pod lupą Komisji Europejskiej",
    "Czy w ciągu ostatnich 48 godzin spożyłeś leki zawierające paracetamol?",
    "Kto ma ochotę zapoznać się z innymi niż w książkach przygodami Muminków i ich przyjaciół, temu polecam komiks Tove Jansson „Muminki i morze”.",
    "Apple está querendo comprar uma startup do Reino Unido por 100 milhões de dólares.",
    "Carros autônomos empurram a responsabilidade do seguro para os fabricantes.."
    "São Francisco considera banir os robôs de entrega que andam pelas calçadas.",
    "Londres é a maior cidade do Reino Unido.",
    # Translations from English:
    "Apple рассматривает возможность покупки стартапа из Соединённого Королевства за $1 млрд",
    "Беспилотные автомобили перекладывают страховую ответственность на производителя",
    "В Сан-Франциско рассматривается возможность запрета роботов-курьеров, которые перемещаются по тротуару",
    "Лондон — это большой город в Соединённом Королевстве",
    # Native Russian sentences:
    # Colloquial:
    "Да, нет, наверное!",  # Typical polite refusal
    "Обратите внимание на необыкновенную красоту этого города-героя Москвы, столицы нашей Родины!",  # From a tour guide speech
    # Examples of Bookish Russian:
    # Quote from "The Golden Calf"
    "Рио-де-Жанейро — это моя мечта, и не смейте касаться её своими грязными лапами!",
    # Quotes from "Ivan Vasilievich changes his occupation"
    "Ты пошто боярыню обидел, смерд?!!",
    "Оставь меня, старушка, я в печали!",
    # Quotes from Dostoevsky:
    "Уж коли я, такой же, как и ты, человек грешный, над тобой умилился и пожалел тебя, кольми паче бог",
    "В мечтах я нередко, говорит, доходил до страстных помыслов о служении человечеству и может быть действительно пошел бы на крест за людей, если б это вдруг как-нибудь потребовалось, а между тем я двух дней не в состоянии прожить ни с кем в одной комнате, о чем знаю из опыта",
    "Зато всегда так происходило, что чем более я ненавидел людей в частности, тем пламеннее становилась любовь моя к человечеству вообще",
    # Quotes from Chekhov:
    "Ненужные дела и разговоры всё об одном отхватывают на свою долю лучшую часть времени, лучшие силы, и в конце концов остается какая-то куцая, бескрылая жизнь, какая-то чепуха, и уйти и бежать нельзя, точно сидишь в сумасшедшем доме или в арестантских ротах!",
    # Quotes from Turgenev:
    "Нравится тебе женщина, старайся добиться толку; а нельзя — ну, не надо, отвернись — земля не клином сошлась",
    "Узенькое местечко, которое я занимаю, до того крохотно в сравнении с остальным пространством, где меня нет и где дела до меня нет; и часть времени, которую мне удастся прожить, так ничтожна перед вечностью, где меня не было и не будет...",
    # Quotes from newspapers:
    # Komsomolskaya Pravda:
    "На заседании президиума правительства Москвы принято решение присвоить статус инвестиционного приоритетного проекта города Москвы киностудии Союзмультфильм",
    "Глава Минобороны Сергей Шойгу заявил, что обстановка на этом стратегическом направлении требует непрерывного совершенствования боевого состава войск",
    # Argumenty i Facty:
    "На реплику лже-Говина — дескать, он (Волков) будет лучшим революционером — Стамп с энтузиазмом ответил: Непременно!",
]
