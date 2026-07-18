import os
import requests
import cloudscraper

class ExternalDB:
    """Client for the external Backend-as-a-Service database API."""

    def __init__(self, base_url=None, api_key=None):
        self.base_url = (base_url or "https://vkserver.vercel.app").rstrip("/")
        self.api_key = api_key or os.environ.get("VKSERVER_API_KEY", "ais_8f293b4a2e5c89d107a6f2b1d3e8a49c")
        self.scraper = cloudscraper.create_scraper()
        self._resolve_base_url()

    def _resolve_base_url(self):
        if not self.base_url:
            return
        try:
            if 'vercel.app' in self.base_url:
                resp = self.scraper.get(f"{self.base_url}/api/zrok", timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get('url'):
                        self.base_url = data['url'].rstrip('/')
                        print(f"Resolved middleman to real backend: {self.base_url}")
        except Exception as e:
            print(f"Could not resolve middleman URL: {e}")

    @classmethod
    def from_config(cls):
        return cls(
            base_url=os.environ.get("EXTERNAL_DB_URL"),
            api_key=os.environ.get("EXTERNAL_DB_API_KEY"),
        )

    def is_configured(self):
        return bool(self.base_url) and bool(self.api_key)

    def _headers(self):
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

    def _request(self, method, path, json_body=None):
        if not self.is_configured():
            return {"success": False, "error": "External DB is not configured"}

        url = f"{self.base_url}{path}"
        try:
            resp = self.scraper.request(
                method,
                url,
                headers=self._headers(),
                json=json_body,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json() if resp.content else {}
            return {"success": True, "data": data, "status_code": resp.status_code}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Could not connect to external DB"}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "External DB request timed out"}
        except requests.exceptions.HTTPError as e:
            error_body = None
            try:
                error_body = e.response.json()
            except Exception:
                error_body = e.response.text
                if len(error_body) > 200:
                    error_body = error_body[:200] + "..."
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "details": error_body,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # CRUD methods
    def create_document(self, collection, data):
        return self._request("POST", f"/api/db/{collection}", json_body=data)

    def list_documents(self, collection):
        return self._request("GET", f"/api/db/{collection}")

    def get_document(self, collection, doc_id):
        return self._request("GET", f"/api/db/{collection}/{doc_id}")

    def update_document(self, collection, doc_id, data):
        return self._request("PUT", f"/api/db/{collection}/{doc_id}", json_body=data)

    def delete_document(self, collection, doc_id):
        return self._request("DELETE", f"/api/db/{collection}/{doc_id}")

external_db = ExternalDB.from_config()
