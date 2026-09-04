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
    import uvicorn
    print("Starting Merchant Dashboard on http://localhost:8000")
    print("Audit trail:  http://localhost:8000/api/audit")
    print("Live stream:  http://localhost:8000/api/audit/stream")
    print("API docs:     http://localhost:8000/docs\n")
    uvicorn.run(
        "src.dashboard.app:app",
        host = "0.0.0.0",
        port = 8000,
        reload = True,
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
    