import click
import re
import os
import string
from urllib.parse import unquote
import numpy as np
import socket
import string
import numpy
from IPy import IP

##save unique users
List_user = []

#import pdb;pdb.set_trace()

def get_query(mode_search, dic_queries, list_line, mode):
    if mode == "API":
        if "&" not in list_line[6]:
            query = list_line[6].replace("/" + mode_search +"?q=", "")
        else:
            query = list_line[6][list_line[6].find("q=")+1 : list_line[6].find("$")]
            if "&" in query:
                query = query[query.find("=")+1 : query.find("&")]
            else:
                query = query.replace("=", " ")
    else:
        if "&" not in list_line[6]:
            query = list_line[6].replace("/" + mode_search +"?query=", "")
        else:
            query = list_line[6][list_line[6].find("query=")+5 : list_line[6].find("$")]
            if "&" in query:
                query = query[query.find("=")+1 : query.find("&")]
            else:
                query = query.replace("=", " ")
    ##Process query 
    query = unquote(query)
    query = query.replace("+", " ")
    query = query.strip()
    ##Check if it is not an advanced search
    if "adv_and" not in list_line[6]:
        ##Get the user agent from the line
        user_agent = '-'.join(list_line[11:-1]).lower()
        ##Get the IP address from the line
        IP_address = list_line[0]
        user = IP_address + " &&&& " + user_agent
        ##Check if the combination between IP address and user agent is in the list of unique users
        if user not in List_user:
            List_user.append(user)
        ##Check if the query is in the dictionary
        if query not in dic_queries:
            dic_queries[query] = 1
        else:
            dic_queries[query] = dic_queries[query] + 1
    else:
        query = "Not considered"
    return dic_queries, query

def script(path_logs):
    ##store queries from logs
    dic_imagesearch = {}
    dic_imagesJSP = {}
    dic_textsearch = {}
    dic_textJSP = {}
    ##Processing logs
    for subdir, dirs, files in os.walk(path_logs):
        with click.progressbar(length=len(files), show_pos=True) as progress_bar:
            ##Process each file from the path_logs
            for file in files:
                progress_bar.update(1)
                if file.startswith("logfile."):
                    file_name = os.path.join(subdir, file)
                    with open(file_name) as file:
                        ##Process each line of the current file
                        for line in file:
                            list_line = line.split(" ")
                            ##Process lines from API requests
                            if "/imagesearch?" in line or "/textsearch?" in line:
                                ##Check if is the first request of a given query
                                if "offset=0" in line or "offset" not in line:
                                    ##Check if the user agent is not (python, bot, crawl)
                                    if "python" not in '-'.join(list_line[11:-1]).lower() and "crawl" not in '-'.join(list_line[11:-1]).lower() and "bot" not in '-'.join(list_line[11:-1]).lower(): 
                                        ##Check if there is a query on the line
                                        if "q" in list_line[6] and ("textsearch?q=" in list_line[6] or "imagesearch?q=" in list_line[6]):
                                            ##Check if the IP is not private (i.e., from FCT or FCCN) (e.g., 172.16.10.130, 127.0.*, 10.0.*)
                                            if IP(list_line[0]).iptype() != "PRIVATE" and IP(list_line[0]).iptype() != "LOOPBACK": 
                                                try:
                                                    ##Get the hostname from IP address
                                                    hostname = socket.gethostbyaddr(list_line[0])[0]
                                                except:
                                                    hostname = "ERROR"
                                                ##Check if the IP is not internal (fccn, rcts, arquivo.pt) or from other services (uptimerobot, googlebot, semrush)
                                                if "fccn.pt" not in hostname and "uptimerobot.com" not in hostname and "googlebot.com" not in hostname and "rcts.pt" not in hostname and "arquivo.pt" not in hostname and "semrush.com" not in hostname:
                                                    if "imagesearch?q=" in list_line[6]:
                                                        ##Check if the previous request is not also from images.jsp or imagesearch
                                                        if "images.jsp?" not in list_line[10] and "imagesearch?" not in list_line[10]:
                                                            dic_imagesearch, query = get_query("imagesearch", dic_imagesearch, list_line, "API")
                                                    else:
                                                        ##Check if the previous request is not also from search.jsp or textsearch
                                                        if "search.jsp?" not in list_line[10] and "textsearch?" not in list_line[10]:
                                                            dic_textsearch, query = get_query("textsearch", dic_textsearch, list_line, "API")
                            ##Process lines from .JSP requests
                            elif ("/images.jsp?" in list_line[6] or "/search.jsp?" in list_line[6]) and ("images.jsp?" not in list_line[10] or "search.jsp?" not in list_line[10]) and "query=" in list_line[6]:
                                if "python" not in '-'.join(list_line[11:-1]).lower() and "crawl" not in '-'.join(list_line[11:-1]).lower() and "bot" not in '-'.join(list_line[11:-1]).lower():
                                    if IP(list_line[0]).iptype() != "PRIVATE" and IP(list_line[0]).iptype() != "LOOPBACK":
                                        try:
                                            hostname = socket.gethostbyaddr(list_line[0])[0]
                                        except:
                                            hostname = "ERROR"
                                        if "fccn.pt" not in hostname and "uptimerobot.com" not in hostname and "googlebot.com" not in hostname and "rcts.pt" not in hostname and "arquivo.pt" not in hostname and "semrush.com" not in hostname:
                                            if "images.jsp?" in list_line[6]:
                                                if "images.jsp?" not in list_line[10] and "imagesearch?" not in list_line[10]:
                                                    dic_imagesJSP, query = get_query("images.jsp", dic_imagesJSP, list_line, "JSP")
                                            else:
                                                if "search.jsp?" not in list_line[10] and "textsearch?" not in list_line[10]:
                                                    dic_textJSP, query = get_query("search.jsp", dic_textJSP, list_line, "JSP")

    ##Print the results
    with open('dic_imagesearch.txt', 'w') as f:
        print(dic_imagesearch, file=f)

    with open('dic_textsearch.txt', 'w') as f:
        print(dic_textsearch, file=f)

    with open('dic_imagesJSP.txt', 'w') as f:
        print(dic_imagesJSP, file=f)

    with open('dic_textJSP.txt', 'w') as f:
        print(dic_textJSP, file=f)

    with open('list_users.txt', 'w') as f:
        print(List_user, file=f)


if __name__ == '__main__':
    ##Localization of the logs files
    path_logs = "./Data"
    script(path_logs)


"""
###Problems:
#Segurança
1.  ../../../../../../../../../etc/passwd\x00

2.  ><script >alert(String.fromCharCode(88,83,83))</script>
    String.fromCharCode(88,83,83)

3.  fccn site:fccn.pt" and "x"="
    fccn site:fccn.pt'[0]
    Jorge Sampaio' and 'x'='
    Jorge Sampaio'A=0

#Problemas de caracters para resolver
educa\\xc3\\xa7\\xc3\\xa3o sexual
print(u.replace("\\/", "/").encode().decode('unicode_escape'))

#Queries enormes
e.g., scientific amusing helpless soak industrious (...)




###Exemplo de bots/crawls
46.229.168.161
46.229.168.144

149.255.59.14
https://moi.ir/getmedia/  (....)

185.7.215.112 [17/Jan/2020:15:28:46 +0000] "GET /noFrame/replay/20131105174658/http://ww (.....)

#Indonesia
180.241.213.132 [09/Apr/2020:06:51:27 +0100] "GET /images.jsp?l=en&size=all&type=&tools=off&safeSearch=on&query=fccn%20site:fccn.pt\'[0]&btnSubmit=(.....)
180.241.213.132 [09/Apr/2020:06:51:48 +0100] "GET /images.jsp?l=en&size=all&type=&tools=off&safeSearch=on&query=\\"><script%20>alert(String.fromCharCode(88,83,83))</script>&btnSubmit=Pesquisar(.....)
180.241.213.132 [09/Apr/2020:06:52:06 +0100] "GET /images.jsp?l=en&size=all&type=&tools=off&safeSearch=on&query=/etc/passwd&btnSubmit=Pesquisar(.....)

#Russia:
95.106.79.146 - - [02/Apr/2020:04:27:25 +0100] "GET /images.jsp?l=pt&query=Pizza\'[0]&dateSta (.....)


"""