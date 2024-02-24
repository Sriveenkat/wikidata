#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2024 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import html
import random
import re
import sys
import time
import urllib
import urllib.parse
import urllib.request

import pywikibot
from pywikibot import pagegenerators
from wikidatafun import *

publishers = {
    "bne": {"domain": "bne.es", "q": "Q50358336"}, 
    "bnf": {"domain": "bnf.fr", "q": "Q19938912"}, 
    
    "europapress": {"domain": "europapress.es", "q": "Q3060712"}, 
    "rtve": {"domain": "rtve.es", "q": "Q54829"}, 
}
languages = {
    "es": "Q1321", 
    "en": "Q1860", 
}

def addHumanRef(repo="", item=""):
    global publishers
    if not repo or not item:
        return
    today = datetime.date.today()
    year, month, day = [int(today.strftime("%Y")), int(today.strftime("%m")), int(today.strftime("%d"))]
    itembne = pywikibot.ItemPage(repo, publishers["bne"]["q"])
    itembnf = pywikibot.ItemPage(repo, publishers["bnf"]["q"])
    bneinref = False
    bnfinref = False
    if 'P31' in item.claims and len(item.claims['P31']) == 1:
        #print(item.claims['P31'][0].getTarget())
        sources = item.claims['P31'][0].getSources()
        for source in sources:
            #print(source)
            if ("P248" in source and source["P248"][0].getTarget() == itembne) or \
               ("P950" in source) or \
               ("P854" in source and publishers["bne"]["domain"] in source["P854"][0].getTarget()):
                bneinref = True
            if ("P248" in source and source["P248"][0].getTarget() == itembnf) or \
               ("P268" in source) or \
               ("P854" in source and publishers["bnf"]["domain"] in source["P854"][0].getTarget()):
                bnfinref = True
    else:
        print("Not Q5")
        return
    """
    if bnfinref:
        print("Ya tiene BNF en referencia")
    else:
        print("NO tiene BNF en referencia")
    """
    if bneinref:
        print("Ya tiene BNE en referencia, skiping")
        return
    else:
        print("NO tiene BNE en referencia")
    
    bneid = ""
    if 'P950' in item.claims:
        if len(item.claims['P950']) == 1:
            bneid = item.claims['P950'][0].getTarget()
            print(bneid)
        else:
            print("More than one ID, skiping")
            return
    else:
        print("No tiene BNE id, skiping")
        return
    
    if not bneid:
        print("No BNE id, skiping")
        return
    if not bneid.startswith("XX"):
        print("BNE ID not starts with XX, skiping")
        return
    
    if itembne and bneid:
        claim = item.claims['P31'][0]
        refstatedinclaim = pywikibot.Claim(repo, 'P248')
        refstatedinclaim.setTarget(itembne)
        refretrieveddateclaim = pywikibot.Claim(repo, 'P813')
        refretrieveddateclaim.setTarget(pywikibot.WbTime(year=year, month=month, day=day))
        refbneidclaim = pywikibot.Claim(repo, 'P950')
        refbneidclaim.setTarget(bneid)
        claim.addSources([refstatedinclaim, refretrieveddateclaim, refbneidclaim], summary='BOT - Adding 1 reference')
        print("Adding BNE reference to P31 claim")
    
    return

def addGenderRef(repo="", item=""):
    if not repo or not item:
        return
    today = datetime.date.today()
    year, month, day = [int(today.strftime("%Y")), int(today.strftime("%m")), int(today.strftime("%d"))]
    maleitem = pywikibot.ItemPage(repo, "Q6581097")
    malegivennameitem = pywikibot.ItemPage(repo, "Q12308941")
    femaleitem = pywikibot.ItemPage(repo, "Q6581072")
    femalegivennameitem = pywikibot.ItemPage(repo, "Q11879590")
    if 'P21' in item.claims and len(item.claims['P21']) == 1:
        #print(item.claims['P21'][0].getTarget())
        sources = item.claims['P21'][0].getSources()
        if not sources:
            if 'P735' in item.claims and len(item.claims['P735']) == 1: #given name
                givennameitem = item.claims['P735'][0].getTarget()
                if not givennameitem: #sometimes no value https://www.wikidata.org/wiki/Q1918629
                    return
                givennameitem.get()
                if "P31" in givennameitem.claims and len(givennameitem.claims['P31']) == 1:
                    inferredfromgivenname = pywikibot.ItemPage(repo, "Q69652498")
                    if givennameitem.claims["P31"][0].getTarget() == malegivennameitem and item.claims['P21'][0].getTarget() == maleitem:
                        print("Male given name")
                        claim = item.claims['P21'][0]
                        refheuristicclaim = pywikibot.Claim(repo, 'P887')
                        refheuristicclaim.setTarget(inferredfromgivenname)
                        claim.addSources([refheuristicclaim], summary='BOT - Adding 1 reference')
                        print("Adding reference to claim")
                        return
                    elif givennameitem.claims["P31"][0].getTarget() == femalegivennameitem and item.claims['P21'][0].getTarget() == femaleitem:
                        print("Female given name")
                        claim = item.claims['P21'][0]
                        refheuristicclaim = pywikibot.Claim(repo, 'P887')
                        refheuristicclaim.setTarget(inferredfromgivenname)
                        claim.addSources([refheuristicclaim], summary='BOT - Adding 1 reference')
                        print("Adding reference to claim")
                        return
                    else:
                        return
    return

def ddgSearch(search=""):
    if not search:
        return
    time.sleep(2)
    #search = search + " " + str(random.randint(100, 999))
    ddgurl = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote_plus(search)
    print(ddgurl)
    raw = getURL(url=ddgurl)
    resulturl = ""
    if '<div class="no-results">' in raw:
        print("Sin resultados")
    else:
        splits = raw.split('<h2 class="result__title">')[1:]
        for split in splits:
            resulturl = ""
            #print(split)
            m = re.findall(r'(?im)<a rel="nofollow" class="result__a" href="([^"]+?)">[^<>]*?</a>', split)
            if m and len(m) == 1:
                resulturl = urllib.parse.unquote_plus(m[0]).split('uddg=')[1].split('&amp;rut=')[0]
                print("Found", resulturl)
            break #just first result
    
    return resulturl

def rtve(repo="", itemlabel="", deathdate=""):
    global publishers
    resultpublisher = pywikibot.ItemPage(repo, publishers["rtve"]["q"])
    search = 'fallece muere "%s" %s' % (itemlabel, deathdate.year)
    search = search + " rtve.es"
    resulturl = ddgSearch(search=search)
    resulttitle, resultdate, resulttext = "", "", ""
    if "rtve.es" in resulturl:
        try:
            raw = getURL(url=resulturl)
            #<meta name="DC.title" content="Muere el actor Francisco Merino, uno de los grandes secundarios del cine español"/>
            #<meta name="DC.date" content="2022-10-09T18:07:00+02:00"/>
            resulttitle = re.findall(r'(?im)<meta name="DC.title" content="([^<>]+?)" */>', raw)[0]
            resulttitle = unquote(resulttitle)
            resultdate = re.findall(r'(?im)<meta name="DC.date" content="([^<>]+?)" */>', raw)[0].split("T")[0]
            resultdate = datetime.datetime(year=int(resultdate.split("-")[0]), month=int(resultdate.split("-")[1]), day=int(resultdate.split("-")[2]))
            resulttext = raw.split('<div class="artBody">')[1].split('<div class="slideH">')[0]
            resulttext = unquote(resulttext)
            if not itemlabel in resulttitle and not itemlabel in resulttext:
                return
            refcandidate = {"title": resulttitle, "publisher": resultpublisher, "date": resultdate, "url": resulturl, "lang": "es"}
            return refcandidate
        except:
            pass
    
    return 

def europapress(repo="", itemlabel="", deathdate=""):
    global publishers
    resultpublisher = pywikibot.ItemPage(repo, publishers["europapress"]["q"])
    search = 'fallece muere "%s" %s' % (itemlabel, deathdate.year)
    search = search + " europapress.es"
    resulturl = ddgSearch(search=search)
    resulttitle, resultdate, resulttext = "", "", ""
    if "europapress.es" in resulturl:
        try:
            raw = getURL(url=resulturl)
            #<meta name="DC.title" content="Muere el actor Francisco Merino, uno de los grandes secundarios del cine español"/>
            #<meta name="DC.date.issued" content="2022-07-07T20:48:47 +02:00" />
            resulttitle = re.findall(r'(?im)<meta name="DC.title" content="([^<>]+?)" */>', raw)[0]
            resulttitle = unquote(resulttitle)
            resultdate = re.findall(r'(?im)<meta name="DC.date.issued" content="([^<>]+?)" */>', raw)[0].split("T")[0]
            resultdate = datetime.datetime(year=int(resultdate.split("-")[0]), month=int(resultdate.split("-")[1]), day=int(resultdate.split("-")[2]))
            resulttext = raw.split('<!-- fin firma-equipo -->')[1].split('<!-- Inicio entidades -->')[0]
            resulttext = unquote(resulttext)
            if not itemlabel in resulttitle and not itemlabel in resulttext:
                return
            refcandidate = {"title": resulttitle, "publisher": resultpublisher, "date": resultdate, "url": resulturl, "lang": "es"}
            return refcandidate
        except:
            pass
    
    return 

def unquote(s=""):
    s = urllib.parse.unquote_plus(s)
    s = html.unescape(s)
    return s

def searchDeathdateRef(repo="", item="", itemlabel="", deathdate=""):
    if not repo or not item:
        return
    if not itemlabel or not deathdate:
        return
    
    refcandidate = ""
    if 'P27' in item.claims and len(item.claims['P27']) == 1:
        itemcountry = item.claims['P27'][0].getTarget()
        itemcountry.get()
        if itemcountry.labels["en"] == "Spain":
            refcandidate = rtve(repo=repo, itemlabel=itemlabel, deathdate=deathdate)
            if not refcandidate:
                refcandidate = europapress(repo=repo, itemlabel=itemlabel, deathdate=deathdate)
        else:
            return
    return refcandidate

def usedsources(sources=""):
    global publishers
    used = False
    if not sources:
        return used
    for source in sources:
        #print(source)
        for publisher, props in publishers.items():
            if 'P854' in source:
                if props["domain"] in source['P854'][0].getTarget():
                    print("Ya tiene referencia", props["domain"])
                    used = True
    return used

def addDeathdateRef(repo="", item=""):
    global languages
    if not repo or not item:
        return
    today = datetime.date.today()
    year, month, day = [int(today.strftime("%Y")), int(today.strftime("%m")), int(today.strftime("%d"))]
    
    if ('P569' in item.claims and len(item.claims['P569']) == 1) and \
       ('P570' in item.claims and len(item.claims['P570']) == 1):
        #print(item.claims['P570'][0].getTarget())
        sources = item.claims['P570'][0].getSources()
        if not sources or not usedsources(sources):
            itemlabel = "es" in item.labels.keys() and item.labels["es"] or "en" in item.labels.keys() and item.labels["en"] or ""
            birthdate = item.claims['P569'][0].getTarget()
            deathdate = item.claims['P570'][0].getTarget()
            if itemlabel and deathdate:
                refcandidate = searchDeathdateRef(repo=repo, item=item, itemlabel=itemlabel, deathdate=deathdate)
                if refcandidate:
                    if not re.search(r"(?im)(fallece|falleció|muere|murió|dies|died)", refcandidate["title"]):
                        print("Not found keywords in title", refcandidate["title"])
                        return
                    if deathdate.year != refcandidate["date"].year:
                        print("Death year and news year are different")
                        return 
                    claim = item.claims['P570'][0]
                    reftitleclaim = pywikibot.Claim(repo, 'P1476')
                    reftitlemonotext = pywikibot.WbMonolingualText(text=refcandidate["title"], language=refcandidate["lang"])
                    reftitleclaim.setTarget(reftitlemonotext)
                    refpublisherclaim = pywikibot.Claim(repo, 'P123')
                    refpublisherclaim.setTarget(refcandidate["publisher"])
                    refpublisheddateclaim = pywikibot.Claim(repo, 'P577')
                    refpublisheddateclaim.setTarget(pywikibot.WbTime(year=refcandidate["date"].year, month=refcandidate["date"].month, day=refcandidate["date"].day))
                    reflanguageofworkclaim = pywikibot.Claim(repo, 'P407')
                    reflanguageofworkclaim.setTarget(pywikibot.ItemPage(repo, languages[refcandidate["lang"]]))
                    refreferenceurlclaim = pywikibot.Claim(repo, 'P854')
                    refreferenceurlclaim.setTarget(refcandidate["url"])
                    refretrieveddateclaim = pywikibot.Claim(repo, 'P813')
                    refretrieveddateclaim.setTarget(pywikibot.WbTime(year=year, month=month, day=day))
                    newsource = [reftitleclaim, refpublisherclaim, refpublisheddateclaim, reflanguageofworkclaim, refreferenceurlclaim, refretrieveddateclaim]
                    try:
                        print(newsource)
                        print("Adding deathdate reference")
                        claim.addSources(newsource, summary='BOT - Adding 1 reference')
                    except:
                        print("Error while saving, skipping")
    return

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    
    for i in range(1000):
        queries = [
        """
        SELECT ?item
        WHERE {
          SERVICE bd:sample {
            ?item wdt:P950 ?id. #P950 BNE id
            bd:serviceParam bd:sample.limit 10000 .
            bd:serviceParam bd:sample.sampleType "RANDOM" .
          }
          ?item wdt:P31 wd:Q5.
        }
        #random%d
        """ % (random.randint(1000000, 9999999))
        ]
        queries = [
        """
        SELECT ?item
        WHERE {
          SERVICE bd:sample {
            ?item wdt:P31 wd:Q5 .
            bd:serviceParam bd:sample.limit 10000 .
            bd:serviceParam bd:sample.sampleType "RANDOM" .
          }
          ?item wdt:P31 wd:Q5.
        }
        #random%d
        """ % (random.randint(1000000, 9999999))
        ]
        queries = [ #para testear noticias de deathdate
        """
        SELECT ?item
        WHERE {
          ?item wdt:P31 wd:Q5.
          ?item wdt:P27 wd:Q29.
          ?item wdt:P570 ?deathdate.
          FILTER (?deathdate > "2020-01-01"^^xsd:dateTime).
        }
        #random%d
        """ % (random.randint(1000000, 9999999))
        ]
        for query in queries:
            time.sleep(1)
            url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query))
            url = '%s&format=json' % (url)
            print("Loading...", url)
            sparql = getURL(url=url)
            json1 = loadSPARQL(sparql=sparql)
            
            for result in json1['results']['bindings']:
                q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
                #bneid = 'bneid' in result and result['item']['value'] or ''
                if not q:
                    break
                print('\n== %s ==' % (q))
                item = pywikibot.ItemPage(repo, q)
                try: #to detect Redirect because .isRedirectPage fails
                    item.get()
                except:
                    print('Error while .get()')
                    continue
                
                #addHumanRef(repo=repo, item=item) #bne, orcid, google scholar...
                #addGenderRef(repo=repo, item=item)
                
                #addCitizenshipRef #based on birthplace when birthdate >= 1950 (cuidado países que ya no existen)
                #addGivennameRef inferred from full name when fullname.split = 2 y esta en la label inglesa
                #addFamilynameRef inferred from full name when fullname.split = 2 y esta en la label inglesa
                
                addDeathdateRef(repo=repo, item=item)

if __name__ == "__main__":
    main()
