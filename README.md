# Portfolio · Yoan Rousselot

Site statique bilingue (français / anglais) présentant mon parcours : de sous-officier de gendarmerie à l'ingénierie biomédicale.

- Français : `index.html` et les pages `experiences/`, `projects/`, `education/`
- Anglais : `en/` (même arborescence)

## Structure

```
index.html            page d'accueil FR (profil, compétences, parcours, projets, recommandations, contact)
en/                   version anglaise
experiences/ projects/ education/   pages détaillées (générées)
assets/css/style.css  styles (thème sombre, accents or)
assets/js/main.js     menu mobile, filtres du parcours, animations, visionneuse d'images
assets/img/           photos et visuels
assets/docs/          lettres de recommandation (PDF)
src/content.py        TOUT le contenu du site (textes FR et EN)
src/build.py          générateur des pages HTML
render.yaml           configuration de déploiement Render
```

## Modifier le contenu

1. Modifier les textes dans `src/content.py`.
2. Regénérer les pages :
   ```bash
   python src/build.py
   ```
3. Commit et push sur `main` : Render redéploie automatiquement.

## Déploiement sur Render

1. Sur [render.com](https://render.com), **New → Static Site**, puis connecter le dépôt GitHub `Yoanrslt/Portfolio`.
2. Branche : `main` · Build command : *(vide)* · Publish directory : `.`
3. Valider : le site est en ligne et se met à jour à chaque push.

(Alternative : **New → Blueprint** utilise directement `render.yaml`.)
