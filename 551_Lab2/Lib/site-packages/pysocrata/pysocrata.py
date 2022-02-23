"""
Implements the socrata-reducer Client class and the Pythonic dataset lister.

The raw JSON endpoint, accessed by appending "data.json" to the end of a portal's base URI (for example,
New York City's is at http://nycopendata.socrata.com/data.json) provides metadata about every dataset (according to
one definition of the term, there are several but this is the one we stick with here) on a Socrata portal. In the
case of the New York City open data portal, for example, this endpoint returns 1500 entities---the number that we
keep on the page as an introductory banner.

Not everything on an open data portal is a dataset. Charts, for example, aren't in anyone's definition of one,
but they nevertheless take up a URI on the portal and have a unique hash that you can link to and find them
with---in technical terms they are an "endpoint".

The Socrata Catalog API (http://labs.socrata.com/docs/search.html), by contrast, provides metadata about
individual *endpoints*. It provides more and better information, with one critical shortcoming: all maps on the
portal are returned as "maps", whether or not they are derived from a separate dataset (in which case they are
clearly not classifiable as datasets proper) or are simply visual wrappers of an underlying geospatial file (in which
case they clearly are).

The raw JSON endpoint *does* make this distinction, so to get a proper count we query both endpoints, scrape the data
off of them, and then match raw JSON datasets with Catalog API datasets, and throw out what's left out.

This is e.g. how the count returned by `get_dataset_counts.py` is implemented. Note that since these two data sources
are very slightly out of date with one another (for reasons indeterminate) there is also an artifical "new" column for
datasets which are missing when the two endpoint sets are matched.
"""
import requests
from collections import Counter


def get_endpoints_using_raw_json_emission(domain):
    """
    Implements a raw HTTP GET against the entire Socrata portal for the domain in question. This method uses the
    first of the two ways of getting this information, the raw JSON endpoint.

    Parameters
    ----------
    domain: str
        A Socrata data portal domain. "data.seattle.gov" or "data.cityofnewyork.us" for example.

    Returns
    -------
    Portal dataset metadata from the JSON endpoint.
    """
    uri = "http://{0}/data.json".format(domain)
    r = requests.get(uri)
    r.raise_for_status()
    return r.json()


def get_endpoints_using_catalog_api(domain, token):
    """
    Implements a raw HTTP GET against the entire Socrata portal for the domain in question. This method uses the
    second of the two ways of getting this information, the catalog API.

    Parameters
    ----------
    domain: str
        A Socrata data portal domain. "data.seattle.gov" or "data.cityofnewyork.us" for example.
    token: str
        A Socrata application token. Application tokens can be registered by going onto the Socrata portal in
        question, creating an account, logging in, going to developer tools, and spawning a token.

    Returns
    -------
    Portal dataset metadata from the catalog API.
    """
    # Token required for all requests. Providing login info instead is also possible but I didn't implement it.
    headers = {"X-App-Token": token}

    # The API will return only 100 requests at a time by default. We can ask for more, but the server seems to start
    # to lag after a certain N requested. Instead, let's pick a less conservative pagination limit and spool up with
    # offsets.
    #
    # At the time this library was written, Socrata would return all of its results in a contiguous list. Once you
    # maxed out, you wouldn't get any more list items. Later on this was changed so that now if you exhaust portal
    # entities, it will actually take you back to the beginning of the list again!
    #
    # As a result we need to perform our own set-wise check to make sure that what we get isn't just a bit of the
    # same list all over again.
    uri = "http://api.us.socrata.com/api/catalog/v1?domains={0}&offset={1}&limit=1000"
    ret = []
    endpoints_thus_far = set()
    offset = 0

    while True:
        try:
            r = requests.get(uri.format(domain, offset), headers=headers)
            r.raise_for_status()
        except requests.HTTPError:
            raise requests.HTTPError("An HTTP error was raised during Socrata API ingestion.".format(domain))
        data = r.json()

        endpoints_returned = {r['resource']['id'] for r in data['results']}
        new_endpoints = endpoints_returned.difference(endpoints_thus_far)

        if len(new_endpoints) >= 999:  # we are continuing to stream
            # TODO: 999 not 1000 b/c the API suffers off-by-one errors. Can also do worse, however. Compensate?
            # cf. https://github.com/ResidentMario/pysocrata/issues/1
            ret += data['results']
            endpoints_thus_far.update(new_endpoints)
            offset += 1000
            continue
        else:  # we are ending on a stream with some old endpoints on it
            ret += [r for r in data['results'] if r['resource']['id'] in new_endpoints]
            break

    return ret


def get_resources(domain, token):
    """
    Returns a list of resources (data endpoints) on a Socrata domain.

    The catalog API and JSON endpoint both return useful information, but the information that they return is useful
    in slightly different ways. The JSON endpoint provides less information about the resource in question,
    including lacking a field for what *type* of resources the entity in question is, but has the advantage of
    returning only data resources (endpoints of other things, like charts and filters, are excluded). The catalog API
    provides more information, and does so for all endpoints, but provides no way of filtering that set down to
    resources only because of issues with its categorization of "map" entities.

    Hence, to capture the actual data resources on the portal, we match the APIs against one another.

    Note that it is technically possible for a resource to be published as a filter or view of a private endpoint.
    This method does not capture resources published in this (highly discouraged, but nevertheless occasionally
    practiced) manner.

    Also note that this method does not filter out resources with a community provenance. You can filter these out
    yourself downstream using the `provenance` metadata field.

    Parameters
    ----------
    domain: str
        A Socrata data portal domain. "data.seattle.gov" or "data.cityofnewyork.us" for example.
    token: str
        A Socrata application token. Application tokens can be registered by going onto the Socrata portal in
        question, creating an account, logging in, going to developer tools, and spawning a token.

    Returns
    -------
    A list of metadata stores for all data resources on the domain.
    """
    json_endpoints = get_endpoints_using_raw_json_emission(domain)
    catalog_api_output = get_endpoints_using_catalog_api(domain, token)
    catalog_endpoints = [d['permalink'].split("/")[-1] for d in catalog_api_output]
    json_endpoints = [d['landingPage'].split("/")[-1] for d in json_endpoints['dataset']]
    resources = []
    for i, endpoint in enumerate(json_endpoints):
        try:
            catalog_ind = catalog_endpoints.index(json_endpoints[i])
        except ValueError:  # The catalog does not contain this dataset. Skip it.
            pass
        else:
            resources.append(catalog_api_output[catalog_ind])

    # Exclude stories, which are remixed, not published, data.
    resources = [d for d in resources if d['resource']['type'] != 'story']

    return resources


def count_resources(domain, token):
    """
    Given the domain in question, generates counts for that domain of each of the different data types.

    Parameters
    ----------
    domain: str
        A Socrata data portal domain. "data.seattle.gov" or "data.cityofnewyork.us" for example.
    token: str
        A Socrata application token. Application tokens can be registered by going onto the Socrata portal in
        question, creating an account, logging in, going to developer tools, and spawning a token.

    Returns
    -------
    A dict with counts of the different endpoint types classifiable as published public datasets.
   """
    resources = get_resources(domain, token)
    return dict(Counter([r['resource']['type'] for r in resources if r['resource']['type'] != 'story']))
