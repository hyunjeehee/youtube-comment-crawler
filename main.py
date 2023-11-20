import pandas as pd
from googleapiclient.discovery import build
import pytz
from datetime import datetime, timedelta

api_key = 'AIzaSyCJDn1Id_1SF1E4iHK2XNmHWocp0Ptin1c'
api_obj = build('youtube', 'v3', developerKey= api_key)

def convert_utc_to_kst(utc_timestamp):
    utc_time = datetime.strptime(utc_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo= pytz.UTC)
    kst_time = utc_time.astimezone(pytz.timezone('Asia/Seoul'))
    return kst_time.strftime("%Y-%m-%d %H:%M:%S")

def get_keyword(keyword):
    search_response = api_obj.search().list(
        q= keyword,
        type= 'video',
        order= 'date',
        part= 'snippet',
        maxResults= 10
    ).execute()

    video_ids = []

    for item in search_response['items']:
        video_ids.append(item['id']['videoId'])

    return video_ids 

def get_comment(video_id, within_hours= None):
    try:
        response = api_obj.commentThreads().list(part= 'snippet,replies', videoId= video_id, maxResults= 100).execute()
    except:
        return

    comments = list()
    current_time = datetime.now(pytz.timezone('Asia/Seoul')).replace(tzinfo= None)
    url = ("https://www.youtube.com/watch?v=" + video_id)


    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_date = comment['publishedAt']
            kst_date = convert_utc_to_kst(comment_date)
            comment_time = datetime.strptime(kst_date, "%Y-%m-%d %H:%M:%S")

            if within_hours is None:
                comment_text = comment['textDisplay']
                comments.append({'publishedAt': kst_date, 'comment': comment_text, 'url': url})
            else:
                time_gap = current_time - comment_time
                if time_gap <= timedelta(hours= within_hours):
                    comment_text = comment['textDisplay']
                    comments.append({'publishedAt': kst_date, 'comment': comment_text, 'url': url})
            
            if item['snippet']['totalReplyCount'] > 0:
                for reply_item in item['replies']['comments']:
                    reply = reply_item['snippet']
                    reply_date = reply['publishedAt']
                    kst_reply_date = convert_utc_to_kst(reply_date)
                    reply_time = datetime.strptime(kst_reply_date, "%Y-%m-%d %H:%M:%S")

                    if within_hours is None:
                        reply_text = reply['textDisplay']
                        comments.append({'publishedAt': kst_reply_date, 'comment': reply_text, 'url': url})
                    else:
                        reply_time_gap = current_time - reply_time
                        if reply_time_gap <= timedelta(hours= within_hours):
                            reply_text = reply['textDisplay']
                            comments.append({'publishedAt': kst_reply_date, 'comment': reply_text, 'url': url})

        if 'nextPageToken' in response:
            pageToken = response['nextPageToken']
            response = api_obj.commentThreads().list(part= 'snippet,replies', videoId= video_id, pageToken= pageToken, maxResults= 100).execute()
        else:
            break

    return comments

keyword = "김길수"      # 테스트용 키워드 
video_ids = get_keyword(keyword)  

comment_list = []
total_comments = 0
hours_within = 24        # 몇 시간 내로 작성된 댓글 추출할 건지 ( None 입력 시 전체 댓글 추출 )

print(f'"{keyword}"로 검색해서 {hours_within}시간 이내의 댓글만 가지고 옵니다.\n')
for video_id in video_ids:
    url = ("https://www.youtube.com/watch?v=" + video_id)
    comments = get_comment(video_id, hours_within)
    try:
        if comments:
            # print(comments)
            total_comments += len(comments)
            comment_list.extend(comments)
            print(f'{url} 댓글 {len(comments)}개')
        else:
            raise ValueError(url + " 댓글 0개")
    except ValueError as ve:
        print(f"{ve}")
        
try:
    if total_comments > 0:
        df = pd.DataFrame(comment_list, columns= ['publishedAt', 'comment','url'])
        df.to_excel('results.xlsx', columns=['publishedAt', 'comment','url'], index=None)
        print(f"\n{hours_within} 시간 이내 작성된 댓글 개수: {total_comments}")
except KeyError:
        print(f'지정된 시간 내에 작성된 댓글 없음')

