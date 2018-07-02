import centralnotice_analytics as cna

class CampaignSpec:
    """A specification of CentralNotice campaign settings for querying data."""

    def __init__( self, names = None, name_regex = None, projects = None,
            languages = None, countries = None, devices = None ):
        """Create a specification of CentralNotice campaign settings for querying data.

        Settings should correspond to those in CentralNotice.

        :param list names: Names of CentralNotice campaigns. (Either names or name_regex
            may be provided, but not both. However, both may be omitted.)
        :param str name_regex: Regular expression pattern to select campaigns.
        :param list projects: Names of CentralNotice projects targeted by the campaign.
            (Omit for campaigns targeting all projects.)
        :param list languages: Language codes of the languages targeted by the campaign.
            (Omit for campaigns targeting all languages.)
        :param list countries: Country codes of the countries targeted by the
            campaign. (Omit for campaigns that are not geotargeted.)
        :param list devices: Devices targeted by banners assigned to the campaign.
            (Omit for campaigns with banners targeting all devices.)
        """

        # Basic input validation
        if ( ( names is not None ) and ( name_regex is not None ) ):
            raise ValueError( 'name and name_regex cannot both be set.' )

        if ( projects ):
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
        title_parts = []

        if ( self.name_regex ):
            title_parts.append( '/{0}/'.format( self.name_regex ) )

        if ( self.names):
            title_parts.append( self._make_str_for_title( self.names, 'campaigns' ) )

        if ( self.projects ):
            title_parts.append( self._make_str_for_title( self.projects, 'projects' ) )

        if ( self.languages ):
            title_parts.append( self._make_str_for_title( self.languages, 'languages' ) )

        if ( self.countries ):
            title_parts.append( self._make_str_for_title( self.countries, 'countries' ) )

        if ( self.devices ):
            title_parts.append( self._make_str_for_title( self.devices, 'devices' ) )

        return ', '.join( title_parts )


    def default_projects( self ):
        return list( cna.config[ 'project_lang_url_selection' ].keys() )


    def _make_str_for_title( self, spec, plural_name ):
            l = len( spec )
            if ( l > 1 ):
                return '{0} {1}'.format( l, plural_name )

            return spec[0]
