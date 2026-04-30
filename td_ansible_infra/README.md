# TD/TP Ansible — Configuration d'une infrastructure réseau

**Module :** R4.ROM.09 — Outils DevOps  
**Auteur :** Ponthieux Léo 
**Année :** 2025/2026

## 🎯 Objectif

Ce projet utilise **Ansible** pour automatiser la configuration :

- d'un **routeur Cisco CSR1000v** (interfaces, DHCP, NAT/PAT dynamique, redirection de ports),
- d'un **serveur web Debian** (installation Apache + déploiement d'un site statique).

## 🗺️ Architecture cible

```
                  Internet / Réseau IUT
                          |
                    [Bridge filaire]
                          |
                  ┌───────────────┐
                  │   CSR1000v    │
                  │               │
                  │ G1 : DHCP/WAN │
                  │ G2 : 192.168.2.1/24  (LAN_ENTREPRISE)
                  │ G3 : 192.168.3.1/24  (LAN_DMZ)
                  │ G4 : 192.168.4.1/24  (LAN_ADMIN)
                  └───────┬───────┘
                          |
        ┌─────────────────┼─────────────────┐
        |                 |                 |
   PC Entreprise     Serveur Web      VM Ansible
   (LAN_ENT, DHCP)   192.168.3.2      192.168.4.2
                     (LAN_DMZ)        (LAN_ADMIN)
```

## 🚪 Redirections de ports (PAT statique)

| Service externe | IP WAN du CSR : Port | → IP LAN : Port |
|----|----|----|
| Site web | `IP_WAN:80` | `192.168.3.2:80` |
| SSH Ansible | `IP_WAN:2222` | `192.168.4.2:22` |

## 📂 Contenu du dépôt

| Fichier / Dossier | Description |
|----|----|
| `install.sh` | Script d'installation des dépendances (Ansible, paramiko, git) |
| `ansible/ansible.cfg` | Configuration globale d'Ansible |
| `ansible/inventaire/hosts` | Inventaire des hôtes (routeur + serveurs) |
| `ansible/host_vars/` | Variables propres à chaque hôte |
| `ansible/playbook_lireconfigcsr.yml` | Sauvegarde de la `running-config` du routeur |
| `ansible/playbook_configurecsr.yml` | Configuration complète du routeur (interfaces, DHCP, NAT, PAT) |
| `ansible/playbook_configureweb.yml` | Installation Apache + déploiement du site |
| `ansible/site.yml` | Playbook orchestrateur (lance tout) |
| `ansible/files/site_web/` | Contenu HTML du site web déployé |

## 🚀 Utilisation

```bash
# 1. Installer les dépendances (à faire une seule fois)
./install.sh

# 2. Se placer dans le répertoire ansible
cd ansible

# 3. Vérifier l'inventaire
ansible-inventory --graph
ansible-inventory --list

# 4. Tester la connectivité
ansible -m ios_command -a "commands='show version'" csr1000
ansible -m ping web

# 5. Déployer toute l'infrastructure
ansible-playbook site.yml

# Ou exécuter les playbooks individuellement
ansible-playbook playbook_lireconfigcsr.yml
ansible-playbook playbook_configurecsr.yml
ansible-playbook playbook_configureweb.yml
```

## ✅ Tests de validation

| Test | Commande | Résultat attendu |
|----|----|----|
| Inventaire | `ansible-inventory --graph` | Groupes `routeurs` et `serveurs` |
| Ping CSR | `ansible -m ios_command -a "commands='show version'" csr1000` | `SUCCESS` |
| Ping web | `ansible -m ping web` | `pong` |
| DHCP | VM dans `LAN_ENTREPRISE` reçoit IP `192.168.2.X` | OK |
| NAT | `ping 8.8.8.8` depuis `LAN_ENTREPRISE` | Réponse |
| Site web | `curl http://IP_WAN_CSR` | Page HTML |
| SSH redirigé | `ssh -p 2222 utilisateur@IP_WAN_CSR` | Connexion OK |

## 📜 Licence

Projet pédagogique sous licence MIT.
