import os

from app import celery, UPLOAD_FOLDER
from models import ChatVideos, StreamModel
from moviepy.editor import  VideoFileClip, clips_array, concatenate
from utils import random_name
from datetime import datetime
@celery.task()
def merge_streams(peer1ID, peer2ID):
    chatVideo = ChatVideos()
    chatVideo.peer1 = peer1ID
    chatVideo.peer2 = peer2ID
    peer1Videos = StreamModel.select().where((StreamModel.peer1ID == peer1ID) & (StreamModel.peer2ID == peer2ID))\
    .order_by(StreamModel.streamID)
    peer2Videos = StreamModel.select().where((StreamModel.peer1ID == peer2ID) & (StreamModel.peer2ID == peer1ID))\
        .order_by(StreamModel.streamID)
    finalClipName = os.path.join(UPLOAD_FOLDER + '/chats',random_name() + '.mp4')
    videos = StreamModel.select()
    print(StreamModel.get(peer1ID == peer1ID))
    print(StreamModel.get(peer2ID == peer1ID))
    for n in videos:
        print n
    return
    for n1,n2 in peer1Videos,peer2Videos :
        print ('v1 name is : {0}'.format(peer1Videos))
        v1 = VideoFileClip(os.path.join(UPLOAD_FOLDER + '/streams',n1.fileName))
        v2 = VideoFileClip(os.path.join(UPLOAD_FOLDER + '/streams',n2.fileName))
        finalClip = concatenate([clips_array([[v1,v2]])])
    finalClip.write_videofile(os.path.join(UPLOAD_FOLDER + '/chats',random_name()+'.mp4'))
    chatVideo = ChatVideos()
    chatVideo.peer1 = peer1ID
    chatVideo.peer2 = peer2ID
    chatVideo.chatDate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    chatVideo.save()
    for v in peer1Videos + peer2Videos:
        os.remove(os.path.join(UPLOAD_FOLDER+'/chats',v.fileName))
        v.delete_instance()
    print("finished")
    pass


