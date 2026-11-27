"""Public HTTP verification of exact reader contracts; never writes or publishes."""
import re,time
from urllib.request import Request,urlopen
BASE="https://xfederiko11.github.io/gta-6/"
CHECKS={
 "":('data-chronology-path="garage-gratuiti/southside-storage/"','id="ultimi-articoli"'),
 "articoli/":('data-chronology-search','data-chronology-category="HDR OLED"','data-chronology-category="Trucchi"'),
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
                print("PUBLIC_EDITORIAL_RELEASE_OK",BASE+path)
                break
            except (OSError,AssertionError):
                if attempt==3:raise
                time.sleep(4*(attempt+1))
if __name__=="__main__":verify()
