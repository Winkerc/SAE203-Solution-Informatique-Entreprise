import config
from fabric import Connection
import sys


def check_dhcp(ip: str = "all"):
    cfg = config.load_config('config.yaml', create=False)
    dhcp_servers = cfg['dhcp-servers']

    if ip == "all":
        server_ip = dhcp_servers.keys()

    else:
        dhcp_server = config.get_dhcp_server(ip, cfg)

        if dhcp_server is None:
            print(f"ERREUR : Aucun serveur DHCP trouvé pour l'adresse IP {ip}.")
            return
        else:
            server_ip = list(dhcp_server.keys())

    utilisateur = cfg['user']
    chemin_config_dnsmasq = cfg['dhcp_hosts_cfg']

    total_clients = []
    for server in server_ip:

        cnx = Connection(
            host=server,
            user=utilisateur,
            connect_kwargs={"key_filename": "/home/sae203/cles_ssh/sae203_ssh_key", }
        )
        result = cnx.run(f"sudo cat {chemin_config_dnsmasq}", hide=True)
        contenu_dhcp = result.stdout.strip().split("\n")

        for elem in contenu_dhcp:
            if elem.strip():  # Ignorer les lignes vides
                total_clients.append(elem)


    # Analyser les doublons
    macs_vues = {}
    ips_vues = {}

    for ligne in total_clients:
        try:
            mac = ligne.split('=')[1].split(',')[0]  # Récupérer la MAC
            ip = ligne.split(',')[1].strip()  # Récupérer l'IP

            # Stocker les lignes par MAC et IP
            if mac not in macs_vues:
                macs_vues[mac] = []
            macs_vues[mac].append(ligne)

            if ip not in ips_vues:
                ips_vues[ip] = []
            ips_vues[ip].append(ligne)
        except:
            continue

    # Afficher les doublons MAC
    doublons_mac_trouves = False
    for mac, lignes in macs_vues.items():
        if len(lignes) > 1:
            if not doublons_mac_trouves:
                print("duplicate MAC addresses:")
                doublons_mac_trouves = True
            for ligne in lignes:
                print(ligne)

    # Afficher les doublons IP
    doublons_ip_trouves = False
    for ip, lignes in ips_vues.items():
        if len(lignes) > 1:
            if not doublons_ip_trouves:
                print("duplicate IP addresses:")
                doublons_ip_trouves = True
            for ligne in lignes:
                print(ligne)

    # Si aucun doublon
    if not doublons_mac_trouves and not doublons_ip_trouves:
        print("No duplicates found.")





# [{'mac': '42:46:dd:51:10:c1', 'ip': '10.20.2.100'}, {'mac': '42:46:dd:51:10:c2', 'ip': '10.20.2.102'}]

def main():
    """
    Votre programme principal vient ici, avec obligatoirement un niveau
    d'indentation
    """
    liste_arguments = sys.argv
    liste_arguments.pop(0)

    if len(liste_arguments) > 1:
        print("ERREUR : Nombre d'arguments incorrect. Utilisation : check-dhcp.py <IP> ou 'all'")
        return

    if len(liste_arguments) == 0:
        ip = "all"
    else:
        ip = liste_arguments[0]

    # Exécute la fonction pour ajouter le client DHCP
    check_dhcp(ip)


if __name__ == '__main__':
    main()
