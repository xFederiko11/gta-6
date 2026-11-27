"""Public HTTP verification of exact reader contracts; never writes or publishes."""
import re,time
from urllib.request import Request,urlopen
BASE="https://xfederiko11.github.io/gta-6/"
CHECKS={
 "":('data-chronology-path="garage-gratuiti/southside-storage/"','id="ultimi-articoli"'),
 "articoli/":('data-chronology-search','data-chronology-subfilter','data-archive-pager','archive-summary','data-umami-event="category-open"','<title>Articoli GTA 6: guide, news e aggiornamenti</title>'),
 "guide-e-tutorial/":('data-editorial-route="salvare-auto"','/gta-6/salvare-auto/'),
 "articoli/categoria/veicoli/":('data-archive-group="veicoli"','<title>Auto GTA 6: veicoli, garage e registrazione</title>','aria-label="Percorsi consigliati"'),
 "articoli/pagina/2/":('data-archive-page="2"','data-archive-pager'),
 "articoli/categoria/hdr/":('data-chronology-category="HDR OLED"','data-archive-group="hdr"'),
 "articoli/categoria/trucchi/":('data-chronology-category="Trucchi"','data-archive-group="trucchi"'),
 "articoli/categoria/veicoli/garage/":('data-archive-sub="garage"','data-sub="garage"'),
 "salvare-auto/":('Come salvare e registrare un’auto in GTA 6','data-editorial-next','"datePublished":"2026-11-20"'),
 "guide-e-tutorial/meditazione-capitolo-1/":('data-meditation-map','www.gtabase.com/gta-6/map/?feature=meditation','Port Gellhorn','"datePublished":"2026-11-18"'),
 "glitch/":('data-glitch-index','data-chronology-path="guide-e-tutorial/glitch-prima-persona-ps5/"'),
 "guide-e-tutorial/key-cloner/":("data-legit-guide","Key Cloner"),
 "guide-e-tutorial/vendere-veicoli/":("data-legit-guide","Photo/Shoot"),
 "garage-gratuiti/southside-storage/":('data-vc-code-value value="1010"',),
 "veicoli/pfister-vanessas-growler/":('data-vc-code-value value="92665"',),
 "veicoli/invetero-spiderweb-coquette/":('data-vc-code-value value="092319"',),
 "veicoli/declasse-applesauce-bobcat/":('data-vc-code-value value="360782"',),
}
for key in ("port-gellhorn","thompson-court","ne-15th-street","pegassi-residences"):
    CHECKS["garage-gratuiti/garage-storia/"+key+"/"]=("data-garage-guide","www.gtabase.com/gta-6/properties/")
def verify():
    for path,markers in CHECKS.items():
        for attempt in range(4):
            try:
                with urlopen(Request(BASE+path,headers={"Cache-Control":"no-cache","User-Agent":"GTA6Italia-ReleaseQA/1.0"}),timeout=15) as response:
                    assert response.status==200 and response.geturl()==BASE+path
                    body=response.read(1500001).decode()
                assert len(body)<=1500000
                assert 'rel="canonical" href="'+BASE+path+'"' in body
                assert all(m in body for m in markers),path
                if path=="glitch/":assert len(re.findall(r'data-chronology-path="',body))==1
                if path in ("","articoli/","articoli/pagina/2/"):
                    assert len(re.findall(r'data-chronology-path="',body))==25,path
                if path.startswith("articoli/categoria/"):
                    assert 1<=len(re.findall(r'data-chronology-path="',body))<=25,path
                print("PUBLIC_EDITORIAL_RELEASE_OK",BASE+path)
                break
            except (OSError,AssertionError):
                if attempt==3:raise
                time.sleep(4*(attempt+1))
if __name__=="__main__":verify()
