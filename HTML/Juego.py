from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import time
import subprocess
import sys

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, fps=40)
        self.controller = FirstPersonController(**kwargs)
        self.controller.camera_pivot.y = 2
        self.controller.speed = 8
        self.ball = None
        self.create_ball()

    def create_ball(self):
        self.ball = Entity(parent=self.controller.camera_pivot,
                           position=Vec3(0.7, -0.8, 1.2),
                           rotation=Vec3(0, 170, 0),
                           model='balon.obj',
                           scale=0.1,
                           texture='balon.jpg',
                           collider='box')

    def input(self, key):
        if key == 'escape':
            application.quit()
        if key == 'right mouse down' and self.ball:
            Lanzar(model=self.ball.model,
                   scale=0.1,
                   position=self.controller.camera_pivot.world_position,
                   rotation=self.controller.camera_pivot.world_rotation,
                   texture=self.ball.texture)
            invoke(self.create_ball, delay=1.5)

    def update(self):
        self.controller.camera_pivot.y = 2 - held_keys['left control']
        canasta1 = Canasta(postion=Vec3(-29, 0, 1.22))
        canasta1.rotation_y = 90

        canasta2 = Canasta(postion=Vec3(29,0,0.4))
        canasta2.rotation_y = 270

class Cancha(Entity):
    def __init__(self):
        super().__init__(
            position=Vec3(0, 0, 0),
            collider='box',
            model='cancha.obj',
            scale=(8, 8, 8),
            texture='cancha.png'
        )

class Canasta(Entity):
    def __init__(self, postion=Vec3(0, 0, 0)):
        super().__init__(
            position=postion,
            model='cesta.obj',
            collider='box',
            scale=(10, 10, 10),
            texture='cesta.png'
        )

class Lanzar(Entity):
    def __init__(self, model='', speed=50, lifetime=10, **kwargs):
        super().__init__(**kwargs, Collider='box')
        self.model = model
        self.speed = speed
        self.lifetime = lifetime
        self.start = time.time()

    def update(self):
        self.world_position += self.forward * self.speed * time.dt
        ray = raycast(self.world_position, self.forward, distance=self.speed * time.dt)
        if ray.hit:
            if isinstance(ray.entity, Canasta):
                print("Abriendo página web!!!")
                subprocess.check_output(["python", "C:\\Users\\Equipo\\Documents\\UNIVERSIDAD ROSARIO\\III Semestre\\Ingenieria de datos\\Pagina.py"])
                sys.exit()
            if isinstance(ray.entity, Cancha):
                destroy(self)
        if time.time() - self.start > self.lifetime:
            destroy(self)

app = Ursina(borderless=False)
window.size = Vec2(1000, 1000)

player = Player(position=Vec3(-15, 1, 1))
player.controller.rotation_y = 249.8
player.controller.rotation_x = 10

ground = Cancha()

Sky()

app.run()