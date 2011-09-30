#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licence : GPL

"""
LightPomodoro - petit applet en pyqt4
avec 25 minutes de travail suivi de 5 minutes de break

Usage Console: 
python -u "lightpomodoro.pyw"

Usage Kde:
    Menu KDE
        > Configuration du Système 
        > Démarrage & Arrêt 
        > Démarrage Automatique 
        > Ajouter un programme 
            python -u "/home/XXXX/dev/projects/lightpomodoro/lightpomodoro.pyw"
        > Ok

Usage Gnome:
    Menu Gnome
        > System
        > Preference
        > Startup Applications
        > Add
            python -u "/home/XXXX/dev/projects/lightpomodoro/lightpomodoro.pyw"
        > Ok
        
"""

__author__ = "Alban Minassian (alban.minassian@free.fr)"
__copyright__ = "Copyright (c) 2011, Alban Minassian"
__date__ = "2011/09/30"
__version__ = "0.1"

import sys, os
from PyQt4 import QtCore, QtGui
import icons_rc # pyrcc4 icons.qrc -o icons_rc.py

class LightPomodoroDialog( QtGui.QDialog ):
    """
    Fenêtre de configuration
    """    
    def __init__(self, parent=None):  
        super(LightPomodoroDialog, self).__init__(parent)
        
        self.setWindowIcon(QtGui.QIcon(':/Ressources/working.png'))
        self.setWindowTitle("LightPomodoro");

class LightPomodoroSystray(QtGui.QWidget):
    """
    LightPomodoro 
    """    
    
    # (faux) enum des états
    START = 0
    PAUSE = 1
    STOP = 2
    END_WORK = 3
    END_BREAK = 4
    
    # interval pomodoro
    INTERVAL_WORK = 25 * 60 * 1000 # 25 minutes
    INTERVAL_BREAK_SHORT = 5 * 60 * 1000 # 5 minutes
    INTERVAL_BREAK_LONG = 15 * 60 * 1000 # 15 minutes

    # durée Test :
    #~ INTERVAL_WORK = 2 * 1000 # 25 minutes
    #~ INTERVAL_BREAK_SHORT = 2 * 1000 # 5 minutes
    #~ INTERVAL_BREAK_LONG = 5 * 1000 # 15 minutes
    
    # Compter le nombre de break
    # au bout de X break court alors réaliser un break long
    longBreakAfterXShort = 3 # long break after 3 short break
    countBreakShort = 0;
    
    # Chaine info
    stringTempRestant = ''; # mis à jour toutes les X secondes via fncUpdateSystray
    
    def __init__(self, argDialog):
        """
        Systray & Actions
        """    
        QtGui.QWidget.__init__(self)
        
        # sauvegarder pointeur sur la fenêtre de dialogue
        self.dialog = argDialog; 
        
        # icone
        #~ self.iconStop = QtGui.QIcon("idle.png")
        #~ self.iconStart = QtGui.QIcon("working.png")
        #~ self.iconPause = QtGui.QIcon("pause.png")
        #~ self.iconEnd = QtGui.QIcon("ok.png")
        
        self.iconStop = QtGui.QIcon(":/Ressources/idle.png")
        self.iconStart = QtGui.QIcon(":/Ressources/working.png")
        self.iconPause = QtGui.QIcon(":/Ressources/pause.png")
        self.iconEnd = QtGui.QIcon(":/Ressources/ok.png")
        
        # timer pomodoro en mode travail intensif  (25 minutes)
        self.timerPomodoroWork = QtCore.QTimer();
        self.timerPomodoroWork.setSingleShot(True); # important sinon redémarre dès la fin de son cycle
        QtCore.QObject.connect(self.timerPomodoroWork, QtCore.SIGNAL("timeout()"), self.fncEndWork )
        
        # timer pomodoro en mode break (5minutes ou plus si déjà 3 à 4 pauses)
        self.timerPomodoroBreak = QtCore.QTimer();
        self.timerPomodoroBreak.setSingleShot(True); # important sinon redémarre dès la fin de son cycle
        QtCore.QObject.connect(self.timerPomodoroBreak, QtCore.SIGNAL("timeout()"), self.fncEndBreak )
        
        # timer pour mettre à jour info temps restant
        self.timerSeconde = QtCore.QTimer();
        QtCore.QObject.connect(self.timerSeconde, QtCore.SIGNAL("timeout()"), self.fncUpdateSystray )
        self.timerSeconde.start(1000) ; # appelle fncUpdateSystray() toutes les secondes
        
        # temps ecoulé pour calculer temp restant après une pause
        self.tempsEcoule = QtCore.QTime() # sans (r)
        
        # initialiser trayIcon
        self.trayIcon = QtGui.QSystemTrayIcon(self.iconStop, self)
        self.trayIcon.setToolTip(self.tr("LightPomodoro"))
        QtCore.QObject.connect(self.trayIcon, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.fncSystrayClick )
        self.trayIcon.show()
        
        # créer l'action : quitter 
        self.actionQuit = QtGui.QAction(self.tr("&Quit"), self)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL("triggered()"),	QtGui.qApp, QtCore.SLOT("quit()"))
        # créer l'action : afficher fenêtre de dialogue
        self.actionShowDialog = QtGui.QAction(self.tr("&Dialog"), self)
        QtCore.QObject.connect(self.actionShowDialog, QtCore.SIGNAL("triggered()"), self.fncShowDialog )
        # créer l'action : about
        self.actionShowAbout = QtGui.QAction(self.tr("&A propos"), self)
        QtCore.QObject.connect(self.actionShowAbout, QtCore.SIGNAL("triggered()"), self.fncShowAbout )
        # créer l'action : start
        self.actionStart = QtGui.QAction(self.tr("&Start"), self)
        self.actionStart.setIcon(self.iconStart)
        QtCore.QObject.connect(self.actionStart, QtCore.SIGNAL("triggered()"), self.fncStart )
        # créer l'action : end
        self.actionEnd = QtGui.QAction(self.tr("&End"), self)
        self.actionEnd.setIcon(self.iconEnd)
        QtCore.QObject.connect(self.actionEnd, QtCore.SIGNAL("triggered()"), self.fncEndWork )
        # créer l'action : pause
        self.actionPause = QtGui.QAction(self.tr("&Pause"), self)
        self.actionPause.setIcon(self.iconPause)
        QtCore.QObject.connect(self.actionPause, QtCore.SIGNAL("triggered()"), self.fncPause )
        # créer l'action : stop
        self.actionStop = QtGui.QAction(self.tr("&Stop"), self)
        self.actionStop.setIcon(self.iconStop)
        QtCore.QObject.connect(self.actionStop, QtCore.SIGNAL("triggered()"), self.fncStop )
        # ajouter les actions dans un menu qui sera associé au systray
        self.menuTrayIcon = QtGui.QMenu(self)
        self.menuTrayIcon.addAction(self.actionQuit)
        # self.menuTrayIcon.addAction(self.actionShowDialog) @todo
        self.menuTrayIcon.addAction(self.actionShowAbout)
        self.menuTrayIcon.addSeparator ()
        self.menuTrayIcon.addAction(self.actionStart)
        self.menuTrayIcon.addAction(self.actionPause)
        self.menuTrayIcon.addAction(self.actionStop)
        # associer menu au trayIcon
        self.trayIcon.setContextMenu(self.menuTrayIcon)
        
        # démarrer à l'état Stop
        self.fncStop(False) # argShowMessage=False car au démarrage de GNOME ou Kde, le message est affiché en haut à gauche de l'écran
        
        # info rappel des actions
        #~ self.trayIcon.showMessage (self.tr("LightPomodoro"), self.tr("click gauche : start/pause, click milieu : stop, click droit : menu"), QtGui.QSystemTrayIcon.Information, 3000);        
        

    def fncShowDialog(self):
        """
        Afficher la fenêtre de configuration
        """    
        self.dialog.show()

    def fncShowAbout(self):
        """
        Afficher la fenêtre a propos
        """    
        QtGui.QMessageBox.about(self, self.tr("LightPomodoro"), self.tr("""LightPomodoro - petit applet en pyqt4 avec 25 minutes de travail suivi de 5 minutes de break"""))

    def fncSystrayClick(self, argActivationReason):
        """
        Selon click sur le systray
        """    
        
        if argActivationReason == QtGui.QSystemTrayIcon.DoubleClick :# The system tray entry was double clicked
            pass
        elif argActivationReason == QtGui.QSystemTrayIcon.Trigger : # The system tray entry was clicked
            if self.statut == self.START : 
                self.fncPause()
            elif self.statut == self.END_WORK : 
                self.fncStop()
            else :
                self.fncStart()
        elif argActivationReason == QtGui.QSystemTrayIcon.MiddleClick : # The system tray entry was clicked with the middle mouse button
            self.fncStop()
            
            
    def fncStart(self):
        """
        Démarrer timer selon un interval tenant compte de l'action pause 
        """    
        
        # selon état précédent, réinitialiser temps interval
        if self.statut == self.PAUSE : 
                pass # self.tempsRestant = self.tempsRestant;
        else :
            self.tempsRestant = self.INTERVAL_WORK;
            self.tempsEcoule.restart(); # réinitialiser le temps ecoulé pour gérer la pause
            
        # démarrer le timer
        self.statut = self.START; 
        self.timerPomodoroWork.start(self.tempsRestant) ;# appelle fncEndWork() après ces 25 minutes de travail
        
        # activer l'action pause et désactiver l'action start
        self.actionPause.setEnabled(True);
        self.actionStart.setEnabled(False);
        
        # affichage
        self.trayIcon.setIcon(self.iconStart)
        self.trayIcon.setToolTip(self.tr("LightPomodoro, Start"))
        self.trayIcon.showMessage (self.tr("LightPomodoro"), self.tr("Start"), QtGui.QSystemTrayIcon.Information, 1000);

    def fncPause(self):
        """
        Pause du timer 
        l'absence de méthode pause() nécessite de calculer le temps restant 
        """    
        
        # mettre en pause
        self.statut = self.PAUSE; 
        # self.timerPomodoroWork.pause() < -- n'existe pas
        self.timerPomodoroWork.stop() 
        self.tempsRestant = self.timerPomodoroWork.interval() - self.tempsEcoule.elapsed();   
        if self.tempsRestant < 0 : self.tempsRestant = 0; 
        
        # désactiver l'action pause et activer l'action start
        self.actionPause.setEnabled(False);
        self.actionStart.setEnabled(True);
        
        
        # affichage
        self.trayIcon.setIcon(self.iconPause)
        self.trayIcon.setToolTip(self.tr("LightPomodoro, Pause"))
        self.trayIcon.showMessage (self.tr("LightPomodoro"), self.tr("Pause"), QtGui.QSystemTrayIcon.Information, 2000);
        
    def fncStop(self, argShowMessage=True):
        """
        Stop du timer 
        """    
        
        # arrêter les timer
        self.statut = self.STOP; 
        self.timerPomodoroWork.stop()
        self.timerPomodoroBreak.stop()
        
        # désactiver l'action pause, activer Start
        self.actionStart.setEnabled(True);
        self.actionPause.setEnabled(False);
        
        # affichage
        self.trayIcon.setIcon(self.iconStop)
        self.trayIcon.setToolTip(self.tr("LightPomodoro, Stop"))
        if argShowMessage == True : # mis en place car au démarrage de kde ou Gnome, l'applet se trouve en haut à gauche de l'écran ... le temps que l'os le repositionne dans la barre du systray
            self.trayIcon.showMessage (self.tr("LightPomodoro"), self.tr("Stop"), QtGui.QSystemTrayIcon.Information, 3000);

    def fncEndWork(self):
        """
        Fin du temps pomodoro travail
        """    
        
        # stopper le timer de travail
        self.statut = self.END_WORK; 
        self.timerPomodoroWork.stop()
        
        # démarrer le le timer de break court ou long
        self.countBreakShort += 1;
        if self.countBreakShort <= self.longBreakAfterXShort : 
            self.timerPomodoroBreak.start(self.INTERVAL_BREAK_SHORT) ; # appelle fncEndBreak() après ces 5 minutes de pause
            messageInfoBreak = 'Break'
        else :
            self.timerPomodoroBreak.start(self.INTERVAL_BREAK_LONG) ; # appelle fncEndBreak() après ces 15 minutes de pause
            messageInfoBreak = 'Break LONG ...'
            self.countBreakShort = 0; # réinitialiser
        
        # affichage
        self.trayIcon.setIcon(self.iconEnd)
        self.trayIcon.setToolTip(self.tr("LightPomodoro, ")+self.tr(messageInfoBreak))
        self.trayIcon.showMessage (self.tr("LightPomodoro"), self.tr(messageInfoBreak), QtGui.QSystemTrayIcon.Information, 3000);

    def fncEndBreak(self):
        """
        Fin du temps pomodoro break
        """    
        
        # stopper le timer
        self.statut = self.END_BREAK; 
        self.timerPomodoroBreak.stop()
        
        # stop
        self.fncStop(False); # argShowMessage=False

    def fncUpdateSystray(self):
        """
        Mettre à jour l'icone + tooltip + message du systray
        """    
        if self.statut != self.STOP :
            # @todo : calculer temps restant
            pass
        

if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    dialog = LightPomodoroDialog()
    x = LightPomodoroSystray( dialog )
    sys.exit(app.exec_())		
