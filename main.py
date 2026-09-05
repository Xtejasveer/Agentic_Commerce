"""
Agentic Commerce — Main Entrypoint
Usage:
    # Start the merchant dashboard (FastAPI)
    python main.py dashboard
    # Run the MCP server in stdio mode (for agent integration)
    python main.py mcp
    # Seed the database and catalog
    python main.py seed
"""

import sys

def run_dashboard():
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    is_prod = os.environ.get("ENVIRONMENT", "development") == "production"
    print(f"Starting Merchant Dashboard on http://0.0.0.0:{port}")
    print(f"Audit trail:  http://0.0.0.0:{port}/api/audit")
    print(f"Live stream:  http://0.0.0.0:{port}/api/audit/stream")
    print(f"API docs:     http://0.0.0.0:{port}/docs\n")
    uvicorn.run(
        "src.dashboard.app:app",
        host = "0.0.0.0",
        port = port,
        reload = not is_prod,
    )

def run_mcp():
    from src.mcp_server import mcp
    print("Starting MCP server in stdio mode...")
    mcp.run(transport="stdio")

def run_seed():
    import subprocess
    subprocess.run([sys.executable, "seed_category.py"])

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) >1 else "dashboard"

    if command == "dashboard":
        run_dashboard()
    elif command == "mcp":
        run_mcp()
    elif command == "seed":
        run_seed()

    else: 
        print(f"Unknown command: {command}")
        print("Usage: python main.py [dashboard|mcp|seed]")
        sys.exit(1)
    