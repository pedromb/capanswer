

var game = new Phaser.Game(window.innerWidth,
    window.innerHeight, Phaser.CANVAS, 'capanswer');

Phaser.Device.whenReady(function () {
    game.plugins.add(Fabrique.Plugins.InputField);
    game.scale.refresh();
});

var title;
var bg;
var button;
var connectedPlayers;
var playerAnswering;
var answerStatus = "";
var players;
var username;
var currentQuestion;
var socket = io.connect('http://localhost:5000/game');

var interval;



socket.on('finishgame', function (result) {
    console.log(result)
    if (result == window.localStorage.playerid) {
        game.state.start('winner');
    }
    else {
        game.state.start('looser');
    }
});

socket.on('answerquestion', function (data) {
    var playerid = window.localStorage.playerid;
    playerAnswering = data.nick;
    if (data.playerid == playerid) {
        game.state.start('answerQuestion');
    }
    else {
        game.state.start('waitForAnswer');
    }
});

socket.on('playeracertou', function (data) {
    var playerid = window.localStorage.playerid;
    answerStatus = "acertou e por isso ganhou 1 ponto";
    players = data;
    game.state.start('score');
});

socket.on('playererrou', function (data) {
    var playerid = window.localStorage.playerid;
    answerStatus = "errrrrooooou e por isso perdeu 1 ponto";
    players = data;
    game.state.start('score');
});

socket.on('playertimeout', function (data) {
    var playerid = window.localStorage.playerid;
    answerStatus = "não respondeu e por isso perdeu 1 ponto";
    players = data;
    game.state.start('score');
});

socket.on('newplayeradded', function (data) {
    window.localStorage.playerid = data.playerid;
        username = data.username;
});

socket.on('playeraddedtoroom', function (data) {
    connectedPlayers = data.count + '/5';
    game.state.start('waitRoom');
});

socket.on('startgame', function (data) {
    currentQuestion = data;
    game.state.start('fightForQuestion');
});


function entrarAction() {
    socket.emit('newplayer');
    game.state.start('chooseRoom');
}

function enterRoomAction() {
    var playerid = window.localStorage.playerid;
    socket.emit('playerWantsToEnterRoom', {
        playerid: playerid,
        nick: username
    });
}

function tryAnswerQuestionAction() {
    var playerid = window.localStorage.playerid;
    socket.emit('tryGetLock', { playerid: playerid });
}

function answerQuestionAction(button) {
    clearInterval(interval);
    var userAnswer = "op" + button.key;
    if (userAnswer === currentQuestion.opCerta) {
        socket.emit('acertou');
    }
    else {
        socket.emit('errou');
    }
}

function playAgain() {
    game.state.start('login');
}

var loginState = {

    preload: function () {

        game.load.image('bg', 'assets/img/bg.jpg');
        game.load.image('entrarButton', 'assets/img/entrar.png');
    },
    create: function () {

        var textX = game.width / 2;
        var textY = game.height / 3;
        var styleTitle = { font: "bold 6em Raleway sans-serif", fill: "#fff" };
        bg = game.add.sprite(0, 0, 'bg');
        bg.x = 0;
        bg.y = 0;
        bg.height = game.height;
        bg.width = game.width;
        title = game.add.text(textX, textY, "CAPANSWER:QUANTO VOCÊ \n  SABE SOBRE CAPIVARAS?", styleTitle);
        title.anchor.set(0.5);
        button = game.add.button(textX - 180, textY + 300, 'entrarButton',
            entrarAction, this, 2, 1, 0);
    },
};

var chooseRoomState = {
    preload: function () {
        game.load.image('roomButton', 'assets/img/room.png');
    },
    create: function () {
        game.stage.backgroundColor = "#5bc0de";
        var x = game.width / 2;
        var y = game.height / 5;
        var styleTitle = { font: "normal 5.5em Raleway sans-serif", fill: "#fff" };
        var newTitlteText = username + ", escolha uma sala:";
        var newTitle = game.add.text(x, y, newTitlteText, styleTitle);
        newTitle.anchor.set(0.5);
        button = game.add.button(x, y + 400, 'roomButton',
            enterRoomAction, this, 2, 1, 0);
        button.anchor.set(0.5);
    },
};

var waitRoomState = {
    create: function () {
        var x = game.width / 2;
        var y = game.height / 5;
        var styleTitle = { font: "normal 6em Raleway sans-serif", fill: "#fff" };
        var newTitlteText = "Esperando jogadores...";
        var newTitle = game.add.text(x, y, newTitlteText, styleTitle);
        newTitle.anchor.set(0.5);
        game.stage.backgroundColor = "#5bc0de";
        var loadingProcessInPercentage = game.add.text(game.width / 2 - 20, game.height / 2 - 100,
            connectedPlayers, {
                font: '60px "Press Start 2P"',
                fill: '#ffffff'
            });

    }
};

var fightForQuestionState = {
    preload: function () {
        game.load.image('responderButton', 'assets/img/responder.png');

    },
    create: function () {
        var x = game.width / 2;
        var y = game.height / 8;
        var styleTitle = { font: "normal 5.5em Raleway sans-serif", fill: "#fff", align: "center" };
        var newTitlteText = currentQuestion.questao;
        var newTitle = game.add.text(x, y, newTitlteText, styleTitle);
        var optionText1 = currentQuestion.op1;
        var option1 = game.add.text(x - 300, y + 200, optionText1, styleTitle);
        var optionText2 = currentQuestion.op2;
        var option2 = game.add.text(x - 300, y + 350, optionText2, styleTitle);
        var optionText3 = currentQuestion.op3;
        var option3 = game.add.text(x - 300, y + 500, optionText3, styleTitle);
        var optionText4 = currentQuestion.op4;
        var option4 = game.add.text(x - 300, y + 650, optionText4, styleTitle);
        var optionText5 = currentQuestion.op5;
        var option5 = game.add.text(x - 300, y + 800, optionText5, styleTitle);
        newTitle.anchor.set(0.5)
        game.stage.backgroundColor = "#5bc0de";
        button = game.add.button(x, game.height - 200, 'responderButton',
            tryAnswerQuestionAction, this, 2, 1, 0);
        button.anchor.set(0.5);


    }
};

var answerQuestionState = {
    preload: function () {
        game.load.image('1', 'assets/img/1.png');
        game.load.image('2', 'assets/img/2.png');
        game.load.image('3', 'assets/img/3.png');
        game.load.image('4', 'assets/img/4.png');
        game.load.image('5', 'assets/img/5.png');
    },
    create: function () {
        var playerid = window.localStorage.playerid;
        var x = game.width / 2;
        var y = game.height / 10;
        game.stage.backgroundColor = "#5bc0de";
        var styleTitle = { font: "normal 5.5em Raleway sans-serif", fill: "#fff", align: "center" };
        var newTitle = game.add.text(x, y, "Você tem 10 segundos para responder",
            styleTitle);
        var subTitleText = currentQuestion.questao;
        var subTitle = game.add.text(x, y + 200, subTitleText, styleTitle);
        newTitle.anchor.set(0.5);
        subTitle.anchor.set(0.5);
        var optionText1 = currentQuestion.op1;
        var option1text = game.add.text(x - 400, y + 400, optionText1, styleTitle);
        var optionText2 = currentQuestion.op2;
        var option2text = game.add.text(x - 400, y + 550, optionText2, styleTitle);
        var optionText3 = currentQuestion.op3;
        var option3text = game.add.text(x - 400, y + 700, optionText3, styleTitle);
        var optionText4 = currentQuestion.op4;
        var option4text = game.add.text(x - 400, y + 850, optionText4, styleTitle);
        var optionText5 = currentQuestion.op5;
        var option5text = game.add.text(x - 400, y + 1000, optionText5, styleTitle);
        option1 = game.add.button(x + 300, y + 430, '1',
            answerQuestionAction, this, 2, 1, 0);
        option1.anchor.set(0.5);
        option2 = game.add.button(x + 300, y + 580, '2',
            answerQuestionAction, this, 2, 1, 0);
        option2.anchor.set(0.5);
        option3 = game.add.button(x + 300, y + 730, '3',
            answerQuestionAction, this, 2, 1, 0);
        option3.anchor.set(0.5);
        option4 = game.add.button(x + 300, y + 880, '4',
            answerQuestionAction, this, 2, 1, 0);
        option4.anchor.set(0.5);
        option5 = game.add.button(x + 300, y + 1030, '5',
            answerQuestionAction, this, 2, 1, 0);
        option5.anchor.set(0.5);
        var timer = 10, minutes, seconds;
        interval = setInterval(function () {
            seconds = parseInt(timer % 60, 10);

            seconds = seconds < 10 ? "0" + seconds : seconds;

            var newTitlteText = "Você tem " + seconds + " segundos para responder";
            newTitle.setText(newTitlteText);
            if (timer-- === 0) {
                clearInterval(interval);
                socket.emit('timeoutanswer');
            }
        }, 1000);


    }
};

var waitForAnswerState = {
    create: function () {
        var x = game.width / 2;
        var y = game.height / 2;
        game.stage.backgroundColor = "#5bc0de";
        var styleTitle = { font: "normal 5.5em Raleway sans-serif", fill: "#fff", align: "center" };
        var newTitle = game.add.text(x, y, "O usuário " + playerAnswering + " clicou primeiro\n" +
            "ele tem 10 segundos para responder",
            styleTitle);
        newTitle.anchor.set(0.5);


    }
};

var scoreState = {
    create: function () {
        game.stage.backgroundColor = "#5bc0de";
        var x = game.width / 2;
        var y = game.height / 6;
        var styleTitle = { font: "normal 5.5em Raleway sans-serif", fill: "#fff" };
        var newTitlteText = "O jogador " + playerAnswering;
        var subTitleText = answerStatus;
        var newTitle = game.add.text(x, y, newTitlteText, styleTitle);
        var subTitle = game.add.text(x, y + 60, subTitleText, styleTitle);
        newTitle.anchor.set(0.5);
        subTitle.anchor.set(0.5);
        players.sort(function (a, b) {
            return b.score - a.score;
        });
        var offset = 300;
        for (var index in players) {
            var newPlayer = game.add.text(x - 200, y + offset, players[index].nick, styleTitle);
            var newScore = game.add.text(x + 200, y + offset, players[index].score, styleTitle);
            offset += 100;
            newPlayer.anchor.set(0.5);
            newScore.anchor.set(0.5);
        }

        var gameBegin = game.add.text(x, y + offset + 100, "O jogo vai recomeçar em 10 segundos", styleTitle);
        gameBegin.anchor.set(0.5);
        var timer = 10, minutes, seconds;
        interval = setInterval(function () {
            seconds = parseInt(timer % 60, 10);
            seconds = seconds < 10 ? "0" + seconds : seconds;

            var gameBeginText = "O jogo vai recomeçar em " + seconds + " segundos";

            gameBegin.setText(gameBeginText);
            if (timer-- === 0) {
                timer = 0;
                clearInterval(interval);
                socket.emit('newquestion');
            }
        }, 1000);


    }
};

var winnerState = {
    preload: function () {
        game.load.image('playAgain', 'assets/img/jogar.png');
    },
    create: function () {
        var x = game.width / 2;
        var y = game.height / 2;
        game.stage.backgroundColor = "#5bc0de";
        var styleTitle = { font: "normal 6em Raleway sans-serif", fill: "#fff", align: "center" };
        var newTitle = game.add.text(x, y, "Você venceu! Parabéns, \nvocê sabe tudo sobre capivaras! \n:)",
            styleTitle);
        newTitle.anchor.set(0.5);
        button = game.add.button(x, game.height - 200, 'playAgain',
            playAgain, this, 2, 1, 0);
        button.anchor.set(0.5);

    }
};

var looserState = {
    preload: function () {
        game.load.image('playAgain', 'assets/img/jogar.png');
    },
    create: function () {
        var x = game.width / 2;
        var y = game.height / 2;
        game.stage.backgroundColor = "#5bc0de";
        var styleTitle = { font: "normal 6em Raleway sans-serif", fill: "#fff", align: "center" };
        var newTitle = game.add.text(x, y, "Você perdeu, mas não desanime \nvocê pode jogar novamente! :)",
            styleTitle);
        newTitle.anchor.set(0.5);
        button = game.add.button(x, game.height - 200, 'playAgain',
            playAgain, this, 2, 1, 0);
        button.anchor.set(0.5);

    }
};


game.state.add('login', loginState);
game.state.add('chooseRoom', chooseRoomState);
game.state.add('waitRoom', waitRoomState);
game.state.add('fightForQuestion', fightForQuestionState);
game.state.add('answerQuestion', answerQuestionState);
game.state.add('waitForAnswer', waitForAnswerState);
game.state.add('score', scoreState);
game.state.add('winner', winnerState);
game.state.add('looser', looserState);

game.state.start('login');
