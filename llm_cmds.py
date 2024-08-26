import click
import llm
import subprocess

from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer

SYSTEM_PROMPT = """
Return only the command to be executed as a raw string, no string delimiters
wrapping it, no yapping, no markdown, no fenced code blocks, what you return
will be passed to subprocess.check_output() directly.

For example, if the user asks: undo last git commit

You return only: git reset --soft HEAD~1
""".strip()

@llm.hookimpl
def register_commands(cli):
    @cli.command()
    @click.argument("args", nargs=-1)
    @click.option("-m", "--model", default=None, help="Specify the model to use")
    @click.option("-s", "--system", help="Custom system prompt")
    @click.option("--key", help="API key to use")
    def cmd(args, model, system, key):
        """Generate and execute commands in your shell"""
        from llm.cli import get_default_model

        print("Debug: Entering cmd function")  # Debug print
        prompt = " ".join(args)
        print(f"Debug: Prompt: {prompt}")  # Debug print

        model_id = model or get_default_model()
        print(f"Debug: Model ID: {model_id}")  # Debug print

        try:
            model_obj = llm.get_model(model_id)
            print(f"Debug: Model object: {model_obj}")  # Debug print
            if model_obj.needs_key:
                model_obj.key = llm.get_key(key, model_obj.needs_key, model_obj.key_env_var)
            
            result = model_obj.prompt(prompt, system=system or SYSTEM_PROMPT)
            print(f"Debug: Result from model: {result}")  # Debug print

            interactive_exec(str(result))
        except Exception as e:
            print(f"Debug: Exception occurred in cmd function: {str(e)}")
            traceback.print_exc()
            sys.exit(1)
        print("Debug: Exiting cmd function")

def interactive_exec(command):
    print(f"Debug: Entering interactive_exec with command: {command}")  # Debug print
    if '\n' in command:
        print("Multiline command - Meta-Enter or Esc Enter to execute")
        edited_command = prompt("> ", default=command, lexer=PygmentsLexer(BashLexer), multiline=True)
    else:
        edited_command = prompt("> ", default=command, lexer=PygmentsLexer(BashLexer))
    try:
        print(f"Debug: Attempting to execute command: {edited_command}")
        output = subprocess.check_output(
            edited_command, shell=True, stderr=subprocess.STDOUT
        )
        print(output.decode())
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error (exit status {e.returncode}): {e.output.decode()}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
    print("Debug: Exiting interactive_exec")