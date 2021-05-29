#!/usr/bin/env python3

"""See main() docstring for summary description of this script. (So that
information will display when running with '--help' option.)"""

import click
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
import shlex
import sys
from typing import Dict, List
import xmltodict

default_path = (
    Path("/Applications/data-integration")  # default path for Mac
    if sys.platform == "darwin"
    else Path.home() / "data-integration"  # default path for Linux
)
default_match = "STM"

console = Console(style="bold white")
fail_style = "bold white on red"
warn_style = "bold white on yellow"
pass_style = "bold white on green"  # nosec


def unable_to_locate(filename: Path) -> None:
    """Print unable to locate file message."""
    console.print(f"UNABLE TO LOCATE {filename}!", style=fail_style)


def open_in_editor(filename: Path) -> None:
    """Open specified file in default text editor."""
    try:
        os.system(f"open {shlex.quote(str(filename))}")  # nosec
        console.print(f"Opening {filename} in your text editor . . .", style=pass_style)
    except FileNotFoundError:
        unable_to_locate(filename)
    sys.exit()


def show_contents(filename: Path) -> None:
    """Display contents of specified file."""
    try:
        with open(filename, "r") as k:
            print(k.read())
    except FileNotFoundError:
        unable_to_locate(filename)
    sys.exit()


def validate_file(filename: Path) -> None:
    """Validate if the specified file exists."""
    if filename.exists():
        console.print(f"FILE FOUND AT {filename}", style=pass_style)
    else:
        unable_to_locate(filename)
    sys.exit()


def read_shared_xml(filename: Path) -> List[Dict[str, str]]:
    """Open shared.xml file & return list of dictionaries from XML."""
    try:
        with open(filename, "rb") as k:
            raw_data = k.read()
        xml_data = xmltodict.parse(raw_data)
        return xml_data["sharedobjects"]["connection"]
    except FileNotFoundError:
        unable_to_locate(filename)


def fail_message(message: str) -> None:
    """Print database connection error message."""
    console.print(message, style=fail_style)


def show_all_connections(filename: Path) -> None:
    """Display all database connections found in shared.xml."""
    if filename.exists():
        connections = read_shared_xml(filename)
        table = Table(
            "Connection Name",
            show_header=True,
            header_style="bold gray",
            title="Database Connections",
        )
        for connection in connections:
            for k, v in connection.items():
                if k == "name":
                    table.add_row(v)
        console.print(table)
    else:
        fail_message(f"NO DATABASE CONNECTIONS FOUND IN {filename}!")
    sys.exit()


def show_connection_details(filename: Path, db_name: str) -> None:
    """Display details of specified database connection."""
    hidden_keys = (
        "access",
        "attributes",
        "servername",
        "data_tablespace",
        "index_tablespace",
    )
    table = Table(
        "Element",
        "Value",
        show_header=True,
        header_style="bold gray",
        title=f"Database Connection Properties for {db_name}",
    )
    connections = read_shared_xml(filename)
    for connection in connections:
        if connection.get("server").startswith("${"):
            connection["password"] = connection.get("server").replace(
                "NAME", "PASSWORD"
            )
    details = [
        table.add_row(k, v)
        for connection in connections
        for k, v in connection.items()
        if db_name == connection["name"] and k not in hidden_keys
    ]
    if details:
        console.print(table)
    else:
        fail_message(f"DATABASE CONNECTION {db_name} NOT FOUND IN {filename}!")
    sys.exit()


def show_kettle_matches(filename: Path, matching: str) -> None:
    """Display line(s) from kettle.properties that start with specified string."""
    try:
        table = Table(
            "Property Name",
            "Property Value",
            show_header=True,
            header_style="bold gray",
            title=f"Kettle Properties Containing {matching}",
        )
        for line in open(filename, "r"):
            if line.startswith(matching):
                property_name, property_value = line.strip("\n").split("=")
                table.add_row(property_name, property_value)
        console.print(table)
    except FileNotFoundError:
        unable_to_locate(filename)


@click.command()
@click.option(
    "--kettle-path",
    default=default_path,
    show_default=True,
    help="Path to your kettle.properties file",
)
@click.option(
    "--match",
    default=default_match,
    show_default=True,
    help="String to search from beginning of line for",
)
@click.option(
    "--edit",
    is_flag=True,
    help="Open kettle.properties in associated file type text editor",
)
@click.option(
    "--show",
    is_flag=True,
    help="Display all contents of kettle.properties file",
)
@click.option(
    "--show-path",
    is_flag=True,
    help="Display path to kettle.properties file",
)
@click.option(
    "--edit-spoon",
    is_flag=True,
    help="Open spoon.sh in associated file type text editor",
)
@click.option(
    "--show-spoon",
    is_flag=True,
    help="Display all contents of spoon.sh file",
)
@click.option(
    "--show-spoon-path",
    is_flag=True,
    help="Display path to spoon.sh file",
)
@click.option(
    "--list-connections",
    is_flag=True,
    help="Display list of all database connection names in shared.xml",
)
@click.option(
    "--connection",
    show_default=True,
    help="Display specified database connection details in shared.xml",
)
@click.option(
    "--show-shared-xml-path",
    is_flag=True,
    help="Display path to shared.xml file",
)
def main(
    kettle_path: Path,
    match: str,
    edit: bool,
    show: bool,
    show_path: bool,
    edit_spoon: bool,
    show_spoon: bool,
    show_spoon_path: bool,
    list_connections: bool,
    connection: str,
    show_shared_xml_path: bool,
) -> None:
    """Utility to quickly view or make changes to the following PDI configuration
    files:

    * kettle.properties

    * spoon.sh

    * shared.xml

    Also, this script is currently designed only to be run on Mac OSX."""
    kettle = kettle_path / "kettle.properties"
    spoon_sh = kettle_path / "spoon.sh"
    shared_xml = kettle_path / "shared.xml"
    if edit:
        open_in_editor(kettle)
    if show:
        show_contents(kettle)
    if show_path:
        validate_file(kettle)

    if edit_spoon:
        open_in_editor(spoon_sh)
    if show_spoon:
        show_contents(spoon_sh)
    if show_spoon_path:
        validate_file(spoon_sh)

    if list_connections:
        show_all_connections(shared_xml)
    if connection:
        show_connection_details(shared_xml, connection)
    if show_shared_xml_path:
        validate_file(shared_xml)

    show_kettle_matches(kettle, match)


if __name__ == "__main__":
    main()
else:
    from pytest import mark, raises


def test_unable_to_locate(capsys):
    """Make sure that message is printed when path to config file(s) is invalid."""
    test_path = "/foo/bar/kettle.properties"
    result = unable_to_locate(test_path)
    captured = capsys.readouterr()
    assert result is None  # nosec
    assert test_path in captured.out  # nosec
    assert captured.out.startswith("UNABLE TO LOCATE")  # nosec


@mark.skip(reason="NOTE: This test will cause kettle.properties to be opened!")
def test_open_in_editor(capsys):
    """Make sure that text editor window opens when called.

    NOTE: This test will cause kettle.properties to be opened!"""
    test_path = default_path / "kettle.properties"
    with raises(SystemExit):
        result = open_in_editor(test_path)
        captured = capsys.readouterr()
        assert result is None  # nosec
        assert test_path in captured.out  # nosec
        assert test_path.startswith("Opening")  # nosec


def test_open_in_editor_fails(capsys):
    """Make sure that text editor window opens when called."""
    test_path = Path("/foo/bar") / "kettle.badfile"
    with raises(SystemExit):
        open_in_editor(test_path)
        captured = capsys.readouterr()
        assert captured.out.startswith("UNABLE TO LOCATE")  # nosec
