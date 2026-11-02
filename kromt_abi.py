#!/usr/bin/env python3
"""
KROMT ABI Toolkit
-----------------
Encode / decode function calls and compute selectors offline.
Useful for preparing calldata that the KROMT agent (or any wallet) will sign.

No network required for core operations. No private keys.

https://kromt.xyz  |  https://github.com/kromtxyz
"""

from __future__ import annotations

import json
import sys
from typing import Any, List

import click
from eth_abi import encode, decode
from eth_utils import function_signature_to_4byte_selector, to_hex, decode_hex
from rich.console import Console

console = Console()


def parse_types_and_values(args: tuple[str, ...]) -> tuple[List[str], List[Any]]:
    """Parse 'type:value' pairs or plain values with --types."""
    types: List[str] = []
    values: List[Any] = []
    for a in args:
        if ":" in a:
            t, v = a.split(":", 1)
            types.append(t)
            values.append(auto_cast(t, v))
        else:
            values.append(a)
    return types, values


def auto_cast(typ: str, raw: str) -> Any:
    typ = typ.strip()
    if typ.startswith("uint") or typ.startswith("int"):
        return int(raw, 0)
    if typ == "bool":
        return raw.lower() in ("1", "true", "yes")
    if typ == "address":
        return raw
    if typ.startswith("bytes"):
        if raw.startswith("0x"):
            return decode_hex(raw)
        return raw.encode()
    if typ == "string":
        return raw
    # fallback
    return raw


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """KROMT ABI Toolkit – encode, decode, and compute selectors offline."""


@cli.command("selector")
@click.argument("signature")
def selector_cmd(signature: str) -> None:
    """Compute 4-byte function selector from signature.

    Example: kromt_abi.py selector "transfer(address,uint256)"
    """
    sel = function_signature_to_4byte_selector(signature)
    console.print(f"[cyan]Signature[/cyan] : {signature}")
    console.print(f"[cyan]Selector[/cyan]  : {to_hex(sel)}")


@cli.command("encode")
@click.argument("signature")
@click.argument("args", nargs=-1)
def encode_cmd(signature: str, args: tuple[str, ...]) -> None:
    """Encode calldata for a function signature.

    Example:
      kromt_abi.py encode "transfer(address,uint256)" address:0xabc... uint256:1000
    """
    # Extract types from signature
    if "(" not in signature or not signature.endswith(")"):
        console.print("[red]Invalid signature format[/red]")
        sys.exit(1)
    name, rest = signature.split("(", 1)
    types_str = rest[:-1]
    types = [t.strip() for t in types_str.split(",")] if types_str else []

    if len(args) != len(types):
        # try type:value format
        parsed_types, values = parse_types_and_values(args)
        if parsed_types:
            types = parsed_types
        else:
            console.print(f"[red]Expected {len(types)} args, got {len(args)}[/red]")
            sys.exit(1)
    else:
        values = [auto_cast(t, a) for t, a in zip(types, args)]

    sel = function_signature_to_4byte_selector(signature)
    encoded = encode(types, values)
    calldata = to_hex(sel + encoded)

    console.print(f"[cyan]Signature[/cyan] : {signature}")
    console.print(f"[cyan]Selector[/cyan]  : {to_hex(sel)}")
    console.print(f"[cyan]Calldata[/cyan]  : {calldata}")


@cli.command("decode")
@click.argument("types")
@click.argument("data")
def decode_cmd(types: str, data: str) -> None:
    """Decode ABI-encoded data given comma-separated types.

    Example:
      kromt_abi.py decode "address,uint256" 0x000... 
    """
    type_list = [t.strip() for t in types.split(",")]
    raw = decode_hex(data) if data.startswith("0x") else decode_hex("0x" + data)
    # skip selector if present (4 bytes)
    if len(raw) >= 4 and len(raw) % 32 != 0:
        raw = raw[4:]
    try:
        decoded = decode(type_list, raw)
        console.print("[cyan]Decoded values:[/cyan]")
        for t, v in zip(type_list, decoded):
            console.print(f"  {t}: {v}")
    except Exception as exc:
        console.print(f"[red]Decode error:[/red] {exc}")
        sys.exit(1)


@cli.command("info")
def info_cmd() -> None:
    """Show tool information."""
    console.print(
        "\n[bold cyan]KROMT ABI Toolkit[/bold cyan]\n"
        "Offline encode / decode / selector utility.\n"
        "No network. No private keys.\n\n"
        "[dim]KROMT · https://kromt.xyz · https://github.com/kromtxyz[/dim]\n"
    )


if __name__ == "__main__":
    cli()
