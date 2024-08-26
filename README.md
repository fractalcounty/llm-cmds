# llm-cmds

A fork of [llm-cmd](https://github.com/simonw/llm-cmd) that allows you to use the [LLM](https://llm.datasette.io) CLI tool to generate and execute commands in your shell, but with various enhancements such as chain of thought reasoning and user environment context that can improve results in certain scenarios. 

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/). 
```bash
llm install llm-cmds
```

## Usage

Similar to [llm-cmd](https://github.com/simonw/llm-cmd), this tool can be **very dangerous** if not used with extreme caution. Although the system prompt attempts to mitigate unintentionally harmful operations, it is far from foolproof.

Run `llm cmds` like this:

```bash
llm cmds download youtube.com/watch?v=OGbhJjXl9Rk as webm
```
This will use your [default model](https://llm.datasette.io/en/stable/setup.html#setting-a-custom-default-model) to generate the corresponding shell command based on the prompt and the basic context of your environment.

You may then edit the generated command, hit `<enter>` to execute it, or `Ctrl+C` to cancel.

## Differences from llm-cmd

- **User environment context:** The system prompt is enhanced to include the following basic information about the user's environment:
    - Operating system/platform
    - Version
    - Python version
    - Shell
    - Home directory
    - Current directory
- **Chain of thought reasoning:** The system prompt encourages the LLM to briefly think through the user's request and assumptions that must be made before generating the command, which can improve the quality of the result in certain scenarios (normally hidden, use the `--think` flag to show).
- **Real-time output printing:** Commands that print their progress have their output streamed to the terminal in real-time instead as well as the final result.
- **Pretty formatting:** Printed context, thoughts and generated command output is formatted for more aesthetically appealing syntax highlighting.
- **JSON output:** While not a feature per se, both the user prompt and the LLM output are formatted as JSON, which helps with consistency and seperating the chain of thought from the raw generated command.

While llm-cmds may result in higher quality commands than llm-cmd in certain scenarios, it obviously comes at the cost of increased token usage as both the user prompt and the LLM output can be more than twice as long. For simpler tasks, llm-cmd may still be preferable. You can use both tools in tandem to your advantage.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd llm-cmds
python3 -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
llm install -e '.[test]'
```
To run the tests:
```bash
pytest
```