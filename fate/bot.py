from discord.ext.commands import Bot


class FastBot(Bot):
    """Extension of the Discord Bot class.
    
    Supports a "fast" mode, where certain channel IDs can be labelled in
    the database for special treatment. Any messages sent on fast channels
    are, by default, treated as calls to the `fast_command` command (if set).
    """

    def __init__(self, database, *args, **kwargs):

        self.database = database
        self.fast_command = kwargs.pop("fast_command", None)

        super().__init__(*args, **kwargs)


    async def get_context(self, message):

        context = await super().get_context(message)

        # If this is a fast channel, apply default command
        if (
            context.invoked_with is None and
            self.database.is_fast(context.channel.id)
        ):
            context.command = self.fast_command
        
        return context