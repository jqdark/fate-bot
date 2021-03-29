import yaml

from ..enums import Key


def deserialise(raw):
    """Deserialise key."""

    # Fix change in key
    if raw == "Tech-Use":
        raw = "Tech Use"

    return Key(raw.lower())


class YAMLDatabase:
    """Class for loading and converting legacy YAML storage."""

    def __init__(self, filename):

        with open(filename) as db_file:
            self.data = yaml.safe_load(db_file)

    
    def _save_channels(self, database):
        """Save all channel data to the database."""

        for channel_id in self.data["Fast Channels"]:
            if not database.is_fast(channel_id):
                database.toggle_fast(channel_id)


    def _save_profiles(self, database):
        """Save all profile data to the database."""

        for profile_name, profile_data in self.data["Profiles"].items():

            discord_id = profile_data["Owner"]
            profile = database.new_profile(discord_id, profile_name)

            # Avoid overwriting existing profile data
            if profile is not None:
                for raw, value in profile_data["Sheet"].items():
                    key = deserialise(raw)
                    database.update(discord_id, key, value, profile_name)
                
                # If this was active profile, make switch
                user_data = self.data["Users"].get(discord_id)
                if (
                    user_data is not None and
                    user_data["Profile"] == profile_name
                ):
                    database.switch_profile(discord_id, profile_name)


    def save_all(self, database):
        """Save all data to the database."""

        self._save_channels(database)
        self._save_profiles(database)