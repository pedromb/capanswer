from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
socketio = SocketIO(app)
numOfPlayers = 2
players = []
playerid = 0
answerLock = 0
newQuestion = -numOfPlayers
maxPoints = 2
pergunta1 = {
    "questao": "Sobre a alimentação das capivaras,\n elas são animais: ",
    "op1": "Herbívoros",
    "op2": "Carnívoros",
    "op3": "Onívoros",
    "op4": "Nenhuma das anteriores",
    "op5": "Não sei",
    "opCerta": "op1",
}

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
    global playerid
    playerid = playerid+1
    emit('newplayeradded', {"playerid":playerid})

@socketio.on('playerWantsToEnterRoom', namespace='/game')
def player_enters_room(data):
    global players
    global numOfPlayers
    global currentQuestion
    newPlayer = {
        "nick":data['nick'],
        "score": 0,
        "playerid": data['playerid']
    }
    players.append(newPlayer)
    join_room("mainroom")
    count = len(players)
    startGame = False
    if(count == numOfPlayers):
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
    for player in players:
        if player['playerid'] == answerLock:
            player['score'] = player['score']+1
            if(player['score'] == maxPoints):
                winnderid = answerLock
                players = []
                playerid = 0
                answerLock = 0
                newQuestion = -numOfPlayers
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


if __name__ == '__main__':
    socketio.run(app)