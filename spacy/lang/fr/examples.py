"""
Example sentences to test spaCy and its language models.

>>> from spacy.lang.fr.examples import sentences
>>> docs = nlp.pipe(sentences)
"""


sentences = [
    "Apple cherche à acheter une start-up anglaise pour 1 milliard de dollars",
    "Les voitures autonomes déplacent la responsabilité de l'assurance vers les constructeurs",
    "San Francisco envisage d'interdire les robots coursiers sur les trottoirs",
    "Londres est une grande ville du Royaume-Uni",
    "L’Italie choisit ArcelorMittal pour reprendre la plus grande aciérie d’Europe",
    "Apple lance HomePod parce qu'il se sent menacé par l'Echo d'Amazon",
    "La France ne devrait pas manquer d'électricité cet été, même en cas de canicule",
    "Nouvelles attaques de Trump contre le maire de Londres",

    # additions
    "Où es-tu ?",
    "Qui est le président de la France ?",
    "Où est la capitale des États-Unis ?",
    "Quand est né Barack Obama ?",
    "Où vas-tu?",
    "Où va-t'on?",
    "Je ne sais pas mais on y va depuis le 2023-12-21.",
    "Qu'en est-t-il des autres?",
    "Sont-iels à Villar-le-ruisseau?",
    "Et les non-humain-es?",
    "Et le produit anti-nominaliste?",
    "T'en as? Tu m'en donnnes?",
    "Sinon mets-en un peu par terre.",
    "il n'y a plus rien ici. ",
    "enfin j'crois, nos p'tites affaires ont été enl'vées.",
    "aujourd'hui, c'est comme ça.",
    "(oui) le(s) tableau(x) est là.(dé)croche-le, nan?",
    "(et où est/sont le(s) reste(s))",
    "quelqu'un.e a dit: \"[que] les personnes [s]e promène[nt]\"",
    "et elles se promen(erai)ent.",
    "un.e directeur.ice, des employé.es, ",
    "des juriste.x.s. tout le monde était là.Et à l'heure!et.à.l'heure!",
    "des non-humain-es étaient là aussi, visiblement heureux·ses.",
    "j'ai trouvé ça surhttps://site_inexistant.fr/accueil#milieu ou  www.quelque_part.com/ je pense.",
    "Les numéros 12.1 et 132.121, et 1.213 et 1.2.3,",
    "aussi le 1.a. ",
    "Alors lisez déjà la p.30, la p.3, la p.5 la p. 20 et la p.2.",
    "Ah et le 2.3! Pas le 2.par contre.3 oui 3 aussi. ",
    "Éventuellement le numéro 4.",
    "Le 10.a.2 et A.3.a pourquoi pas.",
    "On est quoi, le 21.12.2023...",
    "2,3 et non,2 c'est pas assez,3 non plus ",
    "et 4,je sais pas.ici il n'y rien/pas grand chose. ",
    "1/mais par contre on s'amuse. et le 20.12, ",
    "ou alors le 21/12 oui c'est ça c'était le 21/12/2023...",
]
