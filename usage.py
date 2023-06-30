from finder import Fetcher
import helpers as h
import time
from datetime import datetime


acm_params = {
    "fillQuickSearch": "false",
    "ContentItemType": "research-article",
    "expand": "dl",
    "AfterMonth": "1",
    "AfterYear": "2013",
    "BeforeMonth": "6",
    "BeforeYear": "2023",
    "AvailableFormat": "lit:pdf",
    "AllField": "(Abstract:meaningful AND Abstract:haptics) OR (Title:meaningful AND Title:haptics)",
    # "AllField": "(Abstract:haptic AND Abstract:experience AND Abstract:design) OR (Title:haptic AND Title:experience AND Title:design)",
}

finders = [
    # UIST
    {
        "name": "uist",
        "config_name": "acm",
        "search_parameters": {
            **{
                "SpecifiedLevelConceptID": "119271",
            },
            **acm_params,
        },
    },
    # CHI
    {
        "name": "chi",
        "config_name": "acm",
        "search_parameters": {
            **{
                "SpecifiedLevelConceptID": "119596",
            },
            **acm_params,
        },
    },
    # ToCHI
    {
        "name": "tochi",
        "config_name": "acm",
        "search_parameters": {
            **{
                "SeriesKey": "tochi",
            },
            **acm_params,
        },
    },
    # WorldHaptics + ToH + HAPTICS Symposium
    {
        "name": "worldhaptics",
        "config_name": "ieee",
        "search_parameters": {
            "action": "search",
            "matchBoolean": True,
            "queryText": '("Publication Title":meaningful haptics) OR ("Abstract":meaningful haptics)',
            "highlight": True,
            "returnType": "SEARCH",
            "matchPubs": True,
            "rowsPerPage": "75",
            "pageNumber": "1",
            "refinements": [
                "PublicationTitle:IEEE Transactions on Haptics",
                "PublicationTitle:2021 IEEE World Haptics Conference (WHC)",
                "PublicationTitle:2019 IEEE World Haptics Conference (WHC)",
                "PublicationTitle:2020 IEEE Haptics Symposium (HAPTICS)",
                "PublicationTitle:2022 IEEE Haptics Symposium (HAPTICS)",
            ],
            "ranges": ["2013_2023_Year"],
            "returnFacets": ["ALL"],
        },
        "headers": {
            "Cookie": "AMCV_8E929CC25A1FB2B30A495C97%40AdobeOrg=1687686476%7CMCIDTS%7C19364%7CMCMID%7C24325535634873532558291481124988846596%7CMCAID%7CNONE%7CMCOPTOUT-1673019272s%7CNONE%7CvVersion%7C3.0.0; cookieconsent_status=dismiss; JSESSIONID=gGr9SbMojMA9XdtFK-B5lbtVjCfoJwcULm7Hl8yxt-3eF7bWONdD!119812709; ipCheck=2620:101:f000:700:0:0:3f81:c714; ERIGHTS=fq07dGkmXVlj0x2Bvl9upDxxmCXQpTvs19O*BtyyzCwEFu3QA9sK6x2B3YxxfnGFu53gZbDxxg63iINbnVsx3D-18x2d1DdquAViiL9xxCitNDM7HnQx3Dx3DsaFXNx2BjkVmS5bKrRWVbHJwx3Dx3D-seCuihlon4Yn6ravae9KzQx3Dx3D-x2BoJmAJK1Z3DbmTWzFvGVAAx3Dx3D; WLSESSION=220357260.20480.0000; TS01b03060=012f35062392a3d57c81cf2c4b561c916b773ceabd8f33d88bdcf197129ba2a4b4c785662107cefaeb52d73b5c20f48f4f50642ac7; TSaeeec342027=080f8ceb8aab20001cee1f7e14abcea6011b151a3a50c4a98896445060225a998aa4da993bf1c18a08e2be40471130000039e88fece3da99d35796d85bcc79ac33d1ac271523cb7655fd14cd6e25e800eb37b7fc5295ce4b48abaabcbfccf456; utag_main=v_id:0188fd49b539000308fb1862327c05050003600d00bd0; ipList=2620:101:f000:700:0:0:3f81:c714; fp=49c339e05f860a34d7790256ea9b0b21; xpluserinfo=eyJpc0luc3QiOiJ0cnVlIiwiaW5zdE5hbWUiOiJVbml2ZXJzaXR5IG9mIFdhdGVybG9vIiwicHJvZHVjdHMiOiJJRUx8RHJhZnR8RUJPT0tTOjE5NzQ6MjAxNXxNSVRQOjIwMTM6MjAxOXxDT05GQVJDSDoxOTUxOjIwMDB8SlJOTEFSQ0g6MTg4NDoxOTk5fElCTToxODcyOjIwMjB8U0FFOjE5OTA6MjAyM3xNSVRQOjIwMjE6MjAyMnxFQk9PS1M6MjAyMToyMDIzfFdJTEVZVEVMRUNPTToyMDIxOjIwMjN8VkRFfE5PS0lBIEJFTEwgTEFCU3wifQ==; seqId=8628"
        },
    },
    # Eurohaptics
    {
        "name": "eurohaptics",
        "config_name": "springer",
        "search_parameters": {
            "use-oscar-shared-search": "true",
            "query": "meaningful haptics Eurohaptics",
            "content-type": "ConferencePaper",
            "date": "custom",
            "dateFrom": "2013",
            "dateTo": "2023",
            "language": "En",
        },
        "postprocessing_paper": [
            {
                "type": "query",
                "query": {
                    "should": [
                        {
                            "must": [
                                {"match": {"title": "meaningful"}},
                                {"match": {"title": "haptics"}},
                            ]
                        },
                        {
                            "must": [
                                {"match": {"abstract": "meaningful"}},
                                {"match": {"abstract": "haptics"}},
                            ]
                        },
                    ]
                },
            }
        ],
    },
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
]

tic = time.perf_counter()
now = datetime.now()
fp = f"./output/meaningful-haptics-title-abstract.csv"

for finder in finders:
    find = Fetcher(load_from={"list": "cache"}, **finder)
    # find = Fetcher(load_from={"list": "url"}, **finder)
    # find = Fetcher(load_from="url", **finder)
    find.run()
    find.export_results_to_csv(
        ["doi_url", "authors", "published_in", "publication_date", "title", "abstract"],
        file_path=fp,
    )

toc = time.perf_counter()
h.console_down()
print(f"Finished everything in {toc - tic:0.4f} seconds\n")
