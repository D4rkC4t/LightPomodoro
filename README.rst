.. -*- coding: utf-8 -

LightPomodoro
=============================

Pomodoro en PyQt4

Préalable
=============================

sudo apt-get install python-qt
sudo apt-get install libnotify-bin

Si gnome : vérifier présence applet "notification area" pour voir l'icône de LightPomodoro s'afficher
Si kde : vérifier présence applet "Boîte à miniatures" pour voir l'icône de LightPomodoro s'afficher

Usage 
==============================

python -u "lightpomodoro.pyw" &

Lancement automatique au démarrage
==============================

Kde:

    - Menu KDE
    - Configuration du Système 
    - Démarrage & Arrêt 
    - Démarrage Automatique 
    - Ajouter un programme : python -u "PATHTO/lightpomodoro.pyw"
    - Ok

Gnome:

    - Menu Gnome
    - System
    - Preference
    - Startup Applications
    - Add : python -u "PATHTO/lightpomodoro.pyw"
    - Ok
