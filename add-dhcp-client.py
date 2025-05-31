#!/usr/bin/env python3

import sys
import validation
import config, dhcp

configuration = config.load_config('config.yaml', create=True)

def add_dhcp_client(mac: str, ip: str):
    """
    Ajoute un client DHCP à la configuration de dnsmasq sur le serveur spécifié.
    :param mac:
    :param ip:
    :return:
    """

    if not validation.is_mac_valide(mac):
        return
    if not validation.is_ip_valide(ip):
        return

    dhcp_server = config.get_dhcp_server(ip, configuration)
    if dhcp_server is None:
        print(f"ERREUR : Aucun serveur DHCP trouvé pour l'adresse IP {ip}.")
        return
    else:
        host = list(dhcp_server.keys())[0]

    # Utiliser la nouvelle fonction
    success = dhcp.dhcp_add(ip, mac, host, configuration)
    if not success:
        return




def main():
    """
    Votre programme principal vient ici, avec obligatoirement un niveau
    d'indentation
    """
    liste_arguments = sys.argv
    liste_arguments.pop(0)

    if len(liste_arguments) != 2:
        print("ERREUR : Nombre d'arguments incorrect. Utilisation : add-dhcp-client.py <MAC> <IP>")
        return

    mac = liste_arguments[0]
    ip = liste_arguments[1]

    # Exécute la fonction pour ajouter le client DHCP
    add_dhcp_client(mac, ip)


if __name__ == '__main__':
    main()
