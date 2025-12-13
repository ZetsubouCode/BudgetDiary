from typing import Iterable, Tuple

from nextcord import Color, Embed


def build_embed(title: str, description: str, *, color: Color = Color.blurple(), fields: Iterable[Tuple[str, str, bool]] | None = None) -> Embed:
    embed = Embed(title=title, description=description, color=color)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed


def success(title: str, description: str, *, fields: Iterable[Tuple[str, str, bool]] | None = None) -> Embed:
    return build_embed(title, description, color=Color.green(), fields=fields)


def error(title: str, description: str) -> Embed:
    return build_embed(title, description, color=Color.red())


def warning(title: str, description: str) -> Embed:
    return build_embed(title, description, color=Color.gold())
