import pytest
from click.testing import CliRunner
from cli import cli

def test_ask_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["ask", "test question"])
    assert result.exit_code == 0
    assert "Asking: test question" in result.output

def test_chat_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["chat"], input="test question\nexit\n")
    assert result.exit_code == 0
    assert "You asked: test question" in result.output
