# `ClipboardToCloud`
* Est une application de gestion du presse-papier qui permet de copier des données vers un service cloud spécifié et de coller ces données depuis le cloud vers un presse-papier distant via un fichier binaire . Il permet donc de récupérer le contenu du presse-papier en temps réel d'un ordinateur à un autre sans tenir compte de l'OS et du réseau, pour cela il faut que l'application soit lancée sur les deux ordinateurs.
Par défaut, il fonctionne avec Dropbox mais il peut être adapté pour d'autres clouds (Google Drive etc...).
Il utilise l'interface graphique Qt (PyQt5) pour afficher une icône dans la barre système et interagir avec l'utilisateur via des actions du menu contextuel :

`Transféré sur Cloud (Dropbox)` : Copie le contenu du presse-papier dans un fichier sur le cloud (Chemin Cloud/.ClipboardToCloud/clipboard.data).

`Coller dans le presse-papier` : Copie le contenu du fichier du cloud dans le presse-papier.

`Afficher le presse-papier` : Permet d'avoir un apercu rapide du contenu du presse-papier
