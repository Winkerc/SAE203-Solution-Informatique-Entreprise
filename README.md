# Système de Gestion Centralisée de Configuration DHCP

## 1. Documentation de présentation générale

### Vue d'ensemble

Ce projet implémente un système de gestion centralisée permettant à un administrateur de gérer des configurations DHCP sur plusieurs serveurs distants utilisant dnsmasq, depuis un point de contrôle unique.

### Architecture

#### Composants principaux

**Serveur Central (Superviseur)**
- Scripts Python de gestion (add-dhcp-client, check-dhcp, list-dhcp, remove-dhcp-client)
- Fichier de configuration centralisé (config.yaml)
- Clés SSH pour l'authentification

**Serveurs DHCP Distants**
- Service dnsmasq configuré
- Script de filtrage SSH sécurisé (/usr/local/bin/filter_ssh_commands.py)
- Configuration des réservations IP (/etc/dnsmasq.d/dhcp_hosts.conf)

#### Flux de fonctionnement

1. **Commande initiale** : L'administrateur exécute une commande depuis le serveur central
2. **Connexion SSH** : Le script se connecte au serveur DHCP approprié via SSH avec authentification par clé
3. **Filtrage sécurisé** : Le script filter_ssh_commands.py valide la commande reçue
4. **Exécution** : Si autorisée, la commande est exécutée sur le serveur distant
5. **Application** : La configuration dnsmasq est mise à jour et le service redémarré si nécessaire

#### Sécurité

- **Authentification SSH par clé** : Connexion sécurisée sans mot de passe
- **Filtrage strict des commandes** : Seules les commandes prédéfinies sont autorisées
- **Privilèges sudo limités** : Accès restreint aux opérations nécessaires
- **Validation des données** : Contrôle de la validité des adresses MAC et IP

### Fonctionnalités

#### Commandes disponibles

- **add-dhcp-client** : Ajouter une réservation IP statique
- **remove-dhcp-client** : Supprimer une réservation IP
- **list-dhcp** : Lister les réservations configurées
- **check-dhcp** : Vérifier la cohérence et détecter les doublons

#### Gestion multi-serveurs

Le système supporte plusieurs serveurs DHCP avec des plages réseau différentes :
- Détection automatique du serveur approprié selon l'IP
- Gestion centralisée depuis un point unique
- Configuration par fichier YAML simple

### Avantages

- **Centralisation** : Gestion unifiée de multiples serveurs DHCP
- **Sécurité** : Contrôle strict des accès et commandes
- **Simplicité** : Interface en ligne de commande intuitive
- **Fiabilité** : Validation des données et gestion d'erreurs

## 2. Guide de mise en place de l'architecture

### Prérequis

#### Serveur Central (Superviseur)
- Python 3.6+
- Modules Python requis : fabric~=3.2.2, pyyaml~=6.0.2, yaml~=0.2.5
- Accès SSH vers les serveurs DHCP distants
- Utilisateur système (ex: sae203)

#### Serveurs DHCP Distants
- Service dnsmasq installé et configuré
- Python 3.6+
- Accès sudo configuré pour l'utilisateur de connexion
- SSH activé et configuré

### Étape 1 : Configuration des serveurs DHCP distants

#### 1.1 Installation des prérequis
```
# Installation de dnsmasq
sudo apt update
sudo apt install dnsmasq python3

# Vérification du service
sudo systemctl enable dnsmasq
sudo systemctl status dnsmasq
```

#### 1.2 Configuration de dnsmasq
```
# Création du répertoire de configuration
sudo mkdir -p /etc/dnsmasq.d/

# Création du fichier de réservations DHCP
sudo touch /etc/dnsmasq.d/dhcp_hosts.conf
sudo chmod 644 /etc/dnsmasq.d/dhcp_hosts.conf

# Configuration de dnsmasq pour inclure le fichier
echo "conf-dir=/etc/dnsmasq.d/" | sudo tee -a /etc/dnsmasq.conf
```

#### 1.3 Installation du script de filtrage SSH
```
# Copier le script de filtrage
sudo cp filter_ssh_commands.py /usr/local/bin/
sudo chmod +x /usr/local/bin/filter_ssh_commands.py
sudo chown root:root /usr/local/bin/filter_ssh_commands.py
```

#### 1.4 Configuration SSH pour l'utilisateur sae203
```
# Création de l'utilisateur
sudo useradd -m -s /bin/bash sae203

# Configuration sudo (ajouter dans /etc/sudoers.d/sae203)
echo "sae203 ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart dnsmasq" | sudo tee /etc/sudoers.d/sae203
echo "sae203 ALL=(ALL) NOPASSWD: /usr/bin/systemctl status dnsmasq" | sudo tee -a /etc/sudoers.d/sae203
echo "sae203 ALL=(ALL) NOPASSWD: /usr/bin/cat /etc/dnsmasq.d/dhcp_hosts.conf" | sudo tee -a /etc/sudoers.d/sae203
echo "sae203 ALL=(ALL) NOPASSWD: /usr/bin/tee -a /etc/dnsmasq.d/dhcp_hosts.conf" | sudo tee -a /etc/sudoers.d/sae203
echo "sae203 ALL=(ALL) NOPASSWD: /usr/bin/sed -i * /etc/dnsmasq.d/dhcp_hosts.conf" | sudo tee -a /etc/sudoers.d/sae203

sudo chmod 440 /etc/sudoers.d/sae203
```

### Étape 2 : Configuration du serveur central

#### 2.1 Préparation de l'environnement
```
# Installation des dépendances Python
pip3 install fabric==3.2.2 pyyaml==6.0.2 yaml==0.2.5

# Création de la structure de répertoires
mkdir -p /home/sae203/dhcp-management/
mkdir -p /home/sae203/cles_ssh/
cd /home/sae203/dhcp-management/
```

#### 2.2 Génération des clés SSH
```
# Génération de la paire de clés SSH
ssh-keygen -t rsa -b 4096 -f /home/sae203/cles_ssh/sae203_ssh_key -N ""

# Copie de la clé publique vers les serveurs DHCP
ssh-copy-id -i /home/sae203/cles_ssh/sae203_ssh_key.pub sae203@10.20.1.5
ssh-copy-id -i /home/sae203/cles_ssh/sae203_ssh_key.pub sae203@10.20.2.5
```

#### 2.3 Configuration SSH sur les serveurs distants
Sur chaque serveur DHCP distant, modifier le fichier ~/.ssh/authorized_keys :
```
# Éditer le fichier pour ajouter la restriction de commande
nano ~/.ssh/authorized_keys

# Modifier la ligne de la clé publique pour inclure :
command="/usr/local/bin/filter_ssh_commands.py",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-rsa AAAAB3N... votre_clé_publique
```

#### 2.4 Installation des scripts Python
Copier tous les fichiers Python dans /home/sae203/dhcp-management/ :
- add-dhcp-client.py
- remove-dhcp-client.py
- list-dhcp.py
- check-dhcp.py
- validation.py
- config.py
- dhcp.py
- filter_ssh_commands.py

```
# Rendre les scripts exécutables
chmod +x *.py
```

#### 2.5 Configuration du fichier config.yaml
```
dhcp_hosts_cfg: "/etc/dnsmasq.d/dhcp_hosts.conf"
user: "sae203"
dhcp-servers:
  10.20.1.5: "10.20.1.0/24"
  10.20.2.5: "10.20.2.0/24"
```

### Étape 3 : Tests de validation

#### 3.1 Test de connectivité SSH
```
# Test de connexion SSH
ssh -i /home/sae203/cles_ssh/sae203_ssh_key sae203@10.20.1.5 "echo test"
```

#### 3.2 Test des commandes autorisées
```
# Test de lecture de configuration
ssh -i /home/sae203/cles_ssh/sae203_ssh_key sae203@10.20.1.5 "sudo cat /etc/dnsmasq.d/dhcp_hosts.conf"

# Test de redémarrage du service
ssh -i /home/sae203/cles_ssh/sae203_ssh_key sae203@10.20.1.5 "sudo systemctl status dnsmasq"
```

#### 3.3 Test du système complet
```
cd /home/sae203/dhcp-management/

# Test d'ajout d'un client
python3 add-dhcp-client.py 42:46:dd:51:10:c2 10.20.1.102

# Test de listage
python3 list-dhcp.py

# Test de suppression
python3 remove-dhcp-client.py 42:46:dd:51:10:c2
```

L'architecture est maintenant fonctionnelle et prête à l'utilisation.

## 3. Guide d'installation et d'utilisation

### Installation rapide

#### Prérequis
- Architecture déjà déployée selon le guide de mise en place
- Accès au serveur central avec l'utilisateur sae203
- Scripts Python installés dans /home/sae203/dhcp-management/

#### Vérification de l'installation
```
cd /home/sae203/dhcp-management/
python3 --version  # Doit être >= 3.6
```

### Utilisation des commandes

#### 1. add-dhcp-client : Ajouter une réservation DHCP

**Syntaxe :**
```
python3 add-dhcp-client.py <ADRESSE_MAC> <ADRESSE_IP>
```

**Description :**
Ajoute une réservation IP statique pour un équipement réseau. Le système détermine automatiquement le serveur DHCP approprié selon la plage IP.

**Exemples :**
```
# Ajouter un client sur le réseau 10.20.1.0/24
python3 add-dhcp-client.py 42:46:dd:51:10:c2 10.20.1.102

# Ajouter un client sur le réseau 10.20.2.0/24  
python3 add-dhcp-client.py aa:bb:cc:dd:ee:ff 10.20.2.150
```

**Gestion d'erreurs :**
- Adresse MAC invalide : format requis XX:XX:XX:XX:XX:XX
- Adresse IP invalide : format IPv4 standard, exclut multicast/loopback/etc.
- Aucun serveur DHCP trouvé pour l'IP spécifiée
- Conflit IP ou MAC déjà existante

#### 2. remove-dhcp-client : Supprimer une réservation DHCP

**Syntaxe :**
```
python3 remove-dhcp-client.py <ADRESSE_MAC>
```

**Description :**
Supprime une réservation IP en recherchant l'adresse MAC sur tous les serveurs DHCP configurés.

**Exemples :**
```
# Supprimer la réservation pour cette MAC
python3 remove-dhcp-client.py 42:46:dd:51:10:c2

# Supprimer un autre équipement
python3 remove-dhcp-client.py aa:bb:cc:dd:ee:ff
```

**Gestion d'erreurs :**
- Adresse MAC invalide
- MAC non trouvée sur aucun serveur

#### 3. list-dhcp : Lister les réservations

**Syntaxe :**
```
python3 list-dhcp.py [<ADRESSE_IP>|all]
```

**Description :**
Affiche les réservations DHCP configurées. Sans paramètre ou avec "all", affiche toutes les réservations de tous les serveurs.

**Exemples :**
```
# Lister toutes les réservations
python3 list-dhcp.py
python3 list-dhcp.py all

# Lister les réservations d'un réseau spécifique
python3 list-dhcp.py 10.20.1.100
```

**Format de sortie :**
```
10.20.1.5 :
42:46:dd:51:10:c2       10.20.1.102
aa:bb:cc:dd:ee:ff       10.20.1.150

10.20.2.5 :
11:22:33:44:55:66       10.20.2.200
```

#### 4. check-dhcp : Vérifier la cohérence

**Syntaxe :**
```
python3 check-dhcp.py [<ADRESSE_IP>|all]
```

**Description :**
Analyse les configurations DHCP pour détecter les doublons d'adresses MAC ou IP et les incohérences.

**Exemples :**
```
# Vérifier toutes les configurations
python3 check-dhcp.py

# Vérifier un réseau spécifique
python3 check-dhcp.py 10.20.1.100
```

**Types d'analyses :**
- Détection des adresses MAC dupliquées
- Détection des adresses IP dupliquées  
- Vérification de la cohérence des plages réseau
- Identification des conflits potentiels

### Configuration avancée

#### Modification du fichier config.yaml

```
dhcp_hosts_cfg: "/etc/dnsmasq.d/dhcp_hosts.conf"  # Chemin du fichier de config dnsmasq
user: "sae203"                                    # Utilisateur SSH
dhcp-servers:                                     # Serveurs DHCP et leurs plages
  10.20.1.5: "10.20.1.0/24"
  10.20.2.5: "10.20.2.0/24"
  # Ajouter d'autres serveurs si nécessaire
```

#### Ajout d'un nouveau serveur DHCP

1. **Configurer le serveur selon le guide de mise en place**
2. **Ajouter la configuration dans config.yaml :**
```
dhcp-servers:
  10.20.1.5: "10.20.1.0/24"
  10.20.2.5: "10.20.2.0/24"
  10.20.3.5: "10.20.3.0/24"  # Nouveau serveur
```
3. **Tester la connectivité :**
```
python3 add-dhcp-client.py test:ma:c0:ad:dr:es 10.20.3.10
```

### Dépannage

#### Erreurs communes

**"ERREUR : Aucun serveur DHCP trouvé pour l'adresse IP"**
- Vérifier que l'IP appartient à une plage configurée dans config.yaml

**"Commande non autorisee"** 
- Problème avec le filtrage SSH
- Vérifier filter_ssh_commands.py sur le serveur distant
- Vérifier les permissions sudo

**"ERREUR : MAC invalide" / "ERREUR : IP invalide"**
- Respecter le format MAC : XX:XX:XX:XX:XX:XX (hexadécimal)
- Utiliser une adresse IP valide (pas de multicast, loopback, etc.)

#### Vérifications de diagnostic

```
# Test de connectivité SSH
ssh -i /home/sae203/cles_ssh/sae203_ssh_key sae203@10.20.1.5 "echo test"

# Vérification de la configuration
cat config.yaml

# Test des modules Python
python3 -c "import fabric, yaml; print('Modules OK')"
```

#### Support

Pour obtenir de l'aide sur une commande spécifique :
```
python3 <commande>.py
# Affiche l'utilisation correcte en cas d'erreur d'arguments
```

Note de fin : Un petit 20/20 ? :)