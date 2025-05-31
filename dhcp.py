from fabric import Connection
def ip_other_mac_exists(cnx, ip, mac, cfg):
    """
    Vérifie si l'IP est déjà utilisée par un hôte avec une adresse MAC différente de mac
    dans la configuration DHCP de l'hôte connecté avec la connexion cnx.

    :param cnx: Objet fabric.Connection
    :param ip: Adresse IP à vérifier
    :param mac: Adresse MAC à exclure de la vérification
    :param cfg: Objet représentant la configuration (lu depuis le fichier YAML)
    :return: True si l'IP est utilisée par une MAC différente, False sinon
    """
    try:
        chemin_config_dnsmasq = cfg['dhcp_hosts_cfg']

        # Lire le fichier de configuration DHCP
        result = cnx.run(f"sudo cat {chemin_config_dnsmasq}", hide=True)
        contenu_dhcp = result.stdout.strip().split("\n")

        # Si le fichier est vide
        if contenu_dhcp == [""]:
            return False

        # Parcourir chaque ligne du fichier de configuration
        for ligne in contenu_dhcp:
            ligne_split = ligne.split(",")

            if len(ligne_split) >= 2:
                ip_config = ligne_split[1]
                mac_config = ligne_split[0].split("=")

                if len(mac_config) >= 2:
                    mac_dans_config = mac_config[1]

                    # Vérifier si l'IP correspond ET que la MAC est différente
                    if ip == ip_config and mac != mac_dans_config:
                        return True

        return False

    except Exception:
        # En cas d'erreur, retourner False
        return False


def mac_exists(cnx, mac, cfg):
    """
    Vérifie si l'adresse MAC est déjà présente dans la configuration DHCP
    de l'hôte connecté avec la connexion cnx.

    :param cnx: Objet fabric.Connection
    :param mac: Adresse MAC à vérifier
    :param cfg: Objet représentant la configuration (lu depuis le fichier YAML)
    :return: True si la MAC est déjà utilisée, False sinon
    """
    try:
        chemin_config_dnsmasq = cfg['dhcp_hosts_cfg']

        result = cnx.run(f"sudo cat {chemin_config_dnsmasq}", hide=True)
        contenu_dhcp = result.stdout.strip().split("\n")

        if not contenu_dhcp == [""]:
            for ligne in contenu_dhcp:
                ligne = ligne.split(",")
                mac_config = ligne[0].split("=")

                # Vérifier si la MAC existe déjà
                if mac == mac_config[1]:
                    return True

        return False

    except Exception:
        return False


def dhcp_add(ip, mac, server, cfg):
    """
    Ajoute une correspondance ip/mac dans le fichier de configuration dnsmasq du serveur.

    :param ip: Adresse IP
    :param mac: Adresse MAC
    :param server: Adresse IP ou nom de domaine du serveur
    :param cfg: Objet représentant la configuration (lu depuis le fichier YAML)
    :return: True si la correspondance a été ajoutée avec succès, False sinon
    """
    try:
        utilisateur = cfg['user']
        chemin_config_dnsmasq = cfg['dhcp_hosts_cfg']

        cnx = Connection(
            host=server,
            user=utilisateur,
            connect_kwargs={"key_filename": "/home/sae203/cles_ssh/sae203_ssh_key", }
        )

        # Vérifier si l'IP est déjà utilisée par une autre MAC
        if ip_other_mac_exists(cnx, ip, mac, cfg):
            print(f"ERREUR : IP déjà attribuée à une autre MAC")
            return False

        # Vérifier si la MAC existe déjà
        if mac_exists(cnx, mac, cfg):
            print(f"MAC {mac} déjà attribuée à une autre IP")
            print(f"Changement de l'adresse IP vers : {ip}")

            # Supprimer l'ancienne entrée
            cnx.run(f"sudo sed -i '/{mac}/d' {chemin_config_dnsmasq}", hide=True)

        result = cnx.run(f"echo dhcp-host={mac},{ip} | sudo tee -a {chemin_config_dnsmasq}", hide=True)

        # Vérifier si la commande a échoué
        if result.return_code != 0 or "pas autorisee" in result.stderr:
            return False
        else:
            print(f"Configuration ajoutée : dhcp-host={mac},{ip} dans {chemin_config_dnsmasq}")
            cnx.run("sudo systemctl restart dnsmasq", hide=True)
            return True

    except Exception as e:
        print(f"ERREUR : Impossible de se connecter à {server} - {str(e)}")
        return False


def dhcp_remove(mac, server, cfg):
    """
    Supprime la configuration DHCP associée à l'adresse MAC.

    :param mac: Adresse MAC à supprimer
    :param server: Adresse IP du serveur
    :param cfg: Objet représentant la configuration (lu depuis le fichier YAML)
    :return: True si la suppression a réussi, False sinon
    """
    try:
        utilisateur = cfg['user']
        chemin_config_dnsmasq = cfg['dhcp_hosts_cfg']

        cnx = Connection(
            host=server,
            user=utilisateur,
            connect_kwargs={"key_filename": "/home/sae203/cles_ssh/sae203_ssh_key", }
        )

        # Vérifier si la MAC existe
        if not mac_exists(cnx, mac, cfg):
            print(f"ERREUR : MAC {mac} non trouvée dans la configuration.")
            return False

        cnx.run(f"sudo sed -i '/{mac}/d' {chemin_config_dnsmasq}")
        print(f"Client DHCP avec MAC {mac} supprimé de {server}.")
        return True

    except Exception as e:
        print(f"Erreur : {e}")
        return False


def dhcp_list(server, cfg):
    """
    Liste les configurations DHCP du serveur.

    :param server: Adresse IP du serveur
    :param cfg: Objet représentant la configuration (lu depuis le fichier YAML)
    :return: Liste des configurations DHCP
    """
    try:
        utilisateur = cfg['user']
        chemin_config_dnsmasq = cfg['dhcp_hosts_cfg']

        cnx = Connection(
            host=server,
            user=utilisateur,
            connect_kwargs={"key_filename": "/home/sae203/cles_ssh/sae203_ssh_key", }
        )

        result = cnx.run(f"sudo cat {chemin_config_dnsmasq}", hide=True)
        contenu_dhcp = result.stdout.strip().split("\n")

        list_dhcp = []
        for elem in contenu_dhcp:
            ip_elem = elem.split(",")[1]
            mac_elem = elem.split("=")[1].split(",")[0]
            list_dhcp.append({
                'mac': mac_elem,
                'ip': ip_elem
            })
        return list_dhcp

    except Exception as e:
        print(f"ERREUR : Impossible de se connecter à {server} - {str(e)}")
        return []
