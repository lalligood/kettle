#!/usr/bin/env python3

"""This is a utility script for managing your PDI (kettle) configuration in your local
development environment."""

import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
import shlex
import sys
import typer
from typing import Dict, List, Optional
import xmltodict

usage = """Utility to quickly view or make changes to the following PDI
configuration files:

\b
* kettle.properties
* spoon.sh
* shared.xml

This script is designed only to be run on Mac OSX or Linux."""
cli = typer.Typer(name="pdi_config", add_completion=False, help=usage)

default_path = (
    Path("/Applications/data-integration")  # default path for Mac
    if sys.platform == "darwin"
    else Path.home() / "data-integration"  # default path for Linux
)
default_match = "STM"

console = Console(style="bold white")
fail_style = "bold white on red"
warn_style = "bold white on yellow"
gain_style = "bold white on green"
show_style = "bold purple"


def unable_to_locate(filename: Path) -> None:
    """Print unable to locate file message."""
    console.print(f"UNABLE TO LOCATE {filename}!", style=fail_style)


def open_in_editor(filename: Path) -> None:
    """Open specified file in default text editor."""
    try:
        if sys.platform == "darwin":
            os.system(f"open {shlex.quote(str(filename))}")
        else:
            os.system(f"xdg-open {shlex.quote(str(filename))}")
        console.print(f"Opening {filename} in your text editor. . .", style=gain_style)
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
        console.print(f"FILE FOUND AT {filename}", style=gain_style)
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
            header_style=show_style,
            title="Database Connections",
            min_width=40,
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
        header_style=show_style,
        title=f"Database Connection Properties for {db_name}",
        min_width=40,
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
            header_style=show_style,
            title=f"Kettle Properties Containing {matching}",
            min_width=40,
        )
        for line in open(filename, "r"):
            if line.startswith(matching):
                property_name, property_value = line.strip("\n").split("=")
                table.add_row(property_name, property_value)
        console.print(table)
    except FileNotFoundError:
        unable_to_locate(filename)


@cli.command()
def kettle(
    filepath: Optional[Path] = typer.Option(
        default_path,
        "--path",
        show_default=True,
        help="Path to your kettle.properties file",
    ),
    match: str = typer.Option(
        default_match,
        show_default=True,
        help="String to search from beginning of line for",
    ),
    edit: bool = typer.Option(
        False,
        "--edit",
        is_flag=True,
        help="Open kettle.properties in associated file type text editor",
    ),
    show: bool = typer.Option(
        False,
        "--show",
        is_flag=True,
        help="Display contents of kettle.properties file",
    ),
    show_path: bool = typer.Option(
        False,
        "--show-path",
        is_flag=True,
        help="Display path to kettle.properties file",
    ),
):
    """Display useful information about kettle.properties file."""
    kettle = filepath / "kettle.properties"
    if edit:
        open_in_editor(kettle)
    if show:
        show_contents(kettle)
    if show_path:
        validate_file(kettle)
    show_kettle_matches(kettle, match)


@cli.command()
def spoon(
    filepath: Optional[Path] = typer.Option(
        default_path,
        "--path",
        show_default=True,
        help="Path to your spoon.sh file",
    ),
    edit: bool = typer.Option(
        False,
        "--edit",
        is_flag=True,
        help="Open kettle.properties in associated file type text editor",
    ),
    show: bool = typer.Option(
        False,
        "--show",
        is_flag=True,
        help="Display contents of kettle.properties file",
    ),
    show_path: bool = typer.Option(
        False,
        "--show-path",
        is_flag=True,
        help="Display path to kettle.properties file",
    ),
):
    """Display useful information about spoon.sh file."""
    spoon_sh = filepath / "spoon.sh"
    if edit:
        open_in_editor(spoon_sh)
    if show:
        show_contents(spoon_sh)
    if show_path:
        validate_file(spoon_sh)
    print("Nothing to do. Exiting. . .")


@cli.command()
def shared(
    filepath: Optional[Path] = typer.Option(
        default_path,
        "--path",
        show_default=True,
        help="Path to your shared.xml file",
    ),
    list_connections: bool = typer.Option(
        False,
        "--list-connections",
        is_flag=True,
        help="Display list of all database connection names in shared.xml",
    ),
    connection: Optional[str] = typer.Option(
        "",
        show_default=False,
        help="Display specified database connection details in shared.xml",
    ),
    show_path: bool = typer.Option(
        False,
        "--show-path",
        is_flag=True,
        help="Display path to shared.xml file",
    ),
):
    """Display useful information about shared.xml file."""
    shared_xml = filepath / "shared.xml"
    if list_connections:
        show_all_connections(shared_xml)
    if connection:
        show_connection_details(shared_xml, connection)
    if show_path:
        validate_file(shared_xml)
    print("Nothing to do. Exiting. . .")
