#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
__version__ = "$Revision: 1.0 $"
__author__ = "Nicolas Seriot"
__date__ = "2004-10-02"

"""
Permet de chiffrer / déchiffrer un no AVS.

TODO :
- retourner des chaînes unicode
- traduire le logiciel
- améliorer les tests
- ajouter entêtes et license
"""

import sys
import re
import dico

from dico import Dico
from avs import *
from string import joinfields

# class defined in AvsMain.nib
class Avs:
    """
    représente un no avs
    """

    # dictionnaire des correspondances nom:chiffre
    __monDico = Dico()
    
    # liste des quatre groupes de chiffre, sous la forme de chaînes de caractères
    __liste = []
    
    def __init__(self, param):
        """
        initialise un no AVS
        
        param peut être :
        - un no avs sous forme de string
        - un dictionnaire avec nom, homme, date, suisse
        """
        
        if type(param) == type({}):#DictType:
            self.__setParam(param)     # construit un no d'après un dictionnaire
        else:
            if type(param) == type(""):#StringType:                
                # contrôle syntaxique
                if not re.match("\d\d\d\.\d\d\.\d\d\d\.\d\d\d", param) :
                    raise SyntaxError
                
                # construction de la liste
                self.__liste = param.split(".")
                
            else:
                raise RuntimeError
    
#    def __getitem__(self, i):
#        return self.__liste[i]
        
    def nom(self):
        """
        renvoie une chaîne indiquant l'intervalle
        dans lequel se situe le nom d'une personne
        """
        
        code = int(self.__liste[0])
        nom  = self.__monDico.d[code]
        
        # concaténer la clé suivante si elle existe
        if code < 999:
            code = code + 1
            while not self.__monDico.d[code] and code < 999:
                code = code + 1
            
            nom = "[ " + nom + " - " + self.__monDico.d[code] + " ["
        else:
            nom = "[ " + nom

        return nom

    def annee(self):
        """
        renvoie l'année de naissance de la personne
        """
        
        n = int(self.__liste[1])
        
        if n == 0:
            return "inconnue"
        elif n > 10: # arbitraire
            prefix = 19 # 20eme sièce
        else:
            prefix = 20 # 21eme siècle
        
        return prefix * 100 + n
            
    def sexe(self):
        """
        renvoie le sexe de la personne
        """
    
        n = int(self.__liste[2]) / 100
        
        if n in range(1,5):
            return "masculin"
        elif n in range(5,9):
            return "feminin"
        else:
            raise AttributeError
        
    def date(self):
        """
        renvoie la date de naissance
        """
        
        n = int(self.__liste[2])
    
        p = n / 100 # le premier chiffre
        
        if p >= 5:
            p = p - 4
            
        p = p - 1
        
        d = n % 100 # deux derniers chiffres
        
        if d in range(1,32):
            jour = d
            mois = ["janvier", "avril", "juillet", "octobre"]
        elif d in range(32,63):
            jour = d % 31
            mois = ["fevrier", "mai", "aout", "novembre"]
        elif d in range(63,94):
            jour = d % 62
            mois = ["mars", "juin", "septembre", "decembre"]
        else:
            raise AttributeError
        
        return str(jour) + " " + mois[p] + " " + str(self.annee())
        
    def ordre(self):
        """
        renvoie le numéro d'ordre
        """
        
        return int(self.__liste[3]) / 10
        
    def nationalite(self):
        """
        renvoie la nationalité de la personne
        """

        n = int(self.__liste[3]) / 10 % 10
        
        print "-", n
        
        if n in range(1,5):
            return "suisse"
        elif n in range(5,9):
            return "étranger / apatride"
        else:
            raise AttributeError

    def controle(self, essai = 0):
        """
        indique si un no est valable au sens de la somme de contrôle
        
        si le paramètre essai est nul, la fonction s'applique sur la liste membre,
        sinon elle s'applique sur le numéro essai passé en paramètre
        """

        if essai:
            n = str(essai)
        else:
            n = self.__liste
    
        n = map(str, n)            # une liste de caractères
        n = reduce(str.__add__, n) # une chaîne de caractères
        n = map(int, n)               # une liste d'entiers

        p = "5432765432"
        p = map(int, p)               # une liste de caractères
        
        checksum = 0
        
        for i in range(0, 10):
            checksum = checksum + n[i]*p[i]
            
        reste = checksum % 11 #divmod(checksum,11)[1]

        if reste == 0:
            controle = reste
        else:
            controle = 11 - reste

        return controle == n[10]

    def __setParam(self, param):
        """
        calcule un numero AVS possible d'après les paramètres donnés
        """
        
        nom    = param['nom']
        homme  = param['homme']
        date   = param['date']
        suisse = param['suisse']
        
        # traitement de la date
        print date
        # controle de la syntaxe de la date
        if not re.match("\d\d\s\d\d\s\d\d\d\d", date):
            raise SyntaxError
        
        date = date.split(" ")
        
        date = map(int, date)
        
        jour  = date[0]        
        mois  = date[1]
        annee = date[2] % 100

        if not (jour and mois) or jour > 31 or mois > 12:
            raise AttributeError

        # traitement du nom
        #nom = nom.encode('latin-1', 'strict') # virer l'unicode
        nom = str(nom)

        # ne garder que le premier mot

        try:
            coupure = nom.index(' ')
            nom = nom[:coupure]
        except ValueError:
            pass

        try:
            coupure = nom.index('-')
            nom = nom[:coupure]
        except ValueError:
            pass
                
        nom = nom[:7]                         # pas besoin de plus de 7 caractères
        
        nom_a = nom[:1].upper()
        nom_b = nom[1:].lower()
        
        nom = nom_a + nom_b
        
        liste = self.__monDico.d.items() # transforme le dico en liste de tuples
        
        val = self.__monDico.d.values()
        
        i = 0
        
        while val[i] <= nom[:len(val[i])]:
            i = i + 1                

            if val[i] >= "Zy":
                i = i + 1
                break
        
        i = i-1
        
        # premier groupe
        c1 = str(liste[i][0])
        
        # deuxière groupe
        c2 = str(annee)
        
        if int(c2) < 10:
            c2 = "0" + c2
        
        # traitement du troisième groupe
        c3_1 = (mois - 1) / 3 + 1
        
        if not homme:
            c3_1 = c3_1 + 4
        
        groupe_mois = (mois - 1) % 3
            
        c3_23 = jour + groupe_mois * 31
        
        # troisième groupe
        c3 = str(100 * c3_1 + c3_23)
        
        controle_ok = False
        
        passe = 0
        
        while not controle_ok:
            passe = passe + 1
            
            c4_12 = "0" + str((not suisse) * 4 + passe)
            
            c1234_sans_ctrl = c1 + c2 + c3 + c4_12
            
            possibles = [c1234_sans_ctrl + str(x) for x in range(0,10)]
            
            solution = filter(self.controle, possibles)
            
            controle_ok = len(solution) == 1
                
        solution = filter(self.controle, possibles)[0]
        
        self.__liste = [solution[0:3], solution[3:5], solution[5:8], solution[8:11]]

    def __str__(self):
        return joinfields(self.__liste, ".")
"""        
    if __name__ == "__main__":
        message = ""
        
        while 1:
            no = raw_input("Entrez un no AVS : > ")

            try:
                print "debut"
                message = ""
                avs = Avs(no)
            except SyntaxError:
                message = "syntaxe incorrecte"
                        
            if not avs.controle():
                message = "somme de controle incorrecte"
            
            if message:
                print message
            else:
                print avs
                print "Nom  : " + avs.nom()
                print "Sexe : " + avs.sexe()
                print "Date : " + unicode(avs.date())
                print "Nat. : " + avs.nationalite()
            
            print ""
"""

if __name__ == "__main__":
    avs = Avs("144.78.123.876")
    print avs.nom()
    print avs.annee()
    print avs.sexe()
    print avs.date()
    print avs.nationalite()
    
    param = {}
    param['nom'] = "Pierre"
    param['homme'] = False
    param['date'] = "10 05 1975"
    param['suisse'] = "suisse"
    avs = Avs(param)
    print avs
    