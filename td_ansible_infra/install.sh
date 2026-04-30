#!/bin/bash
# Script d'installation Ansible et dépendances
# R4.ROM.09 - DevOps Infra Réseau avec Ansible
# Merci l'IA pour ce guide d'installation moi j'aurais pas pu faire mieux 😅

set -e

echo "=== Mise à jour de la liste des paquets ==="
sudo apt update

echo "=== Installation de pip3, paramiko et git ==="
sudo apt install -y python3-pip python3-paramiko git

echo "=== Installation d'Ansible via pip3 ==="
sudo pip3 install ansible

echo "=== Vérification des versions installées ==="
ansible --version
git --version

echo "=== Installation terminée avec succès ==="
