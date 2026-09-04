"""
Hackathon Demo Script — runs three scenarios showing the full agentic commerce flow.

Before running:
    1. python seed_catalog.py         (seed the database)
    2. python main.py dashboard       (start dashboard in another terminal)

Then run:
    python demo.py
"""

import asyncio
import logging
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich.text import Text

logging.basicConfig(level=logging.WARNING)  # Suppress verbose logs during demo

console = Console()
DASHBOARD_URL = "http://localhost:8000"

SCENARIOS = [
    {
        "title": "Scenario 1 — Successful Purchase",
        "description": "agent-buyer-01 (₹5k limit) buys a fast charger under ₹2,000",
        "request": "I need a good fast charger under 2000 rupees",
        "agent_id": "agent-buyer-01",
        "api_key": "key-buyer-01-secret",
        "expect": "success",
        "style": "green",
    },
    {
        "title": "Scenario 2 — Budget Breach (Policy Rejection)",
        "description": "agent-buyer-02 (₹2k limit) tries to buy ₹2,499 earbuds",
        "request": "Buy me the OnePlus Nord Buds 2 earbuds",
        "agent_id": "agent-buyer-02",
        "api_key": "key-buyer-02-secret",
        "expect": "rejected",
        "style": "red",
    },
    {
        "title": "Scenario 3 — Out of Stock (Policy Rejection)",
        "description": "agent-buyer-01 tries to buy the Samsung charger (stock = 0)",
        "request": "Buy the Samsung 45W Super Fast Charger",
        "agent_id": "agent-buyer-01",
        "api_key": "key-buyer-01-secret",
        "expect": "rejected",
        "style": "yellow",
    },
    {
        "title": "Scenario 4 — Bot-to-Bot Negotiation (Auto-Declined Upsell)",
        "description": "agent-buyer-02 (chargers ONLY) buys a charger. Merchant pitches a cable. Agent evaluates & declines due to category mandate.",
        "request": "Buy the Anker 65W charger",
        "agent_id": "agent-buyer-02",
        "api_key": "key-buyer-02-secret",
        "expect": "success_no_upsell",
        "style": "blue",
    },
]


async def run_scenario(scenario: dict) -> dict:
    from src.agent.buyer import run_buyer_agent

    console.print(Rule(f"  {scenario['title']}  ", style=scenario["style"]))
    console.print(f"[dim]  {scenario['description']}[/dim]\n")
    console.print(f"[bold white]  🧑 User:[/bold white]  \"{scenario['request']}\"")
    console.print(f"[bold white]  🤖 Agent:[/bold white] {scenario['agent_id']}\n")

    with console.status("[bold cyan]  Agent working...[/bold cyan]", spinner="dots"):
        final_state = await run_buyer_agent(
            user_request=scenario["request"],
            agent_id=scenario["agent_id"],
            api_key=scenario["api_key"]
        )

    # Show step-by-step agent messages
    console.print("[bold cyan]  ── Agent Steps ──[/bold cyan]")
    for msg in final_state.get("messages", []):
        content = getattr(msg, "content", "")
        if content and "✅" not in content and "❌" not in content:
            console.print(f"  [dim]{content}[/dim]")

    # Show final response in a panel
    response = final_state.get("final_response", "No response.")
    border = scenario["style"]
    console.print(Panel(
        response,
        title="Agent Response",
        border_style=border,
        padding=(1, 2),
    ))

    return final_state


async def show_audit_trail():
    console.print(Rule("  📋 Audit Trail  ", style="cyan"))

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{DASHBOARD_URL}/api/audit?limit=30")
            data = resp.json()
    except Exception:
        console.print(
            "[yellow]  ⚠ Dashboard not running — start it with: python main.py dashboard[/yellow]\n"
        )
        return

    entries = list(reversed(data.get("entries", [])))
    if not entries:
        console.print("  [dim]No audit entries yet.[/dim]")
        return

    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    table.add_column("Time",     style="dim",   width=19)
    table.add_column("Event",    width=26)
    table.add_column("Agent",    width=16)
    table.add_column("Amount",   justify="right", width=10)
    table.add_column("Decision", justify="center", width=10)

    for e in entries:
        event = e.get("event_type", "")

        if "APPROVED" in event or "SUCCESS" in event or "RESERVED" in event:
            event_styled = f"[green]{event}[/green]"
        elif "REJECTED" in event or "FAILED" in event or "RELEASED" in event:
            event_styled = f"[red]{event}[/red]"
        else:
            event_styled = f"[dim]{event}[/dim]"

        decision = ""
        if e.get("policy_decision") is True:
            decision = "[green]✅[/green]"
        elif e.get("policy_decision") is False:
            decision = "[red]❌[/red]"

        amount = f"₹{e['amount_inr']:,.0f}" if e.get("amount_inr") else "—"
        ts = (e.get("timestamp") or "")[:19].replace("T", " ")

        table.add_row(ts, event_styled, e.get("agent_id", ""), amount, decision)

    console.print(table)
    console.print(
        f"\n  [dim]Full trail: {DASHBOARD_URL}/api/audit[/dim]"
        f"\n  [dim]Live stream: {DASHBOARD_URL}/api/audit/stream[/dim]"
    )


async def main():
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Agentic Commerce — Hackathon Demo[/bold cyan]\n"
        "[dim]AI-native merchant infrastructure · MCP · LangGraph · Razorpay[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))
    console.print()

    for scenario in SCENARIOS:
        await run_scenario(scenario)
        console.print()
        await asyncio.sleep(1)  # Brief pause between scenarios

    await show_audit_trail()

    console.print()
    console.print(Panel.fit(
        "[bold green]Demo complete![/bold green]\n"
        f"[dim]Dashboard docs: {DASHBOARD_URL}/docs[/dim]",
        border_style="green",
    ))
    console.print()


if __name__ == "__main__":
    asyncio.run(main())