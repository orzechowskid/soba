"""AI-SDLC Framework MCP Server"""
import logging
import asyncio
import json
import traceback
import sys
import signal
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, PromptMessage, Tool, Prompt, PromptArgument

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-sdlc-mcp")
logger.setLevel(logging.DEBUG)

# Add file handler for debug logging (overwrites on each startup)
_file_handler = logging.FileHandler("/home/dan/repos/sdlc/mcp-server/debug.log", mode="w")
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(_file_handler)

# Ensure logging never silently drops
logging.raiseExceptions = False

def _global_excepthook(exc_type, exc_value, exc_tb):
    logger.critical(
        "UNCAUGHT EXCEPTION (sys.excepthook): %s: %s\n%s",
        exc_type.__name__,
        exc_value,
        "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
    )
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = _global_excepthook

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def _async_exception_handler(loop, context):
    exc = context.get("exception")
    if isinstance(exc, BaseException):
        logger.critical(
            "UNCAUGHT ASYNC EXCEPTION: %s: %s\n%s",
            type(exc).__name__,
            exc,
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        )
    else:
        logger.critical("ASYNC LOOP CONTEXT: %s", context)
    loop.default_exception_handler(context)

# Server instance
app = Server("ai-sdlc-framework")

# Prompt handlers
PHASE_MAP = {
    "requirements": "03-phase-requirements.md",
    "design": "04-phase-design.md",
    "implementation": "05-phase-implementation.md",
    "review": "06-phase-review.md",
    "testing": "07-phase-testing.md",
    "deployment": "08-phase-deployment.md",
    "monitoring": "09-phase-monitoring.md",
}

VALID_PHASES = ("requirements", "design", "implementation", "review", "testing", "deployment", "monitoring")

@app.list_prompts()
async def list_prompts():
    logger.debug("list_prompts: entry")
    try:
        result = [
            Prompt(name="sdlc_bootstrap", description="Load Tier 1 documents (bootstrap + lifecycle overview) as session context", arguments=[]),
            Prompt(name="sdlc_phase", description="Load the relevant Tier 2 playbook for a given phase", arguments=[PromptArgument(name="phase_name", description="Phase name (e.g., implementation)", required=True)]),
            Prompt(name="sdlc_resume", description="Restore context after loss/compaction: loads Tier 1 + current phase playbook + pipeline state", arguments=[PromptArgument(name="project_path", description="Absolute path to project root", required=True)]),
        ]
        logger.debug(f"list_prompts: returning {len(result)} prompts")
        return result
    except Exception:
        logger.exception("list_prompts: exception")
        raise

@app.get_prompt()
async def get_prompt(name, arguments=None):
    logger.debug(f"get_prompt: entry, name={name}, argument_keys={list((arguments or {}).keys())}")
    try:
        arguments = arguments or {}
        
        if name == "sdlc_bootstrap":
            messages = []
            for doc in ["00-bootstrap.md", "01-lifecycle-overview.md"]:
                path = DOCS_DIR / doc
                if path.is_file():
                    messages.append(PromptMessage(role="user", content=TextContent(type="text", text=path.read_text(encoding="utf-8"))))
            logger.debug(f"get_prompt: sdlc_bootstrap returning {len(messages)} messages")
            return {"messages": messages}
        
        elif name == "sdlc_phase":
            phase = arguments.get("phase_name", "")
            doc = PHASE_MAP.get(phase)
            if not doc:
                result = {"messages": [PromptMessage(role="user", content=TextContent(type="text", text=f"Unknown phase: {phase}. Valid: {', '.join(PHASE_MAP.keys())}"))]}
                logger.debug(f"get_prompt: sdlc_phase unknown phase, {len(result['messages'])} messages")
                return result
            path = DOCS_DIR / doc
            if not path.is_file():
                result = {"messages": [PromptMessage(role="user", content=TextContent(type="text", text=f"Document not found: {doc}"))]}
                logger.debug(f"get_prompt: sdlc_phase doc missing, {len(result['messages'])} messages")
                return result
            result = {"messages": [PromptMessage(role="user", content=TextContent(type="text", text=path.read_text(encoding="utf-8")))]}
            logger.debug(f"get_prompt: sdlc_phase returning {len(result['messages'])} messages")
            return result
        
        elif name == "sdlc_resume":
            messages = []
            # Load Tier 1
            for doc in ["00-bootstrap.md", "01-lifecycle-overview.md"]:
                path = DOCS_DIR / doc
                if path.is_file():
                    messages.append(PromptMessage(role="user", content=TextContent(type="text", text=path.read_text(encoding="utf-8"))))
            # Load pipeline state
            project_path = Path(arguments.get("project_path", ""))
            state_file = project_path / "sdlc-state.json"
            state_text = "No state file found."
            if state_file.is_file():
                try:
                    state = json.loads(state_file.read_text(encoding="utf-8"))
                    state_text = json.dumps(state, indent=2)
                    current_phase = state.get("current_phase", "requirements")
                except json.JSONDecodeError:
                    current_phase = "requirements"
            else:
                # Infer phase
                current_phase = "requirements"
                if (project_path / "docs/adr").exists(): current_phase = "design"
                if (project_path / "docs/implementation").exists(): current_phase = "implementation"
                if (project_path / "docs/review").exists(): current_phase = "review"
                if (project_path / "docs/deploy").exists(): current_phase = "deployment"
                if (project_path / "docs/monitoring").exists(): current_phase = "monitoring"
            
            messages.append(PromptMessage(role="user", content=TextContent(type="text", text=f"Current Pipeline State:\n{state_text}\n\nLoading playbook for phase: {current_phase}")))
            # Load phase playbook
            doc = PHASE_MAP.get(current_phase)
            if doc:
                path = DOCS_DIR / doc
                if path.is_file():
                    messages.append(PromptMessage(role="user", content=TextContent(type="text", text=path.read_text(encoding="utf-8"))))
            logger.debug(f"get_prompt: sdlc_resume returning {len(messages)} messages")
            return {"messages": messages}
        
        logger.debug("get_prompt: unknown prompt name, returning empty")
        return {"messages": []}
    except Exception:
        logger.exception(f"get_prompt: exception for name={name}")
        raise

# Document source directory (parent of mcp-server/)
DOCS_DIR = Path(__file__).parent.parent

@app.list_tools()
async def list_tools():
    logger.debug("list_tools: entry")
    try:
        result = [
            Tool(name="list_documents", description="List available AI-SDLC documents with tier and purpose", inputSchema={"type": "object", "properties": {}, "required": []}),
            Tool(name="get_document", description="Retrieve a specific AI-SDLC document by filename", inputSchema={"type": "object", "properties": {"doc_name": {"type": "string", "description": "Document filename (e.g., '00-bootstrap.md')"}}, "required": ["doc_name"]}),
            Tool(name="get_pipeline_state", description="Read project pipeline state from sdlc-state.json. Requires project_path parameter.", inputSchema={"type": "object", "properties": {"project_path": {"type": "string", "description": "Absolute path to the project root"}}, "required": ["project_path"]}),
            Tool(name="set_pipeline_state", description="Update the project pipeline state in sdlc-state.json. Provide project_path and any fields to update (current_phase, feature, last_gate). Unprovided fields are preserved from existing state.", inputSchema={"type": "object", "properties": {"project_path": {"type": "string", "description": "Absolute path to project root"}, "current_phase": {"type": "string", "enum": list(VALID_PHASES), "description": "Phase name"}, "feature": {"type": "string", "description": "Feature name"}, "last_gate": {"type": "string", "description": "Gate that was just passed"}}, "required": ["project_path"]}),
            Tool(name="begin_sdlc", description="Initialize a new SDLC pipeline for a project. Creates sdlc-state.json starting at the requirements phase. Fails if a state file already exists.", inputSchema={"type": "object", "properties": {"project_path": {"type": "string", "description": "Absolute path to project root"}, "feature": {"type": "string", "description": "Feature name"}}, "required": ["project_path", "feature"]}),
        ]
        logger.debug(f"list_tools: returning {len(result)} tools")
        return result
    except Exception:
        logger.exception("list_tools: exception")
        raise

@app.call_tool()
async def call_tool(name, args):
    logger.debug(f"call_tool: entry, name={name}, arg_keys={list((args or {}).keys())}")
    try:
        if name == "list_documents":
            docs = []
            for f in sorted(DOCS_DIR.glob("*.md")):
                if f.name == "README.md":
                    continue
                docs.append(f"- {f.name}")
            result = [TextContent(type="text", text="\n".join(docs))]
            logger.debug(f"call_tool: list_documents returning {len(result)} items, text length={len(result[0].text) if result else 0}")
            return result
        elif name == "get_document":
            doc_name = args.get("doc_name", "")
            # Prevent path traversal
            if not doc_name or ".." in doc_name or "/" in doc_name or "\\" in doc_name:
                result = [TextContent(type="text", text="Error: Invalid document name.")]
                logger.debug(f"call_tool: get_document invalid name, {len(result)} items")
                return result
            doc_path = DOCS_DIR / doc_name
            if not doc_path.is_file():
                result = [TextContent(type="text", text=f"Error: Document not found: {doc_name}")]
                logger.debug(f"call_tool: get_document not found, {len(result)} items")
                return result
            text = doc_path.read_text(encoding="utf-8")
            result = [TextContent(type="text", text=text)]
            logger.debug(f"call_tool: get_document returning {len(result)} items, text length={len(result[0].text)}")
            return result
        elif name == "get_pipeline_state":
            project_path = Path(args.get("project_path", ""))
            state_file = project_path / "sdlc-state.json"
            if state_file.is_file():
                try:
                    state = json.loads(state_file.read_text(encoding="utf-8"))
                    text = json.dumps(state, indent=2)
                    result = [TextContent(type="text", text=text)]
                    logger.debug(f"call_tool: get_pipeline_state returning {len(result)} items, text length={len(result[0].text)}")
                    return result
                except json.JSONDecodeError:
                    result = [TextContent(type="text", text="Error: Invalid sdlc-state.json format.")]
                    logger.debug(f"call_tool: get_pipeline_state invalid json, {len(result)} items")
                    return result
            # Infer state from docs/ directories
            inferred = {"current_phase": "requirements", "feature": "unknown", "last_gate": "none"}
            if (project_path / "docs/adr").exists():
                inferred["current_phase"] = "design"
                inferred["last_gate"] = "requirements"
            if (project_path / "docs/implementation").exists():
                inferred["current_phase"] = "implementation"
                inferred["last_gate"] = "design"
            if (project_path / "docs/review").exists():
                inferred["current_phase"] = "review"
                inferred["last_gate"] = "implementation"
            if (project_path / "docs/deploy").exists():
                inferred["current_phase"] = "deployment"
                inferred["last_gate"] = "review"
            if (project_path / "docs/monitoring").exists():
                inferred["current_phase"] = "monitoring"
                inferred["last_gate"] = "deployment"
            text = json.dumps(inferred, indent=2)
            result = [TextContent(type="text", text=text)]
            logger.debug(f"call_tool: get_pipeline_state inferred returning {len(result)} items, text length={len(result[0].text)}")
            return result
        elif name == "set_pipeline_state":
            project_path = Path(args.get("project_path", ""))
            if not project_path.is_absolute():
                result = [TextContent(type="text", text="Error: project_path must be an absolute path.")]
                logger.debug(f"call_tool: set_pipeline_state invalid path, {len(result)} items")
                return result
            state_file = project_path / "sdlc-state.json"
            # Load existing state or defaults
            if state_file.is_file():
                try:
                    state = json.loads(state_file.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    state = {}
            else:
                state = {"current_phase": "requirements", "feature": "unknown", "last_gate": "none"}
            # Merge provided fields
            for field in ("current_phase", "feature", "last_gate"):
                if field in args:
                    value = args[field]
                    if field == "current_phase" and value not in VALID_PHASES:
                        result = [TextContent(type="text", text=f"Error: Invalid phase '{value}'. Valid: {', '.join(VALID_PHASES)}")]
                        logger.debug(f"call_tool: set_pipeline_state invalid phase, {len(result)} items")
                        return result
                    state[field] = value
            state["timestamp"] = __import__("datetime").datetime.now().isoformat()
            state_file.parent.mkdir(parents=True, exist_ok=True)
            state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
            text = json.dumps(state, indent=2)
            result = [TextContent(type="text", text=text)]
            logger.debug(f"call_tool: set_pipeline_state wrote state, text length={len(result[0].text)}")
            return result

        elif name == "begin_sdlc":
            project_path = Path(args.get("project_path", ""))
            if not project_path.is_absolute():
                result = [TextContent(type="text", text="Error: project_path must be an absolute path.")]
                logger.debug(f"call_tool: begin_sdlc invalid path, {len(result)} items")
                return result
            feature = args.get("feature", "")
            if not feature:
                result = [TextContent(type="text", text="Error: feature parameter is required.")]
                logger.debug(f"call_tool: begin_sdlc missing feature, {len(result)} items")
                return result
            state_file = project_path / "sdlc-state.json"
            if state_file.is_file():
                existing = json.loads(state_file.read_text(encoding="utf-8"))
                result = [TextContent(type="text", text=f"Error: State file already exists for this project.\nCurrent state:\n{json.dumps(existing, indent=2)}\n\nTo update, use set_pipeline_state instead.")]
                logger.debug(f"call_tool: begin_sdlc state exists, {len(result)} items")
                return result
            import datetime
            state = {"current_phase": "requirements", "feature": feature, "last_gate": "none", "timestamp": datetime.datetime.now().isoformat()}
            state_file.parent.mkdir(parents=True, exist_ok=True)
            state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
            # Create docs directory
            (project_path / "docs").mkdir(parents=True, exist_ok=True)
            text = json.dumps(state, indent=2)
            result = [TextContent(type="text", text=text)]
            logger.debug(f"call_tool: begin_sdlc created state, text length={len(result[0].text)}")
            return result
        logger.debug(f"call_tool: unknown tool name '{name}', returning empty")
        return []
    except Exception:
        logger.exception(f"call_tool: exception for name={name}")
        raise

async def main():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(_async_exception_handler)
    logger.info("Starting AI-SDLC MCP Server...")
    logger.info(f"Server name: {app.name}")
    logger.info(f"Documents directory: {DOCS_DIR}")
    try:
        async with stdio_server() as (read_stream, write_stream):
            init_opts = app.create_initialization_options()
            logger.debug(f"Initialization options: {init_opts}")
            await app.run(read_stream, write_stream, init_opts)
    except Exception:
        logger.exception("main: unhandled exception during server run")
        raise

if __name__ == "__main__":
    asyncio.run(main())
