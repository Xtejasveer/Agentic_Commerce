import asyncio
import sys
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_raw_client():
    print("Raw MCP Client Starting")

    server_params = StdioServerParameters(
        command = sys.executable,
        args = ["src/mcp_server.py"],
        env = {**os.environ, "PYTHONPATH" : os.getcwd()}
    )

    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected to the FastMCP server natively")

            print("\n Executing Tool: search_products (Query: 'power bank')")
            search_result = await session.call_tool("search_products", arguments = {"query" : "power bank"})
            search_response = json.loads(search_result.content[0].text)
            products_list = search_response.get("products", [])
            target_product = products_list[0]
            print(f"Found: {target_product['name']} (ID: {target_product['product_id']})")

            print("\n Executing Tool: execute_purchase (As agent-buyer-01)")
            try:
                purchase_result = await session.call_tool("execute_purchase", arguments={
                    "agent_id" : "agent-buyer-01",
                    "agent_api_key" : "key-buyer-01-secret",
                    "product_id" : target_product["product_id"],
                    "shipping_address" : "456 Raw Script Road, BLR",
                    "quantity" : 1,
                })
                print("\n Purchase Successful!")
                print("Response from server:", purchase_result.content[0].text)
            except Exception as e:
                print(f"Purchase Failed: {e}")

            print("\nCheck your dashboard - the Policy Engine logged this perfectly!")
if __name__ == "__main__":
    asyncio.run(run_raw_client())
