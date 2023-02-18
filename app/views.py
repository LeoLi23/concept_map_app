from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection
from django.urls import reverse
import datetime
import random


def index(request):
    cursor = connection.cursor()
    cursor.execute("select id,name,description,x_position,y_position from concept_node;")
    concepts = cursor.fetchall()
    cursor.close()
    connection.close()
    concepts = [list(concept) for concept in concepts]
    return render(request, './index.html', {
        'nodes': concepts
    })


def createConcept(request):
    if request.method == 'POST':
        conceptName = request.POST.get('conceptName')
        description = request.POST.get('conceptDescription')
        created_at = updated_at = datetime.datetime.now()
        # define range of x and y positions
        x_range, y_range = (0, 4000), (0, 1000)
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
        print("idd is: ", idd)
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
