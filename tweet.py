import requests
import csv
import operator
from datetime import date, timedelta
import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

api_key = os.environ.get("API_key")
api_secret_key = os.environ.get("API_secret_key")
access_token = os.environ.get("access_token")
access_token_secret = os.environ.get("access_token_secret")

def extract_csv():
    r = requests.get(url)
    url_content = r.content

    return url_content

def create_csv(url_content):

    csv_file = open('covid_counties.csv', 'wb')

    csv_file.write(url_content)
    csv_file.close()

def extract_missouri_daily():

    county_results = []

    csv_file = open('covid_counties.csv','r')
    reader = csv.reader(csv_file,delimiter=',')
    for row in reader:
            if row[2] == 'Missouri':
                county_results.append(row)

    return county_results

def sort_by_cases_diff(county_results):

    yesterday_date = date.today() - timedelta(days=1)
    day_before_yesterday_date = date.today() - timedelta(days=2)

    county_cases_diff = []
    counties_day_before_yesterday = []
    counties_yesterday = []
    
    for row in county_results:
        if row[0] == str(day_before_yesterday_date):
            counties_day_before_yesterday.append(row)
        if row[0] == str(yesterday_date):
            counties_yesterday.append(row)

    for county_yesterday in counties_day_before_yesterday:
        county = []
        for county_today in counties_yesterday:
            if county_yesterday[1] == county_today[1]:
                diff = int(county_today[4])-int(county_yesterday[4])
                county.append(county_today[1])
                county.append(diff)
        county_cases_diff.append(county)
            

    return county_cases_diff

def sort_by_deaths_diff(county_results):

    yesterday_date = date.today() - timedelta(days=1)
    day_before_yesterday_date = date.today() - timedelta(days=2)

    county_deaths_diff = []
    counties_day_before_yesterday = []
    counties_yesterday = []

    for row in county_results:
        if row[0] == str(day_before_yesterday_date):
            counties_day_before_yesterday.append(row)
        if row[0] == str(yesterday_date):
            counties_yesterday.append(row)

    for county_yesterday in counties_day_before_yesterday:
        county = []
        for county_today in counties_yesterday:
            if county_yesterday[1] == county_today[1]:
                diff = int(county_today[5])-int(county_yesterday[5])
                county.append(county_today[1])
                county.append(diff)
        county_deaths_diff.append(county)

    return county_deaths_diff

def tweet_template_heading():
    yesterday_date = date.today() - timedelta(days=1)
    headingContent = 'COVID-19 in Missouri (updated as of %s)\n\n' % yesterday_date

    return headingContent

def tweet_template_cases(county_cases_diff):
    
    county_cases_sorted = sorted(county_cases_diff, 
        key=operator.itemgetter(1), reverse=True)

    casesContent = 'Top 3 counties with most new cases:\n\n'

    counter = 0
    for county in county_cases_sorted:
        county_name = county[0]
        county_cases = county[1]
        counter += 1
        if counter == 4:
            break
        if county[1] == 0:
            break
        casesContent += '{0} - {1}\n' .format(county_name, county_cases)
        

    return casesContent

def tweet_template_deaths(county_deaths_diff):

    county_deaths_sorted = sorted(county_deaths_diff, 
        key=operator.itemgetter(1), reverse=True)

    deathsContent = '\nTop 3 counties with most new deaths:\n\n'
    counter = 0
    for county in (county_deaths_sorted):
        county_name = county[0]
        county_deaths = county[1]
        counter += 1
        if counter == 4:
            break
        if county[1] == 0:
            break
        deathsContent += '{0} - {1}\n' .format(county_name, county_deaths)
    
    return deathsContent

def OAuth():
    try:
        auth = tweepy.OAuthHandler(api_key, api_secret_key)  
        auth.set_access_token(access_token, access_token_secret)
        return auth
    except Exception as e:
        print(e)
        return None

def tweet_out(tweet_content):
    oauth = OAuth()
    api = tweepy.API(oauth)
    api.update_status(tweet_content)
    
    
def main():
    print('Updating csv file...')
    url_content = extract_csv()
    create_csv(url_content)
    print("Checking yesterday's COVID-19 stats...")
    county_results = extract_missouri_daily()
    county_cases_diff = sort_by_cases_diff(county_results)
    county_deaths_diff = sort_by_deaths_diff(county_results)
    print('Tweeting out content...')
    wholeContent = tweet_template_heading() + tweet_template_cases(county_cases_diff) + \
        tweet_template_deaths(county_deaths_diff)
    
    print(wholeContent)
    tweet_out(wholeContent)
    print('Content tweeted...')
    

 
if __name__ =='__main__':
    main()
