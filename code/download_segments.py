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


tags = set([])
def extract_text(directory, xmlfname):
    rx_tag = re.compile(r"<.+?>")



    try:
        tree = ET.parse(xmlfname)
        root = tree.getroot()
    #    print("\n!!!\n\n:::\n")
        with open(xmlfname, "r") as f:
            for line in f:
                if "<back" in line:
                    print(xmlfname, line)
                match = rx_tag.findall(line.strip())
                for m in match:
                    if "/" not in m:
                        tags.add(m[0:m.find(" ")])
#            for line in f:
#                print(rx_tag.sub("",line.strip()))
#            print("!\n!\n!\n")
            for tag in root.iter("term"):
                print(term.text)

#            input("...\n\n\n")




#        got = False
#        for p in root.iter("p"):
#            got=True

#        if not got:
#            print(xmlfname)
#            with open(xmlfname, "r") as f:
#                for line in f:
#                    print(line.strip())

#            if p.text and p.text.strip():
#                print(p.text.strip())
    except:
        print("CAN'T PARSE: ", xmlfname)



#    print("\n\n!!!\n\n")

def extract_texts():
    for subdir, dirs, fnames in walk(XMLBASE):
        author = basename(subdir)
        directory = join(TEXTBASE, author)
        if not exists(directory):
            makedirs(directory)
        for fname in fnames:
#            print(fname)
            extract_text(directory, join(subdir,fname))
    
    print(len(tags), tags)

def main():
#    download_htmls()
#    download_xmls()
    extract_texts()
    
if __name__ == "__main__":
    main()
