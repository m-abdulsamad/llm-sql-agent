import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack
import os
import requests
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import logging
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self) -> None:
        """Connect to an MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=["server.py"],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

    async def get_context(self) -> dict[str, any]:
        """Get context for the LLM"""
        try:
            # todo: get tools
            # todo: get prompts from server
                
            schemas = await self.session.read_resource("postgresql://tables/schemas")
            return self.format_schema(schemas.contents[0].text)
        
        except Exception as e:
            return f"Error getting database context: {e}"
    
    def format_schema(self, schema: str) -> str:
        lines = []
        dictionary = json.loads(schema)
        for key, value in dictionary.items():
            lines.append(f"Table: {key}") 
            lines.append("Columns:")
            for col in value["schema"]:
                col_line = f"  - {col['column_name']} ({col['data_type']}"
                if col['constraint_type']:
                    col_line += f", {col['constraint_type']}"
                if col['foreign_table']:
                    col_line += f", foreign key -> {col['foreign_table']}.{col['foreign_column']}"
                col_line += ")"
                lines.append(col_line)
            lines.append("")
        return "\n".join(lines)

    
    def call_llm(self, prompt: str) -> str:
        """ Call the LLM with the provided promot"""
        
        response = requests.post(
            f"{os.getenv("LLM_URL")}/api/generate",
            json= {
                "model": os.getenv("LLM_MODEL"),
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error calling LLAMA: {response.status_code}"
        
    
    async def process(self, prompt: str) -> dict[str, any]:
        #call LLM to generate SQL based on the user prompt

        context = await self.get_context()

        sql_generation_prompt = f"""
            You are a database analyst that generates valid SQL SELECT statements from user prompts.

            ### Database Schema:

            {context}

            ### User Prompt:
            {prompt}

            ### Instructions:
            1. Analyze the user's prompt to determine what data they are requesting.
            2. Use the table schemas above to understand the relationships between tables, especially foreign keys.
            3. Only output a valid SQL SELECT query (no explanations or extra text).
            4. Use JOINs where appropriate (not everywhere) to connect tables using foreign key relationships.
            5. Alias tables if needed for clarity.
            6. Include only relevant columns based on the user prompt.

        """
        
        generated_sql = self.call_llm(sql_generation_prompt)
        
        print("\n SQL:", generated_sql)

        if generated_sql.strip().upper().startswith('SELECT'):
            res = await self.session.call_tool("Execute SQL", {"sql": generated_sql})
            return ''.join(str(content.text) for content in res.content)
        else:
            await self.process(prompt)


    async def chat_loop(self) -> None:
        """Run an interactive chat loop"""
        print("\nYour very own Database Analyst!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                prompt = input("\nQuery: ").strip()

                if prompt.lower() == 'quit':
                    break

                response = await self.process(prompt)
                print("\nResponse: " + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

    
async def main():

    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
