# This is for the RPi to send over periodic images

import time
import paramiko
from scp import SCPClient

import pygame
import pygame.camera

width = 1000; height = 700

pygame.init()
pygame.camera.init()
camlist = pygame.camera.list_cameras()

cam = pygame.camera.Camera(camlist[0], (width, height))

def createClient(server, port, user):
    ssh = paramiko.SSHClient()
    ssh_key = paramiko.RSAKey.from_private_key_file("/home/pi/.ssh/id_rsa")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=user, pkey=ssh_key)
    return ssh



server = "172.20.2.117"
port = "22"
username = "puria"
file = "image.jpg"
enddir = "C:\\Users\\puria\\source\\repos\\puria-radmard\\CambridgeCarbonMap\\python"
recursive = False

while True:
    cam.start()
    image = cam.get_image()
    pygame.image.save(image, "image.jpg")
    cam.stop()

    time.sleep(10)

    ssh = createClient(server, port, username)
    scp = SCPClient(ssh.get_transport())
    scp.put(file, enddir, recursive = recursive)