import centralnotice_analytics as cna

class CampaignSpec:
    """A specification of CentralNotice campaign settings for querying data."""

    def __init__( self, names = None, name_regex = None, projects = None,
            languages = None, countries = None, devices = None ):
        """Create a specification of CentralNotice campaign settings for querying data.

        Settings should correspond to those in CentralNotice.

        :param list names: Names of CentralNotice campaigns. (Either names or name_regex
            must be provided.)
        :param str name_regex: Regular expression pattern to select campaigns.
        :param list projects: Names of CentralNotice projects targeted by the campaign
            (required).
        :param list languages: Language codes of the languages targeted by the campaign.
            (Omit for campaigns targeting all languages.)
        :param list countries: Country codes of the countries targeted by the
            campaign. (Omit for campaigns that are not geotargeted.)
        :param list devices: Devices targeted by banners assigned to the campaign.
            (Omit for campaigns with banners targeting all devices.)
        """

        # Basic input validation
        if ( ( names is None ) and ( name_regex is None ) ):
            raise ValueError( 'Either name or name_regex must be provided.' )

        if ( projects is None ):
            raise ValueError ( 'projects must be provided.' )

        available_projects = cna.config[ 'project_lang_url_selection' ].keys()
        for project in projects:
            if ( project not in available_projects ):
                raise ValueError(
                    'Invalid project "{0}" requested.'.format ( project ) )

        if ( devices ):
            available_devices = cna.config[ 'device_filters' ].keys()
            for device in devices:
                if ( device not in available_devices ):
                    raise ValueError(
                        'Invalid device "{0}" requested.'.format ( device ) )

        # We don't validate countries or languages; however spelling mistakes are less
        # likely in those parameters

        self.names = names
        self.name_regex = name_regex
        self.projects = projects
        self.languages = languages
        self.countries = countries
        self.devices = devices


    def title( self ):
        if ( self.name_regex ):
            title = '/{0}/'.format( self.name_regex )
        else:
            title = self._make_str_for_title( self.names, 'campaigns' )

        title += ', ' + self._make_str_for_title( self.projects, 'projects' )

        if ( self.languages ):
            title += ', ' + self._make_str_for_title( self.languages, 'languages' )

        if ( self.countries ):
            title += ', ' + self._make_str_for_title( self.countries, 'countries' )

        if ( self.devices ):
            title += ', ' + self._make_str_for_title( self.devices, 'devices' )

        return title


    def _make_str_for_title( self, spec, plural_name ):
            l = len( spec )
            if ( l > 1 ):
                return '{0} {1}'.format( l, plural_name )

            return spec[0]