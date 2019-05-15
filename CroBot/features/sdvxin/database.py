#
# database.py
# Contains the database functions for sdvx.in feature functionality
#


# External Imports
import os
import re

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


##############################
# DATABASE SETUP / FUNCTIONS #
##############################


base = declarative_base()
class Song(base):
    """
    The table layout for the charts table containing all general Song information per entry
    """
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True)
    song_id = Column(String)
    title = Column(String)
    title_translated = Column(String)
    title_romanized = Column(String)
    artist = Column(String)

    nov_level = Column(Integer)
    nov_link = Column(String)
    adv_level = Column(Integer)
    adv_link = Column(String)
    exh_level = Column(Integer)
    exh_link = Column(String)
    max_level = Column(Integer)
    max_link = Column(String)

    video_play = Column(String)
    video_nofx = Column(String)
    video_og = Column(String)
    jacket = Column(String)


engine = create_engine('sqlite:///sdvxCharts.db')
session_maker = sessionmaker(bind=engine)


async def recreate_db():
    """
    recreate_db: Renames the current sqlite database, if it exists, and starts a blank database
    Usually ran when the database
    :return: True if successful
             False if failed
    """
    # Create a backup
    session = session_maker()
    now = datetime.now()
    old_name = 'sdvxCharts-'+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'-'+str(now.hour)+'-'+str(now.minute)+'.db'
    if os.path.isfile('sdvxCharts.db'):
        os.rename('sdvxCharts.db', old_name)

    try:
        base.metadata.create_all(engine)
        return True

    except Exception as e:
        print(e)
        session.rollback()
        os.remove('sdvxCharts.db')
        if os.path.isfile(old_name):
            os.rename(old_name, 'sdvxCharts.db')
        return False

    finally:
        session.close()


###############################
# DATABASE SESSION MANAGEMENT #
###############################


async def session_start():
    """
    session_start: Creates a new database session for external functions and returns it
                    - Keep in mind that this is only for external functions that require multiple transactions
                        - Such as adding songs
    :return: A new database session
    """
    return session_maker()


async def session_end(session):
    """
    session_end: Closes the database session
    :param session: The session to be closed
    :return: N/A
    """
    session.close()


##############################
#       DATABASE CHECK       #
##############################


async def song_exists(song_id):
    """
    exist_song: Checks to see if the song exists in the database by sdvx.in song_id
    :param song_id: The song_id of the song to check
    :return: True if the song exists
             False if the song does not exist
    """
    # Set up the database session
    session = session_maker()
    # If the song_id exists
    if session.query(Song).filter_by(song_id=song_id).scalar() is not None:
        session.close()
        return True

    session.close()
    return False


##############################
#    DATABASE ADD / UPDATE   #
##############################


async def song_add(session, song_dict):
    """
    add_song: Attempts to add a song to the database
    :param session: The session to work from
    :param song_dict: A dictionary containing all of the song information
    :return: True if successful
             False if failed
    """
    try:
        # Add the Chart to the session by direct dictionary to constructor conversion
        session.add(Song(**song_dict))
        return True

    except:
        return False


async def song_update(session, song_dict):
    """
    update_song: Updates the song in the database
    :param session: The session to work from
    :param song_dict: the data
    :return: True if successful
             False if unsuccessful
    """
    try:
        # Add the Chart to the session by direct
        session.query(Song).filter_by(song_id=song_dict['song_id']).update(song_dict)
        return True

    except:
        return False

##############################
#       DATABASE FETCH       #
##############################


async def song(song_id):
    """
    song: A function to fetch a song by song_id.
    :param song_id: The song_id of the song to fetch
    :return: A Chart object
    """
    # Set up the database session
    session = session_maker()
    # Attempt to fetch the song
    song = session.query(Song).filter_by(song_id=song_id).first()
    session.close()
    return song


async def song_ids():
    """
    song_ids: Fetches a list of song_ids, for cases where song_list is too much data
    :return: A list containing song_ids,
    """
    # Set up the database session
    session = session_maker()
    # The list of songs
    song_ids = []

    # Iterate through the database, grabbing all of the song_ids
    for id, song_id in session.query(Song.id, Song.song_id):
        song_ids.append(song_id)

    return song_ids


async def song_list():
    """
    song_list: Retrieves a full list of songs from the database
    :return: A list containing Song classes
    """
    # Set up the database session
    session = session_maker()
    # The list of songs
    song_list = []

    for chart in session.query(Song).all():
        song_list.append(chart)

    # Close the session
    session.close()
    return song_list

