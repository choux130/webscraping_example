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
sign = "-"
BASE_URL_monster = 'https://www.monster.com'

#####################################################
##### Function for Transform searching keywords #####
#####################################################
# The default "quote = False"
def transform(input,sign, quote = False):
    syntax = input.replace(" ", sign)
    if quote == True:
        syntax = ''.join(['__22', syntax, '__22'])
    return(syntax)

######################################
########## Generate the URL ##########
######################################
url_monster_list = [ BASE_URL_monster, '/jobs/search/?q=',
                    transform(input_job, sign, input_quote),
                    '&where=', transform(input_city, sign, input_quote),
                    '__2C-', input_state]
url_monster = ''.join(url_monster_list)
print(url_monster)

# get the HTML code from the URL
rawcode_monster = requests.get(url_monster)
# Choose "lxml" as parser
soup_monster = bs4.BeautifulSoup(rawcode_monster.text, "lxml")

# total number of results
num_total_monster = int(soup_monster.find('h2',
                    {'class': 'page-title hidden-xs'}).contents[0].split()[0])
print(num_total_monster)

# total number of pages
num_pages_monster = int(numpy.ceil(num_total_monster/25.0))
print(num_pages_monster)

# create an empty dataframe
job_df_monster = pandas.DataFrame()

########################################
##### Loop for all the total pages #####
########################################
for i in range(1, num_pages_monster+1):
    # generate the URL
    url = ''.join([url_monster, '&page=', str(i)])
    print(url)

    # get the HTML code from the URL
    rawcode = requests.get(url)
    soup = bs4.BeautifulSoup(rawcode.text, "lxml")

    # pick out all the "div" with "class="job-row"
    divs = soup.findAll("div")
    job_divs = [jp for jp in divs if not jp.get('class') is None
                    and 'js_result_container' in jp.get('class')
                    and 'featured-ad' not in jp.get('class')]

    # loop for each div chunk
    for job in job_divs:
        try:
            # job id
            id = job.find('a', attrs={'data-m_impr_a_placement_id': 'JSR2'}).attrs['data-m_impr_j_postingid']
            # job link related to job id
            link = 'http://job-openings.monster.com/monster/' + id
            # job title
            title = job.find('a', attrs={'data-m_impr_a_placement_id': 'JSR2'})
            title = title.find('span').text.strip()
            # job company
            company = job.find('div', {'class': 'company'})
            company = company.find('a')
            company = company.find('span').text.strip()
            # job location
            location = job.find('div', {'class': 'job-specs job-specs-location'})
            location = location.find('p')
            location = location.find('a').text.strip()
        except:
            continue

        job_df_monster = job_df_monster.append({'job_title': title,
                                'job_id': id,
                                'job_company': company,
                                'from':'Monster',
                                'job_location':location,
                                'job_link':link}, ignore_index=True)
cols=['from','job_id','job_title','job_company','job_location','job_link']
job_df_monster = job_df_monster[cols]
print(job_df_monster.shape)

# delete the duplicated jobs using job link
job_df_monster = job_df_monster.drop_duplicates(['job_link'], keep='first')

# print the dimenstion of the dataframe
print(job_df_monster.shape)

# save the dataframe as a csv file
job_df_monster.to_csv( '/Users/chou/Desktop/'+ 'job_monster.csv')
