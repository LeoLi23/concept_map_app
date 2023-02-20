from django.db import connection


def getAllNodes():
    cursor = connection.cursor()
    cursor.execute("select id,name,description,x_position,y_position from concept_node;")
    concepts = cursor.fetchall()
    cursor.close()
    connection.close()
    concepts = [list(concept) for concept in concepts]
    return concepts


def getAllConnections():
    cursor = connection.cursor()
    cursor.execute("select id,source_node_id,target_node_id from connection;")
    connections = cursor.fetchall()
    cursor.close()
    connection.close()
    connections = [list(c) for c in connections]
    return connections
