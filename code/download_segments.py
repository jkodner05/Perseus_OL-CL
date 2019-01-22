import re
import subprocess
from os import listdir, walk, makedirs
from os.path import isfile, join, exists, basename
import xml.etree.ElementTree as ET

AUTHORLIST = "../authorlist.txt"
HTMLBASE = "../rawhtml"
XMLBASE = "../rawxml"
TEXTBASE = "../rawtext" 


def download_html(startpage, directory):
    rx_nexturl = re.compile(r"href=\"(text.+?)\"")
    rx_nextline = re.compile(r"src=\"/img/next.gif\" alt=\"next\"")

    fname = join(directory,startpage.replace("/","_")+".html")
    if exists(fname):
        return
    subprocess.run(["wget", startpage, "-O", fname, "-q"])
    hasnext = True
    while hasnext:
        prevurlbase = ""
        with open(fname, "r") as f:
            for line in f:
                urlmatch = rx_nexturl.search(line.strip())
                if urlmatch:
                    prevurlbase = urlmatch.group(1)
                nextlinematch = rx_nextline.search(line.strip())
                if nextlinematch:
                    print(fname + "\t" + prevurlbase)
                    hasnext = True
                    break
                hasnext = False
        if hasnext:
            newpage = "http://www.perseus.tufts.edu/hopper/" + prevurlbase
            fname = join(directory,newpage.replace("/","_")+".html")
            if exists(fname):
                return
            subprocess.run(["wget", newpage, "-O", fname, "-q"])

def download_htmls():
    with open(AUTHORLIST, "r") as f:
        directory = ""
        for line in f:
            if not line.strip():
                continue
            elif "http" not in line:
                print(line.strip())
                directory = join(HTMLBASE, line.strip())
                if not exists(directory):
                    makedirs(directory)
            else:
                download_html(line.strip(), directory)    


def download_xml(directory, htmlfname):
    rx_xmlurl = re.compile(r"href=\"(xmlchunk.+?)\"")

    xmlfname = join(directory, basename(htmlfname.replace(".html",".xml")))
    if exists(xmlfname):
        return
    with open(htmlfname, "r") as f:
        for line in f:
            urlmatch = rx_xmlurl.search(line.strip())
            if urlmatch:
                newpage = "http://www.perseus.tufts.edu/hopper/" + urlmatch.group(1)
                print(urlmatch.group(1))
                subprocess.run(["wget", newpage, "-O", xmlfname, "-q"])


def download_xmls():
    for subdir, dirs, fnames in walk(HTMLBASE):
        author = basename(subdir)
        directory = join(XMLBASE, author)
        if not exists(directory):
            makedirs(directory)
        for fname in fnames:
            download_xml(directory, join(subdir,fname))


def extract_text(xmlfname):
    rx_singletag = re.compile(r"<.+?/>")
    rx_pairtag = re.compile(r"<.+?>")
    rx_delpairtags = [re.compile(r"<\s*foreign.+?foreign\s*>"),re.compile(r"<\s*unclear.+?unclear\s*>"),re.compile(r"<\s*note.+?note\s*>"),re.compile(r"<\s*cit.+?cit\s*>"),re.compile(r"<\s*ref.+?ref\s*>"),re.compile(r"<\s*bibl.+?bibl\s*>"),re.compile(r"<\s*lemma.+?lemma\s*>")]
    rx_multispace = re.compile(r"\ +")

    try:
#        tree = ET.parse(xmlfname)
#        root = tree.getroot()
    #    print("\n!!!\n\n:::\n")
        with open(xmlfname, "r") as f:
            xmlstr = "\n".join([line.strip() for line in f])
            xmlorig = xmlstr
            xmlstr = rx_singletag.sub(" ", xmlstr)
            for rx in rx_delpairtags:
                xmlstr = rx.sub(" ", xmlstr)
            xmlstr = rx_pairtag.sub(" ", xmlstr)
            xmlstr = rx_multispace.sub(" ", xmlstr)

#            if "<" in xmlstr or ">" in xmlstr:
#                print(xmlfname)
#                print(xmlorig)
#                print("\n-----\n")
#                print(xmlstr)
#                input("\n...\n\n")

            return xmlstr
    except:
        print("CAN'T PARSE: ", xmlfname)
        return ""


def extract_texts():
    for subdir, dirs, fnames in walk(XMLBASE):
        author = basename(subdir)
        outfname = join(TEXTBASE, author.replace(" ","_") + ".txt")
#        if not exists(directory):
#            makedirs(directory)
        if len(fnames) > 0:
            print(outfname)
            with open(outfname, "w") as f:
                for fname in fnames:
                    f.write(extract_text(join(subdir,fname)) + "\n")


def main():
#    download_htmls()
#    download_xmls()
    extract_texts()

    
if __name__ == "__main__":
    main()
