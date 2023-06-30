import helpers as h


class SearchQuery:
    def __init__(self, term={}, year={}, publication={}, additional_fields={}):
        self.query = {}

        pass

    def get_query(self):
        return self.query


def analyze(item, query):
    """Analyses a query on an object.

    Args:
        item (dict): The dict to look in.
        query (dict): Query of "must", "should", and "match". Inspired by ElasticSearch (https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html).

    Raises:
        Exception: Thrown if "match" queries have more that one item.
        Exception: Thrown if the search key is not in the object

    Returns:
        bool: returns the result of the query.
    """
    should = h.get_dict_field(query, "should", [])
    _should = []
    for s in should:
        _should.append(analyze(item, s))
    bShould = len(should) == 0 or any(_should)

    must = h.get_dict_field(query, "must", [])
    _must = []
    for s in must:
        _must.append(analyze(item, s))
    bMust = len(must) == 0 or all(_must)

    match = h.get_dict_field(query, "match", {})
    if len(match) > 1:
        raise Exception(f"match should not be longer than 1, found {len(match)} items")
    for key in match:
        if key not in item:
            raise Exception(f"could not find {key} in desired item")
        f = search_for(item, key, match[key])
        # print(key, match[key], f, item[key], "\n", sep=", ")
        return f

    return bMust and bShould


def search_for(obj, look_in, look_for):
    string = obj[look_in]
    return string.find(look_for.replace("*", "")) > -1
