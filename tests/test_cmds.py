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