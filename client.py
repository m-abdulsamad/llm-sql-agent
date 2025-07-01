import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack
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

    def format_resources(self, resources: list) -> str:
        """Formats a list of resource objects into a readable string."""
        lines = ["Here are the available data resources:"]
        for res in resources:
            lines.append(f"- URI: {res.uri}")
            if res.description:
                lines.append(f"  Description: {res.description}")
        return "\n".join(lines)

    def format_table_list(self, table_list_str: str) -> str:
        """Formats a JSON string of a table list into a readable string."""
        data = json.loads(table_list_str)
        tables = data.get("tables", [])
        if not tables:
            return "No tables found."
        return f"The following tables are available in the database: {', '.join(tables)}."

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
        # 1. List all available resources from the server
        resources_response = await self.session.list_resources()
        available_resources = self.format_resources(resources_response.resources)

        # 2. Ask the LLM to choose the best resource for the query
        resource_selection_prompt = f"""
You are an expert at selecting the correct data source to answer a user's query.
Based on the user's request, choose the single most appropriate resource from the list below.

{available_resources}

### User Prompt:
{query}

### Instructions:
- Analyze the user's prompt and the resource descriptions.
- Respond with ONLY the URI of the best resource to use. Never include any other text or explanation.
"""
        
        resource_selection_message = self.anthropic.messages.create(
            model="claude-3-7-sonnet-latest",
            max_tokens=200,
            messages=[{"role": "user", "content": resource_selection_prompt}],
        )
        
        chosen_resource_uri = resource_selection_message.content[0].text.strip()
        print(f"\n[LLM chose resource: {chosen_resource_uri}]")

        # 3. Fetch the data from the chosen resource and format it appropriately
        try:
            resource_data = await self.session.read_resource(chosen_resource_uri)
            raw_content = resource_data.contents[0].text

            if "/schemas" in chosen_resource_uri or "/schema" in chosen_resource_uri:
                context = self.format_schema(raw_content)
                context_title = "Database Schema"
            elif "/tables" in chosen_resource_uri:
                context = self.format_table_list(raw_content)
                context_title = "Available Tables"
            else:
                context = raw_content
                context_title = "Data"
                
        except Exception as e:
            return f"Error fetching or formatting chosen resource '{chosen_resource_uri}': {e}"

        # 4. Now, with the context, proceed with the tool-use conversation
        tool_use_prompt = f"""
You are a database analyst. Your goal is to answer the user's prompt by generating and executing a SQL SELECT statement using the available tools.

### {context_title}:
(This data was retrieved from the resource '{chosen_resource_uri}')
{context}

### User Prompt:
{query}

### Instructions:
1. Analyze the user's prompt and the provided database schema to determine what data they are requesting.
2. Formulate a SQL SELECT query to answer the prompt.
3. Use JOINs where appropriate (not everywhere) to connect tables using foreign key relationships
4. Include relevant columns based on the user prompt.
5. Use the available tools to execute the SQL SELECT query.
6. Based on the result of the tool, provide a final, natural-language answer to the user.
"""
        
        messages = [
            {
                "role": "user",
                "content": tool_use_prompt
            }
        ]

        tools_response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in tools_response.tools]

        # Initial Claude API call for tool use
        response = self.anthropic.messages.create(
            model="claude-3-7-sonnet-latest",
            max_tokens=1024,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []
        
        # Loop as long as the model wants to use tools
        while response.stop_reason == "tool_use":
            # First, add the assistant's `tool_use` request to the history.
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results_content = []
            text_content_from_turn = []

            for content in response.content:
                if content.type == 'text':
                    text_content_from_turn.append(content.text)
                elif content.type == 'tool_use':
                    tool_name = content.name
                    tool_args = content.input
                    tool_use_id = content.id

                    # Execute tool call
                    final_text.append(f"\n[Calling tool `{tool_name}` with args: {tool_args}]")
                    result = await self.session.call_tool(tool_name, tool_args)
                    
                    tool_output_string = ""
                    if result.content and hasattr(result.content[0], 'text'):
                        tool_output_string = result.content[0].text
                    
                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_output_string
                    })

            if text_content_from_turn:
                final_text.extend(text_content_from_turn)

            # Add the user message containing all tool results
            messages.append({
                "role": "user",
                "content": tool_results_content
            })

            # Get next response from Claude
            response = self.anthropic.messages.create(
                model="claude-3-7-sonnet-latest",
                max_tokens=1024,
                messages=messages,
                tools=available_tools
            )
        
        # The loop has finished. The final response is just text.
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)

        return "\n".join(final_text)

    async def chat_loop(self) -> None:
        """Run an interactive chat loop"""
        print("\nYour very own Database Analyst!")
        print("Type your queries or 'quit' or 'q' to exit.")

        while True:
            try:
                prompt = input("\nQuery: ").strip()

                if prompt.lower() == 'quit' or prompt.lower() == 'q':
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