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
BASE_URL_careerbuilder = 'http://www.careerbuilder.com'

#####################################################
##### Function for Transform searching keywords #####
#####################################################
# The default "quote = False"
def transform(input,sign, quote = False):
    syntax = input.replace(" ", sign)
    if quote == True:
        syntax = ''.join(['%2522', syntax, '%2522'])
    return(syntax)

######################################
########## Generate the URL ##########
######################################
url_careerbuilder_list = [ BASE_URL_careerbuilder, '/jobs-',
    transform(input_job, sign, input_quote), '-in-',
    transform(input_city, sign, input_quote),',', input_state]
url_careerbuilder = ''.join(url_careerbuilder_list)
print(url_careerbuilder)

# get the HTML code from the URL
rawcode_careerbuilder = requests.get(url_careerbuilder)
# Choose "lxml" as parser
soup_careerbuilder = bs4.BeautifulSoup(rawcode_careerbuilder.text, "lxml")

# total number of results
num_total_careerbuilder = soup_careerbuilder.find(
                            'div', {'class' : 'count'}).contents[0]
print(num_total_careerbuilder)
num_total_careerbuilder = int(re.sub('[\(\)\{\}<>]', '',
                            num_total_careerbuilder).split()[0])
print(num_total_careerbuilder)

# total number of pages
num_pages_careerbuilder = int(numpy.ceil(num_total_careerbuilder/25.0))
print(num_pages_careerbuilder)

# create an empty dataframe
job_df_careerbuilder = pandas.DataFrame()

########################################
##### Loop for all the total pages #####
########################################
for i in range(1, num_pages_careerbuilder+1):
    # generate the URL
    url = ''.join([url_careerbuilder,'?page_number=', str(i)])
    print(url)

    # get the HTML code from the URL
    rawcode = requests.get(url)
    soup = bs4.BeautifulSoup(rawcode.text, "lxml")

    # pick out all the "div" with "class="job-row"
    divs = soup.findAll("div")
    job_divs = [jp for jp in divs if not jp.get('class') is None
                            and 'job-row' in jp.get('class')]

    # loop for each div chunk
    for job in job_divs:
        try:
            # job id
            id = job.find('h2',{'class' : 'job-title'}).find('a').attrs['data-job-did']
            # job link related to job id
            link = BASE_URL_careerbuilder + '/job/' + id
            # job title
            title = job.find('h2', {'class' : 'job-title'}).text.strip()
            # job company
            company = job.find('div', {'class' : 'columns large-2 medium-3 small-12'}).find(
                        'h4', {'class': 'job-text'}).text.strip()
            # job location
            location = job.find('div', {'class' : 'columns end large-2 medium-3 small-12'}).find(
                        'h4', {'class': 'job-text'}).text.strip()
        except:
            continue

        job_df_careerbuilder = job_df_careerbuilder.append({'job_title': title,
                                'job_id': id,
                                'job_company': company,
                                'from':'Careerbuilder',
                                'job_location':location,
                                'job_link':link},ignore_index=True)
cols=['from','job_id','job_title','job_company','job_location','job_link']
job_df_careerbuilder = job_df_careerbuilder[cols]
print(job_df_careerbuilder.shape)

# delete the duplicated jobs using job link
job_df_careerbuilder = job_df_careerbuilder.drop_duplicates(['job_link'], keep='first')

# print the dimenstion of the dataframe
print(job_df_careerbuilder.shape)

# save the dataframe as a csv file
job_df_careerbuilder.to_csv( '/Users/chou/Desktop/'+ 'job_careerbuilder.csv')
