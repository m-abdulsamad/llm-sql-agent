import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack
import os
import requests
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic

import logging
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

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

    async def process_query(self, query: str) -> str:
        context = await self.get_context()

        sql_generation_prompt = f"""
            You are a database analyst that receives a prompt and creates a SQL SELECT statement and then
            executes it using the tools available

            ### Database Schema:

            {context}

            ### User Prompt:
            {query}

            ### Instructions:
            1. Analyze the user's prompt to determine what data they are requesting.
            2. Use the table schemas above to understand the relationships between tables, especially foreign keys.
            3. Use JOINs where appropriate (not everywhere) to connect tables using foreign key relationships.
            4. Include only relevant columns based on the user prompt.
            5. Execute the SQL SELECT statement

        """

        messages = [
            {
                "role": "user",
                "content": sql_generation_prompt
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []

        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                assistant_message_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def chat_loop(self) -> None:
        """Run an interactive chat loop"""
        print("\nYour very own Database Analyst!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                prompt = input("\nQuery: ").strip()

                if prompt.lower() == 'quit':
                    break

                # response = await self.process(prompt)
                response = await self.process_query(prompt)
                print("\nResponse: \n" + response)

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
