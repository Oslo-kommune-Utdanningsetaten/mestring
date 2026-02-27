import re


def camelize_path_parameter_variables(result, generator, **kwargs):
    """
    drf-spectacular postprocessing hook that updates path template variables
    to match their camelized parameter names.

    The `camelize_serializer_fields` hook camelizes parameter names (e.g.
    org_number → orgNumber) but leaves path templates unchanged
    (e.g. /api/foo/{org_number}/). This causes a mismatch in generated
    API clients that use the camelized name as the object key but the
    snake_case template variable for URL construction.

    This hook builds a rename map from each path's "in: path" parameters
    and replaces the template variables in the path string accordingly.
    """
    new_paths = {}
    for path, path_item in result.get("paths", {}).items():
        rename_map = {}  # old_name -> new_name
        for method_detail in path_item.values():
            if not isinstance(method_detail, dict):
                continue
            for param in method_detail.get("parameters", []):
                if param.get("in") == "path":
                    param_name = param["name"]
                    # Find the matching template variable (snake_case version)
                    snake = re.sub(
                        r"([A-Z])", lambda m: "_" + m.group(1).lower(), param_name
                    )
                    if snake != param_name and f"{{{snake}}}" in path:
                        rename_map[snake] = param_name

        new_path = path
        for old_name, new_name in rename_map.items():
            new_path = new_path.replace("{" + old_name + "}", "{" + new_name + "}")
        new_paths[new_path] = path_item

    result["paths"] = new_paths
    return result
