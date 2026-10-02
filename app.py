# -*- coding: utf-8 -*-
import os
import io
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_file, abort
)
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user, login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

import db
from items import (
    SECTION_II, SECTION_III, SECTION_IV, SECTION_V, SECTION_B,
    AGE_CHOICES, SEXE_CHOICES, SITUATION_FAMILIALE_CHOICES,
    DATA_COLUMNS, build_dictionnaire_rows
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-moi-en-production")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.role = row["role"]


@login_manager.user_loader
def load_user(user_id):
    conn = db.get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return User(row) if row else None


def admin_required(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return fn(*args, **kwargs)
    return wrapper


# ---------- Auth ----------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        conn = db.get_db()
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if row and check_password_hash(row["password_hash"], password):
            login_user(User(row))
            return redirect(url_for("dashboard"))
        flash("Identifiants incorrects.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ---------- Dashboard / liste ----------

@app.route("/")
@login_required
def dashboard():
    conn = db.get_db()
    students = conn.execute(
        "SELECT id, nom, prenom, age, sexe, classe, etablissement, date_soumission AS created_at "
        "FROM reponses ORDER BY date_soumission DESC"
    ).fetchall()
    return render_template("dashboard.html", students=students)


# ---------- Fiche élève : création ----------

def _collect_form_answers():
    """Récupère toutes les réponses du formulaire dans un dict {code: valeur}."""
    answers = {}
    for code, _ in SECTION_II:
        answers[code] = request.form.get(code)
    for code, _, _, _ in SECTION_III:
        answers[code] = request.form.get(code)
    for code, _, _, _ in SECTION_IV:
        answers[code] = request.form.get(code)
    for code, _ in SECTION_V:
        answers[code] = request.form.get(code)
    for code, _ in SECTION_B:
        answers[code] = request.form.get(code)
    return answers


@app.route("/students/new", methods=["GET", "POST"])
@login_required
def student_new():
    if request.method == "POST":
        answers = _collect_form_answers()
        total_oui_ii = sum(1 for code, _ in SECTION_II if answers.get(code) == "Oui")
        total_vrai_b = sum(1 for code, _ in SECTION_B if answers.get(code) == "Vrai")

        fields = ["nom", "prenom", "age", "sexe", "classe", "etablissement",
                  "situation_familiale"]
        values = [request.form.get(f) for f in fields]

        columns_sql = fields + list(answers.keys()) + \
            ["PP", "PN", "Total_Oui_II", "Total_Vrai_B", "remarques", "created_by"]
        placeholders = ", ".join(["?"] * len(columns_sql))
        all_values = values + list(answers.values()) + [
            request.form.get("PP") or None,
            request.form.get("PN") or None,
            total_oui_ii,
            total_vrai_b,
            request.form.get("remarques"),
            current_user.id,
        ]

        conn = db.get_db()
        conn.execute(
            f"INSERT INTO students ({', '.join(columns_sql)}) VALUES ({placeholders})",
            all_values,
        )
        conn.commit()
        flash("Élève enregistré.", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "student_form.html",
        student=None,
        section_ii=SECTION_II, section_iii=SECTION_III, section_iv=SECTION_IV,
        section_v=SECTION_V, section_b=SECTION_B,
        age_choices=AGE_CHOICES, sexe_choices=SEXE_CHOICES,
        situation_choices=SITUATION_FAMILIALE_CHOICES,
    )


@app.route("/students/<int:student_id>")
@login_required
def student_view(student_id):
    import json as _json
    conn = db.get_db()
    row = conn.execute("SELECT * FROM reponses WHERE id = ?", (student_id,)).fetchone()
    if not row:
        abort(404)

    # Reconstruire un dict compatible avec le template student_view.html
    student = dict(row)

    # Section II : liste de 40 items oui/non
    s2 = _json.loads(row["section2_json"]) if row["section2_json"] else []
    for i, item in enumerate(s2, start=1):
        student["II_" + str(i)] = item.get("reponse", "")

    # Section III
    student["III_1"] = row["section3_niveau"] or ""
    student["III_2"] = row["section3_q2"] or ""
    student["III_3"] = row["section3_q3"] or ""

    # Section IV : dict {q1:..., q2:..., ...}
    s4 = _json.loads(row["section4_json"]) if row["section4_json"] else {}
    for i in range(1, 13):
        student["IV_" + str(i)] = s4.get("q" + str(i), "")

    # Section V : liste
    s5 = _json.loads(row["section5_json"]) if row["section5_json"] else []
    for i, item in enumerate(s5, start=1):
        student["V_" + str(i)] = item.get("reponse", "")

    # Section B (SEI) : liste
    sb = _json.loads(row["sei_json"]) if row["sei_json"] else []
    for i, item in enumerate(sb, start=1):
        student["B_" + str(i)] = item.get("reponse", "")

    # Totaux
    student["Total_Oui_II"] = row["score_estime_soi"] or 0

    # Calculer Total_Vrai_B : compter les reponses conformes a la polarite
    total_vrai_b = 0
    for item in sb:
        pol = item.get("polarite", "")
        rep = item.get("reponse", "").lower()
        if pol == "vrai_pos" and rep == "vrai":
            total_vrai_b += 1
        elif pol == "vrai_neg" and rep == "faux":
            total_vrai_b += 1
    student["Total_Vrai_B"] = total_vrai_b

    student["PP"] = 0
    student["PN"] = 0
    student["remarques"] = ""

    return render_template(
        "student_view.html", student=student,
        section_ii=SECTION_II, section_iii=SECTION_III, section_iv=SECTION_IV,
        section_v=SECTION_V, section_b=SECTION_B,
    )


@app.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
@admin_required
def student_delete(student_id):
    conn = db.get_db()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    flash("Fiche supprimée.", "success")
    return redirect(url_for("dashboard"))


# ---------- Export Excel ----------

@app.route("/export.xlsx")
@login_required
def export_xlsx():
    import openpyxl
    from openpyxl.utils import get_column_letter

    import json as _json
    conn = db.get_db()
    raw_rows = conn.execute("SELECT * FROM reponses ORDER BY id").fetchall()

    # Reconstruire chaque ligne pour qu'elle contienne les cles II_x, III_x, IV_x, V_x, B_x
    rows = []
    for row in raw_rows:
        student = dict(row)
        # Section II
        s2 = _json.loads(row["section2_json"]) if row["section2_json"] else []
        for i, item in enumerate(s2, start=1):
            student["II_" + str(i)] = item.get("reponse", "")
        # Section III
        student["III_1"] = row["section3_niveau"] or ""
        student["III_2"] = row["section3_q2"] or ""
        student["III_3"] = row["section3_q3"] or ""
        # Section IV
        s4 = _json.loads(row["section4_json"]) if row["section4_json"] else {}
        for i in range(1, 13):
            student["IV_" + str(i)] = s4.get("q" + str(i), "")
        # Section V
        s5 = _json.loads(row["section5_json"]) if row["section5_json"] else []
        for i, item in enumerate(s5, start=1):
            student["V_" + str(i)] = item.get("reponse", "")
        # Section B (SEI)
        sb = _json.loads(row["sei_json"]) if row["sei_json"] else []
        for i, item in enumerate(sb, start=1):
            student["B_" + str(i)] = item.get("reponse", "")
        # Totaux
        student["Total_Oui_II"] = row["score_estime_soi"] or 0
        tvb = 0
        for item in sb:
            pol = item.get("polarite", "")
            rep = item.get("reponse", "").lower()
            if pol == "vrai_pos" and rep == "vrai":
                tvb += 1
            elif pol == "vrai_neg" and rep == "faux":
                tvb += 1
        student["Total_Vrai_B"] = tvb
        student["PP"] = 0
        student["PN"] = 0
        student["remarques"] = ""
        rows.append(student)

    wb = openpyxl.Workbook()

    # --- Dictionnaire ---
    ws_dict = wb.active
    ws_dict.title = "Dictionnaire"
    for row in build_dictionnaire_rows():
        ws_dict.append(row)

    # --- Données ---
    ws_data = wb.create_sheet("Données")
    ws_data.append(DATA_COLUMNS)
    col_index = {name: i + 1 for i, name in enumerate(DATA_COLUMNS)}

    field_map = {
        "ID": "id", "Nom": "nom", "Prénom": "prenom", "Age": "age", "Sexe": "sexe",
        "Classe": "classe", "Etablissement": "etablissement",
        "Situation_familiale": "situation_familiale",
        "Total_Oui_II": "Total_Oui_II", "Total_Vrai_B": "Total_Vrai_B",
        "Remarques": "remarques",
    }

    for r_idx, s in enumerate(rows, start=2):
        for col_name in DATA_COLUMNS:
            db_field = field_map.get(col_name, col_name)  # sinon même nom (II_1, B_15, PP, PN, ...)
            try:
                value = s[db_field]
            except (IndexError, KeyError):
                value = None
            ws_data.cell(row=r_idx, column=col_index[col_name], value=value)

    last_row = max(len(rows) + 1, 2)

    # --- Synthèse (mêmes formules que le classeur d'origine) ---
    ws_synth = wb.create_sheet("Synthèse")
    sexe_col = get_column_letter(col_index["Sexe"])
    ii_col = get_column_letter(col_index["Total_Oui_II"])
    b_col = get_column_letter(col_index["Total_Vrai_B"])
    iv1_col = get_column_letter(col_index["IV_1"])
    iv4_col = get_column_letter(col_index["IV_4"])
    id_col = get_column_letter(col_index["ID"])

    ws_synth.append(["Synthèse automatique", None])
    ws_synth.append([None, None])
    ws_synth.append(["Indicateur", "Valeur"])
    ws_synth.append(["Nombre d'élèves enquêtés", f"=COUNTA(Données!{id_col}2:{id_col}200)"])
    ws_synth.append(["Nombre de filles", f'=COUNTIF(Données!{sexe_col}2:{sexe_col}200,"F")'])
    ws_synth.append(["Nombre de garçons", f'=COUNTIF(Données!{sexe_col}2:{sexe_col}200,"M")'])
    ws_synth.append(["Moyenne des 'Oui' - Section II (estime de soi)",
                      f"=AVERAGE(Données!{ii_col}2:{ii_col}200)"])
    ws_synth.append(["Moyenne des 'Vrai' - Test SEI",
                      f"=AVERAGE(Données!{b_col}2:{b_col}200)"])
    ws_synth.append(["Nb élèves n'ayant pas encore choisi d'orientation (IV_1=Non)",
                      f'=COUNTIF(Données!{iv1_col}2:{iv1_col}200,"Non")'])
    ws_synth.append(["Nb élèves ayant hésité par manque de confiance (IV_4=Oui)",
                      f'=COUNTIF(Données!{iv4_col}2:{iv4_col}200,"Oui")'])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"Depouillement_Enquete_EstimeDeSoi_{datetime.now():%Y%m%d}.xlsx"
    return send_file(
        buf, as_attachment=True, download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ---------- Import Excel (reprise des anciennes fiches) ----------

# Correspondance nom de colonne Excel -> nom de colonne SQLite (seuls les
# champs "texte" ont un nom différent ; tous les codes II_x/III_x/IV_x/V_x/B_x
# sont identiques des deux côtés)
_IMPORT_FIELD_MAP = {
    "Nom": "nom", "Prénom": "prenom", "Age": "age", "Sexe": "sexe",
    "Classe": "classe", "Etablissement": "etablissement",
    "Situation_familiale": "situation_familiale", "Remarques": "remarques",
}


@app.route("/admin/import", methods=["GET", "POST"])
@login_required
@admin_required
def admin_import():
    if request.method == "POST":
        file = request.files.get("xlsx_file")
        if not file or file.filename == "":
            flash("Aucun fichier sélectionné.", "error")
            return redirect(url_for("admin_import"))

        import openpyxl
        wb = openpyxl.load_workbook(file, data_only=True)
        if "Données" not in wb.sheetnames:
            flash('Feuille "Données" introuvable dans ce fichier.', "error")
            return redirect(url_for("admin_import"))

        ws = wb["Données"]
        headers = [c.value for c in ws[1]]
        conn = db.get_db()
        imported = 0

        for row in ws.iter_rows(min_row=2, values_only=True):
            row_dict = dict(zip(headers, row))
            # Ignore les lignes vides (pas de nom)
            if not row_dict.get("Nom"):
                continue

            db_row = {}
            for col_name, value in row_dict.items():
                if col_name in (None, "ID"):
                    continue
                db_field = _IMPORT_FIELD_MAP.get(col_name, col_name)
                db_row[db_field] = value

            db_row["created_by"] = current_user.id
            columns_sql = list(db_row.keys())
            placeholders = ", ".join(["?"] * len(columns_sql))
            conn.execute(
                f"INSERT INTO students ({', '.join(columns_sql)}) VALUES ({placeholders})",
                list(db_row.values()),
            )
            imported += 1

        conn.commit()
        flash(f"{imported} fiche(s) importée(s) avec succès.", "success")
        return redirect(url_for("dashboard"))

    return render_template("admin_import.html")


# ---------- Gestion des utilisateurs (admin) ----------

@app.route("/admin/users", methods=["GET", "POST"])
@login_required
@admin_required
def admin_users():
    conn = db.get_db()
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        role = request.form.get("role", "enqueteur")
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), role),
            )
            conn.commit()
            flash(f"Utilisateur {username} créé.", "success")
        except Exception as e:
            flash(f"Erreur : {e}", "error")
    users = conn.execute("SELECT id, username, role, created_at FROM users").fetchall()
    return render_template("admin_users.html", users=users)




# ==================== ENTRE-TIENS ====================

def can_rename_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ("admin", "editeur"):
            abort(403)
        return fn(*args, **kwargs)
    return wrapper


@app.route("/entretien", methods=["GET", "POST"])
@login_required
def entretien():
    conn = db.get_db()
    from items import GUIDE_ENTRETIEN
    if request.method == "POST":
        nom_eleve = request.form.get("nom_eleve", "").strip()
        reponses = {}
        for key, _ in GUIDE_ENTRETIEN:
            reponses[key] = request.form.get(key, "").strip()
        if nom_eleve:
            conn.execute(
                "INSERT INTO entretiens (date_entretien, nom_eleve, reponses_json) VALUES (datetime('now'), ?, ?)",
                (nom_eleve, json.dumps(reponses, ensure_ascii=False)),
            )
            conn.commit()
            flash("Entretien enregistre.", "success")
            return redirect(url_for("entretien"))
    return render_template("entretien.html", questions=GUIDE_ENTRETIEN)


@app.route("/admin/entretiens")
@login_required
def admin_entretiens():
    conn = db.get_db()
    entretiens = conn.execute(
        "SELECT id, date_entretien, nom_eleve FROM entretiens ORDER BY LOWER(TRIM(nom_eleve)) ASC, id DESC"
    ).fetchall()
    return render_template("admin_entretiens.html", entretiens=entretiens)


@app.route("/admin/renommer_entretien/<int:ent_id>", methods=["POST"])
@login_required
@can_rename_required
def renommer_entretien(ent_id):
    nom = request.form.get("nom_eleve", "").strip()
    if nom:
        conn = db.get_db()
        conn.execute("UPDATE entretiens SET nom_eleve=? WHERE id=?", (nom, ent_id))
        conn.commit()
    return redirect(url_for("admin_entretiens"))


@app.route("/admin/supprimer_entretien/<int:ent_id>", methods=["POST"])
@login_required
@admin_required
def supprimer_entretien(ent_id):
    conn = db.get_db()
    conn.execute("DELETE FROM entretiens WHERE id=?", (ent_id,))
    conn.commit()
    flash("Entretien supprime.", "success")
    return redirect(url_for("admin_entretiens"))


@app.route("/entretien/modifier/<int:ent_id>", methods=["GET", "POST"])
@login_required
@admin_required
def modifier_entretien(ent_id):
    conn = db.get_db()
    from items import GUIDE_ENTRETIEN
    ent = conn.execute("SELECT * FROM entretiens WHERE id=?", (ent_id,)).fetchone()
    if not ent:
        abort(404)
    if request.method == "POST":
        nom_eleve = request.form.get("nom_eleve", "").strip()
        reponses = {}
        for key, _ in GUIDE_ENTRETIEN:
            reponses[key] = request.form.get(key, "").strip()
        conn.execute(
            "UPDATE entretiens SET nom_eleve=?, reponses_json=? WHERE id=?",
            (nom_eleve, json.dumps(reponses, ensure_ascii=False), ent_id),
        )
        conn.commit()
        flash("Entretien modifie.", "success")
        return redirect(url_for("admin_entretiens"))
    reponses = json.loads(ent["reponses_json"]) if ent["reponses_json"] else {}
    return render_template("entretien.html", questions=GUIDE_ENTRETIEN, ent=ent, reponses=reponses, modifier=True)


@app.cli.command("create-admin")
def create_admin_command():
    """Commande CLI pour créer le premier compte admin : flask create-admin"""
    import getpass
    username = input("Nom d'utilisateur admin : ").strip()
    password = getpass.getpass("Mot de passe : ")
    with app.app_context():
        conn = db.get_db()
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
            (username, generate_password_hash(password)),
        )
        conn.commit()
    print(f"Admin {username} créé.")


with app.app_context():
    db.init_db(app)
    # Crée un compte admin par défaut si la base est vierge (à changer immédiatement)
    conn = db.get_db()
    count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    if count == 0:
        default_user = os.environ.get("ADMIN_USERNAME", "admin")
        default_pass = os.environ.get("ADMIN_PASSWORD", "admin123")
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
            (default_user, generate_password_hash(default_pass)),
        )
        conn.commit()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
