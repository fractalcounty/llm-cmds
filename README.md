# llm-cmds
<img width="944" alt="image" src="https://github.com/user-attachments/assets/b0398b99-53b7-4610-8635-f18af2922528">

A WIP fork of [llm-cmd](https://github.com/simonw/llm-cmd) that allows you to use the [LLM](https://llm.datasette.io) CLI tool to generate and execute commands in your shell, but with various enhancements such as chain of thought reasoning and user environment context that can greatly improve results in certain scenarios. 

## Installation
Install this plugin in the same environment as [LLM](https://llm.datasette.io/). 
```bash
Coming soon
```

## Usage
> [!CAUTION]
> This tool can be **very dangerous** if not used with extreme caution. Always manually review commands before executing them!

Run `llm cmds` like this:

```bash
llm cmds "download youtube.com/watch?v=OGbhJjXl9Rk as webm"
```
This will use your [default model](https://llm.datasette.io/en/stable/setup.html#setting-a-custom-default-model) to generate a shell command based on your prompt and context of your user environment. You may then edit the generated command, hit `<enter>` to execute it, or `Ctrl+C` to cancel.

To view the LLM's thought process or context sent to the LLM, append the `--think` or `--context` flag respectively:

```bash
llm cmds --think --context "find example.txt for me"
```

## Differences from llm-cmd
- **Chain of thought reasoning:** The system prompt encourages the LLM to briefly think through the user's request before generating the command, which can greatly improve the quality generated commands in certain scenarios. Both the [OpenAI](https://platform.openai.com/docs/guides/prompt-engineering/strategy-give-models-time-to-think) and [Anthropic](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought) documentation emphasize the importance of chain of thought prompting in model performance (even for basic tasks)
- **Context gathering:** The following basic information about the user's environment is appended to the request:
    - Operating system/platform
    - Version
    - Python version
    - Shell
    - Home directory
    - Current directory
- **Real-time output printing:** Commands that print their progress have their output streamed to the terminal in real-time instead as well as the final result.
- **Pretty formatting:** Printed context, thoughts and generated command output is formatted for more aesthetically appealing syntax highlighting.
- **JSON output:** While not a feature per se, both the user prompt and the LLM output are formatted as JSON, which helps with consistency and seperating the chain of thought from the raw generated command.

While `llm-cmds` may result in higher quality commands than `llm-cmd` in certain scenarios, it obviously comes at the cost of increased token usage as both the user prompt and the LLM output can be more than twice as long. For simpler tasks, llm-cmd may still be preferable. You can use both tools in tandem to your advantage.

## Planned features
- [x] JSON parsing and formatting for the request and response
- [x] Context gathering
- [x] Chain of thought reasoning 
- [ ] Actually publishing the project as a python application
- [ ] More detailed context gathering (installed packages, command history, etc)
- [ ] Context caching to reduce overhead
- [ ] Support for generaitng multiple commands
- [ ] Fine-tuned commands for [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://www.ffmpeg.org/)

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
