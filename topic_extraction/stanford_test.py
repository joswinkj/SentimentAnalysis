import sys
import stanford_extraction as ste

def test_stanford(text):
    se = ste.StanforExtractor()
    rels = se.return_rels(text)
    print(rels)
    times = se.identify_time(text)
    print(times)

if __name__ == '__main__':
    if len(sys.argv)>1:
        text=sys.argv[1]
        test_stanford(text)
    else:
        text = "Yes. This is of interest. I am out of the country all through next week. Though I can have a call tomorrow (Saturday) at 1.30 p.m. Do let me know if this works?"
        test_stanford(text)