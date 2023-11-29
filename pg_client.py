import sys
import pickle
import socket
import threading

from time import sleep

import pygame as pg
from debug import debug

HOST = '192.168.0.104'
PORT = 47353
ADDR = (HOST, PORT)

class Game():
    
    def __init__(self) -> None:
        pg.init()
        self.display = pg.display.set_mode((1280, 720))
        self.clock = pg.time.Clock()
        self.characters = {}
        self.connect()
        self.running = True
        threading.Thread(target=self.networking).start()

    def send(self, data):
        data = pickle.dumps(data)
        self.client.send(data)

    def recive(self):
        data = self.client.recv(1024)
        data = pickle.loads(data)
        return data

    def connect(self):
        self.client = socket.socket()
        self.client.connect(ADDR)
        print('connected')

        self.send({'signal': 'connect'})
        data = self.recive()
        print(data)
        player_id = data['id']
        players = data['data']
        print(players)
        
        for id in players:
            pos = players[id]['pos']
            if id == player_id:
                self.player = Player(id, pos)
                self.characters.update({id: self.player})
            else:
                self.characters.update({id: Character(id, pos)})

        print(self.characters)

    def networking(self):
        while self.running:
            self.update_player_data()
            #sleep(0.0002)
            self.get_players()
            #sleep(0.0002)

    def update_player_data(self):
        data = {
            'signal': 'update_player_data',
            'data': {
                'id': self.player.id,
                'pos': self.player.rect.topleft
            }
        }
        self.send(data)

    def get_players(self):
        data = {
            'signal': 'get_players'
        }
        self.send(data)
        data = self.recive()
        
        for id in data:
            pos = data[id]['pos']
            if id == self.player.id:
                continue
            elif id not in list(self.characters.keys()):
                self.characters.update({id: Character(id, pos)})
            else:
                self.characters[id].rect.topleft = pos

    def draw_characters(self):
        if not self.characters:
            return
        for id in self.characters:
            self.characters[id].draw(self.display)

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    pg.quit()
                    
            self.display.fill('black')
            self.draw_characters()

            debug(int(self.clock.get_fps()))
            pg.display.flip()
            
            self.clock.tick(60)

class Player():
    def __init__(self, p_id, pos):
        print(p_id, pos)
        self.id = p_id
        self.surf = pg.Surface((10,10))
        self.surf.fill('green')
        self.rect = self.surf.get_rect(topleft=pos)
        
    def move(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.rect.y -= 3
        elif keys[pg.K_DOWN]:
            self.rect.y += 3
        if keys[pg.K_LEFT]:
            self.rect.x -= 3
        elif keys[pg.K_RIGHT]:
            self.rect.x += 3  
            
    def draw(self, display_surf):
        self.move()
        display_surf.blit(self.surf, self.rect)

class Character(Player):
    def draw(self, display_surf):
        display_surf.blit(self.surf, self.rect)

game = Game()
game.run()

