import os

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

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
    for v in peer1Videos + peer2Videos:
        os.remove(os.path.join(UPLOAD_FOLDER + '/streams', v.streamName))
        v.delete_instance()
    print("finished")
    pass



@celery.task()
def merge_audio_streams(peer1ID, peer2ID):
    chatVideo = ChatVideos()
    chatVideo.peer1 = peer1ID
    chatVideo.peer2 = peer2ID
    peer1Audios = StreamModel.select().order_by(StreamModel.streamID)\
        .where((StreamModel.peer1ID == peer1ID) & (StreamModel.peer2ID == peer2ID))
    peer2Audios = StreamModel.select().where((StreamModel.peer1ID == peer2ID) & (StreamModel.peer2ID == peer1ID)) \
        .order_by(StreamModel.streamID)
    finalAudioName =  random_name() + '.mp4'
    finalAudio = None
    for n1, n2 in zip(peer1Audios, peer2Audios):
        v1 = AudioFileClip(os.path.join(UPLOAD_FOLDER + '/streams', n1.streamName))
        v2 = AudioFileClip(os.path.join(UPLOAD_FOLDER + '/streams', n2.streamName))
        finalAudio = CompositeAudioClip([clips_array([[v1, v2]])])
    finalAudio.write_audiofile(os.path.join(UPLOAD_FOLDER + '/chats',finalAudioName),fps = 44100)
    chatVideo = ChatVideos()
    chatVideo.peer1 = peer1ID
    chatVideo.peer2 = peer2ID
    chatVideo.fileAddress = finalAudioName
    chatVideo.chatDate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    chatVideo.save()
    for v in peer1Audios + peer2Audios :
        os.remove(os.path.join(UPLOAD_FOLDER + '/streams', v.streamName))
        v.delete_instance()
    print("finished")
