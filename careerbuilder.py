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
input_quote = False
input_city = "New York"
input_state = "NY"

BASE_URL_careerbuilder = 'http://www.careerbuilder.com'

# class syntax:
#     def __init__(self, input, sign, quote = False):
#         self.input = input
#         self.sign = sign
#         self.quote = quote
#
#     def transform(self):
#         syntax.output = self.input.replace(" ", self.sign)
#         if self.quote == True:
#              syntax.output = ''.join(['"', syntax.output, '"'])
#         return(syntax.output)

def transform(input,sign, quote = False):
    syntax = input.replace(" ", sign)
    if quote == True:
        syntax = ''.join(['%2522', syntax, '%2522'])
    return(syntax)


############### Careerbuilder ###############
### The example url
### http://www.careerbuilder.com/jobs-data-scientist-in-Cary,NC
### http://www.careerbuilder.com/jobs-data-scientist-in-new-york,ny

sign = "-"

url_careerbuilder_list = [ BASE_URL_careerbuilder, '/jobs-',
                    transform(input_job, sign, input_quote), '-in-', transform(input_city, sign, input_quote),
                    ',', input_state]
url_careerbuilder = ''.join(url_careerbuilder_list)
print(url_careerbuilder)

rawcode_careerbuilder = requests.get(url_careerbuilder)
soup_careerbuilder = bs4.BeautifulSoup(rawcode_careerbuilder.text, "lxml")
num_total_careerbuilder = soup_careerbuilder.find(
                            'div', {'class' : 'count'}).contents[0]
print(num_total_careerbuilder)
num_total_careerbuilder = int(re.sub('[\(\)\{\}<>]', '',
                            num_total_careerbuilder).split()[0])
print(num_total_careerbuilder)

num_pages_careerbuilder = int(numpy.ceil(num_total_careerbuilder/25.0))
print(num_pages_careerbuilder)


job_df_careerbuilder = pandas.DataFrame()
for i in range(1, num_pages_careerbuilder+1):
    print(i)
    url_careerbuilder_list = [ BASE_URL_careerbuilder, '/jobs-',
                        transform(input_job, sign, input_quote), '-in-', transform(input_city, sign, input_quote),
                        ',', input_state,"&page_number=", i]
    url = ''.join([url_careerbuilder,'?page_number=', str(i)])
    print(url)

    rawcode = requests.get(url)
    soup = bs4.BeautifulSoup(rawcode.text, "lxml")

    divs = soup.findAll("div")
    job_divs = [jp for jp in divs if not jp.get('class') is None
                    and 'job-row' in jp.get('class')]

    for job in job_divs:
        try:
            id = job.find('h2',{'class' : 'job-title'}).find('a').attrs['data-job-did']
            title = job.find('h2', {'class' : 'job-title'}).text.strip()
            company = job.find('div', {'class' : 'columns large-2 medium-3 small-12'}).find(
                        'h4', {'class': 'job-text'}).text.strip()
            location = job.find('div', {'class' : 'columns end large-2 medium-3 small-12'}).find(
                        'h4', {'class': 'job-text'}).text.strip()
            link = BASE_URL_careerbuilder + '/job/' + id
        except:
            continue

        job_df_careerbuilder = job_df_careerbuilder.append({'job_title': title,
                                'job_id': id,
                                'job_company': company,
                                'from':'Careerbuilder',
                                'job_location':location,
                                'job_link':link},ignore_index=True)
cols=['from','job_id','job_title','job_company','job_location','job_link']
job_df_careerbuilder = job_df_careerbuilder[cols] # reorder the columns of dataframe
job_df_careerbuilder = job_df_careerbuilder.drop_duplicates(['job_link'], keep='first')
print(job_df_careerbuilder.shape)

job_df_careerbuilder.to_csv('/Users/chou/Desktop/job.csv')






### Job types
type = ['Full-time', 'Part-time', 'Contractor', 'Contract', 'Full time', 'Part time']
type_lower = [s.lower() for s in type]
type_map = pandas.DataFrame({'raw':type, 'lower':type_lower})
type_dic = list(type_map.set_index('lower').to_dict().values()).pop()

### Skills
skills = ['Scala', 'Ruby', 'C++', 'Perl', 'R', 'Java', 'Matlab', 'JavaScript',
          'Python', 'SPSS', 'D3.js', 'Tableau', 'Excel', 'SAS', 'D3', 'Mahout',
          'Hadoop', 'Pig', 'Spark', 'ZooKeeper', 'MapReduce', 'Shark', 'Hive',
          'Oozie', 'Flume', 'HBase', 'Cassandra', 'NoSQL', 'SQL', 'MongoDB', 'GIS',
          'AWS', 'Haskell', 'PHP', 'Perl', 'Stata', 'Shiny']
skills_lower = [s.lower() for s in skills]
skills_map = pandas.DataFrame({'raw':skills, 'lower':skills_lower})
skills_dic = list(skills_map.set_index('lower').to_dict().values()).pop()

### Education
edu = ['Bachelor', 'Master', 'PhD', 'MBA', 'M.S.', 'M.S', 'MS', 'Ph.D.', 'BS',
        "Bachelor's", "Master's", "PhD's"]
edu_lower = [s.lower() for s in edu]
edu_map = pandas.DataFrame({'raw':edu, 'lower':edu_lower})
edu_dic = list(edu_map.set_index('lower').to_dict().values()).pop()

### Major
major = ['Computer Science', 'Statistics', 'Mathematics', 'Math','Physics',
            'Machine Learning','Economics','Software Engineering', 'Engineering',
            'Information System', 'Quantitative Finance', 'Biostatistics', 'Bioinformatics']
major_lower = [s.lower() for s in major]
major_map = pandas.DataFrame({'raw':major, 'lower':major_lower})
major_dic = list(major_map.set_index('lower').to_dict().values()).pop()

# Certain parts of English speech, like conjunctions (“for”, “or”) or the word “the” are meaningless to a topic model.
# These terms are called stop words and need to be removed from our token list.
stop_words = stop_words.get_stop_words('english')

def scrape_job(data):
    job_type = []
    job_skills = []
    job_edu = []
    job_major = []
    job_words = []

    for i in range(len(data)): #len(job_df)
    # https://www.tutorialspoint.com/python/python_exceptions.htm
        print(i)
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'}
            job_page = requests.get(data.iloc[i, 5], headers=headers)
        except:
            job_type.append('Forbidden')
            job_skills.append('Forbidden')
            job_edu.append('Forbidden')
            job_major.append('Forbidden')
            job_words.append('Forbidden')
            continue

        soup = bs4.BeautifulSoup(job_page.text, "lxml")
        for elem in soup.findAll(['script','style','head','title']):
            elem.extract()
        texts = soup.getText(separator=' ').lower()

        string = re.sub(r'\,', ' ', texts) # remove ","
        # print(string.encode('utf-8'))
        string = re.sub('/', ' ', string) # remove "/"
        # print(string.encode('utf-8'))
        string = re.sub(r'\(', ' ', string) # remove "("
        # print(string.encode('utf-8'))
        string = re.sub(r'\)', ' ', string) # remove ")"
        # print(string.encode('utf-8'))
        string = re.sub(r'[\n\r\t]', ' ', string) # remove "\n", "\r", "\t"
        # print(string.encode('utf-8'))
        string = re.sub(' +',' ',string) #remove more than one space
        string = re.sub(r'r\s&\sd', ' ', string)
        string = re.sub(r'r&d', ' ', string)
        print(string.encode('utf-8'))

        # http://stackoverflow.com/questions/30242709/matching-terms-that-contain-special-characters-with-re-findall
        required_skills = []
        required_edu = []
        required_major = []
        required_type= []

        for typ in type_lower :
            if any(x in typ for x in ['+', '#', '.']):
                typp = re.escape(typ)
            else:
                typp = typ
            result = re.search(r'(?:^|(?<=\s))' + typp + r'(?=\s|$)', string)
            if result:
                required_type.append(typ)

        for sk in skills_lower :
            if any(x in sk for x in ['+', '#', '.']):
                skk = re.escape(sk)
            else:
                skk = sk
            result = re.search(r'(?:^|(?<=\s))' + skk + r'(?=\s|$)',string)
            if result:
                required_skills.append(sk)
        print(required_skills)

        for ed in edu_lower :
            if any(x in ed for x in ['+', '#', '.']):
                edd = re.escape(ed)
            else:
                edd = ed
            result = re.search(r'(?:^|(?<=\s))' + edd + r'(?=\s|$)', string)
            if result:
                required_edu.append(ed)

        for maj in major_lower :
            if any(x in maj for x in ['+', '#', '.']):
                majj = re.escape(maj)
            else:
                majj = maj
            result = re.search(r'(?:^|(?<=\s))' + majj + r'(?=\s|$)', string)
            if result:
                required_major.append(maj)

        string = re.sub('\.\s+', ' ', string)
        words = str.split(string)
        words = set(words) - set(stop_words)  # remove stop words

        # Tells the scraper to wait for the assigned seconds between each loop
        time.sleep(1 + numpy.random.rand(1))

        job_type.append(required_type)
        job_skills.append(required_skills)
        job_edu.append(required_edu)
        job_major.append(required_major)
        job_words.append(list(words))


    data['job_type'] = job_type
    data['job_skills'] = job_skills
    data['job_edu'] = job_edu
    data['job_major'] = job_major
    data['job_words'] = job_words

    cols=['from','job_id','job_title','job_company','job_location','job_link','job_type',
            'job_skills', 'job_edu', 'job_major', 'job_words']
    data=data[cols]
    return(data)

now = datetime.datetime.now()
now_str = now.strftime("%m%d%Y")
dir_str = '/Users/chou/Google Drive/websites/github/web_scraping/data/'

df_detail = scrape_job(job_df_careerbuilder)
df_detail.to_csv(dir_str + now_str + 'job_df_careerbuilder.csv')
