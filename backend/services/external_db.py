import os
import requests
import cloudscraper

class ExternalDB:
    """Client for the external Backend-as-a-Service database API."""

    def __init__(self, base_url=None, api_key=None):
        self.base_url = (base_url or "http://localhost:8000").rstrip("/")
        # Never hardcode API keys — use environment variable only
        self.api_key = api_key or os.environ.get("VKSERVER_API_KEY", "")
        self.scraper = cloudscraper.create_scraper()
        pass

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
