# -*- coding: utf-8 -*-
"""
Définition centralisée de tous les items du questionnaire.
Utilisé à la fois pour générer le formulaire web et pour générer
l'onglet "Dictionnaire" + les colonnes de l'onglet "Données" du fichier Excel,
afin de garantir que le formulaire colle exactement au questionnaire papier.
"""

# Section II - Estime de soi de l'élève (40 items, Oui/Non)
SECTION_II = [
    ("II_1", "Je suis satisfait(e) de moi-même."),
    ("II_2", "Je me sens souvent inutile."),
    ("II_3", "Je pense avoir de bonnes qualités."),
    ("II_4", "Je doute souvent de mes capacités."),
    ("II_5", "Je suis fier(ère) de ce que je fais."),
    ("II_6", "Je me sens aimé(e) par les autres."),
    ("II_7", "Je me sens rejeté(e)."),
    ("II_8", "Je suis capable de prendre des décisions."),
    ("II_9", "Je me sens inférieur(e) aux autres."),
    ("II_10", "Je crois en mes capacités."),
    ("II_11", "Les autres élèves m'apprécient."),
    ("II_12", "J'ai du mal à me faire des amis."),
    ("II_13", "Je me sens à l'aise en groupe."),
    ("II_14", "Je suis timide avec les autres."),
    ("II_15", "Je participe facilement en classe."),
    ("II_16", "Mes parents me soutiennent."),
    ("II_17", "Je me sens compris(e) à la maison."),
    ("II_18", "On me critique souvent chez moi."),
    ("II_19", "Je me sens important(e) dans ma famille."),
    ("II_20", "Je me sens seul(e) à la maison."),
    ("II_21", "Je réussis bien à l'école."),
    ("II_22", "Je comprends mes leçons."),
    ("II_23", "Je me sens incapable de réussir."),
    ("II_24", "Je participe aux activités scolaires."),
    ("II_25", "Je suis confiant(e) pour mon avenir scolaire."),
    ("II_26", "Je pense que je peux réussir dans une filière difficile."),
    ("II_27", "J'abandonne facilement face aux difficultés."),
    ("II_28", "Je suis motivé(e) pour réussir."),
    ("II_29", "Je me compare souvent négativement aux autres."),
    ("II_30", "Je pense que je suis une personne de valeur."),
    ("II_31", "Je suis satisfait(e) de mon apparence."),
    ("II_32", "Je me sens gêné(e) facilement."),
    ("II_33", "Je prends des initiatives."),
    ("II_34", "Je me décourage rapidement."),
    ("II_35", "Je crois que j'ai un avenir prometteur."),
    ("II_36", "Je me sens inutile dans la société."),
    ("II_37", "Je suis fier(ère) de mes réussites."),
    ("II_38", "Je me sens incapable de faire mieux."),
    ("II_39", "Je suis optimiste pour mon avenir."),
    ("II_40", "Je me sens respecté(e) par les autres."),
]

# Section III - Perception des capacités scolaires
# III_1: choix Faible/Moyen/Bon/Très bon ; III_2 et III_3: Oui/Non
SECTION_III = [
    ("III_1", "Comment évalues-tu ton niveau scolaire ?", "choice",
        ["Faible", "Moyen", "Bon", "Très bon"]),
    ("III_2", "Penses-tu que tes résultats influencent ton orientation ?", "oui_non", None),
    ("III_3", "As-tu confiance en ta réussite dans la filière que tu souhaites ?", "oui_non", None),
]

# Section IV - Orientation scolaire (12 questions, formats variés)
SECTION_IV = [
    ("IV_1", "As-tu déjà choisi une orientation après la 3e ?", "oui_non", None),
    ("IV_2", "Si oui, laquelle ?", "choice",
        ["Enseignement général", "Technique", "Formation professionnelle", "Autre"]),
    ("IV_3", "Qui influence le plus ton choix ?", "choice",
        ["Moi-même", "Parents", "Enseignants", "Amis", "Autres"]),
    ("IV_4", "As-tu déjà hésité à choisir une filière par manque de confiance en toi ?", "oui_non", None),
    ("IV_5", "Penses-tu que tu pourrais réussir dans une filière difficile ?", "oui_non", None),
    ("IV_6", "Penses-tu avoir suffisamment d'informations pour choisir une bonne filière scolaire ?", "oui_non", None),
    ("IV_7", "Penses-tu connaître les débouchés des filières qui t'intéressent ?", "oui_non", None),
    ("IV_8", "As-tu confiance en tes capacités pour atteindre tes objectifs scolaires ?", "oui_non", None),
    ("IV_9", "La filière que tu suis correspond-elle à tes intérêts personnels ?", "oui_non", None),
    ("IV_10", "Penses-tu que ta personnalité est prise en compte dans ton orientation scolaire ?", "oui_non", None),
    ("IV_11", "Penses-tu que certaines personnes doutent de tes capacités scolaires ?", "oui_non", None),
    ("IV_12", "Les paroles décourageantes influencent-elles tes résultats et choix scolaires ?", "oui_non", None),
]

# Section V - Influence de l'estime de soi sur l'orientation (5 items, Oui/Non)
SECTION_V = [
    ("V_1", "Je choisis une filière en fonction de ce que je crois être capable de faire."),
    ("V_2", "Le manque de confiance en moi influence mes choix scolaires."),
    ("V_3", "J'évite certaines filières parce que je pense ne pas être à la hauteur."),
    ("V_4", "Je suis influencé(e) par le regard des autres dans mon orientation."),
    ("V_5", "Je peux réussir si je crois en moi."),
]

# Section B - Test d'estime de soi SEI (15 affirmations, Vrai/Faux)
SECTION_B = [
    ("B_1", "Je suis satisfait(e) de moi-même"),
    ("B_2", "Je pense que je suis quelqu'un de valeur"),
    ("B_3", "Je me sens souvent inutile"),
    ("B_4", "Je suis capable de faire aussi bien que les autres"),
    ("B_5", "Je me sens fier (e) de moi"),
    ("B_6", "Je doute souvent de moi-même"),
    ("B_7", "Je me sens aimé (e) par ma famille"),
    ("B_8", "Je me sens rejeté (e) par les autres"),
    ("B_9", "Je réussis ce que j'entreprends"),
    ("B_10", "Je suis inférieur (e) aux autres"),
    ("B_11", "Je suis confiant (e) en moi"),
    ("B_12", "Je me décourage facilement"),
    ("B_13", "Les autres m'apprécient"),
    ("B_14", "Je me sens important (e) dans ma famille"),
    ("B_15", "Je pense que je suis un échec"),
]

AGE_CHOICES = ["13-14", "15-16", "17", "17+"]
SEXE_CHOICES = ["F", "M"]
SITUATION_FAMILIALE_CHOICES = ["Deux parents", "Un seul parent", "Tuteur / autre"]

# Ordre exact des colonnes de l'onglet "Données", identique au fichier existant
DATA_COLUMNS = (
    ["ID", "Nom", "Prénom", "Age", "Sexe", "Classe", "Etablissement", "Situation_familiale"]
    + [code for code, _ in SECTION_II]
    + [code for code, _, _, _ in SECTION_III]
    + [code for code, _, _, _ in SECTION_IV]
    + [code for code, _ in SECTION_V]
    + [code for code, _ in SECTION_B]
    + ["PP", "PN", "Total_Oui_II", "Total_Vrai_B", "Remarques"]
)


def build_dictionnaire_rows():
    """Reconstruit les lignes de l'onglet Dictionnaire (Code, Section, N°, Libellé)."""
    rows = [("Code colonne", "Section", "N°", "Libellé de la question / item")]
    for code, libelle in SECTION_II:
        n = int(code.split("_")[1])
        rows.append((code, "II - Estime de soi de l'élève", n, libelle))
    for code, libelle, _typ, choices in SECTION_III:
        n = int(code.split("_")[1])
        label = libelle if not choices else f"{libelle} ({' / '.join(choices)})"
        rows.append((code, "III - Perception des capacités scolaires", n, label))
    for code, libelle, _typ, choices in SECTION_IV:
        n = int(code.split("_")[1])
        label = libelle if not choices else f"{libelle} ({' / '.join(choices)})"
        rows.append((code, "IV - Orientation scolaire", n, label))
    for code, libelle in SECTION_V:
        n = int(code.split("_")[1])
        rows.append((code, "V - Influence de l'estime de soi sur l'orientation", n, libelle))
    for code, libelle in SECTION_B:
        n = int(code.split("_")[1])
        rows.append((code, "B - Test d'estime de soi (SEI)", n, libelle))
    return rows
