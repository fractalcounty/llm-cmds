import click
import llm
import subprocess

from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer


SYSTEM_PROMPT = """
You are a terminal command generator. Your task is to analyze the user's request carefully in a very concise manner, thinking through the steps required to achieve the desired outcome and any assumptions you make about the request. Provide your thoughts and the final command to be executed in JSON format, separating the chain of reasoning from the command via two JSON keys: "thoughts" and "command". Thoughts will not be shown to the user. The command you return will be passed to subprocess.check_output() directly.

If the request is ambiguous, make the safest assumption. If the command is likely to fail, dangerous, harmful, or unclear, explain why in an echo command.

<example>
# User request: undo last git commit
{
    "thoughts": "The user wants to undo the last commit in their Git repository. The appropriate command for this is to use 'git reset' with the '--soft' flag to keep the changes staged, and 'HEAD~1' to target the last commit.",
    "command": "git reset --soft HEAD~1"
}
</example>

<example>
# User request: 'find all '.txt' files in the current directory'
{
    "thoughts": "The user wants to find all files with the '.txt' extension in the current directory. The 'find' command is appropriate for searching, with '-name' to specify the file pattern.",
    "command": "find . -name '*.txt'"
}
</example>

<example>
# User request: 'https://www.youtube.com/watch?v=mpW1wcHEMkA as wav'
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
    def cmds(args, model, system, key):
        """Generate and execute commands in your shell"""
        from llm.cli import get_default_model

        prompt = " ".join(args)

        model_id = model or get_default_model()

        model_obj = llm.get_model(model_id)
        if model_obj.needs_key:
            model_obj.key = llm.get_key(key, model_obj.needs_key, model_obj.key_env_var)

        result = model_obj.prompt(prompt, system=system or SYSTEM_PROMPT)

        interactive_exec(str(result))


def interactive_exec(command):
    if '\n' in command:
        print("Multiline command - Meta-Enter or Esc Enter to execute")
        edited_command = prompt("> ", default=command, lexer=PygmentsLexer(BashLexer), multiline=True)
    else:
        edited_command = prompt("> ", default=command, lexer=PygmentsLexer(BashLexer))
    try:
        output = subprocess.check_output(
            edited_command, shell=True, stderr=subprocess.STDOUT
        )
        print(output.decode())
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error (exit status {e.returncode}): {e.output.decode()}")
