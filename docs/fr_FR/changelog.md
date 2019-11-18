### V1.108 du 18/11/2019 20:45
-   Mise à jour du plugin pour compatibilité Jeedom V4 + correction template 88306

### V1.107 du 16/01/2019 17:47
-   Mise à jour de la doc au nouveau format

### V1.106 du 04/10/2017 10:11
-   Mise a jour pour compatibilité 3.1.3

### V1.105 du 13/05/2017 17:11
-   Correction d'un bug sur le retour d'etat des lumières

### V1.104 du 08/05/2017 10:41
-   Correction d'un bug sur le retour d'etat des variateurs

### V1.103 du 12/04/2017 19:45
-   Modification du core du plugin pour gestion du retour d'etat des variateurs

### V1.102 du 31/02/2017 19:30
-   Changement du format de l'ID (Hexadecimal vs Decimal)
-   Mise en place de l'autodetection du port USB utilisé pour l'interface 3578/088328
-   Ajout de la trame de management *13*66*## (trame de supervision) à chaque démarrage du daemon 
-   Ajout de la fonctionnalité Volet Inversé
-   Gestion des onglets dans l'équipement MyHome (Equipement/Commandes)
-   Ajout de la fonction dupliquer un équipement
-   Suppression des bootstraps
-   Ajout d'un menu Health

### V1.101 du 11/11/2016 18:21
-   Correction d'un bug sur l'update des templates
-   Correction de problemes sur la mise a jour des status
-   Correction de la fonction update_shutter

### V1.100 du 30/10/2016 21:38
-   Ajout de la gestion des Shutters
-   Ajout du template Shutter
-   Modification des templates pour intégrer les generic_type (necessaire à l'appli 
mobile)
-   Ajout d'une fonction pour mettre à jour les templates via github sans pousser une 
nouvelle release de boxio
-   Modification de l'affichage de l'equipement pour connaitre la version installée/
disponible du template, ainsi qu'une courte description des changements de celle-ci
-   Rajout de la possibilité de lier une commande action a une commande info (necessaire 
à l'appli mobile)
-   Ajout du mode inclusion (detection auto des modules) dans le plugin (vs config)
-   Correction du demarrage du daemon en mode debug

### V1.000 du 21/06/2016 23:43
-   Version initial
