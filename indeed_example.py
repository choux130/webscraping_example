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
BASE_URL_indeed = 'http://www.indeed.com'

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
url_indeed_list = [ BASE_URL_indeed, '/jobs?q=', transform(input_job, sign, input_quote),
                    '&l=', transform(input_city, sign, input_quote), '%2C+', input_state]
url_indeed = ''.join(url_indeed_list)
print(url_indeed)

# get the HTML code from the URL
rawcode_indeed = requests.get(url_indeed)
# Choose "lxml" as parser
soup_indeed = bs4.BeautifulSoup(rawcode_indeed.text, "lxml")

# total number of results
num_total_indeed = int(soup_indeed.find(
                        id = 'searchCount').contents[0].split()[-1].replace(',', ''))
print(num_total_indeed)

# total number of pages
num_pages_indeed = int(numpy.ceil(num_total_indeed/10.0))
print(num_pages_indeed)

# create an empty dataframe
job_df_indeed = pandas.DataFrame()

########################################
##### Loop for all the total pages #####
########################################
for i in range(1, num_pages_indeed+1):
    # generate the URL
    url = ''.join([url_indeed, '&start=', str(i*10)])
    print(url)

    # get the HTML code from the URL
    rawcode = requests.get(url)
    soup = bs4.BeautifulSoup(rawcode.text, "lxml")

    # pick out all the "div" with "class="job-row"
    divs = soup.findAll("div")
    job_divs = [jp for jp in divs if not jp.get('class') is None
                    and 'row' in jp.get('class')]

    # loop for each div chunk
    for job in job_divs:
        try:
            # job id
            id = job.get('data-jk', None)
            # job link related to job id
            link = BASE_URL_indeed + '/rc/clk?jk=' + id
            # job title
            title = job.find('a', attrs={'data-tn-element': 'jobTitle'}).attrs['title']
            # job company
            company = job.find('span', {'class': 'company'}).text.strip()
            # job location
            location = job.find('span', {'class': 'location'}).text.strip()
        except:
            continue

        job_df_indeed = job_df_indeed.append({'job_title': title,
                                'job_id': id,
                                'job_company': company,
                                'from':'Indeed',
                                'job_location':location,
                                'job_link':link},ignore_index=True)
cols=['from','job_id','job_title','job_company','job_location','job_link']
job_df_indeed = job_df_indeed[cols]
print(job_df_indeed.shape)

# delete the duplicated jobs using job link
job_df_indeed = job_df_indeed.drop_duplicates(['job_link'], keep='first')

# print the dimenstion of the dataframe
print(job_df_indeed.shape)

# save the dataframe as a csv file
job_df_indeed.to_csv( '/Users/chou/Desktop/'+ 'job_indeed.csv')
