import os

from app import celery, UPLOAD_FOLDER
from models import ChatVideos, StreamModel
from moviepy.editor import VideoFileClip, clips_array, concatenate
from utils import random_name
from datetime import datetime


@celery.task()
def merge_streams(peer1ID, peer2ID):
    chatVideo = ChatVideos()
    chatVideo.peer1 = peer1ID
    chatVideo.peer2 = peer2ID
    peer1Videos = StreamModel.select().order_by(StreamModel.streamID)\
        .where((StreamModel.peer1ID == peer1ID) & (StreamModel.peer2ID == peer2ID))
    peer2Videos = StreamModel.select().where((StreamModel.peer1ID == peer2ID) & (StreamModel.peer2ID == peer1ID)) \
        .order_by(StreamModel.streamID)
    finalClipName =  random_name() + '.mp4'
    finalClip = None
    for n1, n2 in zip(peer1Videos, peer2Videos):
        v1 = VideoFileClip(os.path.join(UPLOAD_FOLDER + '/streams', n1.streamName))
        v2 = VideoFileClip(os.path.join(UPLOAD_FOLDER + '/streams', n2.streamName))
        finalClip = concatenate([clips_array([[v1, v2]])])
    finalClip.write_videofile(os.path.join(UPLOAD_FOLDER + '/chats',finalClipName))
    chatVideo = ChatVideos()
    chatVideo.peer1 = peer1ID
    chatVideo.peer2 = peer2ID
    print(finalClipName)
    chatVideo.fileAddress = finalClipName
    chatVideo.chatDate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    chatVideo.save()
    for v in peer1Videos :
        os.remove(os.path.join(UPLOAD_FOLDER + '/streams', v.streamName))
        v.delete_instance()
    print("finished")
    pass
