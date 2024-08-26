import pytest
from click.testing import CliRunner
from llm.plugins import pm
from llm_cmds import register_commands
from unittest.mock import patch, MagicMock
import click

@pytest.fixture
def cli():
    @click.group()
    def cli():
        pass
    register_commands(cli)
    return cli

def test_plugin_is_installed():
    names = [mod.__name__ for mod in pm.get_plugins()]
    assert "llm_cmds" in names

def test_cmd_command_exists(cli):
    runner = CliRunner()
    result = runner.invoke(cli, ['cmds', '--help'])
    assert result.exit_code == 0
    assert 'Generate and execute commands in your shell' in result.output

def test_cmds_with_custom_model_and_system_prompt(cli):
    runner = CliRunner()
    mock_model = MagicMock()
    mock_model.needs_key = False
    mock_model.prompt.return_value = "echo 'Hello, World!'"

    with patch('llm.get_model', return_value=mock_model) as mock_get_model, \
         patch('llm_cmds.interactive_exec') as mock_interactive_exec:
        result = runner.invoke(cli, ['cmds', '-m', 'custom-model', '-s', 'Custom system prompt', 'test command'])

        assert result.exit_code == 0
        mock_get_model.assert_called_once_with('custom-model')
        mock_model.prompt.assert_called_once_with('test command', system='Custom system prompt')
        mock_interactive_exec.assert_called_once_with("echo 'Hello, World!'")