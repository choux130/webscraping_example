############################
##### Import Libraries #####
############################
import bs4
import numpy
import pandas
import re
import requests
import stop_words

############################################################################
##### Define the terms that I am interested and would like to pick out #####
############################################################################
# define the stop_words for future use
stop_words = stop_words.get_stop_words('english') # list out all the English stop word
# print(stop_words)

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
def scrape_job(link):
    # empty list to store details for each job
    required_type= []
    required_skills = []
    required_edu = []
    required_major = []
    required_keywords = []
    required_text = []

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'}
        job_page = requests.get(link, headers=headers)
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
        # Skills
        for sk in skills_lower :
            if any(x in sk for x in ['+', '#', '.']):
                skk = re.escape(sk)
            else:
                skk = sk
            result = re.search(r'(?:^|(?<=\s))' + skk + r'(?=\s|$)',string)
            if result:
                required_skills.append(skills_dic[sk])

        # Education
        for ed in edu_lower :
            if any(x in ed for x in ['+', '#', '.']):
                edd = re.escape(ed)
            else:
                edd = ed
            result = re.search(r'(?:^|(?<=\s))' + edd + r'(?=\s|$)', string)
            if result:
                required_edu.append(edu_dic[ed])

        # Major
        for maj in major_lower :
            if any(x in maj for x in ['+', '#', '.']):
                majj = re.escape(maj)
            else:
                majj = maj
            result = re.search(r'(?:^|(?<=\s))' + majj + r'(?=\s|$)', string)
            if result:
                required_major.append(major_dic[maj])

        # Key Words
        for key in keywords_lower :
            if any(x in key for x in ['+', '#', '.']):
                keyy = re.escape(key)
            else:
                keyy = key
            result = re.search(r'(?:^|(?<=\s))' + keyy + r'(?=\s|$)', string)
            if result:
                required_keywords.append(keywords_dic[key])

        # All text
        words = string.split(' ')
        job_text = set(words) - set(stop_words) # drop stop words
        required_text.append(list(job_text))

    except:
        required_type= 'Forbidden'
        required_skills = 'Forbidden'
        required_edu = 'Forbidden'
        required_major = 'Forbidden'
        required_keywords = 'Forbidden'
        required_text = 'Forbidden'

    all_job ={'type':required_type, 'skills':required_skills, 'edu':required_edu,
                'major':required_major, 'keywords':required_keywords, 'text':required_text}
    return(all_job)
