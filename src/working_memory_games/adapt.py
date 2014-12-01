# -*- coding: utf-8 -*-
"""
Pelin vaikeustason johtaminen pelaajakohtaisesta pelihistoriasta
bayesilaisella algoritmilla

(c) Janne V. Kujala

Janne V. Kujala: Obtaining the Best Value for Money in Adaptive Sequential
Estimation. Journal of Mathematical Psychology, Vol. 54, Issue 6, pp. 475-480,
December 2010.

Janne V. Kujala, Ulla Richardson, and Heikki Lyytinen: A Bayesian-Optimal
Principle for Learner-Friendly Adaptation in Learning Games. Journal of
Mathematical Psychology, Vol. 54, Issue 2, pp. 247-255, April 2010.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from __future__ import division
from numpy import *
from numpy.random import random

# Mahdolliset tuntemattoman arvot
kvals = arange(1,21)

# Mahdolliset n:n arvot
nvals = arange(2,20)

def psi(k,n):
    # Todenmukaisessa mallissa on aina oltava pieni todennäköisyys
    # saada vahingossa väärin vaikka osaisi.  Kaavassa on hihasta
    # ravistettuna 5% vahinkotodennäköisyys ja lisäksi hatusta vedetty
    # 5% arvaustodennäköisyys, eli todennäköisyys jolla huonoinkin
    # pelaaja saa tehtävän oikein (tämän voi useimmiten päätellä
    # tehtävästä, esimerkiksi jos valitaan n:stä vaihtoehdosta, on
    # arvaustodennäköisyys 1/n).
    gamma = 1./4.**n
    return gamma + (1 - gamma - 0.05)/(1+exp(n-k))
    #return 0.05 + 0.9/(1+exp(n-k))

"""
gnuplot
psi(k,n) = 0.05 + 0.9/(1+exp(n-k))
plot [2:9] psi(1,x),psi(2,x),psi(3,x),psi(4,x),psi(5,x),psi(6,x),psi(7,x),psi(8,x),psi(9,x),psi(10,x)
"""

#p0 = ones(shape(kvals),float)
#p0 = 1.0 / where(kvals>2,kvals,2)**2
p0 = 1.0 / where(kvals>2,kvals,3)**2
p0 *= 1 / sum(p0)

def update(p,n,res):
    if res:
        p = p * psi(kvals, n)
    else:
        p = p * (1 - psi(kvals, n))
    return p * (1 / sum(p))

def entropy(p):
    return -sum(p * log(p + 1e-100))/log(2)

def simulate_result(n):
    p_succ = psi(true_k,n)
    return random() < p_succ

def expected_gain(p, n, child_friendly=False):
    # oikean vastauksen estimoitu todennäköisyys
    p_succ = sum( p * psi(kvals,n) )

    # väärän vastauksen estimoitu todennäköisyys
    p_fail = 1 - p_succ

    # entropian odotusarvo vastauksen jälkeen
    expected_entropy = (  p_succ * entropy(update(p,n,1))
                          + p_fail * entropy(update(p,n,0)))

    # entropian pieneniminen  = saatu informaatio
    gain = entropy(p) - expected_entropy

    if child_friendly:
        # lapsiystävällinen versio:
        # mitataan saadun informaatiomäärän odotusarvo
        # suhteessa "hinnan" odotusarvoon, missä hinta
        # on määritelty siten, että väärä vastaus
        # maksaa yhden yksikön
        gain /= n # p_fail

    return gain


# simuloitu todellinen pelaajan parametri
true_k = 7

# käytetäänkö "lapsiystävällistä versiota"
child_friendly = True


if 0:
    p = p0
    for i in range(20):
        print
        print 'p_%d = [%s]' % (i, ' '.join('%.2f' % prob for prob in p))
        gains = [expected_gain(p,n,child_friendly=child_friendly) for n in nvals]

        print 'Expected gains in bits for n = %s:' % nvals
        print '[%s]' % (' '.join('%.3f' % g for g in gains))

        n = nvals[argmax(gains)]
        print 'Best n to present next:', n

        res = simulate_result(n)
        print 'Trial result:', res

        p = update(p,n,res)
else:

    #import pydot

    simulations = 7 #12
    for x in range(2**simulations):
        s = ''.join(str((x>>i)&1) for i in xrange(simulations-1,-1,-1))
        print s
        s = map(lambda x: int(x) == 1, s)
        print s

        p = p0
        n = 3
        for i in range(len(s)+1):
            current = n
            #print
            #print 'p_%d = [%s]' % (i, ' '.join('%.2f' % prob for prob in p))
            gains = [expected_gain(p,n,child_friendly=child_friendly) for n in nvals]

            #print 'Expected gains in bits for n = %s:' % nvals
            #print '[%s]' % (' '.join('%.3f' % g for g in gains))

            n = nvals[argmax(gains)]
            if n > current + 2:
                n = current + 2
            print 'Best n to present next:', n

            if i >= len(s): break
            res = simulate_result(n)
            res = s[i]
            #print 'Trial result:', res

            p = update(p,n,res)

        #print 'Best n to present next:', n

# Koodi yllä simuloi 20 trialia ja joka välissä päivittää k:n
# todennäiköisyysjakauman. Simulaation edetessä tämä jakauma aina
# konvergoituu enemmin tai myöhemmin true_k-arvoon (kokeile eri
# arvoja), jonka mukaisesti vastaukset simuloidaan.

# Tämä on nyt jo varsin toimiva malli, mahdollisia parannuksia olisi
# lähinnä
#
#   - arvaustodennäköisyyden tarkentaminen (ks. psi-funkio yllä)
#
#   - mahdollisesti lisää tuntemattomia parametreja k:n lisäksi, kuten
#     sigmoidin kulmakerroin
#
#   - sen huomioiminen, että pelaajan todellinen parametri k muuttuu
#     aikaa myöten (eli pelaaja oppii)
#
#        - voidaan joko aloittaa pelisessio aina olettamalla
#          tasajakauma (eli ei tiedetä mitään pelaajan tasosta) ja
#          pitämällä sessiot niin lyhyinä ettei merkittävää muutosta
#          tapahdu session sisällä
#
#        - tai sitten voidaan eksplisiittisesti mallintaa pelaajan
#          tason muutos joko sessioiden välillä tai tarvittaessa
#          session sisällä
