import bibtexparser
import json
import yaml
import textwrap
from collections import OrderedDict
import numpy as np

tags_mapping = {
    'article':{'show':'Journal', 'backcolor':'#dafbe1', 'fontcolor':'#2da44e'},
    'inproceedings': {'show': 'Conference', 'backcolor': '#fff8c5', 'fontcolor':'#bf8700'},
    'engineering': {'show': 'Engineering', 'backcolor': '#ddf4ff', 'fontcolor':'#218bff'},
    'clinical': {'show': 'Clinical', 'backcolor': '#ffeff7', 'fontcolor':'#e85aad'},
}

def write_frontmatter(fp):
    text = '''---\npermalink: /\n---\n\n'''
    fp.write(text)

def write_navigation(fp):
    text = '<span style="color:blue;font-weight:700;font-size:25px">\n' \
           '[People](#people) &ensp; &ensp; ' \
           '[Goals](#goals) &ensp; &ensp; ' \
           '[Results](#results)' \
           '\n</span>\n\n'
    fp.write(text)

def write_people(fp, ppl):
    text = '# Team Members <a name="people"></a>\n' \
           '### Principal Investigators\n'
    for cnt, pi in enumerate(ppl['pi']):
        text += '[%s](%s) '%(pi['name'], pi['homepage']) if 'homepage' in pi.keys() else '%s '%pi['name']
        text += '(%s) '%pi['role']
        text += '&ensp; | &ensp; ' if (cnt+1)<len(ppl['pi']) else '\n'

    text += '### Research Fellows\n'
    for cnt, fe in enumerate(ppl['fellows']):
        text += '[%s](%s) '%(fe['name'], fe['homepage']) if 'homepage' in fe.keys() else '%s '%fe['name']
        text += '&ensp; | &ensp; ' if (cnt+1)<len(ppl['fellows']) else '\n'

    text += '### Students\n'
    for cnt, st in enumerate(ppl['student']):
        text += '[%s](%s) '%(st['name'], st['homepage']) if 'homepage' in st.keys() else '%s '%st['name']
        text += '&ensp; | &ensp; ' if (cnt+1)<len(ppl['student']) else '\n'

    text += '\n'
    fp.write(text)

def write_goal(fp):
    text = '# Major Goals <a name="goals"></a>\n' \
           'The objective of the project is to develop deep-learning based multimodal retinal image registration methods ' \
           'to help the ophthalmologist to quickly detect and diagnose retinal diseases.  Four major goals: ' \
           '(1). Collect and prepare a wide range of retina images/data to support algorithm development and testing; ' \
           '(2). Develop algorithm to align ultra-widefield, color fundus and multicolor images to help with early ' \
           'diagnosis of cardiovascular diseases, ' \
           '(3).  Develop segmentation algorithm for OCT volumes with the help of motion correction, and ' \
           '(4).  Evaluate and assess the ability of goals 2 and 3 in diagnosis evaluation using human experts ' \
           '(clinical specialist). \n\n'
    fp.write(text)

def process_author_add_link(author, people_json):
    for ppl in people_json.keys():
        if people_json[ppl]['link'] is None:
            continue
        candidate_list = people_json[ppl]['search']
        match = [candidate in author.lower() for candidate in candidate_list]
        if sum(match)==len(candidate_list):
            # if people_json[ppl]['link'] is not None:
            author = '[%s](%s)'%(author, people_json[ppl]['link'])
            if 'junkang' in author and 'zhang' in author:
                author = '**'+author+'**'
            break
    return author


def process_bibtex_authors(authors, people_json):
    '''
    change from 'lastname1, firstname1 and lastname2, firstname2' to 'firstname1 lastname1, firstname2 lastname2'
    :param authors: author string from bibtex
    :return:
    '''
    if 'and' in authors:
        authors_list = authors.split(' and ')
        for idx, author in enumerate(authors_list):
            author = author.strip()
            if ',' in author:
                last, first = author.rsplit(',', 1)
                author = first.strip() + ' ' + last.strip()
            authors_list[idx] = process_author_add_link(author, people_json)
        authors = ', '.join(authors_list)
    return authors

def _prepend_emoji(text, bib_c):
    '''https://github.com/ikatyang/emoji-cheat-sheet'''
    if bib_c['type'] in ['clinical']:
        text += u'⬜ &ensp; '
    elif bib_c['ENTRYTYPE'] in ['patent']:
        text += u'🟩 &ensp; '
    elif bib_c['ENTRYTYPE'] in ['article']:
        text += u'🟧 &ensp; '
    elif bib_c['ENTRYTYPE'] in ['inproceedings']:
        text += u'🟦 &ensp; '
    return text


def process_publications(fp_w, bib, orders, people_json=None):
    # order_c = orders[0]
    order = orders[0]
    sort_key, sort_order, sort_output = order['key'], order['order'], order['output']
    if type(sort_order) is not list:
        allvalues = list( set([_v.get(sort_key, None) for _v in bib.values()]) )
        if sort_order=='ascend':
            allvalues = sorted(allvalues)
        elif sort_order=='descend':
            allvalues = sorted(allvalues)[::-1]
        else:
            assert 0
        sort_order = allvalues
    bibnew = OrderedDict({_k:OrderedDict() for _k in sort_order})
    for bib_key, bib_entry in bib.items():
        # if bib[kb][sort_key] not in values
        belongs_to = bib_entry.get(sort_key, None)
        bibnew[ belongs_to ][bib_key]= bib_entry
        if sort_output.startswith('tag'):
            if 'tags' not in bibnew[belongs_to][bib_key].keys():
                bibnew[belongs_to][bib_key]['tags'] = []
            bibnew[belongs_to][bib_key]['tags'] += [bib_entry[sort_key]]
    for kn in bibnew.keys():
        if sort_output=='title':
            text = '### %s\n'%kn
            fp_w.write(text)
            print(text)
        if len(orders) > 1:
            process_publications(fp_w, bibnew[kn], orders[1:], people_json)
        else:
            for kb in bibnew[kn].keys():
                text = u''
                bib_c = bibnew[kn][kb]
                # if 'tags' in bib_c.keys():
                #     text += '<div>\n'
                #     for tag in bib_c['tags']:
                #         text += '<span style="' \
                #                 'display: inline-block; ' \
                #                 'padding-top: 2px; ' \
                #                 'padding-right: 10px; ' \
                #                 'padding-bottom: 2px; ' \
                #                 'padding-left: 10px; ' \
                #                 'border-radius: 20px; ' \
                #                 'background-color: %s; ' \
                #                 'color: %s; ' \
                #                 'font-size: 14px; ' \
                #                 '">' \
                #                 '<strong>%s</strong>' \
                #                 '</span>\n' % \
                #                 (tags_mapping[tag]['backcolor'], tags_mapping[tag]['fontcolor'], tags_mapping[tag]['show'])
                #         # 'font-family:\'Courier\'"> ' \
                #     text += '</div>\n'

                # text += '- ' # bullet
                text = _prepend_emoji(text, bib_c)
                text += '**%s** <br>\n' % bib_c['title'].replace('{','').replace('}','')
                authors = process_bibtex_authors(bib_c['author'], people_json)
                text += '%s <br>\n' % authors

                if bib_c['ENTRYTYPE'] in ['patent']:
                    text += '*US Patent %s*, ' % bib_c['number']
                    text += '%s <br>\n' % bib_c['year']
                else: # 'article', 'inproceedings'
                    text += '*%s*, ' % bib_c['journal'] if 'journal' in bib_c.keys() else '*%s*, ' % bib_c['booktitle']
                    text += '%s <br>\n' % bib_c['year']

                # text = _prepend_emoji(text, bib_c)
                if 'links' in bib_c.keys():
                    for link_key, link_val in bib_c['links'].items():
                        text += '**\[[%s](%s)\]** &ensp; ' % (link_key, link_val)
                else:
                    text += '**\[[DOI](%s)\]**' % ('https://doi.org/'+bib_c['doi']) if 'doi' in bib_c.keys() else ''
                    text += ' &ensp; **\[[PDF](%s)\]**' % bib_c['pdf'] if 'pdf' in bib_c.keys() else ''
                    text += ' &ensp; **\[[Supplementary](%s)\]**' % bib_c['supplementary'] if 'supplementary' in bib_c.keys() else ''
                    text += ' &ensp; **\[[Code](%s)\]**' % bib_c['code'] if 'code' in bib_c.keys() else ''
                    text += ' &ensp; **\[[Data](%s)\]**' % bib_c['data'] if 'data' in bib_c.keys() else ''
                text += '<br>\n\n'

                # text += '<details> ' \
                #         '<summary>Abstract</summary> ' \
                #         '%s ' \
                #         '</details>\n' % bib_c['abstract'] if 'abstract' in bib_c.keys() else ''

                # text += '<p align="center"> ' \
                #         '<img src="{{site.baseurl}}%s" > ' \
                #         '</p>\n' % bib_c['image_bar'] if 'image_bar' in bib_c.keys() else ''
                # text += '<br>\n'
                fp_w.write(text)
                print(text)


if __name__=='__main__':
    def _check_keys_match(k1s, k2s):
        match = True
        for k1 in k1s:
            if k1 not in k2s:
                print(k1, ' not found')
                match = False
        return match

    if 1 and 0:
        bibtex_dict = OrderedDict(bibtexparser.load(open('data/reference.bib', 'rt')).entries_dict)
    else:
        from bibtexparser.bparser import BibTexParser
        parser_non_standard = BibTexParser(ignore_nonstandard_types=False)
        bibtex_dict = OrderedDict(bibtexparser.load(open('data/reference.bib', 'rt'), parser=parser_non_standard).entries_dict)
    reference_json = json.load(open('data/reference.json', 'rt'))

    print('check if reference.bib and reference.json match with each other')
    match = _check_keys_match(list(bibtex_dict.keys()), list(reference_json.keys()))
    match = match and _check_keys_match(list(reference_json.keys()), list(bibtex_dict.keys()))
    print(match)
    assert match==True, 'not match'

    for k1 in bibtex_dict.keys():
        for k2 in reference_json[k1].keys():
            bibtex_dict[k1][k2] = reference_json[k1][k2]
    # people_yaml = yaml.safe_load(open('data/people.yml'))
    people_json = json.load(open('data/people.json', 'rt'))
    print(' ')

    fp_w = open('index.md', 'wt', encoding='utf-8')
    write_frontmatter(fp_w)
    # write_navigation(fp_w)
    # write_people(fp_w, people_yaml)
    # write_goal(fp_w)
    fp_w.write('# Publications <a name="publications"></a>\n\n')
    # fp_w.write('<h2 id="test-page">Test page</h2>\n')
    legend = (u'| 🟩 | Patent | 🟧 | Journal (Engineering) | 🟦 | Conference (Engineering) | ⬜ | Clinical Paper |\n'
              u'|-|-|-|-|-|-|-|-|\n\n')
    fp_w.write(legend)

    # 'order': None (just group), 'ascend', 'descend', [list] (sort according to the list)
    orders = [{'key': 'year', 'order': 'descend', 'output': 'title'},
              {'key': 'type', 'order': ['engineering', 'clinical'], 'output': 'tag'},
              {'key': 'ENTRYTYPE', 'order': ['article', 'inproceedings', 'patent'], 'output': 'tag'},
              ]

    process_publications(fp_w, bibtex_dict, orders, people_json)

