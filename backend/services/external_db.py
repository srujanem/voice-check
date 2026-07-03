import os
import requests


class ExternalDB:
    """Client for the external Backend-as-a-Service database API."""

    def __init__(self, base_url=None, api_key=None):
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = api_key
        # If the URL is a Vercel middleman, resolve the real backend
        self._resolve_base_url()

    def _resolve_base_url(self):
        """If the server uses a Vercel middleman (e.g. vkserver.vercel.app),
        fetch the real zrok backend URL from /api/zrok."""
        if not self.base_url:
            return
        try:
            if 'vercel.app' in self.base_url:
                resp = requests.get(f"{self.base_url}/api/zrok", timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get('url'):
                        self.base_url = data['url'].rstrip('/')
                        print(f"Resolved middleman to real backend: {self.base_url}")
        except Exception as e:
            print(f"Could not resolve middleman URL: {e}")

    # ------------------------------------------------------------------
    # Factory / helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls):
        """Create an instance from environment variables."""
        return cls(
            base_url=os.environ.get("EXTERNAL_DB_URL"),
            api_key=os.environ.get("EXTERNAL_DB_API_KEY"),
        )

    def is_configured(self):
        """Return True when both base_url and api_key are set."""
        return bool(self.base_url) and bool(self.api_key)

    # ------------------------------------------------------------------
    # Internal request helper
    # ------------------------------------------------------------------

    def _headers(self):
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def _request(self, method, path, json_body=None):
        """Send a request and return a normalised dict response."""
        if not self.is_configured():
            return {"success": False, "error": "External DB is not configured"}

        url = f"{self.base_url}{path}"
        try:
            resp = requests.request(
                method,
                url,
                headers=self._headers(),
                json=json_body,
                timeout=30,
            )
            resp.raise_for_status()

            # Some endpoints may return empty bodies (e.g. 204 on delete)
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
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "details": error_body,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # CRUD methods
    # ------------------------------------------------------------------

    def create_document(self, collection, data):
        """POST /api/db/{collection}"""
        return self._request("POST", f"/api/db/{collection}", json_body=data)

    def list_documents(self, collection):
        """GET /api/db/{collection}"""
        return self._request("GET", f"/api/db/{collection}")

    def get_document(self, collection, doc_id):
        """GET /api/db/{collection}/{id}"""
        return self._request("GET", f"/api/db/{collection}/{doc_id}")

    def update_document(self, collection, doc_id, data):
        """PUT /api/db/{collection}/{id}"""
        return self._request("PUT", f"/api/db/{collection}/{doc_id}", json_body=data)

    def delete_document(self, collection, doc_id):
        """DELETE /api/db/{collection}/{id}"""
        return self._request("DELETE", f"/api/db/{collection}/{doc_id}")


# Module-level singleton (mirrors ml_engine.py pattern)
external_db = ExternalDB.from_config()
