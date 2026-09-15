"""MCP server exposing the Site Intelligence API to LLM coding agents.

This is a distribution channel, not a new product: it is a thin stdio client
for the already-deployed RapidAPI listing. Each user supplies their own
RapidAPI key, so billing, rate limits and quota all stay on rails that
already exist — this package holds no credentials of its own and reaches no
service that the RapidAPI listing does not already expose publicly.
"""
import os
from importlib.metadata import PackageNotFoundError, version as _pkg_version
from typing import Any, Literal

import httpx
from mcp.server.mcpserver import MCPServer

RAPIDAPI_HOST = os.environ.get(
    "BEELOCATE_RAPIDAPI_HOST", "site-intelligence-api.p.rapidapi.com"
)
REQUEST_TIMEOUT_S = 60.0

try:
    __version__ = _pkg_version("site-intelligence-mcp")
except PackageNotFoundError:  # running from a source checkout
    __version__ = "0.0.0+dev"

mcp = MCPServer(
    name="site-intelligence",
    title="Site Intelligence",
    description=(
        "Score any coordinate for ecological and agricultural land suitability "
        "from satellite and climate data."
    ),
    website_url="https://rapidapi.com/bayrakdaralper/api/site-intelligence-api",
    version=__version__,
)


def _api_key() -> str:
    key = os.environ.get("RAPIDAPI_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "RAPIDAPI_KEY is not set. Get a key at "
            f"https://rapidapi.com/ and add it to this server's env block."
        )
    return key


def _summarize(payload: dict[str, Any]) -> dict[str, Any]:
    """Compact the full response to the fields an agent reasons over.

    The raw payload nests per-metric diagnostic sub-objects that can run to
    several KB. Tool results are spent directly from the model's context
    window, so the full response is opt-in via detail="full".
    """
    metrics = []
    for m in payload.get("metrics", []):
        if not isinstance(m, dict):
            continue
        metrics.append(
            {
                "key": m.get("key"),
                "score": m.get("score"),
                "label": m.get("label"),
            }
        )
    return {
        "score": payload.get("score"),
        "location": {
            "lat": payload.get("lat"),
            "lon": payload.get("lon"),
            "radius_m": payload.get("radius_m"),
        },
        "month": payload.get("month"),
        "metrics": metrics,
    }


@mcp.tool()
async def site_score(
    lat: float,
    lon: float,
    radius_m: int = 2000,
    month: int | None = None,
    detail: Literal["summary", "full"] = "summary",
) -> dict[str, Any]:
    """Score a geographic coordinate for ecological and agricultural land suitability.

    Analyses satellite and climate data for the area around a point and returns a
    weighted suitability score plus per-metric breakdown: vegetation health, water
    access, precipitation, terrain, cropland proximity, urbanisation pressure,
    climate, and distance to infrastructure.

    Use for site selection and land assessment — agtech, precision agriculture,
    ecological field research, conservation planning, environmental consulting,
    apiculture. Not a weather forecast and not a property-value estimate.

    Args:
        lat: Latitude, -90 to 90.
        lon: Longitude, -180 to 180.
        radius_m: Analysis radius in metres, 200 to 5000. Defaults to 2000.
        month: Month 1-12 to evaluate seasonally. Omit for an annual view.
        detail: "summary" returns scores only; "full" adds per-metric raw
            diagnostics, which is considerably larger.
    """
    params: dict[str, Any] = {"lat": lat, "lon": lon, "radius_m": radius_m}
    if month is not None:
        params["month"] = month

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/v1/site-score",
            params=params,
            headers={
                "X-RapidAPI-Key": _api_key(),
                "X-RapidAPI-Host": RAPIDAPI_HOST,
            },
        )

    if response.status_code == 429:
        raise RuntimeError(
            "Rate limit or quota reached. Check your RapidAPI plan, or retry later."
        )
    if response.status_code in (401, 403):
        raise RuntimeError("RapidAPI rejected the key. Verify RAPIDAPI_KEY and your subscription.")
    response.raise_for_status()

    payload = response.json()
    return payload if detail == "full" else _summarize(payload)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
