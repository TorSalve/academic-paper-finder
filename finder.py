import requests
from urllib import parse
from urllib.parse import urlencode
import re
import json
import PyPDF2
import progressbar
import validators

import pandas as pd

import os
import io
import math
import time
import warnings

import helpers as h
import query


class Fetcher:
    def __init__(
        self,
        search_parameters={},
        load_from={},
        **kwargs,
    ):
        """Initialise the fetcher, geared to fetch a few academic papers.
        Depending on configuration, it searches a provider (library) and downloads .pdfs (if they are open to download on the current network).

        -- Warning. Some providers do not like to be searched.

        Args:
            * search_parameters (dict, optional): The search parameters used to search a particular provider. These are send with the GET or POST HTTP request to the provider. Defaults to {}.
            * load_from (str, optional): each argument is either "cache" or "url". If "cache", the finder will look in the chached folder to find the searched for item (will look online if not found). This is helpful when limiting the number of requests to the provider. If "url", the finder will search online. Arguments default to "cache".
                * list (str): argument for finding the list
                * papers (str): argument for finding the papers
                * pdf (str): argument for downloading the pdfs
            * kwargs: provide additional arguments to augment the finder
                * name (str): Name the finder. The cache folder will be named after this, to make multiple searches possible with different settings. Defaults to "finder".
                * cache_folder (str): The base path of the cache. Defaults to "./cache".
                * headers (dict): Headers for the HTTP request to the provider. Defaults to {}.
                * config_name (str): The configuration to use for this search. The configuration describes how to search the fetched HTML from the provider. Config files should be placed in the ./configs folder. Defaults to the "name" kwarg.
                * restrict_identifiers_to (list): Restict the search to a particular set of identifiers. Helpful when downloading a specific set of .pdfs, for instance. Defaults to [].
        """
        self.load_from = {
            **{"list": "cache", "papers": "cache", "pdf": "cache"},
            **load_from,
        }

        self.name = kwargs.get("name", "finder")
        self.cache_folder = kwargs.get("cache_folder", "./cache")
        self.headers = kwargs.get("headers", {})

        self.search_parameters = search_parameters
        self.config_name = kwargs.get("config_name", self.name)

        config_path = "./configs/%s.json" % self.config_name
        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.list_is_json = self.get_config("urls.list.expect-json", False)
        self.paper_is_json = self.get_config("urls.paper.expect-json", False)
        self.per_page = self.get_config("urls.list.per-page")

        self.preprocessing_paper = self.get_config(
            "preprocessing.paper", []
        ) + kwargs.get("preprocessing_paper", [])
        self.preprocessing_list = self.get_config(
            "preprocessing.list", []
        ) + kwargs.get("preprocessing_list", [])
        self.postprocessing_paper = self.get_config(
            "postprocessing.paper", []
        ) + kwargs.get("postprocessing_paper", [])
        self.postprocessing_list = self.get_config(
            "postprocessing.list", []
        ) + kwargs.get("postprocessing_list", [])

        self.restrict_identifiers_to = kwargs.get("restrict_identifiers_to", [])

    @property
    def header_user_agent(self):
        """The default user-agent header.

        Returns:
            str: A very common user-agent header.
        """
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"

    def list_file_name(self, page):
        """generate the filepath of a searched list to be cached

        Args:
            page (int): The current page we are searching on

        Returns:
            str: the filename
        """
        return "%s/%s/list/%s/%s.html" % (
            self.cache_folder,
            self.config_name,
            self.name,
            "page-%d" % page,
        )

    def paper_file_name(self, identifier):
        """generate the filepath of the found paper to be cached

        Args:
            identifier (str-like): the identifier of the paper. Typically DOI or similar. Will be sanitised.

        Returns:
            str: the filename
        """
        safe_identifier = h.safe_filename(identifier)
        return "%s/%s/papers/%s.html" % (
            self.cache_folder,
            self.config_name,
            safe_identifier,
        )

    def pdf_file_name(self, identifier, only_filename=False):
        """generate the filepath of the to be saved .pdf-file

        Args:
            identifier (str-like): the identifier of the paper. Typically DOI or similar. Will be sanitised.
            only_filename (bool, optional): If True, only returns filename without path. If False, return full path. Defaults to False.

        Returns:
            str: the filename / the filepath
        """
        safe_identifier = h.safe_filename(identifier)
        filename = "%s.pdf" % safe_identifier
        if only_filename:
            return filename
        return "%s/%s/pdfs/%s" % (self.cache_folder, self.config_name, filename)

    def result_file_name(self):
        """generate the filepath of the list of parsed found papers to be cached

        Returns:
            str: the filepath
        """
        return "%s/%s/result_%s.json" % (self.cache_folder, self.config_name, self.name)

    def url_get(self, url, payload={}, headers={}):
        """Make a GET request

        Args:
            url (str): the url to query
            payload (dict, optional): The payload to send. Defaults to {}.
            headers (dict, optional): Request headers. Defaults to {}.

        Returns:
            response: the response
        """
        headers = {"user-agent": self.header_user_agent, **headers}
        return requests.get(h.url_base_with_path(url), headers=headers, params=payload)

    def url_post_json(self, url, payload={}, headers={}):
        """Make a POST request with JSON body

        Args:
            url (str): the url to query
            payload (dict, optional): The payload to send. Defaults to {}.
            headers (dict, optional): Request headers. Defaults to {}.

        Returns:
            response: the response
        """
        headers = {
            "user-agent": self.header_user_agent,
            "accept": "*/*",
            "content-type": "application/json",
            **self.headers,
            **headers,
        }
        return requests.post(
            h.url_base_with_path(url), headers=headers, data=json.dumps(payload)
        )

    def url_post(self, url, payload={}, headers={}):
        """Make a POST request with urlencoded body

        Args:
            url (str): the url to query
            payload (dict, optional): The payload to send. Defaults to {}.
            headers (dict, optional): Request headers. Defaults to {}.

        Returns:
            response: the response
        """
        headers = {
            "user-agent": self.header_user_agent,
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            **self.headers,
            **headers,
        }
        return requests.post(h.url_base_with_path(url), headers=headers, data=payload)

    def ensure_cache_folder_exists(self):
        if not h.check_file_exists(self.cache_folder):
            os.mkdir(self.cache_folder)

    def paper_file_exists(self, identifier):
        return h.check_file_exists(self.paper_file_name(identifier))

    def pdf_file_exists(self, identifier):
        return h.check_file_exists(self.pdf_file_name(identifier))

    def list_file_exists(self, page):
        return h.check_file_exists(self.list_file_name(page))

    def fetch_list(self, page):
        if self.load_from["list"] == "cache":
            if self.list_file_exists(page):
                return self.from_cache(self.list_file_name(page), self.list_is_json)
            else:
                return self.from_url_list(page)
        elif self.load_from["list"] == "url":
            return self.from_url_list(page)
        else:
            raise Exception("load_from['list'] could not be found")

    def fetch_paper(self, identifier):
        if self.load_from["papers"] == "cache":
            if self.paper_file_exists(identifier):
                return self.from_cache(
                    self.paper_file_name(identifier), self.paper_is_json
                )
            else:
                return self.from_url_paper(identifier)
        elif self.load_from["papers"] == "url":
            return self.from_url_paper(identifier)
        else:
            raise Exception("load_from['papers'] could not be found")

    def fetch_pdf(self, identifier):
        if self.load_from["pdf"] == "cache":
            if self.pdf_file_exists(identifier):
                with open(self.pdf_file_name(identifier), "rb") as f:
                    return f.read()
            else:
                return self.from_url_pdf(identifier)
        elif self.load_from["pdf"] == "url":
            return self.from_url_pdf(identifier)
        else:
            raise Exception("load_from['pdf'] could not be found")

    def from_cache(self, path, is_json):
        html = h.read_file(path)
        should_not_be_decoded = not is_json or isinstance(html, dict)
        return html if should_not_be_decoded else json.loads(html)

    def from_url_pdf(self, identifier):
        r = requests.get(self.pdf_url(identifier))
        file_name = self.pdf_file_name(identifier)
        h.ensure_path_exists(file_name)
        with open(file_name, "wb") as f:
            f.write(r.content)
        sleep_for = h.sleep_for_sec(self.get_config("sleep_between_requests"))
        time.sleep(sleep_for)
        return r.content

    def from_url_list(self, page):
        html = self.fetch_list_from_url(page)
        h.write_file(self.list_file_name(page), html)
        shouldNotBeDecoded = not self.list_is_json or isinstance(html, dict)
        sleep_for = h.sleep_for_sec(self.get_config("sleep_between_requests"))
        time.sleep(sleep_for)
        return html if shouldNotBeDecoded else json.loads(html)

    def from_url_paper(self, identifier):
        html = self.fetch_paper_from_url(identifier)
        h.write_file(self.paper_file_name(identifier), html)
        shouldNotBeDecoded = not self.paper_is_json or isinstance(html, dict)
        sleep_for = h.sleep_for_sec(self.get_config("sleep_between_requests"))
        time.sleep(sleep_for)
        return html if shouldNotBeDecoded else json.loads(html)

    def re_list(self, pattern, html):
        if len(pattern) == "":
            return []
        return h.unique(
            map(
                lambda s: h.strip_html(s).replace("\n", " ").strip(),
                re.findall(pattern, html),
            )
        )

    def re_item(self, pattern, html):
        if len(pattern) == "":
            return ""
        find = re.findall(pattern, html)
        if len(find) <= 0:
            return ""
        f = find[0] if not isinstance(find[0], tuple) else find[0][0]
        return h.strip_html(f).replace("\n", " ").strip()

    def get_config(self, field, default=""):
        try:
            return h.get_dict_field(self.config, field)
        except ValueError:
            return default

    def list_url(self, page):
        return h.insert_identifier(self.get_config("urls.list.url"), page, "page")

    def paper_url(self, identifier):
        return h.insert_identifier(self.get_config("urls.paper.url"), identifier)

    def pdf_url(self, identifier):
        return h.insert_identifier(self.get_config("urls.pdf"), identifier)

    def identifiers(self, _list):
        if self.list_is_json:
            return h.get_dict_field(_list, self.get_config("json.list.identifiers"))
        else:
            pattern = self.get_config("regex.list.identifiers")
            return self.re_list(pattern, _list)

    def total_number_of_results(self, _list):
        if self.list_is_json:
            scount = h.get_dict_field(
                _list, self.get_config("json.list.total_number_of_results")
            )
        else:
            pattern = self.get_config("regex.list.total_number_of_results")
            scount = self.re_item(pattern, _list)
            scount = scount.replace(",", "")
        try:
            count = int(scount)
        except ValueError:
            count = 0
        return count

    def fetch_list_from_url(self, page):
        payload = self.search_parameters

        per_page_param = self.get_config("urls.list.params.per-page", "")
        if not per_page_param == "":
            payload[per_page_param] = self.per_page

        page_param = self.get_config("urls.list.params.page", "")
        if not page_param == "":
            if self.get_config("urls.list.params.offset", False):
                page = page * payload[per_page_param]
            payload[page_param] = page

        headers = self.get_config("urls.list.headers", {})
        if self.list_is_json:
            headers["accept"] = "application/json"

        method = self.get_config("urls.list.method", "GET")
        url = self.list_url(page)
        if method == "GET":
            print("Fetching: %s?%s" % (h.url_base_with_path(url), urlencode(payload)))
            txt = self.url_get(url, payload, headers).text
            return txt
        elif method == "POST" and not self.get_config("urls.list.send-json", False):
            return self.url_post(url, payload, headers).text
        else:
            return self.url_post_json(url, payload, headers).json()

    def fetch_paper_from_url(self, identifier):
        method = self.get_config("urls.paper.method", "GET")
        if method == "GET":
            return self.url_get(self.paper_url(identifier)).text
        elif method == "POST" and not self.paper_is_json:
            return self.url_post(self.paper_url(identifier)).text
        else:
            return self.url_post_json(self.paper_url(identifier)).json()

    def from_paper(self, key, _paper, item=True, default=""):
        fun = self.re_item if item else self.re_list
        is_pre_json = "embedded_json" in self.get_config(
            "preprocessing.paper.*.type", []
        )
        value = (
            fun(self.get_config("regex.paper.%s" % key, default=default), _paper)
            if not is_pre_json
            else h.get_dict_field(_paper, self.get_config("json.paper.%s" % key), "")
        )
        return h.safe_csv(value)

    def authors(self, _paper):
        return list(
            map(
                lambda s: s.title(),
                h.flatten(self.from_paper("authors", _paper, False)),
            )
        )

    def keywords(self, _paper):
        return h.flatten(self.from_paper("keywords", _paper, False))

    def title(self, _paper):
        return self.from_paper("title", _paper)

    def abstract(self, _paper):
        return self.from_paper("abstract", _paper)

    def publication_date(self, _paper):
        return self.from_paper("publication_date", _paper)

    def published_in(self, _paper):
        return self.from_paper("published_in", _paper)

    def citations(self, _paper):
        return self.from_paper("citations", _paper)

    def isbn(self, _paper):
        return self.from_paper("isbn", _paper)

    def doi(self, _paper):
        return self.from_paper("doi", _paper)

    def doi_url(self, _paper):
        return "https://doi.org/%s" % self.doi(_paper)

    def preprocess_paper(self, _paper):
        if len(self.preprocessing_paper) > 0:
            for pre in self.preprocessing_paper:
                if pre["type"] == "embedded_json":
                    raw_paper = self.re_item(pre["regex"], _paper)
                    _paper = json.loads(raw_paper)
        return _paper

    def preprocess_list(self, _list):
        if len(self.preprocessing_list) > 0:
            for _, _ in enumerate(self.preprocessing_list):
                pass
        return _list

    def postprocess_paper(self, paper):
        if len(self.postprocessing_paper) > 0:
            for i, post in enumerate(self.postprocessing_paper):
                if post["type"] == "query":
                    qry = h.get_dict_field(self.postprocessing_paper, f"{i}.query", {})
                    f = query.analyze(paper, qry)
                    paper = paper if f else None
        return paper

    def parse_paper(self, identifier, _paper):
        _paper = self.preprocess_paper(_paper)
        paper = {
            "title": self.title(_paper),
            "authors": self.authors(_paper),
            "abstract": self.abstract(_paper),
            "keywords": self.keywords(_paper),
            "published_in": self.published_in(_paper),
            "publication_date": self.publication_date(_paper),
            "citations": self.citations(_paper),
            "isbn": self.isbn(_paper),
            "doi": self.doi(_paper),
            "doi_url": self.doi_url(_paper),
            "pdf_url": self.pdf_url(identifier),
            "pdf_file_name": self.pdf_file_name(identifier, True),
            "paper_url": self.paper_url(identifier),
            "identifier": identifier,
        }
        paper = self.postprocess_paper(paper)
        return paper

    def fetch_parse_papers(self, identifiers):
        sub = h.get_progressbar(len(identifiers))
        sub.start()
        papers = []
        for i, identifier in enumerate(identifiers):
            sub.update(i)
            if (
                len(self.restrict_identifiers_to) > 0
                and identifier not in self.restrict_identifiers_to
            ):
                continue
            _paper = self.fetch_paper(identifier)
            paper = self.parse_paper(identifier, _paper)
            if paper is not None:
                papers.append(paper)
        sub.finish()
        return papers

    def fetch_parse_list(self, page):
        _list = self.fetch_list(page)
        _list = self.preprocess_list(_list)
        identifiers = self.identifiers(_list)
        return _list, self.fetch_parse_papers(identifiers)

    def run(self):
        tic = time.perf_counter()
        print(
            "",
            "---------------",
            "starting on %s - %s" % (self.config_name, self.name),
            sep="\n",
        )

        print(" - fetching first page")
        start_page = self.get_config("urls.list.start-page", 0)
        _list, papers = self.fetch_parse_list(start_page)
        result = {
            "papers": [papers],
            "total_results": self.total_number_of_results(_list),
        }

        pages_to_fetch = math.ceil(result["total_results"] / self.per_page) - 1

        sleep_for = h.sleep_for_sec(self.get_config("sleep_between_requests"))
        print(
            "This will take at least %.2f minutes if the cache is clean"
            % ((result["total_results"] * sleep_for) / 60)
        )

        if (pages_to_fetch) > 0:
            print(" - fetching the rest of the pages: %d" % (pages_to_fetch))

            h.console_down()
            total = h.get_progressbar(pages_to_fetch, "lists")
            total.start()
            for i, page in enumerate(
                range(start_page + 1, pages_to_fetch + start_page + 1)
            ):
                total.update(i)
                # if page >= 2: break
                h.console_up()
                _, papers = self.fetch_parse_list(page)
                result["papers"].append(papers)
            total.finish()

        result["papers"] = h.flatten(result["papers"])
        result["total_filtered_results"] = len(result["papers"])
        result["total_pages"] = pages_to_fetch + 1
        h.write_json_file(self.result_file_name(), result)
        toc = time.perf_counter()
        h.console_down()
        print(
            f"Finished {self.config_name} - {self.name} in {toc - tic:0.4f} seconds\n"
        )
        return result

    def export_results_to_csv(
        self,
        fields=[],
        file_path="./total.csv",
        override=False,
        defaults={},
        sort_by=None,
    ):
        result = h.read_json_file(self.result_file_name())
        if not "papers" in result:
            raise Exception("Illformed %s" % self.result_file_name())
        if len(result["papers"]) <= 0:
            return
        if len(fields) <= 0:
            fields = list(result["papers"][0].keys())

        if h.check_file_exists(file_path) and not override:
            df = pd.read_csv(file_path)
        else:
            df = pd.DataFrame(columns=fields)

        print(f"Exporting {self.config_name} - {self.name} paper to csv.")
        total = h.get_progressbar(len(result["papers"]), "csv", "Exporting")
        total.start()
        for i, paper in enumerate(result["papers"]):
            if (
                len(self.restrict_identifiers_to) > 0
                and paper["identifier"] not in self.restrict_identifiers_to
            ):
                continue
            paper_dict = {
                k: (paper[k] if not isinstance(paper[k], list) else ", ".join(paper[k]))
                if k in paper
                else (defaults[k] if k in paper else None)
                for k in fields
            }
            df = pd.concat([df, pd.DataFrame([paper_dict])], ignore_index=True)
            total.update(i)
        total.finish()

        if sort_by is not None:
            if not isinstance(sort_by, list):
                sort_by = [sort_by]

            if all(map(lambda x: x in fields, sort_by)):
                df.sort_values(by=sort_by)
            else:
                warnings.warn(
                    f"could not find sorting field: {str(sort_by)} is not completely in {str(fields)}"
                )

        df.to_csv(file_path, index=False)

    def download_pdfs(
        self, save_folder="./pdfs", save_name="identifier", override=False
    ):
        result = h.read_json_file(self.result_file_name())
        if not "papers" in result:
            raise Exception("Illformed %s" % self.result_file_name())
        if len(result["papers"]) <= 0:
            return

        save_folder = f"{save_folder}"
        h.ensure_path_exists(save_folder, True)

        print(f"Downloading {self.name} - {self.config_name} paper pdfs.")
        sleep_for = h.sleep_for_sec(self.get_config("sleep_between_requests"))
        print(
            "This will take at least %.2f hours if all papers need to be downloaded"
            % ((result["total_results"] * sleep_for) / 60 / 60)
        )

        total = h.get_progressbar(len(result["papers"]), "pdf")
        total.start()
        for i, paper in enumerate(result["papers"]):
            total.update(i)
            if (
                len(self.restrict_identifiers_to) > 0
                and paper["identifier"] not in self.restrict_identifiers_to
            ):
                continue

            num_pages_key = "pdf_num_pages"
            if num_pages_key in paper and not override:
                continue

            file_name = h.safe_filename(f"{paper[save_name]}.pdf")
            file_name = f"{save_folder}/{file_name}"

            content = self.fetch_pdf(paper["identifier"])
            with open(file_name, "wb") as f:
                f.write(content)

            try:
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfFileReader(pdf_file)
                paper[num_pages_key] = pdf_reader.getNumPages()
                result["papers"][i] = paper
            except PyPDF2.utils.PdfReadError:
                os.remove(self.pdf_file_name(paper["identifier"]))
                h.console_down()
                print(f"Reading PDF failed: id {paper['identifier']}")

        total.finish()
        h.write_json_file(self.result_file_name(), result)
