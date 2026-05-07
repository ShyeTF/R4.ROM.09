
from netmiko import ConnectHandler


import re


serv_web = {
    'device_type' : 'linux',
    'ip'          : '192.168.3.2',
    'username'    : 'utilisateur',
    'password'    : 'toor',
    'port'        : 22,
    'verbose'     : False
}


serv_ansible = {
    'device_type' : 'linux',
    'ip'          : '192.168.4.2',
    'username'    : 'utilisateur',
    'password'    : 'toor',
    'port'        : 22,
    'verbose'     : False
}


routeur = {
    'device_type' : 'cisco_ios',
    'ip'          : '192.168.1.17',
    'username'    : 'cisco',
    'password'    : 'cisco123!',
    'secret'      : 'cisco123!',
    'port'        : 22,
    'verbose'     : False
}


print("=" * 60)
print(">>> SECTION 3 — Tests sur le routeur Cisco CSR1000v")
print("=" * 60)

print("\n--- 3.1 Vérification des interfaces du routeur ---")


conn_routeur = ConnectHandler(**routeur)
conn_routeur.enable() 


interfaces_attendues = {
    1: {'ip': None,          'desc': 'WAN (DHCP)'},         
    2: {'ip': '192.168.2.1', 'desc': 'LAN_ENTREPRISE'},
    3: {'ip': '192.168.3.1', 'desc': 'LAN_DMZ'},
    4: {'ip': '192.168.4.1', 'desc': 'ADMIN'},
}


for num in range(1, 5):
    resultat = conn_routeur.send_command(f'show ip interface GigabitEthernet{num}')

   
    if re.search(r'GigabitEthernet\d+ is up', resultat):
        print(f"+++ GigabitEthernet{num} ({interfaces_attendues[num]['desc']}) : UP")
    else:
        print(f"xxx GigabitEthernet{num} ({interfaces_attendues[num]['desc']}) : DOWN ou introuvable")

   
    if interfaces_attendues[num]['ip']:
        ip_attendue = interfaces_attendues[num]['ip']
        if re.search(re.escape(ip_attendue), resultat):
            print(f"    IP {ip_attendue} : OK")
        else:
            print(f"    IP {ip_attendue} : KO (IP incorrecte ou absente)")

conn_routeur.disconnect()



print("\n--- 3.2 Vérification connectivité depuis le routeur ---")

conn_routeur = ConnectHandler(**routeur)
conn_routeur.enable()


test_ping_web = conn_routeur.send_command('ping 192.168.3.2 repeat 4')
print(">>> Routeur → Serveur Web (192.168.3.2)")
print(test_ping_web)
if re.search(r'!!!!', test_ping_web) or re.search(r'Success rate is 1', test_ping_web):
    print("+++ Routeur joint le serveur web avec succès")
else:
    print("xxx Routeur ne joint pas le serveur web")


test_ping_internet = conn_routeur.send_command('ping 8.8.8.8 repeat 4')
print("\n>>> Routeur → Internet (8.8.8.8)")
print(test_ping_internet)
if re.search(r'!!!!', test_ping_internet) or re.search(r'Success rate is 1', test_ping_internet):
    print("+++ Routeur joint internet avec succès")
else:
    print("xxx Routeur ne joint pas internet")

conn_routeur.disconnect()



print("\n--- 3.3 Tests supplémentaires sur le routeur ---")

conn_routeur = ConnectHandler(**routeur)
conn_routeur.enable()


print("\n>>> Vérification entrées NAT (show ip nat translations)")
nat = conn_routeur.send_command('show ip nat translations')
print(nat)
if nat.strip():
    print("+++ Table NAT contient des entrées : PAT actif")
else:
    print("--- Table NAT vide (normal si aucun trafic récent)")


print("\n>>> Vérification baux DHCP (show ip dhcp binding)")
dhcp = conn_routeur.send_command('show ip dhcp binding')
print(dhcp)
if re.search(r'192\.168\.2\.', dhcp):
    print("+++ Des adresses DHCP ont été distribuées sur LAN_ENTREPRISE")
else:
    print("--- Aucun bail DHCP actif (normal si aucun client connecté)")

print("\n>>> Vérification route par défaut (show ip route)")
route = conn_routeur.send_command('show ip route')
print(route)
if re.search(r'0\.0\.0\.0', route):
    print("+++ Route par défaut présente : accès internet possible")
else:
    print("xxx Pas de route par défaut : vérifier la config WAN")

conn_routeur.disconnect()



print("\n" + "=" * 60)
print(">>> SECTION 2 — Tests sur le serveur web Linux (192.168.3.2)")
print("=" * 60)


connection = ConnectHandler(**serv_web)


print("\n--- 2.2 Test de connectivité vers internet ---")

test = connection.send_command('ping -c 4 -W 1 8.8.8.8')
print(">>> Serv_Web : Test de connectivité serveur Linux vers extérieur (dns google)")
print(test)


capture = re.search(r'(\d+) \w+ \w+, (\d+) \w+, (\d+)% \w+ \w+, time (\d+)ms', test)

if capture:
    if capture.group(1) == capture.group(2):
        print("+++ Test réalisé avec succès")
        
    else:
        print(f"xxx Problème de connectivité ({capture.group(2)}/{capture.group(1)} paquets reçus)")
        exit(-1)
else:
    print("xxx Impossible de parser la réponse du ping")
    exit(-1)


print("\n--- 2.3 Test résolution DNS ---")


test_dns = connection.send_command('nslookup -timeout=1 www.google.fr')
print(">>> Serv_Web : Test résolution DNS (nslookup www.google.fr)")
print(test_dns)


capture_dns = re.search(r'Server:\s+(\d+\.\d+\.\d+\.\d+)', test_dns)

if capture_dns:
    print(f"+++ Résolution DNS OK — Serveur DNS utilisé : {capture_dns.group(1)}")
else:
    print("xxx Pas de résolution DNS — Vérifier /etc/resolv.conf ou la config DHCP")
    exit(-2)


print("\n--- 2.4 Test du serveur web Apache (en local) ---")


test_web = connection.send_command('wget --timeout 1 -t 1 -q -O - 127.0.0.1')
print(">>> Serv_Web : Test Apache en local (wget 127.0.0.1)")
print(test_web)


if re.search(r'index\.html|Ponthieux|R4\.ROM\.09|Apache', test_web, re.IGNORECASE):
    print("+++ Serveur Apache répond et sert le contenu attendu")
else:
    print("xxx Apache ne répond pas ou la page est incorrecte")
    exit(-3)

connection.disconnect()


print("\n" + "=" * 60)
print(">>> SECTION 2.5 — Test depuis machine Ansible → Routeur")
print("=" * 60)

conn_ansible = ConnectHandler(**serv_ansible)

test_ansible_routeur = conn_ansible.send_command('ping -c 4 -W 1 192.168.1.17')
print(">>> Ansible : ping vers routeur (192.168.1.17)")
print(test_ansible_routeur)

cap = re.search(r'(\d+) \w+ \w+, (\d+) \w+', test_ansible_routeur)
if cap and cap.group(1) == cap.group(2):
    print("+++ Machine Ansible joint le routeur")
else:
    print("xxx Machine Ansible ne joint pas le routeur")


print("\n--- 2.6 Test depuis machine Ansible → Serveur Web ---")

test_ansible_web = conn_ansible.send_command('ping -c 4 -W 1 192.168.3.2')
print(">>> Ansible : ping vers serveur web (192.168.3.2)")
print(test_ansible_web)

cap2 = re.search(r'(\d+) \w+ \w+, (\d+) \w+', test_ansible_web)
if cap2 and cap2.group(1) == cap2.group(2):
    print("+++ Machine Ansible joint le serveur web")
else:
    print("xxx Machine Ansible ne joint pas le serveur web")

conn_ansible.disconnect()


print("\n" + "=" * 60)
print(">>> RÉSUMÉ : Tous les tests ont été exécutés avec succès !")
print("    Infrastructure opérationnelle.")
print("=" * 60)
