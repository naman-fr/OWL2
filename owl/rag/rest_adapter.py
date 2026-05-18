import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RestRAGAdapter:
    """REST client for querying an external Knowledge Base or Vector DB."""
    
    def __init__(self, endpoint_url: str, api_key: Optional[str] = None):
        self.endpoint_url = endpoint_url
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def query(self, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        """Query the RAG service via REST."""
        payload = {"query": query_text, "top_k": top_k}
        try:
            response = self.session.post(f"{self.endpoint_url}/search", json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"REST RAG query failed: {e}")
            return {"error": str(e), "results": []}
