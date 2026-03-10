"""Entry point for Gothic City of Pepruvia."""

import asyncio
import pygame
from src.core.game import Game


async def main():
    game = Game()
    await game.run()


asyncio.run(main())
