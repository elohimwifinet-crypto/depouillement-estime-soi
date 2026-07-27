# Dépouillement Enquête Estime de Soi — Application web

Application Flask + SQLite pour remplacer le dépouillement manuel par chat.
Déployée en container sur RouterOS (HP Z420).

## 1. Publier le code sur GitHub

```bash
git init
git add .
git commit -m "Version initiale"
git branch -M main
git remote add origin https://github.com/<ton-pseudo>/depouillement-estime-soi.git
git push -u origin main
```

## 2. Configurer les secrets GitHub Actions

Dans le repo GitHub : **Settings → Secrets and variables → Actions → New repository secret**

- `DOCKERHUB_USERNAME` : ton nom d'utilisateur Docker Hub
- `DOCKERHUB_TOKEN` : un access token Docker Hub (Docker Hub → Account Settings → Security → New Access Token)

Dès que ces secrets sont ajoutés, le premier `git push` déclenche le build et publie
l'image sur `docker.io/<ton-pseudo>/depouillement-estime-soi:latest`.

Vérifie que le workflow a réussi dans l'onglet **Actions** du repo GitHub avant de
passer à l'étape suivante.

## 3. Déployer sur RouterOS (HP Z420)

Le routeur a déjà été préparé (veth6 / 192.168.3.7, bridge `containers`,
mount `depouillement-data` → `/app/data`).

Il ne reste que la commande finale, à adapter avec ton pseudo Docker Hub :

```
/container/add remote-image=docker.io/<ton-pseudo>/depouillement-estime-soi:latest interface=veth6 root-dir=depouillement/root mounts=depouillement-data dns=192.168.3.1 start-on-boot=yes envlist=depouillement-env
```

Puis démarrer le container :

```
/container/start [find where root-dir=depouillement/root]
```

Vérifier qu'il tourne :

```
/container/print
```

Accès web : `http://192.168.3.7:5000`

**Identifiants par défaut** : `admin` / `admin123` — à changer immédiatement
via le menu "Utilisateurs" une fois connecté.

## 4. Variables d'environnement optionnelles

Pour changer les identifiants admin par défaut ou la clé secrète Flask, créer
une liste d'environnement RouterOS avant l'étape 3 :

```
/container/envs/add name=depouillement-env key=SECRET_KEY value="une-longue-chaine-aleatoire"
/container/envs/add name=depouillement-env key=ADMIN_USERNAME value="ton_identifiant"
/container/envs/add name=depouillement-env key=ADMIN_PASSWORD value="un_mot_de_passe_fort"
```

## 5. Mettre à jour l'application plus tard

1. Modifier le code localement
2. `git add . && git commit -m "..." && git push`
3. GitHub Actions republie l'image automatiquement
4. Sur RouterOS :
   ```
   /container/stop [find where root-dir=depouillement/root]
   /container/remove [find where root-dir=depouillement/root]
   ```
   puis relancer la commande `/container/add` de l'étape 3 (RouterOS retélécharge
   la nouvelle image). La base SQLite est conservée car elle vit dans le mount
   `depouillement-data`, pas dans l'image.
