import obspython as obs

from twitchAPI.twitch import Twitch
from igdb.wrapper import IGDBWrapper

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