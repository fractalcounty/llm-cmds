import pytest
from click.testing import CliRunner
from llm.plugins import pm
from llm_cmds import register_commands
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
    result = runner.invoke(cli, ['cmd', '--help'])
    assert result.exit_code == 0
    assert 'Generate and execute commands in your shell' in result.output

@pytest.mark.parametrize("args, expected_in_output", [
    (["list", "files"], "ls"),
    (["current", "directory"], "pwd"),
])
def test_cmd_command_generates_command(cli, mocker, args, expected_in_output):
    mock_model = mocker.Mock()
    mock_model.prompt.return_value = expected_in_output
    mock_model.needs_key = False
    mocker.patch('llm.get_model', return_value=mock_model)
    
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['cmd'] + args, input='\n', catch_exceptions=False)
    
    print(f"Command output: {result.output}")
    print(f"Exception: {result.exception}")
    print(f"Stderr: {result.stderr_bytes.decode() if result.stderr_bytes else 'None'}")
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}"
    assert expected_in_output in result.output

def test_cmd_command_executes_command(cli, mocker):
    mock_model = mocker.Mock()
    mock_model.prompt.return_value = "echo 'Hello, World!'"
    mock_model.needs_key = False
    mocker.patch('llm.get_model', return_value=mock_model)
    
    runner = CliRunner()
    result = runner.invoke(cli, ['cmd', 'print', 'hello', 'world'], input='\n')
    
    print(f"Command output: {result.output}")
    print(f"Exception: {result.exception}")
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}"
    assert "Hello, World!" in result.output

def test_cmd_command_with_custom_model(cli, mocker):
    mock_model = mocker.Mock()
    mock_model.prompt.return_value = "echo 'Custom model'"
    mock_model.needs_key = False
    mocker.patch('llm.get_model', return_value=mock_model)
    
    runner = CliRunner()
    result = runner.invoke(cli, ['cmd', '-m', 'custom_model', 'test'], input='\n')
    
    print(f"Command output: {result.output}")
    print(f"Exception: {result.exception}")
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}"
    assert "Custom model" in result.output

def test_cmd_command_with_custom_system_prompt(cli, mocker):
    mock_model = mocker.Mock()
    mock_model.prompt.return_value = "echo 'Custom system prompt'"
    mock_model.needs_key = False
    mocker.patch('llm.get_model', return_value=mock_model)
    
    runner = CliRunner()
    result = runner.invoke(cli, ['cmd', '-s', 'Custom prompt', 'test'], input='\n')
    
    print(f"Command output: {result.output}")
    print(f"Exception: {result.exception}")
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}"
    assert mock_model.prompt.call_args[1]['system'] == 'Custom prompt'
    assert "Custom system prompt" in result.output