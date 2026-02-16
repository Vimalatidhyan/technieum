"""
ReconX API Server — compatibility shim.

The canonical server implementation is in backend/api/server.py.
This module re-exports that app and adds web-UI (static file) routes so that
the original launch command still works:

    uvicorn api.server:app --host 0.0.0.0 --port 8000

All API routes, authentication, rate limiting, and CSRF protection are
inherited from the canonical backend app.
"""

from pathlib import Path

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Re-export the canonical, fully-featured application.
from app.api.server import app  # noqa: F401

# ─── Static web-UI routes ───────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "web" / "static"
ASSETS_DIR = STATIC_DIR / "assets"


def _serve(filename: str):
    """Return a static HTML page, or a JSON fallback if the file is missing."""
    p = STATIC_DIR / filename
    if p.exists():
        return FileResponse(p, media_type="text/html")
    return {"message": "ReconX API", "docs": "/docs"}


@app.get("/", include_in_schema=False)
@app.get("/dashboard", include_in_schema=False)
async def page_dashboard():
    return _serve("index.html")


@app.get("/assessments", include_in_schema=False)
async def page_assessments():
    return _serve("scan_viewer_v2.html")


@app.get("/vulnerabilities", include_in_schema=False)
async def page_vulnerabilities():
    return _serve("findings_v2.html")


@app.get("/graph", include_in_schema=False)
async def page_graph():
    return _serve("graph_viewer_v2.html")


@app.get("/attack-surface", include_in_schema=False)
async def page_attack_surface():
    return _serve("attack_surface_v2.html")


@app.get("/reports", include_in_schema=False)
async def page_reports():
    return _serve("reports_v2.html")


@app.get("/compliance", include_in_schema=False)
async def page_compliance():
    return _serve("compliance_v2.html")


@app.get("/alerts", include_in_schema=False)
async def page_alerts():
    return _serve("alerts_v2.html")


@app.get("/settings", include_in_schema=False)
async def page_settings():
    return _serve("settings_v2.html")


@app.get("/threat-intel", include_in_schema=False)
async def page_threat_intel():
    return _serve("scan_viewer_v2.html")


# Legacy page routes
@app.get("/scan_viewer.html", include_in_schema=False)
async def legacy_scan_viewer():
    return _serve("scan_viewer.html")


@app.get("/findings.html", include_in_schema=False)
async def legacy_findings():
    return _serve("findings.html")


@app.get("/graph_viewer.html", include_in_schema=False)
async def legacy_graph_viewer():
    return _serve("graph_viewer.html")


# Static asset files (CSS, JS, images) — mount after explicit routes.
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
