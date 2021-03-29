from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection

from ..enums import Key, Attack


Base = declarative_base()


class Channel(Base):
    """Class to represent a Discord text channel."""

    __tablename__ = "channel"

    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer, unique=True, nullable=False)
    is_fast = Column(Boolean, default=False)



class User(Base):
    """Class to represent a Discord account."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer, unique=True, nullable=False)

    profile_id = Column(Integer, ForeignKey("profile.id"))
    profile = relationship(
        "Profile",
        uselist=False,
        foreign_keys=[profile_id],
        lazy="joined"
    )



class Macro(Base):
    """Class used to represent a macro command."""

    __tablename__ = "macro"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    command = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(
        "User",
        backref=backref(
            "macros",
            collection_class=attribute_mapped_collection("name")
        )
    )



class Profile(Base):
    """Class to represent a player profile."""

    __tablename__ = "profile"
    __table_args__ = (
        UniqueConstraint("name", "user_id"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    long_name = Column(String, nullable=False)
    
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(
        "User",
        foreign_keys=[user_id],
        backref=backref(
            "all_profiles",
            collection_class=attribute_mapped_collection("name"),
            lazy="joined"
        )
    )

    def get(self, key, default=None):
        """Get value paired with key."""

        entry = self.entries.get(key, None)
        if entry is None:
            return default
        else:
            return entry.value



class Entry(Base):
    """Class to represent entries on a player profile."""

    __tablename__ = "entry"
    __table_args__ = (
        UniqueConstraint("key", "profile_id"),
    )

    id = Column(Integer, primary_key=True)
    key = Column(Enum(Key), nullable=False)
    value = Column(Integer)
    
    profile_id = Column(Integer, ForeignKey("profile.id"))
    profile = relationship(
        "Profile",
        backref=backref(
            "entries",
            collection_class=attribute_mapped_collection("key"),
            lazy="joined"
        )
    )