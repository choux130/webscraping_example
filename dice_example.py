########################################################
#################### IMPORT LIBRARY ####################
########################################################
import bs4
import numpy
import pandas
import re
import requests

###################################################
#################### ARGUMENTS ####################
###################################################
input_job = "data scientist"
input_quote = False # add "" on your searching keywords
input_city = "New York"
input_state = "NY"
sign = "+"
BASE_URL_dice = 'https://www.dice.com'

#####################################################
##### Function for Transform searching keywords #####
#####################################################
# The default "quote = False"
def transform(input,sign, quote = False):
    syntax = input.replace(" ", sign)
    if quote == True:
        syntax = ''.join(['"', syntax, '"'])
    return(syntax)

######################################
########## Generate the URL ##########
######################################
url_dice_list = [ BASE_URL_dice, '/jobs?q=', transform(input_job, sign , input_quote),
                    '&l=', transform(input_city, sign , input_quote), '%2C+', input_state ]
url_dice = ''.join(url_dice_list)
print(url_dice)

# get the HTML code from the URL
rawcode_dice = requests.get(url_dice)
# Choose "lxml" as parser
soup_dice = bs4.BeautifulSoup(rawcode_dice.text, "lxml")

# total number of results
num_total_dice = int(soup_dice.find(id = 'posiCountMobileId').contents[0].replace(',', ''))
print(num_total_dice)

# total number of pages
num_pages_dice = int(numpy.ceil(num_total_dice/30.0))
print(num_pages_dice)

# create an empty dataframe
job_df_dice = pandas.DataFrame()

########################################
##### Loop for all the total pages #####
########################################
for i in range(num_pages_dice+1):
    # generate the URL
    url_list = [ BASE_URL_dice, '/jobs/q-', transform(input_job, sign , input_quote),
                        '-l-', transform(input_city, sign , input_quote), '%2C_',
                        input_state, '-startPage-', str(i),'-jobs']
    url = ''.join(url_list)
    print(url)

    # get the HTML code from the URL
    rawcode = requests.get(url)
    soup = bs4.BeautifulSoup(rawcode.text, "lxml")

    # pick out all the "div" with "class="job-row"
    divs = soup.findAll("div")
    job_divs = [jp for jp in divs if not jp.get('class') is None
                    and 'complete-serp-result-div' in jp.get('class')]

    # loop for each div chunk
    for job in job_divs:
        try:
            # job id
            id = job.find('input', {'type':'hidden'}).attrs['id']
            # job link related to job id
            link = 'http://job-openings.monster.com/monster/' + id
            # job title
            title = job.find('ul', {'class': 'list-inline'}).find('li').find(
                                'h3').find('a').attrs['title']#text.strip()
            # job company
            company = job.find('ul', {'class': 'list-inline details row'}).find(
                    'li', {'class':'employer col-sm-3 col-xs-12 col-md-2 col-lg-3 text-ellipsis'}).find(
                    'span', {'class':'hidden-xs'}).find('a').text.strip()
            # job location
            location = job.find('ul', {'class': 'list-inline details row'}).find(
                    'li', {'class':'location col-sm-3 col-xs-12 col-md-2 col-lg-3 margin-top-3 text-ellipsis'}).text
        except:
            continue

        job_df_dice = job_df_dice.append({'job_title': title,
                                'job_id': id,
                                'job_company': company,
                                'from':'Dice',
                                'job_location':location,
                                'job_link':link},ignore_index=True)
cols=['from','job_id','job_title','job_company','job_location','job_link']
job_df_dice=job_df_dice[cols]
print(job_df_dice.shape)

# delete the duplicated jobs using job link
job_df_dice = job_df_dice.drop_duplicates(['job_link'], keep='first')

# print the dimenstion of the dataframe
print(job_df_dice.shape)

# save the dataframe as a csv file
job_df_dice.to_csv( '/Users/chou/Desktop/'+ 'job_dice.csv')
