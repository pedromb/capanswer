# CapAnswer

Um jogo multiplayer online de perguntas e respostas sobre Capivaras.

# Requisitos

Para executar localmente é necessário o ```npm``` e ```python3```, também é necessário
o ```pip3```. Para instalar execute

```
sudo apt-get install npm
sudo apt-get install python3-pip
```

# Para executar localmente

Clone o repositório e execute os passos abaixo

Na pasta capclient execute:

```
npm install

```

Na pasta capserver execute:

```
pip3 install -r requirements.txt
python3 app.py

```

Caso deseje pode utilizar o browser-sync para servir os arquivos do cliente.
Instale o browser-sync utilizando o comando

```
npm install -g browser-sync

```

Na pasta capclient execute

```
browser-sync start --server
```

O jogo estará disponivel em http://localhost:3000/www/index.html

No momento o jogo encontra-se disponivel no link: http://capanswer.s3-website-sa-east-1.amazonaws.com/

Obs.: Esse jogo foi feito para ser executado em dispositivos móveis. Embora ele execute
em um browser no desktop o layout não fica adequado. Para contornar isso, utilize o developer
tools do Google Chrome (Ctrl+Shift+I), utilize o comando Ctrl+Shift+M para redimensionar
a página no tamanho de uma tela de um celular. Talvez seja necessário atualizar a página
para que o redimensionamento aconteça, basta clicar F5.