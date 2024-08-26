import click
import llm
import subprocess
import json
import platform
import os
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from rich.live import Live
from rich.spinner import Spinner
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.styles import style_from_pygments_cls

def safe_get(func, default='N/A'):
    try:
        return func()
    except:
        return default

def get_system_info():
    return {
        'platform': safe_get(platform.platform),
        'version': safe_get(platform.version),
        'python_version': safe_get(platform.python_version),
        'shell': safe_get(lambda: os.environ.get('SHELL', 'Unknown')),
        'home_dir': safe_get(lambda: os.path.expanduser('~')),
        'current_dir': safe_get(os.getcwd)
    }

SYSTEM_PROMPT = """
You are a terminal command generator. Your task is to analyze context about the user's system as well as the user's request, briefly thinking through the steps required to fulfill the request and any assumptions made about it. Then, generate a command that will achieve the desired outcome.

Always provide both your thought processs and the final generated command in valid JSON format, separating your chain of thought reasoning from the command via two JSON keys: "thoughts" (will not be shown to the user) and "command" (contents will be passed to subprocess.check_output() directly). Ensure proper escaping of special characters, especially quotes. Use '\n' for multiline commands and whatnot.

If the request is ambiguous, make the safest assumption. If the command is likely to fail, dangerous, harmful, or unclear, include the command and/or an explanation via an echo command or similar.

Examples:

<example>
# User request: find all '.txt' files in the current directory
{
    "thoughts": "The user wants to find all files with the '.txt' extension in the current directory. The 'find' command is appropriate for searching, with '-name' to specify the file pattern.",
    "command": "find . -name \"*.txt\""
}
</example>

<example>
# User request: undo last git commit
{
    "thoughts": "The user wants to undo the last commit in their Git repository. The appropriate command for this is to use 'git reset' with the '--soft' flag to keep the changes staged, and 'HEAD~1' to target the last commit.",
    "command": "git reset --soft HEAD~1"
}
</example>

<example>
# User request: https://www.youtube.com/watch?v=mpW1wcHEMkA as wav
{
    "thoughts": "The user presumably wants to download media from YouTube in the wav format to the current active directory. The 'yt-dlp' command line utility is appropriate here. We must shorten the URL to its video ID and add '--extract-audio --audio-format wav' to download the best available source and convert it to the waveform format.",
    "command": "yt-dlp mpW1wcHEMkA --extract-audio --audio-format wav"
}
</example>
""".strip()

@llm.hookimpl
def register_commands(cli):
    @cli.command()
    @click.argument("args", nargs=-1)
    @click.option("-m", "--model", default=None, help="Specify the model to use")
    @click.option("-s", "--system", help="Custom system prompt")
    @click.option("--key", help="API key to use")
    @click.option("--think", is_flag=True, help="Show the LLM's thought process")
    @click.option("--context", is_flag=True, help="Show the context passed to the LLM")
    def cmds(args, model, system, key, think, context):
        """Generate and execute commands in your shell"""
        from llm.cli import get_default_model

        console = Console()
        user_prompt = " ".join(args)

        system_info = get_system_info()
        prompt_data = {
            "context": system_info,
            "request": {
                "user": user_prompt
            }
        }

        if context:
            context_str = "\n".join(f"[bold yellow]{k}[/bold yellow]: {v}" for k, v in system_info.items())
            console.print(Panel(context_str, title="Context", border_style="yellow", expand=False))

        model_id = model or get_default_model()

        model_obj = llm.get_model(model_id)
        if model_obj.needs_key:
            model_obj.key = llm.get_key(key, model_obj.needs_key, model_obj.key_env_var)

        with console.status("[bold green]Thinking...[/bold green]", spinner="dots") as status:
            result = model_obj.prompt(json.dumps(prompt_data), system=system or SYSTEM_PROMPT)

            try:
                parsed_result = json.loads(str(result))
                if think:
                    thoughts = parsed_result.get("thoughts", "No thoughts provided")
                command = parsed_result.get("command", "")
                if not command:
                    raise ValueError("No command provided in the LLM output")
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON output from LLM")

        if think:
            console.print(Panel(thoughts, title="Thoughts", border_style="cyan"))
        
        if command:
            interactive_exec(command)
        else:
            console.print("[bold red]Error:[/bold red] No command was generated.")


def interactive_exec(command):
    console = Console()

    pygments_style = style_from_pygments_cls(get_style_by_name('github-dark'))
    
    if '\n' in command:
        console.print("Multiline command - Meta-Enter or Esc Enter to execute")
        edited_command = prompt(
            [('class:prompt', "❯ ")],
            default=command,
            lexer=PygmentsLexer(BashLexer),
            multiline=True,
            style=pygments_style
        )
    else:
        edited_command = prompt(
            [('class:prompt', "❯ ")],
            default=command,
            lexer=PygmentsLexer(BashLexer),
            style=pygments_style
        )
    
    try:
        with Live(Spinner("dots", text="Executing..."), refresh_per_second=10) as live:
            process = subprocess.Popen(
                edited_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in process.stdout:
                live.stop()
                console.print(line, end='')
            
            process.wait()
        
        if process.returncode != 0:
            console.print(f"[bold red]Command failed with exit status {process.returncode}[/bold red]")
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")