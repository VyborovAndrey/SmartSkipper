import math
import random
#import turtle

from createGPX import create_gpx

def waygen(startPoint: list[int], endPoint: list[int], is_forward: bool):
    if is_forward:
        step = 5000
        angle = random.randint(0, 1) * 90 + 45
        way = []
        way.append(startPoint.copy())
        blockTurn = False
        boatspeed = random.randint(7, 14) / 10
        while startPoint[0] < endPoint[0]:
            if -1/step < (abs(endPoint[0] - startPoint[0]) - abs(endPoint[1] - startPoint[1])) < 1/step:
                if endPoint[1] > startPoint[1]:
                    angle = 45
                else:
                    angle = 135
                blockTurn = True
            if not blockTurn:
                if random.randint(0, 150) > 149:
                    if angle > 90:
                        angle -= 90 #+ random.randint(-5, 5)
                    else:
                        angle += 90 #+ random.randint(-5, 5)

            startPoint[1] += math.cos(math.radians(angle))/step*boatspeed
            startPoint[0] += math.sin(math.radians(angle))/step*boatspeed
            #turtle.goto(startPoint[1] * 50, startPoint[0] * 50)
            way.append(startPoint.copy())

        return way
    step = 5000
    angle = random.randint(0, 1) * -90 - 45
    way = []
    way.append(startPoint.copy())
    blockTurn = False
    boatspeed = random.randint(6, 13) / 10
    if random.randint(0, 1):
        going_forde = True
    else:
        going_forde = False
    while startPoint[0] > endPoint[0]:
        if going_forde:
            startPoint[0] -= 1/step*boatspeed
            #turtle.goto(startPoint[1] * 50, startPoint[0] * 50)
            way.append(startPoint.copy())
        else:
            if -1/step < (abs(endPoint[0] - startPoint[0]) - abs(endPoint[1] - startPoint[1])) < 1/step:
                if endPoint[1] > startPoint[1]:
                    angle = -45
                else:
                    angle = -135
                blockTurn = True
            if not blockTurn:

                if random.randint(0, 150) > 149:
                    if angle < -90:
                        angle += 90 #+ random.randint(-5, 5)
                    else:
                        angle -= 90 #+ random.randint(-5, 5)

            startPoint[1] += math.cos(math.radians(angle))/step*boatspeed
            startPoint[0] += math.sin(math.radians(angle))/step*boatspeed
            #turtle.goto(startPoint[1] * 50, startPoint[0] * 50)
            way.append(startPoint.copy())
    return way


def racegen(startPoint: list[int], boatCount: int):
    ways = [[]] * boatCount
    distbetweenboats = 0.0001
    startx = startPoint[1]
    dist = 0.1
    if boatCount != 1:
        startx = startPoint[1] - boatCount * distbetweenboats / 2

    for i in range(boatCount):
        way = []
        for j in (waygen([startPoint[0], startx], [startPoint[0] + dist, startPoint[1]], True)):
            way.append(j)
        for j in (waygen([startPoint[0] + dist, startPoint[1]], startPoint, False)):
            way.append(j)
        ways[i] = way.copy()
        startx += distbetweenboats
    return ways


race = racegen([59.870800772291446, 30.05910063608237], 5)
for i in range(len(race)):
    for j in range(len(race[i])):
        race[i][j].append(j)
    create_gpx(race[i], f"boat{i+1}")

