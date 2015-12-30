import sys
import pdb
sys.path.insert(0, 'corenlp-python')

from corenlp import StanfordCoreNLP

class StanforExtractor(object):
    def __init__(self):
        corenlp_dir = "corenlp-python/stanford-corenlp-full-2014-08-27/"
        self.corenlp = StanfordCoreNLP(corenlp_dir)  # wait a few minutes...

    def tag_text(self,text):
        '''
        :param text:
        :return:
        '''
        assert type(text) == str
        sents = self.corenlp.raw_parse(text)
        return sents

    def identify_rels(self,tagged_text):
        '''
        :param tagged_text:
        :return:
        '''
        assert 'sentences' in tagged_text.keys()
        assert 'dependencies' in tagged_text['sentences'][0].keys()
        all_rels = []
        for sent in tagged_text['sentences']:
            tmp_rels = []
            for rel in sent['dependencies']:
                if rel[0] in [u'nn',u'dobj']:
                    tmp_rels.append(rel)
            if len(tmp_rels)>0:
                final_rels = self.expand_rels(tmp_rels,sent['dependencies'])
                all_rels.append(final_rels)
        return all_rels

    def expand_rels_single(self,rel_words,sent):
        '''
        :param rel_words: list of words
        :param sent:
        :return:
        '''
        rel_tmp = [rel_words[0],rel_words[1]]
        for rel_1 in sent:
            if rel_1[1] == rel_words[0] and rel_1[2] == rel_words[1]:
                continue
            rel_1 = list(rel_1)
            # print(rel_1)
            #if prep_ or prepc_ is the tag
            # appos_tag = 1
            neg_tag = 0
            if rel_1[0].startswith(u'prep_') or rel_1[0].startswith(u'prepc_'):
                middle_word = rel_1[0][rel_1[0].find('_')+1:]
                rel_1 = [rel_1[1],middle_word,rel_1[2]]
            elif rel_1[0] == u'appos':
                rel_1 = [rel_1[1],rel_1[2]]
                # appos_tag = -1
            elif rel_1[0] == u'neg':
                # neg_tag = 1
                rel_1 = [rel_1[1],rel_1[2]]
            else:
                continue
            if rel_words[0] in rel_1:
                append_start = 1
                rel_1.remove(rel_words[0])
            elif rel_words[1] in rel_1:
                append_start = -1
                rel_1.remove(rel_words[1])
            else:
                continue
            # append_start = append_start*appos_tag
            # if neg_tag == 1:
            #
            if append_start == 1:
                rel_tmp = [' '.join(rel_1)]+rel_tmp
            else:
                rel_tmp = rel_tmp+[' '.join(rel_1)]
        return rel_tmp

    def expand_rels(self,tmp_rels,sent):
        '''
        add relevant sents to start or end of tmp_rels
        :param tmp_rels:
        :param sent:
        :return:
        '''
        # pdb.set_trace()
        print('sent',sent)
        final_rels = []
        for rel_full in tmp_rels:
            rel_words = [rel_full[1],rel_full[2]]
            rel_tmp = [rel_full[1],rel_full[2]]
            for rel_1 in sent:
                if rel_1 == rel_full:
                    continue
                rel_1 = list(rel_1)
                # print(rel_1)
                #if prep_ or prepc_ is the tag
                # appos_tag = 1
                neg_tag = 0
                if rel_1[0].startswith(u'prep_') or rel_1[0].startswith(u'prepc_'):
                    middle_word = rel_1[0][rel_1[0].find('_')+1:]
                    rel_1 = [rel_1[1],middle_word,rel_1[2]]
                elif rel_1[0] == u'appos':
                    rel_1 = [rel_1[1],rel_1[2]]
                    # appos_tag = -1
                elif rel_1[0] == u'neg':
                    # neg_tag = 1
                    rel_1 = [rel_1[1],rel_1[2]]
                else:
                    continue
                if rel_words[0] in rel_1:
                    append_start = 1
                    rel_1.remove(rel_words[0])
                elif rel_words[1] in rel_1:
                    append_start = -1
                    rel_1.remove(rel_words[1])
                else:
                    continue
                # append_start = append_start*appos_tag
                # if neg_tag == 1:
                #
                if append_start == 1:
                    rel_tmp = [' '.join(rel_1)]+rel_tmp
                else:
                    rel_tmp = rel_tmp+[' '.join(rel_1)]
            final_rels.append(rel_tmp)
        # print('final_res:',final_rels)
        return final_rels

    def return_rels(self,text):
        '''
        :param text:
        :return:
        '''
        text_tag = self.tag_text(text)
        rels_all = self.identify_rels(text_tag)
        return rels_all

    def identify_time(self,text):
        '''
        :param text:
        :return:
        '''
        time_strs = []
        text_tag = self.tag_text(text)
        for sent in text_tag['sentences']:
            words = sent['words']
            prev_wrd_tag = False
            for wrd in words:
                wrd_tag = wrd[1]
                assert type(wrd_tag) == dict
                # if u'Timex' in wrd_tag:
                #     timex_string = wrd_tag['Timex']
                #     new_end = timex_string.rfind('</TIMEX3>')
                #     timex_string = timex_string[:new_end]
                #     new_start = timex_string.rfind('>')
                #     time_word = timex_string[new_start+1:]
                #     time_strs.append(time_word)
                if u'NamedEntityTag' in wrd_tag:
                    if wrd_tag[u'NamedEntityTag'] in [u'DATE',u'TIME']:
                        if not prev_wrd_tag:
                            time_strs.append(wrd[0])
                        else:
                            prev_wrd = time_strs.pop()
                            new_wrd = prev_wrd+' '+wrd[0]
                            time_strs.append(new_wrd)
                        prev_wrd_tag = True
                    else:
                        prev_wrd_tag = False
                else:
                    prev_wrd_tag = False
        time_final = []
        for wrd in time_strs:
            if wrd not in time_final:
                time_final.append(wrd)
        return time_final

    def ret_time_rels(self,text):
        '''
        :param text:
        :return:
        '''
        print(' ')
