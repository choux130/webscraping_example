################################
##### Assign the directory #####
################################
import os

path = '/Users/chou/Google Drive/Websites/github/webscraping_example'
os.chdir(path) # change the directory to the assigned path
print(os.getcwd())

#######################################################
##### Import the customized package and libraries #####
#######################################################
import pandas
import numpy
import datetime
import multiprocessing as mp
import scrape_pack.one_url
import scrape_pack.multi_url

#############################
##### Setting Arguments #####
#############################
input_job = "Data Scientist"
input_quote = False # add quotation marks("") to your input_job
input_city = "Durham" # leave empty if input_city is not specified
input_state = "NC"

sign_indeed = "+"
sign_monster = "-"
sign_dice = "+"
sign_careerbuilder = "-"

BASE_URL_indeed = 'http://www.indeed.com'
BASE_URL_monster = 'https://www.monster.com'
BASE_URL_dice = 'https://www.dice.com'
BASE_URL_careerbuilder = 'http://www.careerbuilder.com'

now = datetime.datetime.now()
now_str_name = now.strftime("%m%d%Y")

###############################
##### Scrape from one url #####
###############################
job_df_indeed = scrape_pack.one_url.basic_indeed(BASE_URL_indeed, input_job, input_city, input_state, input_quote, sign_indeed)
job_df_monster = scrape_pack.one_url.basic_monster(BASE_URL_monster, input_job, input_city, input_state, input_quote, sign_monster)
job_df_dice = scrape_pack.one_url.basic_dice(BASE_URL_dice, input_job, input_city, input_state, input_quote, sign_dice)
job_df_careerbuilder = scrape_pack.one_url.basic_careerbuilder(BASE_URL_careerbuilder, input_job, input_city, input_state, input_quote, sign_careerbuilder)

# print(job_df_indeed.shape)
# print(job_df_monster.shape)
# print(job_df_dice.shape)
# print(job_df_careerbuilder.shape)

# combine the four dataframes
job_df_all = [job_df_indeed, job_df_monster, job_df_dice, job_df_careerbuilder]
df = pandas.concat(job_df_all)
df.columns = ['from','date','job_id','job_title','job_company','job_location','job_link']
df.drop_duplicates(['job_title', 'job_company'], keep='first') # delete duplicates
print(df.shape)

######################################
##### Scrape from a list of URLs #####
######################################
lks = df['job_link']
ll = [link for link in lks]
# print(len(ll))

# parallel computing to increse the speed
if __name__ == '__main__':
    pool = mp.Pool(processes = 8)
    results = pool.map(scrape_pack.multi_url.scrape_job, ll)
    pool.close()
    pool.join()

job_type = [d['type'] for d in results]
job_skills = [d['skills'] for d in results]
job_edu = [d['edu'] for d in results]
job_major = [d['major'] for d in results]
job_keywords = [d['keywords'] for d in results]

df['job_type'] = job_type
df['job_skills'] = job_skills
df['job_edu'] = job_edu
df['job_major'] = job_major
df['job_keywords'] = job_keywords

# save the dataframe
df.to_csv(path + '/output/'+ 'job_all_' + now_str_name + '.csv')
