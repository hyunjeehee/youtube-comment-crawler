import pandas
from googleapiclient.discovery import build

api_key = 'AIzaSyCJDn1Id_1SF1E4iHK2XNmHWocp0Ptin1c'
 
api_obj = build('youtube', 'v3', developerKey=api_key)


def get_keyword(keyword):
    search_response = api_obj.search().list(
            q=keyword,
            order='viewCount',
            part='snippet',
            maxResults=20
        ).execute()

    video_ids = []


    for item in search_response['items']:
        video_ids.append(item['id']['videoId'])

    return video_ids 


def get_comment(video_id):
    try:
        response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id).execute()
    except:
        return

    comments = list() 

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append([comment['textDisplay']])

            if item['snippet']['totalReplyCount'] > 0:
                for reply_item in item['replies']['comments']:
                    reply = reply_item['snippet']
                    comments.append([reply['textDisplay']])

        if 'nextPageToken' in response:
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, pageToken=response['nextPageToken']).execute()
        else:
            break

    return comments



video_ids = get_keyword("다꾸")             #테스트용 키워드 "다꾸"

comment_list=[]
for video_id in video_ids:
    comments = get_comment(video_id)
    if comments:
        comment_list.extend(comments)


df = pandas.DataFrame(comment_list)
df.to_excel('results.xlsx', header=['comment'], index=None)

