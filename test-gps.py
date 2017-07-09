from gps import *
import os

# Creons une fonction
def mon_cgps():
 # On ouvre une session
 session = gps(mode=WATCH_ENABLE)
 # On prevoit les soucis
 try:
  # Et on envoie une boucle infinie
  while True:
   # On envoie les elements de next() dans une variable
   donnees = session.next()
   # Ce qui nous permet de verifier lorsque les "fix" sont
   # actualises (on utilise "class" parce qu'elle est toujours
   # presente)
   if donnees['class'] == "TPV":
    # Pour afficher le resultat
    # On commence par tout effacer
    os.system('clear')
    # Puis on s'amuse !
    print
    print ' Information GPS'
    print '----------------------------------------'
    print 'latitude      ' , session.fix.latitude
    print 'longitude     ' , session.fix.longitude
    print 'temps utc     ' , session.utc
    print 'altitude (m)  ' , session.fix.altitude
    print 'vitesse (m/s) ' , session.fix.speed
    #print()
    #print( 'satellites    ' , session.satellites)
 # En cas de probleme
 except KeyError:
  pass
 except KeyboardInterrupt:
  print()
  print( "Ferme par l'utilisateur")
 except StopIteration:
  print()
  print( "GPSD s'est arrete")
 finally:
  session = None


mon_cgps()
