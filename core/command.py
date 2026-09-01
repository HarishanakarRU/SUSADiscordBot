from abc import ABC, abstractmethod
import discord

class BaseCommand(ABC):
    """
    Abstract base class for all Discord commands following the Command Pattern.
    """
    
    @abstractmethod
    async def execute(self, interaction: discord.Interaction, *args, **kwargs) -> None:
        """
        Executes the command logic. Must be overridden by concrete implementations.
        """
        pass