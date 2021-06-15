from pathlib import Path
from pytest import mark, raises
from typer.testing import CliRunner

from kettle import cli, default_path, open_in_editor, unable_to_locate

runner = CliRunner()


def test_unable_to_locate(capsys):
    """Make sure that message is printed when path to config file(s) is invalid."""
    test_path = "/foo/bar/kettle.properties"
    result = unable_to_locate(test_path)
    captured = capsys.readouterr()
    assert result is None
    assert test_path in captured.out
    assert captured.out.startswith("UNABLE TO LOCATE")


def test_open_in_editor(capsys):
    """Make sure that text editor window opens when called.

    NOTE: This test will cause kettle.properties to be opened!"""
    test_path = default_path / "kettle.properties"
    with raises(SystemExit):
        result = open_in_editor(test_path)
        captured = capsys.readouterr()
        assert result is None
        assert test_path in captured.out
        assert test_path.startswith("Opening")


def test_open_in_editor_fails(capsys):
    """Make sure that text editor window opens when called."""
    test_path = Path("/foo/bar") / "kettle.badfile"
    with raises(SystemExit):
        open_in_editor(test_path)
        captured = capsys.readouterr()
        assert captured.out.startswith("UNABLE TO LOCATE")


class TestCliKettle:
    """Tests involving the use of 'kettle' command."""

    def test_cli_kettle_kettle_no_options(self):
        """Make sure that 'UNABLE TO LOCATE' message is returned when running
        `kettle` and no other options."""
        result = runner.invoke(cli, ["kettle"])
        assert result.exit_code == 0
        assert "UNABLE TO LOCATE" in result.stdout

    def test_cli_kettle_kettle_with_path(self):
        """Make sure that when `kettle --path .` is run, it returns table of lines
        starting with 'STM'."""
        result = runner.invoke(cli, ["kettle", "--path", "."])
        assert result.exit_code == 0
        assert "STM" in result.stdout

    @mark.parametrize(
        "text, expected", [("INSIGHTS", "INSIGHTS"), ("POSTGRES", "POSTGRES")]
    )
    def test_cli_kettle_kettle_match(self, text, expected):
        """Make sure that `kettle --match ...` returns expected values."""
        result = runner.invoke(cli, ["kettle", "--path", ".", "--match", text])
        assert result.exit_code == 0
        assert expected in result.stdout

    def test_cli_kettle_kettle_show(self):
        """Make sure that `kettle --show` returns expected values."""
        result = runner.invoke(cli, ["kettle", "--path", ".", "--show"])
        assert result.exit_code == 0
        assert "KETTLE" in result.stdout

    def test_cli_kettle_kettle_show_path(self):
        """Make sure that `kettle --show-path` returns information about path to
        kettle.properties file."""
        result = runner.invoke(cli, ["kettle", "--path", ".", "--show-path"])
        assert result.exit_code == 0
        assert "FILE FOUND AT kettle.properties" in result.stdout


class TestCliSpoon:
    """Tests involving use of 'spoon' command."""

    @mark.parametrize("spoon_option", [("spoon"), ("spoon --path .")])
    def test_cli_kettle_spoon(self, spoon_option):
        """Make sure that 'Nothing to do' message is returned when running
        `spoon` with no options or with only '--path .'."""
        result = runner.invoke(cli, spoon_option.split())
        assert result.exit_code == 0
        assert "Nothing to do" in result.stdout

    def test_cli_kettle_spoon_show(self):
        """Make sure that when `spoon --show is run, it returns contents of
        spoon.sh file."""
        result = runner.invoke(cli, ["spoon", "--path", ".", "--show"])
        assert result.exit_code == 0
        assert "#!/bin/sh" in result.stdout

    def test_cli_kettle_spoon_show_path(self):
        """Make sure that `spoon --show-path` returns information about path to
        spoon.sh file."""
        result = runner.invoke(cli, ["spoon", "--path", ".", "--show-path"])
        assert result.exit_code == 0
        assert "FILE FOUND AT spoon.sh" in result.stdout


class TestCliShared:
    """Tests involving use of 'shared' command."""

    @mark.parametrize("shared_option", [("shared"), ("shared --path .")])
    def test_cli_kettle_shared(self, shared_option):
        """Make sure that 'Nothing to do' message is returned when running
        `spoon` with no options or with only '--path .'."""
        result = runner.invoke(cli, shared_option.split())
        assert result.exit_code == 0
        assert "Nothing to do" in result.stdout

    def test_cli_kettle_shared_list_connections(self):
        """Make sure that `shared --list-connections` returns list of database
        connections found in shared.xml file."""
        pass

    def test_cli_kettle_shared_connection(self):
        """Make sure that `shared --connection ...` returns information about a
        database connection found in shared.xml file."""
        pass

    def test_cli_kettle_shared_show_path(self):
        """Make sure that `shared --show-path` returns information about path to
        shared.xml file."""
        result = runner.invoke(cli, ["shared", "--path", ".", "--show-path"])
        assert result.exit_code == 0
        assert "FILE FOUND AT shared.xml" in result.stdout
