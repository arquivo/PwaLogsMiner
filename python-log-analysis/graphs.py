import click
import re
import os
import string
from urllib.parse import unquote
import matplotlib.pyplot as plt
import numpy as np
import spacy
import ast
from urlextract import URLExtract
from ipstack import GeoLookup
import argparse

##These imports are used in the future Profanity figure
#from googletrans import Translator
#from dictionary_profanity_filter import ProfanityFilter

##Debug
#import pdb;pdb.set_trace()

##Model from spacy to classify the terms in the queries 
##More info: https://spacy.io/models/pt#pt_core_news_sm
##It is necessary to download the model (Please read the readme.md)
nlp = spacy.load("pt_core_news_sm")


parser = argparse.ArgumentParser(description='Graphs Log Analysis')
parser.add_argument('-k','--key', help='Private Key GeoLookup ipstack', default= "error")
args = vars(parser.parse_args())


def predict_label(elem):
    """
    The function receives a query (list of terms) and returns the category of that query and the dictionary.
    For each term/entity we predict a label and then choose the label with the highest occurrence in that query.
    """
    dict_predict = {}
    doc = nlp(elem)
    for elem in doc.ents:
        predic = elem.label_
        if predic not in dict_predict:
            dict_predict[predic] = 1
        else:
            dict_predict[predic] += 1
    try:
        final_predict = max(dict_predict, key=dict_predict.get)
    except:
        final_predict = "OTHER"
    return final_predict, dict_predict


###PROCESS FILES INPUT FROM log_analyzer_pg.py

##Process the .TXT and then transform the string in a dictionary
with open('dic_imagesearch.txt') as f:
    dic_imagesearch = f.read()
    dic_imagesearch = ast.literal_eval(dic_imagesearch)

##sort the dictionary
dic_imagesearch = {k: v for k, v in sorted(dic_imagesearch.items(), key=lambda item: item[1])}

with open('dic_textsearch.txt') as f:
    dic_textsearch = f.read()
    dic_textsearch = ast.literal_eval(dic_textsearch)

dic_textsearch = {k: v for k, v in sorted(dic_textsearch.items(), key=lambda item: item[1])}


with open('dic_imagesJSP.txt') as f:
    dic_imagesJSP = f.read()
    dic_imagesJSP = ast.literal_eval(dic_imagesJSP)

dic_imagesJSP = {k: v for k, v in sorted(dic_imagesJSP.items(), key=lambda item: item[1])}


with open('dic_textJSP.txt') as f:
    dic_textJSP = f.read()
    dic_textJSP = ast.literal_eval(dic_textJSP)

dic_textJSP = {k: v for k, v in sorted(dic_textJSP.items(), key=lambda item: item[1])}

with open('list_users.txt') as f:
    list_users = f.read()
    list_users = ast.literal_eval(list_users)

##Since the API used to detect the regions of the IP addresses is paid, 
##we keep a file that contains the processed IPs in order not to process the same IP address a second time.
with open('list_users_processed_country.txt') as f:
    list_users_processed_country = f.read()
    list_users_processed_country = ast.literal_eval(list_users_processed_country)

###Extract all queries from all dictionaries
def extract_queries(dic):
    """
    The function receives a dictionary and returns the queries that are not urls
    """
    extractor = URLExtract()   
    for elem in dic.keys():
        if extractor.find_urls(elem) == []:
            dic_all_queries[elem] = dic[elem]

dic_all_queries = {}
extract_queries(dic_imagesearch)
extract_queries(dic_textsearch)
extract_queries(dic_imagesJSP)
extract_queries(dic_textJSP)

dic_all_queries = {k: v for k, v in sorted(dic_all_queries.items(), key=lambda item: item[1])}

with open('list_queries.txt', 'w') as f:
    print(dic_all_queries, file=f)

###Process the list of users to get the country and city of the IP address
##We used the ipstack. More info: https://ipstack.com/
##10.000 requests/month
key_geolookup = args['key']
geo_lookup = GeoLookup(key_geolookup)

##Process each user to get the country and city and save the result in a list
for elem in list_users:
    IP = elem.split(' &&&& ')[0]
    if IP not in list_users_processed_country:
        try:
            information = geo_lookup.get_location(IP)
            country = information["country_name"]
            city = information["city"]
            list_users_processed_country[IP] = [country, city]
        except:
            print("ERROR Limited Request per Month. Wait to save the IPs processed in a file")

with open('list_users_processed_country.txt', 'w') as f:
    print(list_users_processed_country, file=f)



####FIGURES

##################################################################################################################################################################

#####COUNTRIES

##Preprocessing the list_users_processed_country.txt 

#Get a dictionary with all countries
dic_aux_country = {}
for elem in list_users_processed_country:
    if list_users_processed_country[elem][0] not in dic_aux_country:
        dic_aux_country[list_users_processed_country[elem][0]] = 1
    else:
        dic_aux_country[list_users_processed_country[elem][0]] += 1
    
#Sort dictionary
dic_aux_country = {k: v for k, v in sorted(dic_aux_country.items(), key=lambda item: item[1])}

#Get a dictionary with all cities in Portugal
dic_aux_city_portugal = {}
for elem in list_users_processed_country:
    if list_users_processed_country[elem][0] == "Portugal":
        if list_users_processed_country[elem][1] not in dic_aux_city_portugal:
            dic_aux_city_portugal[list_users_processed_country[elem][1]] = 1
        else:
            dic_aux_city_portugal[list_users_processed_country[elem][1]] += 1

#Sort dictionary 
dic_aux_city_portugal = {k: v for k, v in sorted(dic_aux_city_portugal.items(), key=lambda item: item[1])}

##Get the sum of the values of each dictionary to calculate the percentage of each country or city.
count_all_values_country = sum(dic_aux_country.values())
count_all_values_city_portugal = sum(dic_aux_city_portugal.values())


###FIGURE Countries

plt.figure()
top_1 = dic_aux_country.popitem()
top_2 = dic_aux_country.popitem()
top_3 = dic_aux_country.popitem()
top_4 = dic_aux_country.popitem()
top_5 = dic_aux_country.popitem()
top_6 = dic_aux_country.popitem()
top_7 = dic_aux_country.popitem()
top_8 = dic_aux_country.popitem()
top_1_country = (top_1[1])/(count_all_values_country)
top_2_country = (top_2[1])/(count_all_values_country)
top_3_country = (top_3[1])/(count_all_values_country)
top_4_country = (top_4[1])/(count_all_values_country)
top_5_country = (top_5[1])/(count_all_values_country)
top_6_country = (top_6[1])/(count_all_values_country)
top_7_country = (top_7[1])/(count_all_values_country)
top_8_country = (top_8[1])/(count_all_values_country)
top_others_country = (sum(dic_aux_country.values()))/(count_all_values_country)
labels = [top_1[0], top_2[0], top_3[0], top_4[0], top_5[0], top_6[0], top_7[0], top_8[0], "Others"]
sizes = [top_1_country, top_2_country, top_3_country, top_4_country, top_5_country, top_6_country, top_7_country, top_8_country, top_others_country]
colors = ['green', 'blue', 'yellow', 'red', 'purple', 'brown', 'grey', 'pink', 'orange']
explode = (0.1, 0, 0, 0, 0, 0, 0, 0, 0)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.axis('equal')
plt.title('Top countries')
plt.savefig('Top_countries.png')

###FIGURE Cities in Portugal

plt.figure()
top_1 = dic_aux_city_portugal.popitem()
top_2 = dic_aux_city_portugal.popitem()
top_3 = dic_aux_city_portugal.popitem()
top_4 = dic_aux_city_portugal.popitem()
top_5 = dic_aux_city_portugal.popitem()
top_6 = dic_aux_city_portugal.popitem()
top_7 = dic_aux_city_portugal.popitem()
top_8 = dic_aux_city_portugal.popitem()
top_1_country = (top_1[1])/(count_all_values_city_portugal)
top_2_country = (top_2[1])/(count_all_values_city_portugal)
top_3_country = (top_3[1])/(count_all_values_city_portugal)
top_4_country = (top_4[1])/(count_all_values_city_portugal)
top_5_country = (top_5[1])/(count_all_values_city_portugal)
top_6_country = (top_6[1])/(count_all_values_city_portugal)
top_7_country = (top_7[1])/(count_all_values_city_portugal)
top_8_country = (top_8[1])/(count_all_values_city_portugal)
top_others_country = (sum(dic_aux_city_portugal.values()))/(count_all_values_city_portugal)
labels = [top_1[0], top_2[0], top_3[0], top_4[0], top_5[0], top_6[0], top_7[0], top_8[0], "Others"]
sizes = [top_1_country, top_2_country, top_3_country, top_4_country, top_5_country, top_6_country, top_7_country, top_8_country, top_others_country]
colors = ['green', 'blue', 'yellow', 'red', 'purple', 'brown', 'grey', 'pink', 'orange']
explode = (0.1, 0, 0, 0, 0, 0, 0, 0, 0)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.axis('equal')
plt.title('Top cidades em Portugal')
plt.savefig('Top_city_Portugal.png')


##################################################################################################################################################################


###FIGURE to Categorize queries (Person, Location, Organization, Miscellany)

##Imagesearch

count_person_imagesearch = 0
count_location_imagesearch = 0
count_entities_imagesearch = 0
count_miscellaneous_imagesearch = 0
count_others_imagesearch = 0
count = 0
extractor = URLExtract()
for elem in dic_imagesearch:
    if extractor.find_urls(elem) == []:
        label, dict_predict = predict_label(elem)
        count += 1
        if label == "PER":
            count_person_imagesearch += 1
        elif label == "LOC":
            count_location_imagesearch += 1
        elif label == "ORG":
            count_entities_imagesearch += 1
        elif label == "MISC":
            count_miscellaneous_imagesearch += 1  
        else:
            count_others_imagesearch += 1

plt.figure()
person_imagesearch = (count_person_imagesearch)/(count)
location_imagesearch = (count_location_imagesearch)/(count)
entities_imagesearch = (count_entities_imagesearch)/(count)
miscellaneous_imagesearch = (count_miscellaneous_imagesearch)/(count)
others_imagesearch = (count_others_imagesearch)/(count)
labels = ['Person', 'Locations', 'Entities', 'Miscellaneous', "Not defined"]
sizes = [person_imagesearch, location_imagesearch, entities_imagesearch, miscellaneous_imagesearch, others_imagesearch]
colors = ['green', 'blue', 'yellow', 'red', 'orange']
explode = (0, 0.1, 0, 0, 0)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.axis('equal')
plt.title('Labels From Imagesearch')
plt.savefig('Imagesearch_Labels.png')

####Textsearch
count_person_textsearch = 0
count_location_textsearch = 0
count_entities_textsearch = 0
count_miscellaneous_textsearch = 0
count_others_textsearch = 0
count = 0
extractor = URLExtract()
for elem in dic_textsearch:
    if extractor.find_urls(elem) == []:
        label, dict_predict = predict_label(elem)
        count += 1
        if label == "PER":
            count_person_textsearch += 1
        elif label == "LOC":
            count_location_textsearch += 1
        elif label == "ORG":
            count_entities_textsearch += 1
        elif label == "MISC":
            count_miscellaneous_textsearch += 1  
        else:
            count_others_textsearch += 1

plt.figure()
person_textsearch = (count_person_textsearch)/(count)
location_textsearch = (count_location_textsearch)/(count)
entities_textsearch = (count_entities_textsearch)/(count)
miscellaneous_textsearch = (count_miscellaneous_textsearch)/(count)
others_textsearch = (count_others_textsearch)/(count)
labels = ['Person', 'Locations', 'Entities', 'Miscellaneous', "Not defined"]
sizes = [person_textsearch, location_textsearch, entities_textsearch, miscellaneous_textsearch, others_textsearch]
colors = ['green', 'blue', 'yellow', 'red', 'orange']
explode = (0.1, 0, 0, 0, 0)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.axis('equal')
plt.title('Labels From Textsearch')
plt.savefig('Textsearch_Labels.png')

##########################################################################################################################################################

###FIGURE to check the percentage of URLs per valid request

##Image JSP
count_URL_imageJSP = 0
count_query_imageJSP = 0
count = 0
for elem in dic_imagesJSP.keys():
    elem = elem.replace("“", "")
    elem = elem.replace("”", "")
    elem = elem.replace("\"", "")
    elem = elem.replace("\'", "")
    if elem != "":
        count += 1
        if extractor.find_urls(elem) != []:
            count_URL_imageJSP += 1
        else:
            count_query_imageJSP += 1

plt.figure()
perc_URL = (count_URL_imageJSP)/(count)
perc_query = (count_query_imageJSP)/(count) 
labels = ['URL', "Query"]
sizes = [perc_URL, perc_query]
colors = ['green', 'red']
explode = (0.1, 0)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.axis('equal')
plt.title('Image JSP')
plt.savefig('Image_JSP.png')

##Text JSP

count_URL_text = 0
count_query_text = 0
for elem in dic_textJSP.keys():
    elem = elem.replace("“", "")
    elem = elem.replace("”", "")
    elem = elem.replace("\"", "")
    elem = elem.replace("\'", "")
    if elem != "":
        if extractor.find_urls(elem) != []:
            count_URL_text += 1
        else:
            count_query_text += 1

plt.figure()
perc_URL = (count_URL_text)/(count_URL_text+count_query_text)
perc_query = (count_query_text)/(count_URL_text+count_query_text) 
labels = ['URL', "Query"]
sizes = [perc_URL, perc_query]
colors = ['green', 'red']
explode = (0.1, 0)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.axis('equal')
plt.title('Text JSP')
plt.savefig('Text_JSP.png')

######################################################################################################################################################################################

"""

###FIGURE to check the percentage of queries that are related with Profanity (sex, death,...). But, It still doesn't work 100%.

## Profanity Imagesearch


profanity_filter = ProfanityFilter()
translator = Translator()


count_NSFW_ImageSearch = 0
count_normal_ImageSearch = 0
for elem in dic_imagesearch.keys():
    elem = elem.replace("“", "")
    elem = elem.replace("”", "")
    elem = elem.replace("\"", "")
    elem = elem.replace("\'", "")
    if elem != "":
        translate_word = translator.translate(elem, dest='en', src='pt')
        #import pdb;pdb.set_trace()
        if not profanity_filter.is_clean(translate_word.text):
            count_NSFW_ImageSearch += 1
        else:
            count_normal_ImageSearch += 1

plt.figure()
perc_NSFW = (count_NSFW_ImageSearch)/(count_NSFW_ImageSearch+count_normal_ImageSearch)
perc_normal = (count_normal_ImageSearch)/(count_NSFW_ImageSearch+count_normal_ImageSearch) 
labels = ['Profanity', "Normal"]
sizes = [perc_NSFW, perc_normal]
colors = ['green', 'red']
explode = (0.1, 0)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.axis('equal')
plt.title('Imagesearch')
plt.savefig('Imagesearch_NSFW.png')


## Profanity Textsearch

count_NSFW_TextSearch = 0
count_normal_TextSearch = 0
for elem in dic_textsearch.keys():
    elem = elem.replace("“", "")
    elem = elem.replace("”", "")
    elem = elem.replace("\"", "")
    elem = elem.replace("\'", "")
    if elem != "":
        translate_word = translator.translate(elem, dest='en', src='pt')
        #import pdb;pdb.set_trace()
        if not profanity_filter.is_clean(translate_word.text):
            count_NSFW_TextSearch += 1
        else:
            count_normal_TextSearch += 1

plt.figure()
perc_NSFW = (count_NSFW_TextSearch)/(count_NSFW_TextSearch+count_normal_TextSearch)
perc_normal = (count_normal_TextSearch)/(count_NSFW_TextSearch+count_normal_TextSearch) 
labels = ['Profanity', "Normal"]
sizes = [perc_NSFW, perc_normal]
colors = ['green', 'red']
explode = (0.1, 0)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.axis('equal')
plt.title('Textsearch')
plt.savefig('Textsearch_NSFW.png')
"""

####################################################################################################################################################################


###FIGURE to show the 25 TOP queries for each dictionary

##Preprocessing each dictionary

top = 25

new_dic_imagesearch = {}
for i in range(top):
    aux = dic_imagesearch.popitem()
    new_dic_imagesearch[aux[0]] = aux[1]

new_dic_textsearch = {}
for i in range(top):
    aux = dic_textsearch.popitem()
    new_dic_textsearch[aux[0]] = aux[1]

new_dic_textJSP = {}
for i in range(top):
    aux = dic_textJSP.popitem()
    new_dic_textJSP[aux[0]] = aux[1]

new_dic_imagesJSP = {}
for i in range(top):
    aux = dic_imagesJSP.popitem()
    new_dic_imagesJSP[aux[0]] = aux[1]

##Imagesearch

fig, ax = plt.subplots(figsize=(25, 10))
searchQueries = new_dic_imagesJSP.keys()
y_pos = np.arange(len(searchQueries))
internalQueryCount = new_dic_imagesJSP.values()
p1=ax.barh(y_pos, internalQueryCount, align='center',color='green')
ax.set_yticks(y_pos)

ax.set_yticklabels(searchQueries)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Total')
ax.set_ylabel('Queries')
ax.set_title(u'Top 10 Queries Imagesearch')

fig.tight_layout()
plt.subplots_adjust(left=0.38)

plt.grid(axis='x',color='black', linestyle=':', linewidth=0.8, alpha=0.5)
fig.savefig('TopQueriesImagesearch.png', bbox_inches='tight')


##Textsearch


fig, ax = plt.subplots(figsize=(25, 10))
searchQueries = new_dic_textsearch.keys()
y_pos = np.arange(len(searchQueries))
internalQueryCount = new_dic_textsearch.values()
p1=ax.barh(y_pos, internalQueryCount, align='center',color='green')
ax.set_yticks(y_pos)

ax.set_yticklabels(searchQueries)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Total')
ax.set_ylabel('Queries')
ax.set_title(u'Top 10 Queries Textsearch')

fig.tight_layout()
plt.subplots_adjust(left=0.38)

plt.grid(axis='x',color='black', linestyle=':', linewidth=0.8, alpha=0.5)
fig.savefig('TopQueriesTextsearch.png', bbox_inches='tight')


##Images.jsp


fig, ax = plt.subplots(figsize=(25, 10))
searchQueries = new_dic_imagesearch.keys()
y_pos = np.arange(len(searchQueries))
internalQueryCount = new_dic_imagesearch.values()
p1=ax.barh(y_pos, internalQueryCount, align='center',color='green')
ax.set_yticks(y_pos)

ax.set_yticklabels(searchQueries)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Total')
ax.set_ylabel('Queries')
ax.set_title(u'Top 10 Queries ImagesJSP')

fig.tight_layout()
plt.subplots_adjust(left=0.38)

plt.grid(axis='x',color='black', linestyle=':', linewidth=0.8, alpha=0.5)
fig.savefig('TopQueriesImagesJSP.png', bbox_inches='tight')


##Search.jsp


fig, ax = plt.subplots(figsize=(25, 10))
searchQueries = new_dic_textJSP.keys()
y_pos = np.arange(len(searchQueries))
internalQueryCount = new_dic_textJSP.values()
p1=ax.barh(y_pos, internalQueryCount, align='center',color='green')
ax.set_yticks(y_pos)

ax.set_yticklabels(searchQueries)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Total')
ax.set_ylabel('Queries')
ax.set_title(u'Top 10 Queries SearchJSP')

fig.tight_layout()
plt.subplots_adjust(left=0.38)

plt.grid(axis='x',color='black', linestyle=':', linewidth=0.8, alpha=0.5)
fig.savefig('TopQueriesSearchJSP.png', bbox_inches='tight')

