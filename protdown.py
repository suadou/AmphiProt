import requests

'''
Library for downloading/parsing multifasta, unicode and pdb codes.
Returns tuple with name of sequence and sequence.
'''


def unidown(code):
    url = "https://www.uniprot.org/uniprot/" + code + ".fasta"
    r = requests.get(url, allow_redirects=True).content.decode("utf-8")
    return r


def pdbdown(code):
    url = "https://www.rcsb.org/fasta/entry/" + code + "/download"
    r = requests.get(url, allow_redirects=True).content.decode("utf-8")
    return r


def parsepdbgen(code):
    actual_protein = None
    sequence = ""
    string = pdbdown(code)
    for line in string.split("\n"):
        if line.startswith(">"):
            if actual_protein is None:
                line = line.split("|")
                actual_protein = line[0].lstrip(">")
                continue
            yield tuple([actual_protein, sequence])
            line = line.split("|")
            actual_protein = line[0].lstrip(">")
            sequence = ""
            continue
        sequence += line
    yield tuple([actual_protein, sequence])


def parseunicode(code):
    actual_protein = None
    sequence = ""
    string = unidown(code)
    for line in string.split("\n"):
        if line.startswith(">"):
            if actual_protein is None:
                line = line.split("|")
                actual_protein = line[1]
                continue
            yield tuple([actual_protein, sequence])
            line = line.split("|")
            actual_protein = line[1]
            sequence = ""
            continue
        sequence += line
    yield tuple([actual_protein, sequence])


def parsedmulti(string):
    actual_protein = None
    sequence = ""
    for line in string.split("\n"):
        if line.startswith(">"):
            if actual_protein is None:
                actual_protein = line
                continue
            yield tuple([actual_protein, sequence])
            actual_protein = line
            sequence = ""
            continue
        sequence += line
    yield tuple([actual_protein, sequence])
