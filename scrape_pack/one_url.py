############################
##### Import Libraries #####
############################
import bs4
import numpy
import pandas
import re
import requests
import datetime

#####################################################
##### Function for Transform searching keywords #####
#####################################################
# The default "quote = False"
def transform(input,sign, quote = False):
    syntax = input.replace(" ", sign)
    if quote == True:
        syntax = ''.join(['"', syntax, '"'])
    return(syntax)

# the date for today
now = datetime.datetime.now()
now_str = now.strftime("%m/%d/%Y")

#############################################################
##### Function for generating URL and scrape basic Info #####
#############################################################
# Indeed
def basic_indeed(BASE_URL_indeed, input_job, input_city, input_state, input_quote, sign):
    # generate URL
    if not input_city: # if (input_city is "")
        url_indeed_list = [ BASE_URL_indeed, '/jobs?q=', transform(input_job, sign, input_quote),
                        '&l=', input_state]
        url_indeed = ''.join(url_indeed_list)
    else: # input_city is not ""
        url_indeed_list = [ BASE_URL_indeed, '/jobs?q=', transform(input_job, sign, input_quote),
                        '&l=', transform(input_city, sign), '%2C+', input_state]
        url_indeed = ''.join(url_indeed_list)
    print(url_indeed)

    # get the HTML code from the URL
    rawcode_indeed = requests.get(url_indeed)
    # Choose "lxml" as parser
    soup_indeed = bs4.BeautifulSoup(rawcode_indeed.text, "lxml")

    # total number of results
    num_total_indeed = soup_indeed.find(
                            id = 'searchCount').contents[0].split()[-1]
    num_total_indeed = re.sub("[^0-9]","", num_total_indeed) # remove non-numeric characters in the string
    num_total_indeed = int(num_total_indeed)
    print(num_total_indeed)

    # total number of pages
    num_pages_indeed = int(numpy.ceil(num_total_indeed/10.0))
    print(num_pages_indeed)

    # create an empty dataframe
    job_df_indeed = pandas.DataFrame()
    # loop for all the total pages
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
                                    'date': now_str,
                                    'from':'Indeed',
                                    'job_location':location,
                                    'job_link':link},ignore_index=True)
    cols=['from','date','job_id','job_title','job_company','job_location','job_link']
    job_df_indeed = job_df_indeed[cols]

    # delete the duplicated jobs using job link
    job_df_indeed = job_df_indeed.drop_duplicates(['job_link'], keep='first')
    return(job_df_indeed)

# Monster
def basic_monster(BASE_URL_monster, input_job, input_city, input_state, input_quote, sign):
    # generate URL
    if not input_city: # if (input_city is "")
        url_monster_list = [ BASE_URL_monster, '/jobs/search/?q=',
                    transform(input_job, sign, input_quote),
                    '&where=', input_state]
        url_monster = ''.join(url_monster_list)
    else: # input_city is not ""
        url_monster_list = [ BASE_URL_monster, '/jobs/search/?q=',
                        transform(input_job, sign, input_quote),
                        '&where=', transform(input_city, sign),
                        '__2C-', input_state]
        url_monster = ''.join(url_monster_list)
    print(url_monster)

    # get the HTML code from the URL
    rawcode_monster = requests.get(url_monster)
    # Choose "lxml" as parser
    soup_monster = bs4.BeautifulSoup(rawcode_monster.text, "lxml")

    # total number of results
    num_total_monster = soup_monster.find('h2',
                        {'class': 'page-title hidden-xs'}).contents[0].split()[0]
    num_total_monster = re.sub("[^0-9]","", num_total_monster) # remove non-numeric characters in the string
    num_total_monster = int(num_total_monster) # transform from string to integer
    print(num_total_monster)

    # total number of pages
    num_pages_monster = int(numpy.ceil(num_total_monster/25.0))
    print(num_pages_monster)

    # create an empty dataframe
    job_df_monster = pandas.DataFrame()
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
                                    'date': now_str,
                                    'from':'Monster',
                                    'job_location':location,
                                    'job_link':link}, ignore_index=True)
    cols=['from','date', 'job_id','job_title','job_company','job_location','job_link']
    job_df_monster = job_df_monster[cols]

    # delete the duplicated jobs using job link
    job_df_monster = job_df_monster.drop_duplicates(['job_link'], keep='first')
    return(job_df_monster)

# Dice
def basic_dice(BASE_URL_dice, input_job, input_city, input_state, input_quote, sign):
    if not input_city: # if (input_city is "")
        url_dice_list = [ BASE_URL_dice, '/jobs?q=', transform(input_job, sign , input_quote),
                            '+&l=', input_state ]
        url_dice = ''.join(url_dice_list)
    else: # input_city is not ""
        url_dice_list = [ BASE_URL_dice, '/jobs?q=', transform(input_job, sign , input_quote),
                        '&l=', transform(input_city, sign), '%2C+', input_state ]
        url_dice = ''.join(url_dice_list)
    print(url_dice)

    # get the HTML code from the URL
    rawcode_dice = requests.get(url_dice)
    # Choose "lxml" as parser
    soup_dice = bs4.BeautifulSoup(rawcode_dice.text, "lxml")

    # total number of results
    num_total_dice = soup_dice.find(id = 'posiCountMobileId').contents[0]
    num_total_dice = re.sub("[^0-9]","", num_total_dice) # remove non-numeric characters in the string
    num_total_dice = int(num_total_dice) # transform from string to integer
    print(num_total_dice)

    # total number of pages
    num_pages_dice = int(numpy.ceil(num_total_dice/30.0))
    print(num_pages_dice)

    # create an empty dataframe
    job_df_dice = pandas.DataFrame()
    for i in range(num_pages_dice+1):
        # generate the URL
        if not input_city: # if (input_city is "")
            url_list = [ BASE_URL_dice, '/jobs/q-', transform(input_job, sign , input_quote),
                            '-l-', input_state, '-startPage-', str(i),'-jobs']
            url = ''.join(url_list)
        else: # input_city is not ""
            url_list = [ BASE_URL_dice, '/jobs/q-', transform(input_job, sign , input_quote),
                            '-l-', transform(input_city, sign), '%2C_',
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
                link = job.find('ul', {'class': 'list-inline'}).find('li').find('h3').find('a').attrs['href']
                # job title
                title = job.find('ul', {'class': 'list-inline'}).find('li').find(
                                    'h3').find('a').attrs['title']
                # job company
                company = job.find('ul', {'class': 'list-inline details row'}).find(
                        'li', {'class':'employer col-sm-3 col-xs-12 col-md-2 col-lg-3 text-ellipsis'}).find(
                        'span', {'class':'hidden-xs'}).find('a').text.strip()
                # job location
                location = job.find('ul', {'class': 'list-inline details row'}).find(
                        'li', {'class':'location col-sm-3 col-xs-12 col-md-2 col-lg-3 margin-top-3 text-ellipsis'}).find(
                        'span',{'itemprop':'address'}).find('span',{'class':'jobLoc'}).text.strip()
            except:
                continue

            job_df_dice = job_df_dice.append({'job_title': title,
                                    'job_id': id,
                                    'job_company': company,
                                    'date': now_str,
                                    'from':'Dice',
                                    'job_location':location,
                                    'job_link':link},ignore_index=True)
    cols=['from','date','job_id','job_title','job_company','job_location','job_link']
    job_df_dice=job_df_dice[cols]

    # delete the duplicated jobs using job link
    job_df_dice = job_df_dice.drop_duplicates(['job_link'], keep='first')

    # print the dimenstion of the dataframe
    return(job_df_dice)

# Careerbuilder
def basic_careerbuilder(BASE_URL_careerbuilder, input_job, input_city, input_state, input_quote, sign):
    if not input_city: # if (input_city is "")
        url_careerbuilder_list = [ BASE_URL_careerbuilder, '/jobs-',
            transform(input_job, sign, input_quote), '-in-',input_state]
        url_careerbuilder = ''.join(url_careerbuilder_list)
    else: # input_city is not ""
        url_careerbuilder_list = [ BASE_URL_careerbuilder, '/jobs-',
            transform(input_job, sign, input_quote), '-in-',
            transform(input_city, sign),',', input_state]
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
                                    'date': now_str,
                                    'from':'Careerbuilder',
                                    'job_location':location,
                                    'job_link':link},ignore_index=True)
    cols=['from','date','job_id','job_title','job_company','job_location','job_link']
    job_df_careerbuilder = job_df_careerbuilder[cols]

    # delete the duplicated jobs using job link
    job_df_careerbuilder = job_df_careerbuilder.drop_duplicates(['job_link'], keep='first')
    return(job_df_careerbuilder)
