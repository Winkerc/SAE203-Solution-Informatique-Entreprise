import yaml

def load_config(filename, create=False):

    try:
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        if create:
            config = {}
            with open(filename, 'w') as file:
                config = {
                    'dhcp_hosts_cfg': '/etc/dnsmasq.d/dhcp_hosts.conf',
                    'user': 'sae203',
                }
                yaml.dump(config, file)

        else:
            print(f"Fichier de configuration {filename} non trouvé. Note : Si vous voulez le créer, utilisez create=True.")
            return


import ipaddress


def get_dhcp_server(ip: str, cfg: dict):
    """
    Recherche dans un objet de configuration un serveur DHCP correspondant à l'adresse IP.

    :param ip: Adresse IP à rechercher
    :param cfg: Objet de configuration (dictionnaire)
    :return: Dictionnaire avec le serveur DHCP correspondant ou None
    """
    if "/" in ip:
        # Si l'IP est au format CIDR, extraire l'adresse IP
        ip = ip.split('/')[0]

    # Vérifier si la section dhcp-servers existe
    if 'dhcp-servers' not in cfg:
        return None

    dhcp_servers = cfg['dhcp-servers']

    try:
        # Convertir l'IP en objet IPv4Address pour la comparaison
        target_ip = ipaddress.IPv4Address(ip)

        # Parcourir tous les serveurs DHCP
        for server_ip, network_1 in dhcp_servers.items():
            # Créer un objet réseau à partir du CIDR
            network = ipaddress.IPv4Network(network_1, strict=False)

            # Vérifier si l'IP cible est dans ce réseau
            if target_ip in network:
                return {server_ip: network_1}

        # Aucun serveur trouvé
        return None

    except (ipaddress.AddressValueError, ValueError):
        # IP invalide ou format réseau invalide
        return None
