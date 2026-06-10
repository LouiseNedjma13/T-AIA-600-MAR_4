# CLI

Le script `bookworm.py` est le point d'entree du projet.

Il permet de lancer les fonctionnalites demandees par le sujet avec des options en ligne de commande.

## Commandes disponibles

```bash
python3 bookworm.py --lexdiv 11
python3 bookworm.py --topics 11
python3 bookworm.py --entities 11
python3 bookworm.py --summarize 11
python3 bookworm.py --similar 11
python3 bookworm.py --card 11
```

## Collision d'options

Le programme refuse d'executer plusieurs commandes en meme temps.

Exemple invalide :

```bash
python3 bookworm.py --lexdiv 11 --topics 11
```

Le programme affiche alors une erreur claire. Cela valide le trophee `collision`.

## Validation de l'ID

Le programme verifie aussi que l'ID du livre est un entier positif.

Exemple invalide :

```bash
python3 bookworm.py --lexdiv abc
```

## Sortie

Si le resultat est un texte, comme pour `--summarize`, il est affiche directement.

Si le resultat est un dictionnaire ou une liste, il est affiche en JSON lisible.

## Trophees lies

- nomenclature
- collision
- robustesse
