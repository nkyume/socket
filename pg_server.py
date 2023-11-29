import sys
import pickle
import socket
import threading

HOST = '192.168.0.104'
PORT = 47353
ADDR = (HOST, PORT)

class Server():
    def __init__(self):
        self.server = socket.socket()
        self.server.bind(ADDR)

        self.players = {}

    def send(self, conn, data):
        data = pickle.dumps(data)
        conn.send(data)

    def recive(self, conn):
        data = conn.recv(1024)
        data = pickle.loads(data)
        return data

    def connect_new_player(self, conn):
        player_id = len(self.players)
        pos = (200, 200)

        player = {
            player_id: {
                'pos': pos
                }
        }

        data = {
            'signal': 'player_creation',
            'id': player_id,
            'data': self.players
            }

        self.players.update(player)
        self.send(conn, data)
    
    def send_players_data(self, conn):
        self.send(conn, self.players)

    def player_handler(self, conn):
        while True:
            try:
                data = self.recive(conn)
                signal = data['signal']
                if signal == 'connect':
                    player = self.connect_new_player(conn)
                elif signal == 'disconnect':
                    self.disconnect(player)
                    break

                elif signal == 'update_player_data':
                    id = data['data']['id']
                    pos = data['data']['pos']
                    self.players[id]['pos'] = pos

                elif signal == 'get_players':
                    self.send_players_data(conn)
            
                if not data:
                    print(f'{conn} disconected')
                    break
                
            except Exception as e:
                print(e)
                break

    def run(self):
        self.server.listen()
        print('Listening')
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.player_handler, args=(conn,))
            thread.start()
            print(f'Active connections: {threading.active_count() - 1}')

server = Server()
server.run()
            
            
            
