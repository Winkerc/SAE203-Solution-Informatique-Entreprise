import config
from fabric import Connection
import sys

def list_dhcp(ip: str = "all"):
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

    total_clients = {}
    for server in server_ip:

        cnx = Connection(
            host=server,
            user=utilisateur,
            connect_kwargs={"key_filename": "/home/sae203/cles_ssh/sae203_ssh_key", }
        )
        result = cnx.run(f"sudo cat {chemin_config_dnsmasq}", hide=True)
        contenu_dhcp = result.stdout.strip().split("\n")

        total_clients[server] = []  # Initialiser la liste pour chaque serveur

        for elem in contenu_dhcp:
            if elem.strip():  # Ignorer les lignes vides
                total_clients[server].append(elem)


    for ip_serv_dhcp in total_clients.keys():
        if ip == "all":
            print(ip_serv_dhcp, ":")

        for associations in total_clients[ip_serv_dhcp]:

            ip_host = associations.split(",")[1].strip()
            mac_host = associations.split("=")[1].split(",")[0]

            print(f"{mac_host} \t {ip_host}")


# {'10.20.1.5': 'dhcp-host=42:1b:22:55:a5:00,10.20.1.14', '10.20.2.5': 'dhcp-host=42:46:dd:51:10:c2,10.20.2.102'}
def main():
    """
    Votre programme principal vient ici, avec obligatoirement un niveau
    d'indentation
    """
    liste_arguments = sys.argv
    liste_arguments.pop(0)

    if len(liste_arguments) > 1:
        print("ERREUR : Nombre d'arguments incorrect. Utilisation : list-dhcp.py <IP> ou 'all'")
        return

    if len(liste_arguments) == 0:
        ip = "all"
    else:
        ip = liste_arguments[0]

    # Exécute la fonction pour ajouter le client DHCP
    list_dhcp(ip)


if __name__ == '__main__':
    main()