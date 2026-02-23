def get_request_param(query_params, name: str):
    """
    Return a tuple:
    The python value of a query parameter, or None if the parameter is missing, empty, or only whitespace.
    A boolean indicating whether the parameter was present in the query parameters.
    """
    is_key_present = name in query_params
    value = query_params.get(name)
    if value is None:
        return None, is_key_present
    value = value.strip()
    if value == '':
        return None, is_key_present
    if value.lower() == 'false':
        return False, is_key_present
    if value.lower() == 'true':
        return True, is_key_present
    return value, is_key_present
