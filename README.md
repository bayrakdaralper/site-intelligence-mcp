# Site Intelligence MCP

<!-- mcp-name: io.github.bayrakdaralper/site-intelligence-mcp -->

Score any geographic coordinate for **ecological and agricultural land suitability**, directly from your AI coding agent.

Analyses satellite and climate data around a point and returns a weighted suitability score with a per-metric breakdown: vegetation health, water access, precipitation, terrain, cropland proximity, urbanisation pressure, climate, and distance to infrastructure.

Built for agtech, precision agriculture, ecological field research, conservation planning, environmental consulting and apiculture.

## Install

Requires a key for the [Site Intelligence API](https://rapidapi.com/bayrakdaralper/api/site-intelligence-api) on RapidAPI (free tier available).

### Claude Code

```bash
claude mcp add site-intelligence \
  --env RAPIDAPI_KEY=your_key_here \
  -- uvx site-intelligence-mcp
```

### Claude Desktop / Cursor / Windsurf

Add to your MCP config:

```json
{
  "mcpServers": {
    "site-intelligence": {
      "command": "uvx",
      "args": ["site-intelligence-mcp"],
      "env": {
        "RAPIDAPI_KEY": "your_key_here"
      }
    }
  }
}
```

## Usage

Ask your agent in plain language:

> How suitable is 38.42, 27.14 for an apiary? Check May specifically.

> Compare these three coordinates for a reforestation site and tell me which has the best water access.

## Tool

### `site_score`

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `lat` | float | required | -90 to 90 |
| `lon` | float | required | -180 to 180 |
| `radius_m` | int | `2000` | Analysis radius, 200-5000 |
| `month` | int | *(none)* | 1-12 for a seasonal view; omit for annual |
| `detail` | `"summary"` \| `"full"` | `"summary"` | `"full"` adds per-metric raw diagnostics |

`detail` defaults to `"summary"` deliberately: tool results are spent from the
model's context window, and the full diagnostic payload runs to several KB.
Ask for `"full"` only when you need the underlying values.

### Without `uv`

```bash
pip install site-intelligence-mcp
```

then use `site-intelligence-mcp` as the `command` with no `args`.

## Configuration

| Variable | Required | Default |
|---|---|---|
| `RAPIDAPI_KEY` | yes | — |
| `BEELOCATE_RAPIDAPI_HOST` | no | `site-intelligence-api.p.rapidapi.com` |

Get a key from the [Site Intelligence API listing](https://rapidapi.com/bayrakdaralper/api/site-intelligence-api).

## Limits

- Not a weather forecast and not a property-value estimate.
- Resolution is bounded by the underlying satellite sources; very small radii
  will not resolve individual parcels.
- Rate limits and quota follow your RapidAPI plan.

## Licence

MIT
