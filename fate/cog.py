from functools import wraps
from discord import Embed
from discord.ext import commands

from .parsing import Parser
from .enums import Key


def format_response(method):
    """Cog command decorator which formats output as a Discord embed and sends it."""

    @wraps(method)
    async def wrapper(self, context, *args, **kwargs):

        response = await method(self, context, *args, **kwargs)

        # If no response, then give a :warning: react instead
        if response is None:
            await context.message.add_reaction("\N{WARNING SIGN}\N{VARIATION SELECTOR-16}")
            return

        # String responses are used as embed descriptions
        if isinstance(response, str):
            response = {"description": response}


        # Deal with author, footer, and profile arguments
        author = response.pop("author", None) or context.author.name
        footer = response.pop("footer", None)
        profile = response.pop("profile", None)
        if profile is not None:
            author = f"{author} as {profile}"

        # Create the embed
        embed = Embed(**response)
        embed.set_author(name=author, icon_url=context.author.avatar_url)
        if footer is not None:
            embed.set_footer(text=footer)

        # Send embed
        await context.send(embed=embed)
    
    return wrapper



class FateCog(commands.Cog):
    """Cog class for making a Fate Bot."""
    
    def __init__(self, database):

        self.database = database
        self.parser = Parser()


    @commands.command(name="roll")
    @format_response
    async def roll(self, context, *, arg):
        """Perform a roll."""

        discord_id = context.author.id
        request = self.parser.parse(arg)

        # If this is a macro command, load it
        if isinstance(request, str):
            macro_name = request
            stored_command = self.database.fetch_macro(discord_id, macro_name)

            # Stop if no macro found
            if stored_command is None:
                return None
            
            request = self.parser.parse(stored_command)

        # Stop if request could not be parsed
        if request is None:
            return None
        
        # Only load profile if needed
        if request.is_complex:
            profile = self.database.fetch_profile(discord_id, request.profile_name)
        else:
            profile = None

        # Invoke request
        return request(profile)


    @commands.command(name="set")
    @format_response
    async def update_profile(self, context, raw_key, value):
        """Set a stat value on current profile."""

        discord_id = context.author.id

        key = Key.get(raw_key)
        if key is None:
            return f"No characteristic or skill named \"{raw_key}\"."

        profile = self.database.update(discord_id, key, value)

        if profile is not None:
            return  f"{key} on profile `{profile.name}` set to `{value}`."
        else:
            return "No profile selected."


    @commands.command(name="rename")
    @format_response
    async def update_name(self, context, profile_name, long_name):
        """Change a player profile's long name."""

        discord_id = context.author.id

        exists = self.database.rename_profile(discord_id, profile_name, long_name)

        if exists:
            return f"Profile `{profile_name.lower()}` renamed \"{long_name}\"."
        else:
            return f"Profile `{profile_name.lower()}` not found."


    @commands.command(name="load")
    @format_response
    async def load_profile(self, context, profile_name):
        """Load a player profile."""

        discord_id = context.author.id
        profile = self.database.switch_profile(discord_id, profile_name)

        if profile is not None:
            return f"Now playing as {profile.long_name}."
        else:
            return f"Profile `{profile_name}` not found."


    @commands.command(name="create")
    @format_response
    async def create_profile(self, context, profile_name, long_name=None):
        """Create a new player profile."""

        if not profile_name.isalnum():
            return "Profile names can only contain letters and numbers."

        discord_id = context.author.id
        profile = self.database.new_profile(discord_id, profile_name, long_name)

        if profile is not None:
            return f"Profile `{profile.name}` created successfully!"
        else:
            return "Profile already exists."

    
    @commands.command(name="show")
    @format_response
    async def show_profile(self, context):
        """Display current player profile."""

        discord_id = context.author.id
        profile = self.database.fetch_profile(discord_id)

        if profile is not None:
            return "\n".join(f"{key} = {entry.value}" for key, entry in profile.entries.items()) ## TODO Refactor
        else:
            return f"No profile selected."


    @commands.command(name="list")
    @format_response
    async def list_profiles(self, context):
        """List all player profiles."""

        discord_id = context.author.id
        user = self.database.fetch_user(discord_id)

        return "Profiles: " + ", ".join(f"`{name}`" for name in user.all_profiles) ## TODO Refactor


    @commands.command(name="toggle-fast")
    @format_response
    async def toggle_fast(self, context):
        """Toggle the fast-roll setting on current channel."""

        channel = context.channel.id
        enabled = self.database.toggle_fast(channel)

        return f"Fast mode **{'enabled' if enabled else 'disabled'}**."


    @commands.command(name="macro")
    @format_response
    async def set_macro(self, context, macro_name, command):
        """Save a command for later use."""

        if not macro_name.isalnum():
            return "Macro names can only contain letters and numbers."

        discord_id = context.author.id
        request = self.parser.parse(command)

        if request is None:
            return "Invalid command."
        elif isinstance(request, str):
            return "Macros cannot call other macros."

        self.database.save_macro(discord_id, macro_name, command)

        return f"Macro `{macro_name.lower()}` saved successfully."