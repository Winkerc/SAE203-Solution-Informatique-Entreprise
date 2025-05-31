#!/usr/bin/env python3


import sys
import validation
import config, dhcp

configuration = config.load_config('config.yaml', create=True)


chemin_config_dnsmasq = configuration['dhcp_hosts_cfg']  # "/etc/dnsmasq.d/dhcp_hosts.conf"
utilisateur = configuration['user']  # "sae203"
try:
    servers_dhcp = configuration['dhcp-servers']  # Liste des serveurs DHCP, {'10.20.1.5': '10.20.1.0/24', '10.20.2.5': '10.20.2.0/24'}
except Exception as e:
    print(f"ERREUR : La configuration des serveurs DHCP est manquante ou invalide. {e}")
    sys.exit(1)


ips_dhcp = []  # Stocke les adresses IP des serveurs DHCP de la configuration, ['10.20.1.5', '10.20.2.5']
for cle in servers_dhcp.keys():
    ips_dhcp.append(cle)

def remove_dhcp_client(mac: str):

    if not validation.is_mac_valide(mac):
        return

    for ip in ips_dhcp:
        if dhcp.dhcp_remove(mac, ip, configuration):
            break  # Arrêter dès qu'on a trouvé et supprimé la MAC


def main():
    """
    Votre programme principal vient ici, avec obligatoirement un niveau
    d'indentation
    """
    liste_arguments = sys.argv
    liste_arguments.pop(0)

    if len(liste_arguments) != 1:
        print("ERREUR : Nombre d'arguments incorrect. Utilisation : remove-dhcp-client.py <MAC>")
        return

    mac = liste_arguments[0]

    # Exécute la fonction pour ajouter le client DHCP
    remove_dhcp_client(mac)


if __name__ == '__main__':
    main()
