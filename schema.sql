-- Schéma SQLite : Dépouillement Enquête Estime de Soi
-- 1 à 5 utilisateurs (rôles : admin / enqueteur)

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'enqueteur' CHECK(role IN ('admin', 'enqueteur')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    age TEXT,                    -- 13-14 / 15-16 / 17 / 17+
    sexe TEXT,                   -- F / M
    classe TEXT,
    etablissement TEXT,
    situation_familiale TEXT,    -- Deux parents / Un seul parent / Tuteur / autre

    -- Section II - 40 items Oui/Non
    II_1 TEXT, II_2 TEXT, II_3 TEXT, II_4 TEXT, II_5 TEXT,
    II_6 TEXT, II_7 TEXT, II_8 TEXT, II_9 TEXT, II_10 TEXT,
    II_11 TEXT, II_12 TEXT, II_13 TEXT, II_14 TEXT, II_15 TEXT,
    II_16 TEXT, II_17 TEXT, II_18 TEXT, II_19 TEXT, II_20 TEXT,
    II_21 TEXT, II_22 TEXT, II_23 TEXT, II_24 TEXT, II_25 TEXT,
    II_26 TEXT, II_27 TEXT, II_28 TEXT, II_29 TEXT, II_30 TEXT,
    II_31 TEXT, II_32 TEXT, II_33 TEXT, II_34 TEXT, II_35 TEXT,
    II_36 TEXT, II_37 TEXT, II_38 TEXT, II_39 TEXT, II_40 TEXT,

    -- Section III
    III_1 TEXT,   -- Faible / Moyen / Bon / Très bon
    III_2 TEXT,   -- Oui / Non
    III_3 TEXT,   -- Oui / Non

    -- Section IV - 12 items, formats variés
    IV_1 TEXT,    -- Oui / Non
    IV_2 TEXT,    -- Enseignement général / Technique / Formation professionnelle / Autre
    IV_3 TEXT,    -- Moi-même / Parents / Enseignants / Amis / Autres
    IV_4 TEXT, IV_5 TEXT, IV_6 TEXT, IV_7 TEXT, IV_8 TEXT,
    IV_9 TEXT, IV_10 TEXT, IV_11 TEXT, IV_12 TEXT,

    -- Section V - 5 items Oui/Non
    V_1 TEXT, V_2 TEXT, V_3 TEXT, V_4 TEXT, V_5 TEXT,

    -- Section B - Test SEI, 15 items Vrai/Faux
    B_1 TEXT, B_2 TEXT, B_3 TEXT, B_4 TEXT, B_5 TEXT,
    B_6 TEXT, B_7 TEXT, B_8 TEXT, B_9 TEXT, B_10 TEXT,
    B_11 TEXT, B_12 TEXT, B_13 TEXT, B_14 TEXT, B_15 TEXT,

    PP INTEGER,   -- score positif, noté manuellement par l'évaluateur
    PN INTEGER,   -- score négatif, noté manuellement par l'évaluateur

    Total_Oui_II INTEGER,  -- calculé automatiquement (nb de "Oui" en section II)
    Total_Vrai_B INTEGER,  -- calculé automatiquement (nb de "Vrai" au test SEI)

    remarques TEXT,

    created_by INTEGER REFERENCES users(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
