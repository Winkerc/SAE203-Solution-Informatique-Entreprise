#!/usr/bin/env python3

import ipaddress as ipv4

def is_ip_valide(ip: str):
    """
    Vérifie si une adresse IPv4 est valide et utilisable sur un réseau standard.

    Exclut les adresses multicast, réservées, loopback, link-local et non spécifiées.

    Args:
        ip (str): L'adresse IPv4 à valider.

    Returns:
        bool: True si l'adresse est valide et utilisable, False sinon.
    """
    try:
        ip = ipv4.ip_address(ip)
        if not ip.is_multicast and not ip.is_unspecified and not ip.is_reserved and not ip.is_loopback and not ip.is_link_local:
            return True
        else:
            print("error: bad IP address.")
            return False
    except ValueError:
        print("error: bad IP address.")
        return False

def is_mac_valide(mac: str):
    """
        Vérifie si une adresse MAC est valide selon le format standard.

        Une adresse MAC valide doit respecter les critères suivants :
        - Être composée de 6 groupes de 2 caractères hexadécimaux
        - Les groupes doivent être séparés par le caractère ":"
        - Les caractères autorisés sont les chiffres (0-9) et les lettres A-F (insensible à la casse)

        Args:
            mac (str): L'adresse MAC à valider sous forme de chaîne de caractères.

        Returns:
            bool: True si l'adresse MAC est valide, False sinon.
        """
    mac = mac.upper()
    splitted_mac = mac.split(":")

    valid_characters = [":", "A", "B", "C", "D", "E", "F"]

    reponse = 1  # Indice qui correspond a la valeur que l'on renverra, 1 pour True et 0 pour False

    # On traite le cas ou le caractere n n'est pas valide
    for elem in mac:
        if not elem.isnumeric() and elem not in valid_characters:
            reponse = 0

    # On traite le cas ou il y a plus de 2 characteres entres chaque ":"
    for elem in splitted_mac:
        if len(elem) != 2:
            reponse = 0

    if len(splitted_mac) != 6 or reponse == 0:
        print("ERREUR : MAC invalide")
        return False
    elif reponse == 1:
        return True
    else:
        print("ERREUR")
        return