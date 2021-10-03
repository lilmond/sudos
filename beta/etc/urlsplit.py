import collections

def split_url(url: str) -> "URLObject":
    try:
        protocol, domain = url.split("://", 1)
    except Exception:
        return

    try:
        domain, path = domain.split("/", 1)
    except Exception:
        path = ""

    try:
        domain, port = domain.split(":", 1)
        port = int(port)
    except Exception:
        if protocol == "https": port = 443
        else: port = 80

    try:
        path, fragments = path.split("#", 1)
    except Exception:
        fragments = None

    try:
        path, parameters = path.split("?", 1)
    except Exception:
        parameters = None

    url_dict = {}
    url_dict["protocol"] = protocol
    url_dict["domain"] = domain
    url_dict["port"] = port
    url_dict["path"] = f"/{path}"
    url_dict["parameters"] = parameters
    url_dict["fragments"] = fragments

    url_structure = collections.namedtuple("URLObject", "protocol domain port path parameters fragments")
    url_object = url_structure(**url_dict)

    return url_object
