from finder import Fetcher
import helpers as h
import time

finders = [
    # # UIST
    # {
    #     "name": "uist",
    #     "config_name": "acm",
    #     "search_parameters": {
    #         'fillQuickSearch': 'false',
    #         'ContentItemType': 'research-article',
    #         'SpecifiedLevelConceptID': '119271',
    #         'expand': 'dl',
    #         'AfterMonth': '1',
    #         'AfterYear': '2000',
    #         'BeforeMonth': '12',
    #         'BeforeYear': '2019',
    #         'AllField': 'Title:((select* OR manipulat*) AND ("virtual" OR "VR")) OR Abstract:((select* OR manipulat*) AND ("virtual" OR "VR"))'
    #     }
    # },
    # CHI
    {
        "name": "chi",
        "config_name": "acm",
        "search_parameters": {
            "fillQuickSearch": "false",
            "ContentItemType": "research-article",
            "SpecifiedLevelConceptID": "119596",
            "expand": "dl",
            "AfterMonth": "1",
            "AfterYear": "2019",
            "BeforeMonth": "12",
            "BeforeYear": "2022",
            "AllField": 'Title:((select* OR manipulat*) AND ("virtual" OR "VR")) OR Abstract:((select* OR manipulat*) AND ("virtual" OR "VR"))',
        },
    },
    # {
    #     "name": "chi",
    #     "config_name": "acm",
    #     "search_parameters": {
    #         "fillQuickSearch": "false",
    #         "target": "advanced",
    #         "ContentItemType": "research-article",
    #         "SpecifiedLevelConceptID": "119596",  # identifier for CHI conference
    #         "expand": "dl",
    #         "AfterMonth": "1",
    #         "AfterYear": "2021",
    #         "BeforeMonth": "12",
    #         "BeforeYear": "2021",
    #         "AllField": "(virtual reality)",
    #     },
    # },
    # # IEEEVR
    # {
    #     "name": "ieeevr",
    #     "config_name": "ieee",
    #     "search_parameters": {
    #         "action":"search",
    #         "matchBoolean":'True',
    #         "newsearch":'True',
    #         "queryText":"((((\"Document Title\": \"select*\" OR \"Document Title\": \"manipulat*\") AND (\"Document Title\": \"virtual\" OR \"Document Title\": \"VR\")) OR ((\"Abstract\": \"select*\" OR \"Abstract\": \"manipulat*\") AND (\"Abstract\": \"virtual\" OR \"Abstract\": \"VR\"))) AND (\"Publication Number\": 8787730 OR \"Publication Number\": 8423729 OR \"Publication Number\": 7889401 OR \"Publication Number\": 7499993 OR \"Publication Number\": 7167753 OR \"Publication Number\": 6786176 OR \"Publication Number\": 6542301 OR \"Publication Number\": 6179238 OR \"Publication Number\": 5753662 OR \"Publication Number\": 5440859 OR \"Publication Number\": 4806856 OR \"Publication Number\": 4472735 OR \"Publication Number\": 4160976 OR \"Publication Number\": 11055 OR \"Publication Number\": 9989 OR \"Publication Number\": 9163 OR \"Publication Number\": 8471 OR \"Publication Number\": 7826 OR \"Publication Number\": 7269 OR \"Publication Number\": 6781))",
    #         "highlight":'True',
    #         "returnFacets":["ALL"],
    #         "returnType":"SEARCH",
    #         "matchPubs":'True'
    #     },
    #     'headers': {
    #         'Cookie': "TS01b03060_26=014082121d70df1295452f0415c1d19d6df9a6f4e38bd41c2416ed80d5811061c6870f476e50edbc299092405b397624fa7a9e687bc99f8ff8a3910f51ad7f146893751e06; s_sq=%5B%5BB%5D%5D; WT_FPC=id=e72f05a8-a59d-4ec5-aec4-1152a199d9c3:lv=1595292510272:ss=1595292510272; JSESSIONID=GUl75h76VZMOs-zuTCaJlFC4zcJ3yP6wtx-cjO8IeePXFReL5bCx!-680779053; ERIGHTS=qdfpefSlqu3uiCGuTKfJucHgx2BppfxxYF3*xxqgiIyDwkBkIPSB6fG511wx3Dx3D-18x2dsWA2HgFqGnNTPTpUU0DGKQx3Dx3DdYHuM4AonsaMwzx2BLPW6f1Ax3Dx3D-seCuihlon4Yn6ravae9KzQx3Dx3D-x2BoJmAJK1Z3DbmTWzFvGVAAx3Dx3D; utag_main=v_id:01735d32e2490000e5080caf193f03072007c06a00fb8$_sn:7$_ss:0$_st:1595513350925$vapi_domain:ieee.org$_se:6$ses_id:1595511548855%3Bexp-session$_pn:1%3Bexp-session; AMCV_8E929CC25A1FB2B30A495C97%40AdobeOrg=1687686476%7CMCIDTS%7C18464%7CMCMID%7C20641728764065869141128774931607118228%7CMCAAMLH-1596116353%7C6%7CMCAAMB-1596116353%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1595518753s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.0.0; xpluserinfo=eyJpc0luc3QiOiJ0cnVlIiwiaW5zdE5hbWUiOiJDb3BlbmhhZ2VuIFVuaXZlcnNpdHkiLCJwcm9kdWN0cyI6IklFTHxNQ1NZTlRINXxNQ1NZTlRIMXxNQ1NZTlRIM3xNQ1NZTlRINHxNQ1NZTlRIMnxNQ1NZTlRIN3xNQ1NZTlRIOHxNQ1NZTlRINnxNQ1NZTlRIOXxNQ1NZTlRIMTB8VkRFfE5PS0lBIEJFTEwgTEFCU3wifQ==; seqId=2644566; WLSESSION=237134476.20480.0000; TS01b03060=012f350623fd5c8dfef53c8016f92209f692fbb878553da77b0d7cb39209593f4e4b723514009901f6c5b52df817feb4a48b460b42d9df924fe4900f2a2d526564dca63f806c55f1e5df6976d59309bdc6da9da559289a09cdd40962dbf4e8de8db87317cf64aab18502ee0ab644b7f10d146a97046589963400ea55e921974f69ce15ca4f1c31e52480121d523b747f9a1b386f836d70ce861539d87205e46153e534c03bdbbad660826925cd8c3991f7bb8ecf77"
    #     }
    # },
    # Virtual Reality (Journal)
    # {
    #     "name": "vr",
    #     "config_name": "springer",
    #     "search_parameters": {
    #         "query": '((select* OR manipulat*) AND ("virtual" OR "VR"))',
    #         "facet-start-year": "2000",
    #         "date-facet-mode": "between",
    #         "facet-end-year": "2019",
    #         "showAll[0]": "false",
    #         "showAll[1]": "true",
    #         "search-within": "Journal",
    #         "facet-journal-id": "10055",
    #     },
    #     "postprocessing_paper": [
    #         {
    #             "type": "query",
    #             "query": {
    #                 "should": [
    #                     {
    #                         "must": [
    #                             {
    #                                 "should": [
    #                                     {"match": {"title": "select*"}},
    #                                     {"match": {"title": "manipulat*"}},
    #                                 ]
    #                             },
    #                             {
    #                                 "should": [
    #                                     {"match": {"title": "virtual"}},
    #                                     {"match": {"title": "VR"}},
    #                                 ]
    #                             },
    #                         ]
    #                     },
    #                     {
    #                         "must": [
    #                             {
    #                                 "should": [
    #                                     {"match": {"abstract": "select*"}},
    #                                     {"match": {"abstract": "manipulat*"}},
    #                                 ]
    #                             },
    #                             {
    #                                 "should": [
    #                                     {"match": {"abstract": "virtual"}},
    #                                     {"match": {"abstract": "VR"}},
    #                                 ]
    #                             },
    #                         ]
    #                     },
    #                 ]
    #             },
    #         }
    #     ],
    # },
    # # VRST
    # {
    #     "name": "vrst",
    #     "config_name": "acm",
    #     "search_parameters": {
    #         'fillQuickSearch': 'false',
    #         'ContentItemType': 'research-article',
    #         'SpecifiedLevelConceptID': '119205',
    #         'expand': 'dl',
    #         'AfterMonth': '1',
    #         'AfterYear': '2000',
    #         'BeforeMonth': '12',
    #         'BeforeYear': '2019',
    #         'AllField': 'Title:((select* OR manipulat*) AND ("virtual" OR "VR")) OR Abstract:((select* OR manipulat*) AND ("virtual" OR "VR"))'
    #     }
    # },
    # Journal of Human-Computer Interaction
    # {
    #     "name": "hci",
    #     "config_name": "taylor_and_francis",
    #     "search_parameters": {
    #         "AllField": 'Title:((select* OR manipulat*) AND ("virtual" OR "VR")) OR Abstract:((select* OR manipulat*) AND ("virtual" OR "VR"))',
    #         "content": "standard",
    #         "target": "default",
    #         "queryID": "60/3256804055",
    #         "AfterYear": "2000",
    #         "BeforeYear": "2019",
    #         "SeriesKey": "hihc20",
    #     },
    # },
    # # International Journal of Human-Computer Studies
    # {
    #     "name": "hcs",
    #     "config_name": "sciencedirect",
    #     "search_parameters": {
    #         "pub": "International Journal of Human-Computer Studies",
    #         "cid": "272548",
    #         "date": "2000-2019",
    #         "tak": "(virtual OR VR) AND (select OR selecting OR selection OR selects OR manipulate OR manipulating OR manipulation)",
    #         "articleTypes": "FLA",
    #         "t": "OEW16T6MXphuPMHOQwJzPnfK4wl9kanAYl%2FZjT4DhuB%2FGrafluSvj1Yn0%2F8mJECuxEsAJTowZht7SvxSxdTKbP%2Fh9%2FP9aljHLM5lLDozQIcI9kan7UWtXlmJ%2BRfjagzavKdDbfVcomCzYflUlyb3MA%3D%3D",
    #     },
    # },
    # # TOCHI
    # {
    #     "name": "tochi",
    #     "config_name": "acm",
    #     "search_parameters": {
    #         'fillQuickSearch': 'false',
    #         'ContentItemType': 'research-article',
    #         'SeriesKey': 'tochi',
    #         'expand': 'dl',
    #         'AfterMonth': '1',
    #         'AfterYear': '2000',
    #         'BeforeMonth': '12',
    #         'BeforeYear': '2019',
    #         'AllField': 'Title:((select* OR manipulat*) AND ("virtual" OR "VR")) OR Abstract:((select* OR manipulat*) AND ("virtual" OR "VR"))'
    #     }
    # },
]


tic = time.perf_counter()

fp = "./output.csv"

for finder in finders:
    find = Fetcher(load_from="cache", **finder)
    # find = Fetcher(load_from="url", **finder)
    find.run()
    find.export_results_to_csv(
        ["pdf_file_name", "title", "authors", "doi_url"], file_path=fp
    )

toc = time.perf_counter()
h.console_down()
print(f"Finished everything in {toc - tic:0.4f} seconds\n")
