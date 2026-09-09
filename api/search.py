
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse
import urllib.request
import xml.etree.ElementTree as ET


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Configuration des en-têtes CORS
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()

        # Récupération de la question (paramètre ?q=...)
        query_params = parse_qs(urlparse(self.path).query)
        q = query_params.get("q", [""])[0]

        snippets = []

        if q:
            # 1. Recherche directe Google Actualités (extrêmement frais pour le sport et l'actualité)
            try:
                gnews_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=fr&gl=FR&ceid=FR:fr"
                req = urllib.request.Request(
                    gnews_url, headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=4) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)
                    for item in root.findall(".//item")[:4]:
                        title = item.find("title").text if item.find("title") is not None else ""
                        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                        if title:
                            snippets.append(f"• [Actualité récente ({pub_date})] : {title}")
            except Exception:
                pass

            # 2. Recherche Web générale via DuckDuckGo
            if len(snippets) < 2:
                try:
                    from duckduckgo_search import DDGS

                    with DDGS() as ddgs:
                        for r in ddgs.text(q, max_results=3):
                            snippets.append(f"• {r.get('title')} : {r.get('body')}")
                except Exception:
                    pass

        result_text = "\n\n".join(snippets) if snippets else ""
        response_payload = json.dumps(
            {"results": result_text}, ensure_ascii=False
        )
        self.wfile.write(response_payload.encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
