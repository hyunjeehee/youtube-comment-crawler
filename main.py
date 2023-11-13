import pandas
from googleapiclient.discovery import build
import pytz
from datetime import datetime

api_key = 'AIzaSyCJDn1Id_1SF1E4iHK2XNmHWocp0Ptin1c'
 
api_obj = build('youtube', 'v3', developerKey=api_key)

def convert_utc_to_kst(utc_timestamp):
    utc_time = datetime.strptime(utc_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_time = utc_time.replace(tzinfo=pytz.UTC)
    kst_time = utc_time.astimezone(pytz.timezone('Asia/Seoul'))
    return kst_time.strftime("%Y-%m-%d %H:%M:%S")

def get_keyword(keyword):
    search_response = api_obj.search().list(
            q=keyword,
            type='video',
            order='date',
            part='snippet',
            maxResults=3
        ).execute()

    video_ids = []

    for item in search_response['items']:
        video_ids.append(item['id']['videoId'])

    return video_ids 


def get_comment(video_id):
    
    try:
        response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults = 100).execute()
    except:
        return

    comments = list() 


    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_text = comment['textDisplay']
            comment_date = comment['publishedAt']
            comments.append({'publishedAt': comment_date, 'comment': comment_text})

            if item['snippet']['totalReplyCount'] > 0:
                for reply_item in item['replies']['comments']:
                    reply = reply_item['snippet']
                    reply_date = reply['publishedAt']
                    reply_text = reply['textDisplay']
                    comments.append({'publishedAt': reply_date, 'comment': reply_text})
            
        if 'nextPageToken' in response:
            print (f"{video_id} -> {response['nextPageToken']}")
            pageToken = response['nextPageToken']
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, pageToken = pageToken, maxResults = 100).execute()
        else:
            break

    return comments

video_ids = get_keyword("김길수")             #테스트용 키워드 

comment_list=[]
total_comments = 0
for video_id in video_ids:
    print(video_id)
    comments = get_comment(video_id)
    if comments:
        # print(comments)
        total_comments += len(comments)
        comment_list.extend(comments)

print(f"Total comments collected: {total_comments}")  


df = pandas.DataFrame(comment_list)
df.to_excel('results.xlsx', columns=['publishedAt', 'comment'], index=None)

