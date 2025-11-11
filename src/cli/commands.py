"""Command handlers for slash commands and bash execution."""

import subprocess
import time
from pathlib import Path

from .config import COLORS, HKEX_AGENT_ASCII, console
from .ui import TokenTracker, show_interactive_help


def handle_command(command: str, agent, token_tracker: TokenTracker) -> str | bool:
    """Handle slash commands. Returns 'exit' to exit, True if handled, False to pass to agent."""
    cmd = command.lower().strip().lstrip("/")

    if cmd in ["quit", "exit", "q"]:
        return "exit"

    if cmd == "clear":
        # Create a new thread_id for fresh conversation
        # Historical data is preserved in database and can be viewed with /history
        new_thread_id = f"main-{int(time.time())}"
        
        # Store new thread_id for use in next conversation
        # This will be picked up by execute_task()
        import os
        os.environ["HKEX_CURRENT_THREAD_ID"] = new_thread_id

        # Reset token tracking to baseline
        token_tracker.reset()

        # Clear screen and show fresh UI
        console.clear()
        # 如果是Text对象（彩虹模式），直接打印；否则应用primary颜色
        from rich.text import Text
        if isinstance(HKEX_AGENT_ASCII, Text):
            console.print(HKEX_AGENT_ASCII)
        else:
            console.print(HKEX_AGENT_ASCII, style=f"bold {COLORS['primary']}")
        console.print()
        console.print(
            "... Fresh start! New conversation started.", style=COLORS["agent"]
        )
        console.print(
            f"[dim]Context reset to baseline ({token_tracker.baseline_context:,} tokens)[/dim]"
        )
        console.print(
            "[dim]💡 Tip: Previous conversations are saved. Use /history to view them.[/dim]"
        )
        console.print()
        return True

    if cmd == "help":
        show_interactive_help()
        return True

    if cmd == "tokens":
        token_tracker.display_session()
        return True

    if cmd == "history":
        # Note: This is a simple synchronous implementation
        # Full async implementation would require refactoring the command handler
        show_conversation_history_sync(agent)
        return True

    if cmd == "sessions":
        show_all_sessions(agent)
        return True

    console.print()
    console.print(f"[yellow]Unknown command: /{cmd}[/yellow]")
    console.print("[dim]Type /help for available commands.[/dim]")
    console.print()
    return True

    return False


def show_conversation_history_sync(agent):
    """Display conversation history from checkpointer."""
    console.print()
    console.print("[bold cyan]📝 Conversation History[/bold cyan]")
    console.print()
    
    try:
        # Get the checkpointer
        checkpointer = agent.checkpointer
        if not checkpointer:
            console.print("[yellow]No conversation history available (checkpointer not configured)[/yellow]")
            console.print()
            return
        
        # Get current thread_id from environment or use default
        import os
        thread_id = os.environ.get("HKEX_CURRENT_THREAD_ID", "main")
        
        # Get state history for current thread
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Get state history (returns iterator of StateSnapshot objects)
            history = list(agent.get_state_history(config))
            
            if not history:
                console.print("[yellow]No conversation history found for current thread.[/yellow]")
                console.print(f"[dim]Thread ID: {thread_id}[/dim]")
                console.print()
                return
            
            console.print(f"[green]Found {len(history)} checkpoints in current thread[/green]")
            console.print(f"[dim]Thread ID: {thread_id}[/dim]")
            console.print()
            
            # Display history (most recent first)
            # Limit to last 10 checkpoints to avoid overwhelming output
            display_limit = 10
            for idx, state in enumerate(history[:display_limit]):
                # Extract messages from state
                messages = state.values.get("messages", [])
                
                if not messages:
                    continue
                
                console.print(f"[bold]Checkpoint {idx + 1}[/bold] [dim](ID: {state.config['configurable'].get('checkpoint_id', 'N/A')[:8]}...)[/dim]")
                
                # Display last few messages from this checkpoint
                recent_messages = messages[-3:] if len(messages) > 3 else messages
                for msg in recent_messages:
                    role = msg.get("role", getattr(msg, "type", "unknown"))
                    content = msg.get("content", str(msg))
                    
                    # Truncate long messages
                    if len(content) > 100:
                        content = content[:100] + "..."
                    
                    # Color code by role
                    if role in ["user", "human"]:
                        console.print(f"  [cyan]👤 User:[/cyan] {content}")
                    elif role in ["assistant", "ai"]:
                        console.print(f"  [green]🤖 Assistant:[/green] {content}")
                    else:
                        console.print(f"  [{role}] {content}")
                
                console.print()
            
            if len(history) > display_limit:
                console.print(f"[dim]... and {len(history) - display_limit} more checkpoints[/dim]")
                console.print(f"[dim]Showing most recent {display_limit} checkpoints[/dim]")
                console.print()
            
            console.print("[dim]💡 Tip: Use /clear to start a new conversation thread[/dim]")
            console.print()
            
        except Exception as e:
            console.print(f"[yellow]Could not retrieve history: {e}[/yellow]")
            console.print("[dim]History exists but may require async access[/dim]")
            console.print()
        
    except Exception as e:
        console.print(f"[red]Error reading history: {e}[/red]")
        import traceback
        traceback.print_exc()
        console.print()


def show_all_sessions(agent):
    """Display all conversation sessions/threads."""
    console.print()
    console.print("[bold cyan]📚 All Conversation Sessions[/bold cyan]")
    console.print()
    
    try:
        # Get the checkpointer
        checkpointer = agent.checkpointer
        if not checkpointer:
            console.print("[yellow]No sessions available (checkpointer not configured)[/yellow]")
            console.print()
            return
        
        # Query database directly to find all threads
        import sqlite3
        from pathlib import Path
        
        # Get agent directory to find database
        assistant_id = "default"  # Default value
        agent_dir = Path.home() / ".hkex-agent" / assistant_id
        db_path = agent_dir / "checkpoints.db"
        
        if not db_path.exists():
            console.print("[yellow]No sessions found yet.[/yellow]")
            console.print("[dim]Start a conversation to create a session.[/dim]")
            console.print()
            return
        
        # Connect to database and query for all threads
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Query to get distinct thread_ids and their checkpoint counts
        cursor.execute("""
            SELECT thread_id, COUNT(*) as checkpoint_count, MAX(checkpoint_id) as latest_checkpoint
            FROM checkpoints
            GROUP BY thread_id
            ORDER BY latest_checkpoint DESC
        """)
        
        threads = cursor.fetchall()
        conn.close()
        
        if not threads:
            console.print("[yellow]No sessions found.[/yellow]")
            console.print()
            return
        
        console.print(f"[green]Found {len(threads)} session(s)[/green]")
        console.print()
        
        # Get current thread_id
        import os
        current_thread = os.environ.get("HKEX_CURRENT_THREAD_ID", "main")
        
        # Display each session
        for thread_id, count, latest in threads:
            is_current = thread_id == current_thread
            marker = "→" if is_current else " "
            style = "bold green" if is_current else "dim"
            
            console.print(f"{marker} [bold]{thread_id}[/bold]", style=style)
            console.print(f"   {count} checkpoints", style=style)
            if is_current:
                console.print("   [green](current session)[/green]")
            console.print()
        
        console.print("[dim]💡 Tip: Use /clear to create a new session[/dim]")
        console.print("[dim]💡 Use /history to view current session's messages[/dim]")
        console.print()
        
    except Exception as e:
        console.print(f"[red]Error listing sessions: {e}[/red]")
        import traceback
        traceback.print_exc()
        console.print()


def execute_bash_command(command: str) -> bool:
    """Execute a bash command and display output. Returns True if handled."""
    cmd = command.strip().lstrip("!")

    if not cmd:
        return True

    try:
        console.print()
        console.print(f"[dim]$ {cmd}[/dim]")

        # Execute the command
        result = subprocess.run(
            cmd, check=False, shell=True, capture_output=True, text=True, timeout=30, cwd=Path.cwd()
        )

        # Display output
        if result.stdout:
            console.print(result.stdout, style=COLORS["dim"], markup=False)
        if result.stderr:
            console.print(result.stderr, style="red", markup=False)

        # Show return code if non-zero
        if result.returncode != 0:
            console.print(f"[dim]Exit code: {result.returncode}[/dim]")

        console.print()
        return True

    except subprocess.TimeoutExpired:
        console.print("[red]Command timed out after 30 seconds[/red]")
        console.print()
        return True
    except Exception as e:
        console.print(f"[red]Error executing command: {e}[/red]")
        console.print()
        return True
