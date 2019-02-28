import json
import re
import requests
import spacy


def get_doc_list(domain, app_name, collection='editions', verbose=True):
    """ retrieves a list of doc-uris stored in a dsebaseapp
        :param domain: Domain hosting the dsebaseapp instance, e.g. "http://127.0.0.1:8080"
        :param app_name: The name of the dsebaseapp instance.
        :param collection: The name of the collection to process
        :verbose: Defaults to True and logs some basic information
        :return: A list of absolut URLs
    """

    endpoint = "{}/exist/restxq/{}/api/collections/{}".format(domain, app_name, collection)
    r = requests.get(endpoint)
    if r.status_code == 200:
        if verbose:
            print('connection to: {} status: all good'.format(endpoint))
    else:
        print(
            "There is a problem with connection to {}, status code: {}".format(
                r.status_code, endpoint
            )
        )
        return None
    hits = r.json()['result']['meta']['hits']
    all_files = requests.get("{}?page[size]={}".format(endpoint, hits)).json()['data']
    files = ["{}{}".format(domain, x['links']['self']) for x in all_files]
    if verbose:
        print("{} documents found".format(len(files)))
    return files


def stream_docs_to_file(
    domain, app_name, collection='editions',
    spacy_model='de_core_news_sm', min_len=15, verbose=True
):

    """ fetches TEI-Docs from an dsebaseapp instance and streams sents to file
        :param domain: Domain hosting the dsebaseapp instance, e.g. "http://127.0.0.1:8080"
        :param app_name: The name of the dsebaseapp instance.\
        This name will be also used as filename
        :param collection: The name of the collection to process
        :spacy_model: Spacy model used for sentence splitting.
        :min_len: The minimum amount of characters for a senetence to be stored.
        :verbose: Defaults to True and logs some basic information
        :return: A list comprehension as well as as the filename where the corpus is stored
    """

    files = get_doc_list(domain, app_name, collection, verbose=verbose)
    filename = '{}.txt'.format(app_name)
    if verbose:
        print("start streaming documents to {}".format(filename))
    nlp = spacy.load(spacy_model)
    with open(filename, 'w', encoding="utf-8") as f:
        for x in files:
            url = "{}?format=text".format(x)
            if verbose:
                print("download doc: {}".format(url))
            r = requests.get(url)
            text = r.text
            text = re.sub('\s+', ' ', text).strip()
            text = re.sub('- ', '', text).strip()
            doc = nlp(text)
            if verbose:
                print("found {} sents in doc".format(len(list(doc.sents))))
            [f.write(str(sent) + '\n') for sent in list(doc.sents) if len(sent) > min_len]
    return filename


def read_input(input_file):
    """ yields preprocessed lines read from a file (document per line)
        :input_file: Name of the file to process
        :return: yields processed lines of file
    """

    with open(input_file, encoding="utf-8") as f:
        for line in f:
            yield simple_preprocess(line)
