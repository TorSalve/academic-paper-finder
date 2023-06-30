import inspect
import re
import os
import sys
import progressbar
from urllib import parse
import io
import json
import random


def sleep_for_sec(sleep_between_requests):
    if type(sleep_between_requests) == float or type(sleep_between_requests) == int:
        return sleep_between_requests
    low, upp = (
        sleep_between_requests["lower_bound"],
        sleep_between_requests["upper_bound"],
    )
    return random.uniform(low, upp)


def insert_identifier(string, identifier, replace="identifier"):
    return string.replace("{%s}" % str(replace), str(identifier))


def get_dict_field(d, field, default=None):
    def throw():
        if default is None:
            raise ValueError("%s could not be found in dict", field)
        else:
            return default

    if not isinstance(d, dict) and not isinstance(d, list):
        raise Exception(
            f"Should not try to access other than dicts and lists: {type(d)}"
        )

    i = field.find(".")
    if i > -1:
        key = field[0:i]
        if key == "*" and isinstance(d, list):
            res = []
            for value in d:
                res.append(get_dict_field(value, field[i + 1 :]))
            return res
        elif isinstance(d, list):
            try:
                index = int(key)
                return get_dict_field(d[index], field[i + 1 :])
            except:
                return throw()
        if key not in d:
            return throw()
        return get_dict_field(d[key], field[i + 1 :])

    if field not in d:
        return throw()
    return d[field]


def check_file_exists(file_path):
    return os.path.exists(file_path)


def strip_html(html):
    return re.sub(r"<[^<]+?>", "", html)


def safe_csv(item):
    if type(item) == int:
        return item
    if type(item) == list:
        return list(map(safe_csv, item))
    item = strip_html(item)
    item = item.replace("\n", " ")
    return item


def safe_filename(filename):
    return re.sub(r"[^\.\w\d-]", "_", filename)


def ensure_path_exists(file_path, is_directory=False):
    if is_directory:
        directory = file_path
    else:
        directory = os.path.dirname(file_path)
    try:
        os.stat(directory)
    except:
        os.makedirs(directory)


def unique(l):
    unique_list = []
    for x in l:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def flatten(l):
    if not any(isinstance(el, list) for el in l):
        return l
    return [item for sublist in l for item in sublist]


def console_up():
    # My terminal breaks if we don't flush after the escape-code
    sys.stdout.write("\x1b[1A")
    sys.stdout.flush()


def console_down():
    # I could use '\x1b[1B' here, but newline is faster and easier
    sys.stdout.write("\n")
    sys.stdout.flush()


def get_progressbar(maxval, obj="papers", function="Fetching"):
    widgets = [
        f"{function} {obj}: ",
        "[",
        progressbar.Counter(),
        "/",
        str(maxval),
        "] ",
        "[",
        progressbar.Timer(),
        "] ",
        progressbar.Bar(),
        " (",
        progressbar.ETA(),
        ") ",
    ]
    return progressbar.ProgressBar(maxval=maxval, widgets=widgets)


def file_name_from_url(url, content_disposition=None, file_ext=".pdf"):
    default = url.rsplit("/", 1)[1]
    if not default.endswith(file_ext):
        default = default + file_ext
    if not content_disposition:
        return default
    fname = re.findall("filename=(.+)", content_disposition)
    if len(fname) == 0:
        return default
    return fname[0]


def url_domain(url):
    return parse.urlparse(url).netloc


def url_scheme(url):
    return parse.urlparse(url).scheme


def url_path(url):
    return parse.urlparse(url).path


def url_base(url):
    return "%s://%s" % (url_scheme(url), url_domain(url))


def url_query(url):
    return dict(parse.parse_qsl(parse.urlsplit(url).query))


def url_base_with_path(url):
    return "%s%s" % (url_base(url), url_path(url))


def read_file(file_path):
    ensure_path_exists(file_path)
    with io.open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(file_path, file_content):
    ensure_path_exists(file_path)
    with io.open(file_path, "w", encoding="utf-8") as f:
        if isinstance(file_content, dict):
            file_content = json.dumps(file_content)
        f.write(file_content)


def read_json_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def write_json_file(file_path, dictionary):
    ensure_path_exists(file_path)
    with open(file_path, "w") as f:
        json.dump(dictionary, f)
