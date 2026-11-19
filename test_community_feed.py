"""Offline regression checks for community feed bridge and safe SEO page inputs."""
import base64
import json
import unittest

from community_page import validate
from fetch_community_feed import extract, ISSUE_TITLE


def feed():
    return {"schema":"gta6-community-feed-v1","generated_utc":"2026-11-19T08:00:00Z",
            "items":[{"source":"PowerPyx","tier":"specialist","title":"GTA VI leaked vehicle data",
                      "url":"https://powerpyx.com/gta-6-vehicles/",
                      "status":"🟠 RUMOR","published_utc":"2026-11-19T07:50:00Z",
                      "verified":False}]}


class BridgeTests(unittest.TestCase):
    def test_safe_unverified_inputs(self):
        self.assertEqual(len(validate(feed())),1)
        o=feed()
        o["items"][0]["verified"]=True
        with self.assertRaises(ValueError):validate(o)
        o=feed()
        o["items"][0]["url"]="https://powerpyx.com.attacker.example/gta6"
        with self.assertRaises(ValueError):validate(o)
        o=feed()
        o["items"][0]["status"]="🟢 UFFICIALE"
        with self.assertRaises(ValueError):validate(o)
        o=feed()
        o["items"][0]["source"]="Rockstar Games"
        with self.assertRaises(ValueError):validate(o)

    def test_single_public_issue_bridge_only(self):
        data=feed()
        encoded=base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
        issue={"title":ISSUE_TITLE,
               "body":"<!-- gta6-verified-source-feed-b64:"+encoded+" -->"}
        self.assertEqual(extract([issue]),data)
        self.assertIsNone(extract([{"title":"Other issue","body":issue["body"]}]))
        self.assertIsNone(extract([{**issue,"pull_request":{}}]))
        with self.assertRaises(ValueError):extract([{**issue,"body":"untrusted text"}])
        with self.assertRaises(ValueError):
            bad=feed()
            bad["items"][0]["verified"]=True
            encoded=base64.urlsafe_b64encode(json.dumps(bad).encode()).decode()
            extract([{"title":ISSUE_TITLE,
                     "body":"<!-- gta6-verified-source-feed-b64:"+encoded+" -->"}])

    def test_count_and_date_validation(self):
        data=feed()
        data["items"]*=26
        with self.assertRaises(ValueError):validate(data)
        data=feed()
        data["items"][0]["published_utc"]="yesterday"
        with self.assertRaises(ValueError):validate(data)
        data=feed()
        data["items"][0]["published_utc"]="2026-11-19"
        with self.assertRaises(ValueError):validate(data)

if __name__=="__main__":
    unittest.main()
