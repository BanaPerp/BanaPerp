import asyncio
import click
from rich.console import Console
from rich.table import Table
from rich import box

from .client import BanaClient

console = Console()


def run(coro):
    return asyncio.run(coro)


@click.group()
@click.version_option()
def main():
    """BANAPERP — Solana perpetual market SDK CLI 🍌"""


@main.command()
def markets():
    """List all available perpetual markets."""
    async def _run():
        async with BanaClient() as client:
            data = await client.get_markets()

        table = Table(title="BANAPERP Markets", box=box.SIMPLE_HEAVY)
        table.add_column("Symbol", style="bold yellow")
        table.add_column("Mark Price", justify="right")
        table.add_column("Index Price", justify="right")
        table.add_column("Funding Rate", justify="right")
        table.add_column("Open Interest", justify="right")
        table.add_column("Spread (bps)", justify="right")

        for m in data:
            color = "green" if m.funding_rate >= 0 else "red"
            table.add_row(
                m.symbol,
                f"${m.mark_price:,.4f}",
                f"${m.index_price:,.4f}",
                f"[{color}]{m.funding_rate:.4f}%[/{color}]",
                f"${m.open_interest:,.0f}",
                f"{m.spread_bps:.2f}",
            )
        console.print(table)

    run(_run())


@main.command()
@click.argument("symbol")
def market(symbol: str):
    """Get details for a specific market (e.g. SOL-PERP)."""
    async def _run():
        async with BanaClient() as client:
            m = await client.get_market(symbol.upper())
        if not m:
            console.print(f"[red]Market {symbol} not found.[/red]")
            return
        console.print(f"\n[bold yellow]{m.symbol}[/bold yellow]")
        console.print(f"  Mark Price  : [green]${m.mark_price:,.4f}[/green]")
        console.print(f"  Index Price : ${m.index_price:,.4f}")
        console.print(f"  Spread      : {m.spread_bps:.2f} bps")
        console.print(f"  Funding     : {m.funding_rate:.4f}%")
        console.print(f"  Open Int.   : ${m.open_interest:,.0f}")
        console.print(f"  Volume 24h  : ${m.volume_24h:,.0f}")
        console.print(f"  Max Lev.    : {m.max_leverage}x\n")

    run(_run())


@main.command()
def funding():
    """Show current funding rates across all markets."""
    async def _run():
        async with BanaClient() as client:
            rates = await client.get_funding_rates()

        table = Table(title="Funding Rates", box=box.SIMPLE_HEAVY)
        table.add_column("Symbol", style="bold yellow")
        table.add_column("Rate", justify="right")
        table.add_column("Annualized", justify="right")
        table.add_column("Direction")

        for r in rates:
            color = "green" if r.is_positive else "red"
            table.add_row(
                r.symbol,
                f"[{color}]{r.rate:.4f}%[/{color}]",
                f"[{color}]{r.annualized:.2f}%[/{color}]",
                r.direction,
            )
        console.print(table)

    run(_run())


@main.command()
@click.argument("symbol")
@click.option("--interval", default=5, help="Refresh interval in seconds")
def watch(symbol: str, interval: int):
    """Watch a market's price live."""
    import time

    async def _fetch():
        async with BanaClient() as client:
            return await client.get_market(symbol.upper())

    console.print(f"[bold]Watching [yellow]{symbol.upper()}[/yellow] — Ctrl+C to stop[/bold]\n")
    try:
        while True:
            m = run(_fetch())
            if m:
                ts = time.strftime("%H:%M:%S")
                color = "green" if m.funding_rate >= 0 else "red"
                console.print(
                    f"[dim]{ts}[/dim] | "
                    f"[bold yellow]{m.symbol}[/bold yellow] | "
                    f"Mark [green]${m.mark_price:,.4f}[/green] | "
                    f"Funding [{color}]{m.funding_rate:.4f}%[/{color}]"
                )
            else:
                console.print(f"[red]Market {symbol} not found[/red]")
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[dim]stopped.[/dim]")
