"""Safe source-scoped community map permalinks; no fabricated GTA VI GPS."""
import json
from pathlib import Path
from copy import deepcopy
import unittest
from interactive_article_maps_v1 import (
    validate_curated_external_refs,external_refs_for,render,render_curated_refs,
    trophy_points,EXTERNAL_ALLOWED
)
from collectible_routes_v4 import render as render_collectibles
from visual_guide_content import enrich

ROOT=Path("_site")


def fixtures():
    rd=lambda x:json.loads(Path(x).read_text(encoding="utf-8"))
    guides=enrich(rd("data/guide.json")["guides"]+rd("data/visual_guides.json")["guides"])
    return guides,rd("data/trofei.json")["trophies"],rd("data/collectible_routes_v4.json"),rd("data/map_external_permalinks_v1.json")


class CommunityMapPermalinkTests(unittest.TestCase):
    def test_indexed_links_only_exact_community_place_not_item(self):
        guides,trophies,items,refs=fixtures()
        audit=validate_curated_external_refs(refs,guides,trophies,items)
        self.assertEqual(audit["external_map_references_reviewed"],7)
        self.assertEqual(audit["external_community_building_markers"],1)
        self.assertEqual(audit["external_community_region_links"],3)
        self.assertEqual(audit["external_location_detail_links"],3)
        self.assertEqual(audit["exact_gameplay_coordinate_pairs_verified"],0)
        self.assertEqual(audit["individual_collectible_pins_verified"],0)
        self.assertEqual(audit["external_link_verification"],"indexed_public_source_not_in_game_or_live_api")
        self.assertEqual({r["id"] for r in refs["items"]},set(EXTERNAL_ALLOWED))
        self.assertEqual(len(external_refs_for(refs,guide="meditazione-capitolo-1")),1)
        self.assertEqual(len(external_refs_for(refs,guide="soldi-facili-capitolo-1")),2)
        self.assertEqual(len(external_refs_for(refs,trophy=28)),1)
        self.assertEqual(len(external_refs_for(refs,trophy=3)),0) # a story trophy, not meditation
        self.assertIn("Jason’s House",trophy_points(28,{"group":"altro"},items)[0]["name"])
        self.assertEqual(trophy_points(3,{"group":"storia"},items),[])
        region=external_refs_for(refs,checkpoints={"pt-122"})
        self.assertEqual([x["id"] for x in region],["belpoint-area"])
        self.assertEqual(region[0]["kind"],"community-region-permalink")
        self.assertEqual(len(external_refs_for(refs,guide="registrare-auto-personale")),1)
        self.assertIn("Hamlet",render_curated_refs(external_refs_for(refs,guide="soldi-facili-capitolo-1")))
        self.assertIn("Mitchel",render_curated_refs(external_refs_for(refs,guide="registrare-auto-personale")))
        matched=external_refs_for(refs,checkpoints={"pt-102","pt-88","pt-108"})
        self.assertEqual({r["id"] for r in matched},{"jasons-safehouse","permit-keys","starlet-motel"})
        self.assertIn("NON pin",render_curated_refs(matched))
        self.assertIn("https://gtamap.io/?m=jasons-safehouse",render_curated_refs(matched))
        self.assertNotIn("data-vim-lat",render_curated_refs(matched))

    def test_invalid_hosts_bogus_gps_and_wrong_links_rejected(self):
        guides,trophies,items,refs=fixtures()
        for bad in ("https://gtamap.io.evil.test/?m=jasons-safehouse",
                    "http://gtamap.io/?m=jasons-safehouse",
                    "https://gtamap.io/?m=unknown"):
            altered=deepcopy(refs);altered["items"][0]["url"]=bad
            with self.assertRaises(ValueError):
                validate_curated_external_refs(altered,guides,trophies,items)
        altered=deepcopy(refs);altered["items"][0]["trophy_numbers"]=[3_000]
        with self.assertRaises(ValueError):
            validate_curated_external_refs(altered,guides,trophies,items)
        altered=deepcopy(refs);altered["items"][1]["checkpoint_ids"]=["pt-nonexistent"]
        with self.assertRaises(ValueError):
            validate_curated_external_refs(altered,guides,trophies,items)
        altered=deepcopy(refs);altered["items"][0]["in_game_coordinate_verified"]=True
        with self.assertRaises(ValueError):
            validate_curated_external_refs(altered,guides,trophies,items)
        altered=deepcopy(refs);altered["items"].append(refs["items"][0])
        with self.assertRaises(ValueError):
            validate_curated_external_refs(altered,guides,trophies,items)

    def test_157_collectibles_keep_count_while_nine_receive_contextual_links(self):
        _,_,items,refs=fixtures()
        html=render_collectibles(items,refs["items"])
        self.assertEqual(html.count('data-cr-step='),157)
        self.assertEqual(html.count('data-cr-curated-link'),10)
        self.assertEqual(html.count('game-map-curated-link-open-intent'),10)
        self.assertIn("NON pin della posizione esatta",html)
        self.assertIn("https://gtamap.io/gta-6-map/starlet-motel/",html)
        self.assertIn('data-vim-map-search=',html)
        self.assertIn("157 checkpoint",html)
        self.assertIn("6/33",html)

    def test_public_build_has_map_panel_and_source_registry_links(self):
        public=ROOT/"map-rollout-v1.json"
        if not public.exists():self.skipTest("Build not created")
        audit=json.loads(public.read_text(encoding="utf-8"))
        self.assertEqual(audit["external_map_references_reviewed"],7)
        self.assertEqual(audit["exact_gameplay_coordinate_pairs_verified"],0)
        self.assertEqual(audit["individual_collectible_pins_verified"],0)
        for path in ("mappe-guide/","collezionabili/percorsi/",
                     "guide-e-tutorial/meditazione-capitolo-1/",
                     "guide-e-tutorial/soldi-facili-capitolo-1/",
                     "trofei/trofeo-28-mentalita-positiva/"):
            src=(ROOT/path/"index.html").read_text(encoding="utf-8")
            self.assertIn('data-vim-curated-link',src,path)
            self.assertIn("https://gtamap.io/",src,path)
        unrelated=(ROOT/"trofei/trofeo-03-paradiso-perduto/index.html").read_text(encoding="utf-8")
        self.assertNotIn("jasons-safehouse",unrelated)
        map_hub=(ROOT/"mappe-guide/index.html").read_text(encoding="utf-8")
        self.assertEqual(map_hub.count('data-vim-curated-link'),7)
        routes=(ROOT/"collezionabili/percorsi/index.html").read_text(encoding="utf-8")
        self.assertEqual(routes.count('data-cr-curated-link'),10)
        self.assertIn("https://gtamap.io/?m=belpoint",routes)



if __name__=="__main__":unittest.main()
