"""MCP server that exposes Pinecone tools for pa-chat-bot."""

import json
import os
import urllib.request

from dotenv import load_dotenv
from mcp.server import MCPServer

mcp = MCPServer("arun-tools")

load_dotenv()
PINECONE_APP_BASE_URL = os.getenv(
    "PINECONE_APP_BASE_URL", "http://54.204.110.222/pineconeapp"
).rstrip("/")


def _get_json(path: str) -> dict:
    url = f"{PINECONE_APP_BASE_URL}{path}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def _post_json(path: str, payload: dict) -> dict:
    url = f"{PINECONE_APP_BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


@mcp.tool()
def list_namespaces() -> list[str]:
    """List available Pinecone namespaces from pinecone-app."""
    body = _get_json("/pinecone/retrievenamespace")
    return [str(name) for name in (body.get("namespaces") or [])]


@mcp.tool()
def retrieve_documents(question: str, namespace: str, top_k: int = 3) -> list[str]:
    """Retrieve relevant document chunks for a question from a Pinecone namespace."""
    body = _post_json(
        "/pinecone/retrievedoc",
        {"question": question, "namespace": namespace, "top_k": top_k},
    )
    return [str(text).strip() for text in (body.get("texts") or []) if str(text).strip()]


if __name__ == "__main__":
    # Streamable HTTP so pa-chat-bot can connect with Client(url)
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8004,
        transport_security=TransportSecuritySettings(
            allowed_hosts=[
                "127.0.0.1",
                "127.0.0.1:*",
                "localhost",
                "localhost:*",
                "54.204.110.222",
                "54.204.110.222:*"
            ]
        )
    )
