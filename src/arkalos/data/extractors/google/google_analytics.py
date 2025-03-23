
# Useful Resources:
# https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema
# https://ga-dev-tools.google/ga4/dimensions-metrics-explorer/

from typing import Any, TYPE_CHECKING
import re
import math

from google.analytics.data_v1beta.types import (
    DateRange, 
    Dimension, 
    Metric, 
    RunReportRequest, 
    OrderBy,
    Filter,
    FilterExpression
)

from arkalos.utils.url import URL
from arkalos.utils.dict_utils import add_count_col, sort_by_col
from arkalos.utils.math_utils import asym_gaussian
from arkalos.utils.str_utils import snake
from arkalos.services.google_service import (
    GoogleService,
    AnalyticsAdminServiceClient,
    BetaAnalyticsDataClient
)
if TYPE_CHECKING:
    from arkalos.services.google_stubs.searchconsole.v1 import SearchConsoleResource



class GoogleAnalytics:

    # Industry categories are defined here:
    # from google.analytics.admin_v1beta import IndustryCategory
    GA_INDUSTRY_CATEGORIES = {
        0: None,
        1: 'Automotive',
        2: 'Business and industrial markets',
        3: 'Finance',
        4: 'Healthcare',
        5: 'Technology',
        6: 'Travel',
        7: 'Other',
        8: 'Arts and entertainment',
        9: 'Beauty and fitness',
        10: 'Books and literature',
        11: 'Food and drink',
        12: 'Games',
        13: 'Hobbies and leisure',
        14: 'Home and garden',
        15: 'Internet and telecom',
        16: 'Law and government',
        17: 'News',
        18: 'Online communities',
        19: 'People and society',
        20: 'Pets and animals',
        21: 'Real estate',
        22: 'Reference',
        23: 'Science',
        24: 'Sports',
        25: 'Jobs and education',
        26: 'Shopping'
    }

    GSC_DIMENSION_QUERY = 'query'
    GSC_DIMENSION_PAGE = 'page'

    service: GoogleService
    searchConsole: 'SearchConsoleResource'
    analytics: BetaAnalyticsDataClient
    analyticsAdmin: AnalyticsAdminServiceClient



    def __init__(self, service: GoogleService):
        self.service = service
        self.searchConsole = self.service.searchConsole()
        self.analytics = self.service.analytics()
        self.analyticsAdmin = self.service.analyticsAdmin()



    @staticmethod
    def calcCTROppScore(clicks: int, impressions: int, position: float = 1.0) -> float:
        k = asym_gaussian(position, 0.001, 0.005, 10, 3, 15)
        return round(100 * (1 - math.exp(-k * (impressions / (clicks + 1)))), 1)



    ###########################################################################
    # GOOGLE ANALYTICS 4                                                      #
    ###########################################################################

    # GA4 private

    def _formatPropertyId(self, property_id: str|int) -> str:
        '''Format property ID to the required format.'''
        property_id_str = str(property_id)
        if not property_id_str.startswith('properties/'):
            property_id_str = f'properties/{property_id_str}'
        return property_id_str
    
    def _createDimensions(self, dimensions: list[str]) -> list[Dimension]:
        '''Convert list of dimension names to Dimension objects.'''
        return [Dimension(name=dim) for dim in dimensions]
    
    def _createMetrics(self, metrics: list[str]) -> list[Metric]:
        '''Convert list of metric names to Metric objects.'''
        return [Metric(name=metric) for metric in metrics]
    
    def _createOrderBy(self, metric_name: str, descending: bool = True) -> list[OrderBy]:
        '''Create OrderBy object for a metric.'''
        return [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=metric_name), desc=descending)]

    def _extractDomain(self, url: str) -> str|None:
        url = url.replace('sc-domain:', '')
        return URL(url).hostname
    
    def _extractPath(self, url: str) -> str:
        return URL(url).pathname
    
    def _convertToSnakeCase(self, name: str) -> str:
        '''Convert camelCase or PascalCase to snake_case.'''
        # Insert underscore before uppercase letters and lowercase the result
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def fetchReport(self, 
        property_id: str|int,
        date_from: str,
        date_to: str,
        dimensions: list[str],
        metrics: list[str],
        order_by_metric: str|None = None,
        descending: bool = True,
        dimension_filter: FilterExpression | None = None,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        '''
        Run a report with the given parameters and return formatted results.
        
        Args:
            property_id: The Google Analytics property ID
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            dimensions: List of dimension names
            metrics: List of metric names
            order_by_metric: Optional metric name to order by
            descending: Whether to sort in descending order
            dimension_filter: Optional filter expression for dimensions
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing the formatted report data
        '''
        property_id_str = self._formatPropertyId(property_id)
        dimension_objects = self._createDimensions(dimensions)
        metric_objects = self._createMetrics(metrics)
        
        request = RunReportRequest(
            property=property_id_str,
            date_ranges=[DateRange(start_date=date_from, end_date=date_to)],
            dimensions=dimension_objects,
            metrics=metric_objects,
            limit=limit
        )
        
        if order_by_metric:
            request.order_bys = self._createOrderBy(order_by_metric, descending)
        
        if dimension_filter:
            request.dimension_filter = dimension_filter
        
        response = self.analytics.run_report(request)
        
        result = []

        for row in response.rows:
            row_data: dict[str, Any] = {}
            
            # Add dimension values with snake_case keys
            for i, dimension in enumerate(row.dimension_values):
                snake_key = snake(dimensions[i])
                row_data[snake_key] = dimension.value
                
                # Add derived columns for URL dimensions
                if dimensions[i] == 'hostName' and dimension.value:
                    row_data['domain'] = self._extractDomain(dimension.value)

                if dimensions[i] == 'pagePath' and dimension.value:
                    row_data['page_path'] = self._extractPath(dimension.value)
            
            # Add metric values with snake_case keys
            for i, metric in enumerate(row.metric_values):
                value = metric.value
                snake_key = snake(metrics[i])
                
                # Convert to appropriate type based on common metrics
                int_metrics = [
                    'screenPageViews', 
                    'activeUsers', 
                    'totalUsers', 
                    'userEngagementDuration',
                    'eventCount',
                    'sessions',
                    'engagedSessions',
                    'conversions',
                ]
                float_metrics = [
                    'engagementRate',
                    'averageSessionDuration',
                    'bounceRate',
                    'eventCountPerUser',
                ]
                if metrics[i] in int_metrics:
                    row_data[snake_key] = int(value)
                elif metrics[i] in float_metrics:
                    row_data[snake_key] = round(float(value), 1)
                else:
                    # Default to string for unknown metrics
                    row_data[snake_key] = value
            
            result.append(row_data)
        
        return result


    # GA4 public

    def listProperties(self):
        properties_list = []
        response = self.analyticsAdmin.list_account_summaries()
        for account_summary in response:
            account_name = account_summary.display_name
            for property_summary in account_summary.property_summaries:
                property_id = property_summary.property.split('/')[-1]
                property_name = property_summary.display_name
                property_resource = self.analyticsAdmin.get_property(name=f'properties/{property_id}')
                url = None
                domain = None
                prop_dict = {
                    'property_id': int(property_id),
                    'property_name': property_name,
                    'account_name': account_name,
                    'url': url,
                    'domain': domain,
                    'last_data_received': None,
                    'created_at': property_resource.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': property_resource.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'timezone': property_resource.time_zone,
                    'currency': property_resource.currency_code,
                    'industry_category_id': property_resource.industry_category,
                    'industry_category_name': GoogleAnalytics.GA_INDUSTRY_CATEGORIES.get(property_resource.industry_category) if property_resource.industry_category is not None else None
                }
                streams_response = self.analyticsAdmin.list_data_streams(parent=f'properties/{property_id}')
                latest_update = None
                for stream in streams_response:
                    if stream.web_stream_data and stream.web_stream_data.measurement_id:
                        if stream.web_stream_data.default_uri:
                            url = stream.web_stream_data.default_uri
                            prop_dict['url'] = url
                            domain = re.sub(r'^(https?://)?(www\.)?', '', url).split('/')[0]
                            prop_dict['domain'] = domain
                    if stream.update_time:
                        stream_update = stream.update_time
                        if not latest_update or stream_update > latest_update:
                            latest_update = stream_update
                if latest_update:
                    prop_dict['last_data_received'] = latest_update.strftime('%Y-%m-%d %H:%M:%S')
                properties_list.append(prop_dict)
        
        #properties_list.sort(key=lambda x: x['last_data_received'] or '0000-00-00 00:00:00', reverse=True)
        properties_list = sort_by_col(properties_list, 'last_data_received', True)
        return properties_list



    def fetchPages(self, 
        property_id: str | int,
        date_from: str,
        date_to: str,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        '''
        Retrieve comprehensive data about top pages, including performance metrics.
        
        Args:
            property_id: The Google Analytics property ID
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing page performance data
        '''
        dimensions = [
            'hostName',
            'pagePath',
            # 'pageTitle',
            # 'fullPageUrl',
            # 'percentScrolled',
            # 'deviceCategory',
            # 'cityId',
            # 'city',
            # 'country'
        ]
        
        metrics = [
            'screenPageViews',
            'activeUsers',
            'totalUsers',
            'engagementRate',
            'userEngagementDuration',
            'averageSessionDuration',
            'bounceRate',
            'eventCount',
            # The request's dimensions & metrics are incompatible.
            # 'organicGoogleSearchAveragePosition',
            # 'organicGoogleSearchClickThroughRate',
            # 'organicGoogleSearchClicks',
            # 'organicGoogleSearchImpressions'
        ]
        
        return self.fetchReport(
            property_id=property_id,
            date_from=date_from,
            date_to=date_to,
            dimensions=dimensions,
            metrics=metrics,
            order_by_metric='screenPageViews',
            descending=True,
            limit=limit
        )



    def fetchTrafficStats(self,
        property_id: str | int,
        date_from: str,
        date_to: str,
        limit: int = 1000
    ) -> list[dict[str, Any]]:
        '''
        Retrieve traffic stats (source, medium, device, country) data from Google Analytics 4.
        
        Args:
            property_id: The Google Analytics property ID
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing search performance data
        '''
        dimensions = [
            'sessionSource',
            'sessionMedium',
            # 'landingPage',
            'deviceCategory',
            'country'
        ]
        
        metrics = [
            'sessions',
            'engagedSessions',
            'averageSessionDuration',
            'bounceRate',
            'conversions',
            'totalUsers',
        ]
        
        # Create a filter for search traffic only
        # source_filter = FilterExpression(
        #     filter=Filter(
        #         field_name='sessionSource',
        #         string_filter=Filter.StringFilter(
        #             match_type=Filter.StringFilter.MatchType.CONTAINS,
        #             value='google'
        #         )
        #     )
        # )
        
        return self.fetchReport(
            property_id=property_id,
            date_from=date_from,
            date_to=date_to,
            dimensions=dimensions,
            metrics=metrics,
            order_by_metric='sessions',
            descending=True,
            # dimension_filter=source_filter,
            limit=limit
        )



    def fetchAdsSearchQueries(self,
        property_id: str | int,
        date_from: str,
        date_to: str,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        '''
        Retrieve data about Google Ads search queries.
        
        Args:
            property_id: The Google Analytics property ID
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing Google Ads search query data
        '''
        dimensions = [
            'sessionGoogleAdsQuery',
            'sessionSource',
            'sessionMedium',
            'sessionCampaignName'
        ]
        
        metrics = [
            'sessions',
            'conversions',
            'engagementRate',
            'sessionConversionRate',
            'averageSessionDuration'
            
        ]
        
        return self.fetchReport(
            property_id=property_id,
            date_from=date_from,
            date_to=date_to,
            dimensions=dimensions,
            metrics=metrics,
            order_by_metric='sessions',
            descending=True,
            limit=limit
        )



    def fetchInternalSiteSearch(self,
        property_id: str | int,
        date_from: str,
        date_to: str,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        '''
        Retrieve internal site search data from Google Analytics 4.
        
        Note: This requires that site search tracking is set up in your GA4 property.
        
        Args:
            property_id: The Google Analytics property ID
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing internal search data
        '''
        dimensions = [
            'searchTerm',
        ]
        
        metrics = [
            'screenPageViews',
            'activeUsers',
            'totalUsers',
            'engagementRate',
            'userEngagementDuration',
            'averageSessionDuration',
            'bounceRate',
            'eventCount',
        ]
        
        return self.fetchReport(
            property_id=property_id,
            date_from=date_from,
            date_to=date_to,
            dimensions=dimensions,
            metrics=metrics,
            order_by_metric='screenPageViews',
            descending=True,
            limit=limit
        )


    def fetchEvents(self,
        property_id: str | int,
        date_from: str,
        date_to: str,
        page_path: str | None = None,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        '''
        Retrieve data about events that occurred on specific pages.
        
        Args:
            property_id: The Google Analytics property ID
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            page_path: Filter events to a specific page path. If None, returns events across all pages.
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing event data for the specified page(s)
        '''
        dimensions = [
            'eventName',
        ]
        
        metrics = [
            'eventCount',
            'eventCountPerUser',
            'screenPageViews',
            'activeUsers',
            'totalUsers',
            'engagementRate',
            'userEngagementDuration',
            'averageSessionDuration',
            'bounceRate',
        ]
        
        # Add page path filter if specified
        dimension_filter = None
        if page_path:
            dimension_filter = FilterExpression(
                filter=Filter(
                    field_name='pagePath',
                    string_filter=Filter.StringFilter(
                        value=page_path,
                        match_type=Filter.StringFilter.MatchType.EXACT
                    )
                )
            )
        
        return self.fetchReport(
            property_id=property_id,
            date_from=date_from,
            date_to=date_to,
            dimensions=dimensions,
            metrics=metrics,
            order_by_metric='eventCount',
            descending=True,
            dimension_filter=dimension_filter,
            limit=limit
        )
    




    ###########################################################################
    # GOOGLE SEARCH CONSOLE                                                   #
    ###########################################################################

    def listGSCSites(self) -> list|str:
        '''List all Google Search Console sites accessible to your account.'''
        response = self.searchConsole.sites().list().execute()
        return [site['siteUrl'] for site in response.get('siteEntry', [])]



    def _queryGSC(self, 
        site: str, 
        start_date: str, 
        end_date: str, 
        dimension: str,
        page: str|None = None,
        search_query: str|None = None,
        limit: int = 50, 
        filters = None
    ) -> list[dict]:
        '''
        Generic GSC query function.
        
        Args:
            site: Site domain to query (from listGSCSites())
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            dimension: constant of the class GSC_DIMENSION_...
            page: for query searches, set page column
            search_query: for page searchers, set query column
            limit: Maximum number of rows to return (default 100)
            filters: Optional filters to apply
            
        Returns:
            List of result rows
        '''
        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': [dimension],
            # GSC API sorts only by Clicks, but not Impressions and Position
            # Fetch more data over the network to get more accurate data
            # Which is closer to the one seen inside the web console
            # But sort manually and return first <limit> rows
            'rowLimit': 1000
        }
        
        if filters:
            request['dimensionFilterGroups'] = [{'filters': filters}]
        
        try:
            response = self.searchConsole.searchanalytics().query(
                siteUrl=site, 
                body=request # type: ignore
            ).execute()
            
            rows = response.get('rows', [])

            data = []
            for row in rows:
                clicks = int(row['clicks'])
                impr = int(row['impressions'])
                ctr = round(row['ctr'] * 100, 1)  # Convert to percentage
                pos = round(row['position'], 1)

                obj: dict[str, Any] = {}
                obj['site'] = site
                # Get domain from site str
                obj['domain'] = self._extractDomain(site)
                
                if (dimension == GoogleAnalytics.GSC_DIMENSION_QUERY):
                    obj['page_url'] = page
                    # Remove domain from URL
                    obj['page_path'] = self._extractPath(page) if page else None
                    obj['search_query'] = row['keys'][0]
                else:
                    obj['page_url'] = row['keys'][0]
                    obj['page_path'] = self._extractPath(row['keys'][0])
                    if search_query:
                        obj['search_query'] = search_query
                obj['clicks'] = clicks
                obj['impressions'] = impr
                obj['ctr'] = ctr
                obj['position'] = pos
                obj['ctr_os'] = GoogleAnalytics.calcCTROppScore(clicks, impr, pos)
                
                data.append(obj)

            data = sort_by_col(data, {
                'clicks': True,
                'impressions': True,
                'position': False
            })

            return data[:limit]

        except Exception as e:
            print(f'Error querying GSC for {site}: {str(e)}')
            return []
    


    def fetchTopGSCPages(self, 
        site: str, 
        start_date: str, 
        end_date: str, 
        search_query: str|None = None, 
        limit: int = 50
    ) -> list[dict]:
        '''
        Fetch top pages by clicks.
        
        Args:
            site: Site URL
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            search_query: optional filter, if provided return only pages with this query
            limit: Maximum number of results to return
            
        Returns:
            List of objects
        '''
        filters = None
        if search_query is not None:
            filters = [{'dimension': 'query', 'expression': search_query}]

        return self._queryGSC(
            site, 
            start_date, 
            end_date, 
            GoogleAnalytics.GSC_DIMENSION_PAGE, 
            search_query=search_query, 
            limit=limit, 
            filters=filters
        )
    
    def fetchTopGSCQueries(self, 
        site: str, 
        start_date: str, 
        end_date: str, 
        page: str|None = None, 
        limit: int = 50
    ) -> list[dict]:
        '''
        Fetch top search queries by clicks.
        
        Args:
            site: Site URL
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            page: optional filter, if provided return queries only for this page
            limit: Maximum number of results to return
            
        Returns:
            List of keyword objects
        '''
        filters = None
        if page is not None:
            filters = [{'dimension': 'page', 'expression': page}]

        return self._queryGSC(
            site, 
            start_date, 
            end_date, 
            GoogleAnalytics.GSC_DIMENSION_QUERY, 
            page=page, 
            limit=limit, 
            filters=filters
        )
    

    def _getGSCStats(self, site, start_date, end_date, pages_first, page_limit, query_limit, with_sections):
        top_results = None
        if pages_first:
            top_results = self.fetchTopGSCPages(site, start_date, end_date, limit=page_limit)
        else:
            top_results = self.fetchTopGSCQueries(site, start_date, end_date, limit=query_limit)
    
        data = []
        data_sections = {}
        for res_data in top_results:
            page_or_query = None
            if pages_first:
                page_or_query = res_data['page_url']
            else:
                page_or_query = res_data['search_query']
            if with_sections:
                res = None
                if pages_first:
                    res = self.fetchTopGSCQueries(site, start_date, end_date, page_or_query, query_limit)
                else:
                    res = self.fetchTopGSCPages(site, start_date, end_date, page_or_query, limit=page_limit)
                res = sort_by_col(res, {
                    'clicks': True,
                    'impressions': True,
                    'position': False
                })
                res = add_count_col(res, 'search_query')
                res = add_count_col(res, 'page_url')
                data_sections[page_or_query] = res
            else:
                if pages_first:
                    data += self.fetchTopGSCQueries(site, start_date, end_date, page_or_query, query_limit)
                else:
                    data += self.fetchTopGSCPages(site, start_date, end_date, page_or_query, limit=page_limit)

        if with_sections:
            return data_sections
        
        data = sort_by_col(data, {
            'clicks': True,
            'impressions': True,
            'position': False
        })
        data = add_count_col(data, 'search_query')
        data = add_count_col(data, 'page_url')
        return data

    def fetchTopGSCPagesThenQueries(
            self, 
            site: str, 
            start_date: str, 
            end_date: str, 
            page_limit: int = 50, 
            query_limit: int = 50, 
            with_sections: bool = False
    ) -> list[dict] | dict[str, list[dict]]:
        '''
        Fetch top pages first and then - top search queries for each page
        
        Args:
            site: Site URL
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            page_limit: Maximum number of pages to fetch
            query_limit: Maximum number of search queries per page
            with_sections: provide True if results shall be nested in a dict
            
        Returns:
            List of dicts
            Dict with list of dicts - if with_sections is provided. The key is the page URL
        '''

        return self._getGSCStats(
            site, 
            start_date, 
            end_date, 
            True, 
            page_limit, 
            query_limit, 
            with_sections
        )
    

    def fetchTopGSCQueriesThenPages(
            self, 
            site: str, 
            start_date: str, 
            end_date: str, 
            query_limit: int = 100, 
            page_limit: int = 50, 
            with_sections: bool = False
    ) -> list[dict] | dict[str, list[dict]]:
        '''
        Fetch top search queries first and then - top pages for each query
        
        Args:
            site: Site URL
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            query_limit: Maximum number of search queries to fetch
            page_limit: Maximum number of pages per query
            with_sections: provide True if results shall be nested in a dict
            
        Returns:
            List of dicts
            Dict with list of dicts - if with_sections is provided. The key is a search query
        '''
        return self._getGSCStats(
            site, 
            start_date, 
            end_date, 
            False, 
            page_limit, 
            query_limit, 
            with_sections
        )
    
    


