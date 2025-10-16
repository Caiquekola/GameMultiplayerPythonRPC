# GameMultiplayerPythonRPC
Seu chefe está convicto que a melhor abordagem de comunicação nesse jogo distribuído é um estilo arquitetônico baseado em eventos. Assim, ele definiu as seguintes tarefas a serem seguidas: Criar um servidor RPC que permita intermediar a comunicação entre todos os jogadores; 


New-NetFirewallRule -DisplayName "RPyC 18861" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 18861

Powershell Admin


python servidorrpc.py

ipconfig

python game.py --server 192.168.2.34 --port 18861 --name Alice

netstat -ano | findstr 18861
