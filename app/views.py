from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .utils import *
import datetime
import random
import azure.cognitiveservices.speech as speechsdk
import time
from django.utils import timezone

speech_recognizer = None


def index(request):
    return render(request, './index.html', {
        'nodes': getAllNodes(),
        'connections': getAllConnections(),
    })


def get_latest_nodes(request, latestCheckTime):
    last_check_time = datetime.datetime.strptime(latestCheckTime, '%Y-%m-%dT%H:%M:%S.%fZ')
    cursor = connection.cursor()
    cursor.execute("select * from concept_node where created_at > %s;", last_check_time)
    rows = cursor.fetchall()
    if rows:
        return JsonResponse({'newNodes': True})
    else:
        return JsonResponse({'newNodes': False})


def createConcept(request):
    if request.method == 'POST':
        conceptName = request.POST.get('conceptName')
        description = request.POST.get('conceptDescription')
        created_at = updated_at = datetime.datetime.now()
        # define range of x and y positions
        x_range, y_range = (50, 1800), (0, 1000)
        # random initial x and y positions
        x_position, y_position = random.randint(x_range[0], x_range[1]), random.randint(y_range[0], y_range[1])
        cursor = connection.cursor()
        args = (conceptName, description, created_at, updated_at, x_position, y_position)
        cursor.execute("Insert into concept_node (name,description,created_at,updated_at,x_position,y_position) values \
                        (%s, %s, %s, %s, %s, %s);", args)
        cursor.close()
        connection.close()
        return HttpResponseRedirect(reverse('app:index'))
    return render(request, './conceptForm.html')


def updateConcept(request):
    if request.method == 'POST':
        idd = request.POST.get('nodeId')
        conceptName = request.POST.get('nodeText')
        updated_at = datetime.datetime.now()
        x_position = request.POST.get('new_x_position')
        y_position = request.POST.get('new_y_position')
        print(idd, conceptName, updated_at, x_position, y_position)
        cursor = connection.cursor()
        if not conceptName:
            cursor.execute("SELECT name from concept_node where id = %s", idd)
            conceptName = cursor.fetchall()[0][0]
        if not x_position:
            cursor.execute("SELECT x_position from concept_node where id = %s", idd)
            x_position = cursor.fetchall()[0][0]
        if not y_position:
            cursor.execute("SELECT y_position from concept_node where id = %s", idd)
            y_position = cursor.fetchall()[0][0]

        cursor.execute("UPDATE concept_node SET name = %s,updated_at = %s,x_position = %s,y_position = %s \
                        WHERE id = %s;", (conceptName, updated_at, x_position, y_position, idd))
        cursor.close()
        connection.close()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


def removeConcept(request):
    if request.method == 'POST':
        idd = request.POST.get('nodeId')
        cursor = connection.cursor()
        cursor.execute("DELETE FROM concept_node WHERE id = %s;", idd)
        cursor.close()
        connection.close()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


def createConnection(request):
    if request.method == 'GET':
        cursor = connection.cursor()
        cursor.execute("select source_node_id,cn.name as 'source_name' \
                       from connection c join concept_node cn on c.source_node_id = cn.id;")
        source_node_data = cursor.fetchall()
        cursor.execute("select target_node_id,cn.name as 'target_name' \
                        from connection c join concept_node cn on c.target_node_id = cn.id;")
        target_node_data = cursor.fetchall()
        cursor.execute("select source_node_id, target_node_id from connection;")
        data = cursor.fetchall()
        # represent connection as hashmaps
        connections = {}  # {source1:[target1,target2,target3,...], source2:[]}
        for source, target in data:
            if source not in connections:
                connections[source] = []
            connections[source].append(target)
        # process source_node
        source_node_data = {source_id: sourceName for source_id, sourceName in source_node_data}
        # process target_node
        target_node_data = {target_id: targetName for target_id, targetName in target_node_data}
        cursor.close()
        connection.close()
        print(source_node_data)
        print(target_node_data)
        print(connections)
        return render(request, "./connectionForm.html", {
            'nodes': getAllNodes(),
            'source_node_data': source_node_data,
            'target_node_data': target_node_data,
            'connections': getAllConnections(),
            'relations': connections  # {6:[7,8,9],4:[1,2]}
        })
    else:
        source_id = request.POST.get('source_node')
        target_id = request.POST.get('target_node')
        print("source_id = {}, target_id = {}".format(source_id, target_id))
        created_at = updated_at = datetime.datetime.now()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO connection(source_node_id, target_node_id, created_at, updated_at) \
                       VALUES(%s,%s,%s,%s);', (source_id, target_id, created_at, updated_at))
        cursor.close()
        connection.close()
        return HttpResponseRedirect(reverse('app:index'))


def removeConnection(request):
    if request.method == 'POST':
        source_node_remove = request.POST.get('source_node_remove')
        target_node_remove = request.POST.get('target_node_remove')
        cursor = connection.cursor()
        cursor.execute("delete from connection where source_node_id = %s and target_node_id = %s;",
                       (source_node_remove, target_node_remove))
        cursor.close()
        connection.close()
        return HttpResponseRedirect(reverse('app:index'))


def startRecording(request):
    global speech_recognizer
    if request.method == 'POST':
        env_dict = parseConfig()
        print(env_dict)
        speech_config = speechsdk.SpeechConfig(subscription=env_dict['SPEECH_KEY'],
                                               region=env_dict['SPEECH_REGION'])
        speech_config.speech_recognition_language = "en-US"

        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        def speech_recognized(evt):
            result = evt.result
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                # last_recognized_time = datetime.datetime.now()
                print("Recognized: {}".format(result.text))
                keywords = extract_keywords(result.text)
                print(keywords)
                sql = "Insert into concept_node (name,description,created_at,updated_at,x_position,y_position) values \
                    (%s, %s, %s, %s, %s, %s);"
                x_range, y_range = (50, 1800), (0, 1000)
                # random initial x and y positions
                x_position, y_position = random.randint(x_range[0], x_range[1]), random.randint(y_range[0],
                                                                                                y_range[1])
                data = [(word,
                         word,
                         datetime.datetime.now(),
                         datetime.datetime.now(),
                         x_position,
                         y_position
                         ) for word in keywords]
                # save to db
                cursor = connection.cursor()
                cursor.executemany(sql, data)
                connection.commit()
                cursor.close()
                connection.close()
                print("added to the database")
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized")
            elif result.reason == speechsdk.ResultReason.Canceled:
                print("Speech recognition canceled: {}".format(result.cancellation_details.reason))

        speech_recognizer.recognized.connect(speech_recognized)
        speech_recognizer.start_continuous_recognition()

        # return a JSON response indicating that the recording has started
        response = {
            'message': 'Recording started'
        }
        return JsonResponse(response)
    else:
        return HttpResponse('Invalid request method')


def stopRecording(request):
    global speech_recognizer

    if request.method == 'POST':
        if speech_recognizer:
            time.sleep(2)  # wait for 2 seconds
            speech_recognizer.stop_continuous_recognition()
            response = {
                'message': 'Recording stopped'
            }
        else:
            response = {
                'message': 'No recording in progress'
            }
        return JsonResponse(response)
    else:
        return HttpResponse('Invalid request method')
