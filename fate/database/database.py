from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, User, Profile, Entry, Channel, Macro


def session_context(method):
    """Database method decorator which encloses the method in a session context.
    
    Note:
        If the method is already being called inside a session context, the session should
        be provided as a keyword argument to the wrapper.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):

        if kwargs.get("session") is None:
            # No existing context, so wrap in a session
            with self.Session.begin() as session:
                kwargs["session"] = session
                result = method(self, *args, **kwargs)
        else:
            # Pass through existing session context
            result = method(self, *args, **kwargs)

        return result

    return wrapper



class Database:
    
    def __init__(self, url):
        """Create a database configuration."""

        self.engine = create_engine(url)

        # Disabling expire_on_commit allows returned data to be accessed outside a session
        self.Session = sessionmaker(self.engine, expire_on_commit=False)


    def create_tables(self):
        """Create the tables."""

        Base.metadata.create_all(self.engine)


    @session_context
    def fetch_user(self, discord_id, create_missing=True, *, session=None):
        """Fetch or make user entry with given discord ID."""

        user = session.query(User).filter_by(discord_id=discord_id).first()

        # Make a user entry if not already present and create_missing option is on
        if user is None and create_missing:
            user = User(discord_id=discord_id)
            session.add(user)

        return user


    @session_context
    def new_profile(self, discord_id, profile_name, long_name=None, *, session=None):
        """Create and return new player profile."""
        
        # Default long name is profile name
        if long_name is None:
            long_name = profile_name

        # Profile names case insensitive
        profile_name = profile_name.lower()

        user = self.fetch_user(discord_id, session=session)

        # If the profile name is not already in use, create the profile
        if profile_name not in user.all_profiles:
            return Profile(user=user, name=profile_name, long_name=long_name)
        else:
            return None
        

    @session_context
    def fetch_profile(self, discord_id, profile_name=None, *, session=None):
        """Fetch a player profile."""

        user = self.fetch_user(discord_id, session=session)

        # If no name provided, fetch active profile
        if profile_name is None:
            profile = user.profile
        else:
            profile = user.all_profiles.get(profile_name.lower())

        return profile


    @session_context
    def rename_profile(self, discord_id, profile_name, new_long_name, *, session=None):
        """Change the long name of a player profile."""

        profile = self.fetch_profile(discord_id, profile_name, session=session)

        if profile is None:
            return False
        else:
            profile.long_name = new_long_name
            return True


    @session_context
    def switch_profile(self, discord_id, profile_name, *, session=None):
        """Change player profile."""

        profile = self.fetch_profile(discord_id, profile_name, session=session)

        # If the profile exists, make the switch
        if profile is not None:
            profile.user.profile = profile
        
        return profile


    @session_context
    def update(self, discord_id, key, value, profile_name=None, *, session=None):
        """Update an entry on a player profile."""

        profile = self.fetch_profile(discord_id, profile_name, session=session)

        # If a profile is currently selected, make the update
        if profile is not None:
            profile.entries[key] = Entry(key=key, value=value)
        
        return profile


    @session_context
    def fetch_channel(self, channel_id, create_missing=True, *, session=None):
        """Fetch or make channel entry with given discord ID."""

        channel = session.query(Channel).filter_by(discord_id=channel_id).first()

        # Make a channel entry if not already present and create_missing option is on
        if channel is None and create_missing:
            channel = Channel(discord_id=channel_id)
            session.add(channel)

        return channel


    @session_context
    def is_fast(self, channel_id, *, session=None):
        """Return is_fast flag for specified channel."""

        return self.fetch_channel(channel_id, session=session).is_fast

    
    @session_context
    def toggle_fast(self, channel_id, *, session=None):
        """Toggle the is_fast flag on specified channel."""

        channel = self.fetch_channel(channel_id, session=session)
        channel.is_fast = not channel.is_fast

        return channel.is_fast


    @session_context
    def fetch_macro(self, discord_id, macro_name, *, session=None):
        """Fetch a saved command."""

        user = self.fetch_user(discord_id, session=session)
        macro = user.macros.get(macro_name.lower())

        if macro is None:
            return None
        else:
            return macro.command


    @session_context
    def save_macro(self, discord_id, macro_name, command, *, session=None):
        """Save command for later use.
        
        Returns:
            The command previously saved under that macro name (if any).
        """

        # Macro names case insensitive
        macro_name = macro_name.lower()

        user = self.fetch_user(discord_id, session=session)
        macro = user.macros.get(macro_name)

        if macro is None:
            user.macros[macro_name] = Macro(name=macro_name, command=command)
            return None
        else:
            old_command = macro.command
            macro.command = command
            return old_command