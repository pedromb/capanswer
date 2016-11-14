from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import calendar
import random
import atexit
import threading


app = Flask(__name__)
socketio = SocketIO(app)
numOfPlayers = 5
players = []
players_ids = [0]
answerLock = 0
newQuestion = -numOfPlayers
maxPoints = 5
HEARTBEAT_TIME = 4
CHECK_HEARTBEAT_TIME = 7
heartbeatThread = threading.Thread()
checkHeartbeatThread = threading.Thread()
gameHappening = False

pergunta1 = {
    "questao": "Sobre a alimentação das capivaras,\n elas são animais: ",
    "op1": "Herbívoros",
    "op2": "Carnívoros",
    "op3": "Onívoros",
    "op4": "Nenhuma das anteriores",
    "op5": "Não sei",
    "opCerta": "op1",}
pergunta2 = {
    "questao": "O tempo médio de gestação de \n uma capivara é de: ",
    "op1": "90 dias",
    "op2": "100 dias",
    "op3": "120 dias",
    "op4": "150 dias",
    "op5": "180 dias",
    "opCerta": "op3",
  }

pergunta3 = {
    "questao": "São animais cuja LARGURA \n média é de: ",
    "op1": "100cm a 130cm",
    "op2": "70cm a 100cm",
    "op3": "130cm a 170cm",
    "op4": "50 a 70cm",
    "op5": "Nenhuma das anteriores",
    "opCerta": "op1",
  }

pergunta4 = {
    "questao": "São animais cuja ALTURA \n média é de: ",
    "op1": "70cm",
    "op2": "50cm",
    "op3": "60cm",
    "op4": "75cm",
    "op5": "55cm",
    "opCerta": "op2",
  }

pergunta5 = {
    "questao": "Um nome comum para as capivaras \n é 'Kapivya'. O significado é: ",
    "op1": "Gigante das Gramas",
    "op2": "Roedor das Gramas",
    "op3": "Grande Roedor",
    "op4": "Dócil Roedor",
    "op5": "Mestre das Gramas",
    "opCerta": "op5",
  }

pergunta6 = {
    "questao": "As capivaras são tipicamente \n encontrados na região: ",
    "op1": "Dos Pampas",
    "op2": "Do Cerrado",
    "op3": "Da Mata Atlântica",
    "op4": "Da Floresta Amazônica",
    "op5": "Nenhuma das anteriores",
    "opCerta": "op4",
  }

pergunta7 = {
    "questao": "Após 18 semanas, o peso médio \n de um filhote pode alcançar: ",
    "op1": "70Kg",
    "op2": "80Kg",
    "op3": "50Kg",
    "op4": "60Kg",
    "op5": "Nenhuma das anteriores",
    "opCerta": "op5",
  }

questions = [pergunta1,pergunta2,pergunta3,pergunta4,pergunta5,pergunta6,pergunta7]
currentQuestion = pergunta1

@socketio.on('newplayer', namespace='/game')
def new_player():

    player_id = get_player_id()
    username = "Capivara "+str(player_id)
    emit('newplayeradded', {"playerid":player_id, "username":username, "gameHappening": gameHappening})

@socketio.on('playerWantsToEnterRoom', namespace='/game')
def player_enters_room(data):
    global players
    global numOfPlayers
    global currentQuestion
    newPlayer = {
        "nick":data['nick'],
        "score": 0,
        "playerid": data['playerid'],
        "heartbeat": calendar.timegm(datetime.utcnow().utctimetuple())
    }
    players.append(newPlayer)
    join_room("mainroom")
    count = len(players)
    if(count == numOfPlayers):
        gameHappening = True
        currentQuestion = random.choice(questions) 
        emit('startgame', currentQuestion, room="mainroom")
    else:
        emit('playeraddedtoroom', {"count":count}, room="mainroom")

@socketio.on('tryGetLock', namespace='/game')
def getLock(data):
    global answerLock
    global players
    if answerLock == 0:
        answerLock = data['playerid']
        for player in players:
            if player['playerid'] == answerLock:
                playerAnswering = player
                emit('answerquestion', playerAnswering, room="mainroom")

@socketio.on('timeoutanswer', namespace='/game')
def timeoutanswer():
    global answerLock
    global players
    for player in players:
        if player['playerid'] == answerLock:
            player['score'] = player['score']-1
    answerLock = 0
    emit('playertimeout', players, room="mainroom")

@socketio.on('errou', namespace='/game')
def errou():
    global answerLock
    global players
    for player in players:
        if player['playerid'] == answerLock:
            player['score'] = player['score']-1
    answerLock = 0
    emit('playererrou', players, room="mainroom")

@socketio.on('acertou', namespace='/game')
def timeoutanswer():
    global answerLock
    global players
    global maxPoints
    global players_ids
    global newquestion
    global gameHappening
    for player in players:
        if player['playerid'] == answerLock:
            player['score'] = player['score']+1
            if(player['score'] == maxPoints):
                winnderid = answerLock
                players = []
                players_ids = [0]
                answerLock = 0
                newQuestion = -numOfPlayers
                gameHappening = False
                emit('finishgame', winnderid, room="mainroom")
            else:
                answerLock = 0
                emit('playeracertou', players, room="mainroom")

@socketio.on('newquestion', namespace='/game')
def waitingforplayers():
    global answerLock
    global players
    global newQuestion
    global numOfPlayers
    newQuestion = newQuestion+1
    if(newQuestion == 0):
        newQuestion = -numOfPlayers
        currentQuestion = random.choice(questions)
        emit('startgame', currentQuestion, room="mainroom")

@socketio.on('leaveroom', namespace='/game')
def leaveroom():
    leave_room("mainroom")
@socketio.on('heartbeat', namespace='/game')
def heartbeat(data):
    global players

    playerid = data['playerid']
    heartbeat = data['heartbeat_time']
    for player in players:
        if player['playerid'] == playerid:
            player['heartbeat'] = heartbeat


def interupt():
    global heartbeatThread
    global checkHeartbeatThread
    checkHeartbeatThread.cancel()
    heartbeatThread.cancel()

def sendHeartbeat():
    global heartbeatThread
    global HEARTBEAT_TIME

    heartbeat = calendar.timegm(datetime.utcnow().utctimetuple())
    socketio.emit('heartbeat', {'time':heartbeat}, namespace='/game')
    
    heartbeatThread = threading.Timer(HEARTBEAT_TIME, sendHeartbeat, ())
    heartbeatThread.start()

def checkHearbeat():
    global checkHeartbeatThread
    global CHECK_HEARTBEAT_TIME
    global players
    global players_ids
    global gameHappening

    timestamp_now = calendar.timegm(datetime.utcnow().utctimetuple())
    new_list = []
    if len(players) > 0:
        for player in players:
            if timestamp_now > int(player['heartbeat'])+CHECK_HEARTBEAT_TIME:
                print('Jogador de id {0} e username {1} falhou. Removendo da sala...'.format(player['playerid'], player['nick']))
                remove_player_id(player['playerid'])
                if(len(players_ids) == 1):
                    gameHappening = False
            else:
                new_list.append(player)
        players = new_list
    checkHeartbeatThread = threading.Timer(CHECK_HEARTBEAT_TIME, checkHearbeat, ())
    checkHeartbeatThread.start()

def get_player_id():

    global players_ids
    player_id = [x for x in range(0, max(players_ids)+2) if x not in players_ids][0]
    players_ids.append(player_id)
    return player_id

def remove_player_id(playerid):
    global players_ids

    new_player_ids = [x for x in players_ids if x != int(playerid)]
    players_ids = new_player_ids
    count = len(players_ids)-1
    print(count)
    socketio.emit('playeraddedtoroom', {"count":count}, room="mainroom", namespace='/game')











if __name__ == '__main__':  
    sendHeartbeat()
    checkHearbeat()
    atexit.register(interupt)
    socketio.run(app)