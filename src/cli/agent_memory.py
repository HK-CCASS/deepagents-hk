"""Middleware for loading agent-specific long-term memory into the system prompt."""

from collections.abc import Awaitable, Callable

from deepagents.backends.protocol import BackendProtocol
from prompts.prompts import get_longterm_memory_prompt
from langchain.agents.middleware.types import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)

AGENT_MEMORY_FILE_PATH = "/agent.md"

# Long-term Memory Documentation
LONGTERM_MEMORY_SYSTEM_PROMPT = get_longterm_memory_prompt()


DEFAULT_MEMORY_SNIPPET = """<agent_memory>
{agent_memory}
</agent_memory>
"""


class AgentMemoryMiddleware(AgentMiddleware):
    """Middleware for loading agent-specific long-term memory.

    This middleware loads the agent's long-term memory from a file (agent.md)
    and injects it into the system prompt. The memory is loaded once at the
    start of the conversation and stored in state.

    Args:
        backend: Backend to use for loading the agent memory file.
        memory_path: Path prefix for memory files (e.g., "/memories/").
    """

    def __init__(
        self,
        *,
        backend: BackendProtocol,
        memory_path: str,
        system_prompt_template: str | None = None,
    ) -> None:
        """Initialize the agent memory middleware.

        Args:
            backend: Backend to use for loading the agent memory file.
            memory_path: Path prefix for memory files.
            system_prompt_template: Optional custom template for injecting
                agent memory into system prompt.
        """
        self.backend = backend
        self.memory_path = memory_path
        self.system_prompt_template = system_prompt_template or DEFAULT_MEMORY_SNIPPET

    def before_agent(
        self,
        state: AgentState,
        runtime,
    ) -> AgentState:
        """Load agent memory from file before agent execution.

        Args:
            state: Current agent state.
            runtime: Runtime context.

        Returns:
            Updated state with agent_memory populated.
        """
        # Only load memory if it hasn't been loaded yet
        if "agent_memory" not in state or state.get("agent_memory") is None:
            try:
                file_data = self.backend.read(AGENT_MEMORY_FILE_PATH)
                return {"agent_memory": file_data or ""}
            except Exception:
                return {"agent_memory": ""}
        return state

    async def abefore_agent(
        self,
        state: AgentState,
        runtime,
    ) -> AgentState:
        """(async) Load agent memory from file before agent execution.

        Args:
            state: Current agent state.
            runtime: Runtime context.

        Returns:
            Updated state with agent_memory populated.
        """
        # Only load memory if it hasn't been loaded yet
        if "agent_memory" not in state or state.get("agent_memory") is None:
            try:
                file_data = self.backend.read(AGENT_MEMORY_FILE_PATH)
                return {"agent_memory": file_data or ""}
            except Exception:
                return {"agent_memory": ""}
        return state

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Inject agent memory into the system prompt.

        Args:
            request: The model request being processed.
            handler: The handler function to call with the modified request.

        Returns:
            The model response from the handler.
        """
        # Get agent memory from state
        agent_memory = request.state.get("agent_memory", "")

        memory_section = self.system_prompt_template.format(agent_memory=agent_memory)
        if request.system_prompt:
            request.system_prompt = memory_section + "\n\n" + request.system_prompt
        else:
            request.system_prompt = memory_section
        request.system_prompt = (
            request.system_prompt
            + "\n\n"
            + LONGTERM_MEMORY_SYSTEM_PROMPT.format(memory_path=self.memory_path)
        )

        return handler(request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        """(async) Inject agent memory into the system prompt.

        Args:
            request: The model request being processed.
            handler: The handler function to call with the modified request.

        Returns:
            The model response from the handler.
        """
        # Get agent memory from state
        agent_memory = request.state.get("agent_memory", "")

        memory_section = self.system_prompt_template.format(agent_memory=agent_memory)
        if request.system_prompt:
            request.system_prompt = memory_section + "\n\n" + request.system_prompt
        else:
            request.system_prompt = memory_section
        request.system_prompt = (
            request.system_prompt
            + "\n\n"
            + LONGTERM_MEMORY_SYSTEM_PROMPT.format(memory_path=self.memory_path)
        )

        return await handler(request)
