import obspython as obs

from twitchAPI.twitch import Twitch
from igdb.wrapper import IGDBWrapper


class GameInfo(object):
    IGDB_REGION_ENUM = {
        1: 'EU',
        2: 'NA',
        3: 'AU',
        4: 'NZ',
        5: 'JP',
        6: 'CN',
        7: 'Asia',
        8: 'World'        
    }

    def __init__(self, twitch_client_id=None, twitch_client_secret=None, twitch_username=None, source_name=None):
        self.source_name = source_name
        self.twitch_client_id = twitch_client_id
        self.twitch_client_secret = twitch_client_secret
        self.twitch_username = twitch_username
        self.twitch_auth_token = None
        self.broadcast_id = None
        self.game_name = None
        
    def twitch_api_connect(self):
        """ authenticate against the Twitch API and set object properties """
        if (self.twitch_client_id is not None) or (self.twitch_client_secret is not None):
            twitch = Twitch(self.twitch_client_id, self.twitch_client_secret)
            try:
                twitch.authenticate_app([])
            except:
                # if something goes wrong, at a minimum we want to unset the auth token
                # so that the script doesn't keep trying to fire unauthorized requests
                # against IGDB.
                self.twitch_auth_token = None
            
            # pull auth token, broadcast id, and game name from Twitch API
            self.twitch_auth_token = twitch.get_app_token()
            self.broadcast_id = twitch.get_users(logins=[self.twitch_username])['data'][0]['id']
            self.game_name = twitch.get_channel_information(self.broadcast_id)['data'][0]['game_name']

        else:
            self.twitch_auth_token = None

    def get_current_game(self):
        """ pull game information from IGDB and update temp HTML file for browser source """
        pass


# create local instance of GameInfo
gi = GameInfo()

def script_description():
    return """Populate local browser source with game information from IGDB.
    
Before using this plugin, you will need to obtain a Twitch API client ID and client secret.  Browse to https://dev.twitch.tv/console/apps and click "Register Your Application", then follow the instructions on the page.

NOTE: treat your client ID and secret like you would your Twitch username and password!

To customize the panel, you should become acquainted with the Jinja2 template language.  Visit https://jinja.palletsprojects.com/en/2.11.x/ for more information."""

def script_update(settings):
    """ Do something when the user changes the settings """
    pass

def script_properties():
    """ Script user interface """
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(
        props,
        "twitch_client_id",
        "Twitch Client ID",
        obs.OBS_TEXT_PASSWORD
    )

    obs.obs_properties_add_text(
        props,
        "twitch_client_secret",
        "Twitch Client Secret",
        obs.OBS_TEXT_PASSWORD
    )

    p_browser_source = obs.obs_properties_add_list(
        props,
        "browser_source",
        "Browser Source",
        obs.OBS_COMBO_TYPE_LIST,
        obs.OBS_COMBO_FORMAT_STRING
    )

    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "browser_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p_browser_source, name, name)
        
        obs.source_list_release(sources)

    obs.obs_property_set_long_description(p_browser_source, "Select the browser source that you want to be used as your gameinfo panel")

    obs.obs_properties_add_text(
        props,
        "jinja2_template",
        "Jinja2 Template",
        obs.OBS_TEXT_MULTILINE
    )

    return props

def script_defaults(settings):
    """ Define the default settings for the plugin """
    pass