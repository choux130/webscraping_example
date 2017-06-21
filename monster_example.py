########################################################
#################### IMPORT LIBRARY ####################
########################################################
import bs4
import numpy
import pandas
import re
import requests
import datetime
import stop_words

###################################################
#################### ARGUMENTS ####################
###################################################
input_job = "Data Scientist"
input_quote = False # add quotation marks("") to your input_job
input_city = "Durham" # leave empty if input_city is not specified
input_state = "NC"
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
# the date for today
now = datetime.datetime.now()
now_str = now.strftime("%m/%d/%Y")
now_str_name=now.strftime('%m%d%Y')

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
                                'date': now_str,
                                'from':'Monster',
                                'job_location':location,
                                'job_link':link}, ignore_index=True)
cols=['from','date', 'job_id','job_title','job_company','job_location','job_link']
job_df_monster = job_df_monster[cols]
print(job_df_monster.shape)

# delete the duplicated jobs using job link
job_df_monster = job_df_monster.drop_duplicates(['job_link'], keep='first')

# print the dimenstion of the dataframe
print(job_df_monster.shape)

# save the dataframe as a csv file
path = '/Users/chou/Google Drive/websites/github/webscraping_example/output/'+'job_monster_' + now_str_name + '.csv'
job_df_monster.to_csv(path)
# job_df_monster.to_csv( '/Users/chou/Desktop/'+ 'job_monster.csv')


############################################################################
##### Define the terms that I am interested and would like to pick out #####
############################################################################
# import library
import bs4
import numpy
import pandas
import re
import requests
import stop_words

# define the stop_words for future use
stop_words = stop_words.get_stop_words('english') # list out all the English stop word
# print(stop_words)

# read the csv file
job_df_monster = pandas.DataFrame.from_csv(path)

##### Job types #####
type = ['Full-Time', 'Full Time', 'Part-Time', 'Part Time', 'Contract', 'Contractor']
type_lower = [s.lower() for s in type] # lowercases
# map the type_lower to type
type_map = pandas.DataFrame({'raw':type, 'lower':type_lower}) # create a dataframe
type_map['raw'] = ["Full-Time", "Full-Time", 'Part-Time', 'Part-Time', "Contract", 'Contract'] # modify the mapping
type_dic = list(type_map.set_index('lower').to_dict().values()).pop() # use the dataframe to create a dictionary
# print(type_dic)

##### Skills #####
skills = ['R', 'Shiny', 'RStudio', 'Markdown', 'Latex', 'SparkR', 'D3', 'D3.js',
            'Unix', 'Linux', 'MySQL', 'Microsoft SQL server', 'SQL',
            'Python', 'SPSS', 'SAS', 'C++', 'C', 'C#','Matlab','Java',
            'JavaScript', 'HTML', 'HTML5', 'CSS', 'CSS3','PHP', 'Excel', 'Tableau',
            'AWS', 'Amazon Web Services ','Google Cloud Platform', 'GCP',
            'Microsoft Azure', 'Azure', 'Hadoop', 'Pig', 'Spark', 'ZooKeeper',
            'MapReduce', 'Map Reduce','Shark', 'Hive','Oozie', 'Flume', 'HBase', 'Cassandra',
            'NoSQL', 'MongoDB', 'GIS', 'Haskell', 'Scala', 'Ruby','Perl',
            'Mahout', 'Stata']
skills_lower = [s.lower() for s in skills]# lowercases
skills_map = pandas.DataFrame({'raw':skills, 'lower':skills_lower})# create a dataframe
skills_map['raw'] = ['R', 'Shiny', 'RStudio', 'Markdown', 'Latex', 'SparkR', 'D3', 'D3',
            'Unix', 'Linux', 'MySQL', 'Microsoft SQL server', 'SQL',
            'Python', 'SPSS', 'SAS', 'C++', 'C', 'C#','Matlab','Java',
            'JavaScript', 'HTML', 'HTML', 'CSS', 'CSS','PHP', 'Excel', 'Tableau',
            'AWS', 'AWS','GCP', 'GCP',
            'Azure', 'Azure', 'Hadoop', 'Pig', 'Spark', 'ZooKeeper',
            'MapReduce', 'MapReduce','Shark', 'Hive','Oozie', 'Flume', 'HBase', 'Cassandra',
            'NoSQL', 'MongoDB', 'GIS', 'Haskell', 'Scala', 'Ruby','Perl',
            'Mahout', 'Stata']
skills_dic = list(skills_map.set_index('lower').to_dict().values()).pop()# use the dataframe to create a dictionary
# print(skills_dic)

##### Education #####
edu = ['Bachelor', "Bachelor's", 'BS', 'B.S', 'B.S.', 'Master', "Master's", 'Masters', 'M.S.', 'M.S', 'MS',
        'PhD', 'Ph.D.', "PhD's", 'MBA']
edu_lower = [s.lower() for s in edu]# lowercases
edu_map = pandas.DataFrame({'raw':edu, 'lower':edu_lower})# create a dataframe
edu_map['raw'] = ['BS', "BS", 'BS', "BS", 'BS', 'MS', "MS", 'MS', 'MS', 'MS', 'MS',
        'PhD', 'PhD', "PhD", 'MBA'] # modify the mapping
edu_dic = list(edu_map.set_index('lower').to_dict().values()).pop()# use the dataframe to create a dictionary
# print(edu_dic)

##### Major #####
major = ['Computer Science', 'Statistics', 'Mathematics', 'Math','Physics',
            'Machine Learning','Economics','Software Engineering', 'Engineering',
            'Information System', 'Quantitative Finance', 'Artificial Intelligence',
            'Biostatistics', 'Bioinformatics', 'Quantitative']
major_lower = [s.lower() for s in major]# lowercases
major_map = pandas.DataFrame({'raw':major, 'lower':major_lower})# create a dataframe
major_map['raw'] = ['Computer Science', 'Statistics', 'Math', 'Math','Physics',
            'Machine Learning','Economics','Software Engineering', 'Engineering',
            'Information System', 'Quantitative Finance', 'Artificial Intelligence',
            'Biostatistics', 'Bioinformatics', 'Quantitative']# modify the mapping
major_dic = list(major_map.set_index('lower').to_dict().values()).pop()# use the dataframe to create a dictionary

##### Key Words ######
keywords = ['Web Analytics', 'Regression', 'Classification', 'User Experience', 'Big Data',
            'Streaming Data', 'Real-Time', 'Real Time', 'Time Series']
keywords_lower = [s.lower() for s in keywords]# lowercases
keywords_map = pandas.DataFrame({'raw':keywords, 'lower':keywords_lower})# create a dataframe
keywords_map['raw'] = ['Web Analytics', 'Regression', 'Classification', 'User Experience', 'Big Data',
            'Streaming Data', 'Real Time', 'Real Time', 'Time Series']# modify the mapping
keywords_dic = list(keywords_map.set_index('lower').to_dict().values()).pop()# use the dataframe to create a dictionary
# print(keywords_dic)

##############################################
##### For Loop for scraping each job URL #####
##############################################
# empty list to store details for all the jobs
list_type = []
list_skill = []
list_text = []
list_edu = []
list_major = []
list_keywords = []

for i in range(len(job_df_monster)):
    # empty list to store details for each job
    required_type= []
    required_skills = []
    required_edu = []
    required_major = []
    required_keywords = []

    try:
        # get the HTML code from the URL
        job_page = requests.get(job_df_monster.iloc[i, 6])
        # Choose "lxml" as parser
        soup = bs4.BeautifulSoup(job_page.text, "lxml")

        # drop the chunks of 'script','style','head','title','[document]'
        for elem in soup.findAll(['script','style','head','title','[document]']):
            elem.extract()
        # get the lowercases of the texts
        texts = soup.getText(separator=' ').lower()

        # cleaning the text data
        string = re.sub(r'[\n\r\t]', ' ', texts) # remove "\n", "\r", "\t"
        string = re.sub(r'\,', ' ', string) # remove ","
        string = re.sub('/', ' ', string) # remove "/"
        string = re.sub(r'\(', ' ', string) # remove "("
        string = re.sub(r'\)', ' ', string) # remove ")"
        string = re.sub(' +',' ',string) # remove more than one space
        string = re.sub(r'r\s&\sd', ' ', string) # avoid picking 'r & d'
        string = re.sub(r'r&d', ' ', string) # avoid picking 'r&d'
        string = re.sub('\.\s+', ' ', string) # remove "." at the end of sentences

        # Job types
        for typ in type_lower :
            if any(x in typ for x in ['+', '#', '.']):
                typp = re.escape(typ) # make it possible to find out 'c++', 'c#', 'd3.js' without errors
            else:
                typp = typ
            result = re.search(r'(?:^|(?<=\s))' + typp + r'(?=\s|$)', string) # search the string in a string
            if result:
                required_type.append(type_dic[typ])
        list_type.append(required_type)

        # Skills
        for sk in skills_lower :
            if any(x in sk for x in ['+', '#', '.']):
                skk = re.escape(sk)
            else:
                skk = sk
            result = re.search(r'(?:^|(?<=\s))' + skk + r'(?=\s|$)',string)
            if result:
                required_skills.append(skills_dic[sk])
        list_skill.append(required_skills)

        # Education
        for ed in edu_lower :
            if any(x in ed for x in ['+', '#', '.']):
                edd = re.escape(ed)
            else:
                edd = ed
            result = re.search(r'(?:^|(?<=\s))' + edd + r'(?=\s|$)', string)
            if result:
                required_edu.append(edu_dic[ed])
        list_edu.append(required_edu)

        # Major
        for maj in major_lower :
            if any(x in maj for x in ['+', '#', '.']):
                majj = re.escape(maj)
            else:
                majj = maj
            result = re.search(r'(?:^|(?<=\s))' + majj + r'(?=\s|$)', string)
            if result:
                required_major.append(major_dic[maj])
        list_major.append(required_major)

        # Key Words
        for key in keywords_lower :
            if any(x in key for x in ['+', '#', '.']):
                keyy = re.escape(key)
            else:
                keyy = key
            result = re.search(r'(?:^|(?<=\s))' + keyy + r'(?=\s|$)', string)
            if result:
                required_keywords.append(keywords_dic[key])
        list_keywords.append(required_keywords)

        # All text
        words = string.split(' ')
        job_text = set(words) - set(stop_words) # drop stop words
        list_text.append(list(job_text))
    except:
        list_type.append('Forbidden')
        list_skill.append('Forbidden')
        list_edu.append('Forbidden')
        list_major.append('Forbidden')
        list_keywords.append('Forbidden')
        list_text.append('Forbidden')
    print(i)

job_df_monster['job_type'] = list_type
job_df_monster['job_skills'] = list_skill
job_df_monster['job_edu'] = list_edu
job_df_monster['job_major'] = list_major
job_df_monster['job_keywords'] = list_keywords
job_df_monster['job_text'] = list_text

cols=['from','date','job_id','job_title','job_company','job_location','job_link','job_type',
        'job_skills', 'job_edu', 'job_major', 'job_keywords','job_text']
job_df_monster = job_df_monster[cols]

# print the dimenstion of the dataframe
print(job_df_monster.shape)

job_df_monster.to_csv(path)
