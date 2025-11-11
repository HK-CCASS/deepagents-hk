"""Command handlers for slash commands and bash execution."""

import subprocess
import time
from pathlib import Path

from .config import COLORS, HKEX_AGENT_ASCII, console
from .ui import TokenTracker, show_interactive_help


def handle_command(command: str, agent, token_tracker: TokenTracker) -> str | bool:
    """Handle slash commands. Returns 'exit' to exit, True if handled, False to pass to agent."""
    cmd = command.strip().lstrip("/")
    
    # Split command and arguments
    parts = cmd.split(None, 1)
    cmd_name = parts[0].lower()
    cmd_arg = parts[1] if len(parts) > 1 else None

    if cmd_name in ["quit", "exit", "q"]:
        return "exit"

    if cmd_name == "session":
        if cmd_arg:
            switch_session(cmd_arg)
        else:
            console.print("[yellow]Usage: /session <thread_id>[/yellow]")
            console.print("[dim]Tip: Use /sessions to see available sessions[/dim]")
        return True

    if cmd_name == "clear":
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

    if cmd_name == "help":
        show_interactive_help()
        return True

    if cmd_name == "tokens":
        token_tracker.display_session()
        return True

    if cmd_name == "history":
        show_conversation_history_direct(agent)
        return True

    if cmd_name == "sessions":
        show_all_sessions(agent)
        return True

    console.print()
    console.print(f"[yellow]Unknown command: /{cmd_name}[/yellow]")
    console.print("[dim]Type /help for available commands.[/dim]")
    console.print()
    return True

    return False


def show_conversation_history_direct(agent):
    """Display conversation history by directly querying database."""
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
        
        # Query database directly
        import sqlite3
        import pickle
        from pathlib import Path
        import os
        
        # Get current thread_id
        thread_id = os.environ.get("HKEX_CURRENT_THREAD_ID", "main")
        
        # Get agent directory to find database
        assistant_id = "default"
        agent_dir = Path.home() / ".hkex-agent" / assistant_id
        db_path = agent_dir / "checkpoints.db"
        
        if not db_path.exists():
            console.print("[yellow]No conversation history found yet.[/yellow]")
            console.print(f"[dim]Thread ID: {thread_id}[/dim]")
            console.print()
            return
        
        # Connect to database and query
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Query for this thread's checkpoints
        cursor.execute("""
            SELECT checkpoint_id, checkpoint, metadata
            FROM checkpoints
            WHERE thread_id = ?
            ORDER BY checkpoint_id DESC
            LIMIT 10
        """, (thread_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            console.print("[yellow]No conversation history found for current thread.[/yellow]")
            console.print(f"[dim]Thread ID: {thread_id}[/dim]")
            console.print()
            return
        
        console.print(f"[green]Found {len(rows)} recent checkpoints in current thread[/green]")
        console.print(f"[dim]Thread ID: {thread_id}[/dim]")
        console.print()
        
        # Display checkpoints
        for idx, (checkpoint_id, checkpoint_data, metadata) in enumerate(rows):
            try:
                # Deserialize checkpoint
                checkpoint = pickle.loads(checkpoint_data)
                
                # Extract messages
                channel_values = checkpoint.get("channel_values", {})
                messages = channel_values.get("messages", [])
                
                if not messages:
                    continue
                
                console.print(f"[bold]Checkpoint {idx + 1}[/bold] [dim](ID: {checkpoint_id[:8]}...)[/dim]")
                
                # Display last few messages
                recent_messages = messages[-3:] if len(messages) > 3 else messages
                for msg in recent_messages:
                    # Handle both dict and object messages
                    if hasattr(msg, 'type'):
                        role = msg.type
                        content = msg.content
                    elif isinstance(msg, dict):
                        role = msg.get("role", msg.get("type", "unknown"))
                        content = msg.get("content", str(msg))
                    else:
                        role = "unknown"
                        content = str(msg)
                    
                    # Truncate long messages
                    if len(str(content)) > 100:
                        content = str(content)[:100] + "..."
                    
                    # Color code by role
                    if role in ["user", "human"]:
                        console.print(f"  [cyan]👤 User:[/cyan] {content}")
                    elif role in ["assistant", "ai"]:
                        console.print(f"  [green]🤖 Assistant:[/green] {content}")
                    else:
                        console.print(f"  [{role}] {content}")
                
                console.print()
                
            except Exception as e:
                console.print(f"[dim]Checkpoint {idx + 1}: (could not parse)[/dim]")
                console.print()
        
        console.print("[dim]💡 Tip: Use /clear to start a new conversation thread[/dim]")
        console.print()
        
    except Exception as e:
        console.print(f"[red]Error reading history: {e}[/red]")
        import traceback
        traceback.print_exc()
        console.print()


def switch_session(thread_id: str):
    """Switch to a different conversation session."""
    console.print()
    console.print(f"[bold cyan]🔄 Switching to session: {thread_id}[/bold cyan]")
    console.print()
    
    try:
        import os
        from pathlib import Path
        import sqlite3
        
        # Get agent directory to find database
        assistant_id = "default"
        agent_dir = Path.home() / ".hkex-agent" / assistant_id
        db_path = agent_dir / "checkpoints.db"
        
        if not db_path.exists():
            console.print("[red]No sessions database found.[/red]")
            console.print()
            return
        
        # Check if thread exists
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = ?", (thread_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            console.print(f"[yellow]Session '{thread_id}' not found.[/yellow]")
            console.print("[dim]Use /sessions to see available sessions[/dim]")
            console.print()
            return
        
        # Set environment variable for next conversation
        os.environ["HKEX_CURRENT_THREAD_ID"] = thread_id
        
        console.print(f"[green]✓ Switched to session: {thread_id}[/green]")
        console.print(f"[dim]Found {count} checkpoints in this session[/dim]")
        console.print()
        console.print("[bold yellow]⚠️  Note:[/bold yellow] To load this session's conversation history,")
        console.print("please restart the program or the change will take effect from next message.")
        console.print()
        console.print("[dim]💡 Tip: Use /history to view session messages[/dim]")
        console.print()
        
    except Exception as e:
        console.print(f"[red]Error switching session: {e}[/red]")
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
