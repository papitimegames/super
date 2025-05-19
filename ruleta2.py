import pygame
import sys
from pygame.locals import *
from typing import Tuple

# Constantes
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ANCHO = 1280
ALTO = 720
FPS = 60

class Ruleta:
    def __init__(self, posicion: Tuple[int, int]):
        self.posicion = posicion
        self.angulo = 0
        self.velocidad_rotacion = 0
        self.imagen = self.cargar_imagen("ruleta.jpg")
        self.rect = self.imagen.get_rect(center=posicion)

    def cargar_imagen(self, ruta: str) -> pygame.Surface:
        imagen = pygame.image.load(ruta).convert_alpha()
        return pygame.transform.smoothscale(imagen, (600, 600))

    def actualizar(self, dt: float):
        if self.velocidad_rotacion > 0:
            self.angulo += self.velocidad_rotacion * dt
            self.velocidad_rotacion *= 0.992  # Fricción
            self.rect = self.imagen.get_rect(center=self.posicion)

    def dibujar(self, superficie: pygame.Surface):
        imagen_rotada = pygame.transform.rotate(self.imagen, self.angulo)
        rect_rotado = imagen_rotada.get_rect(center=self.posicion)
        superficie.blit(imagen_rotada, rect_rotado)

class Bola:
    def __init__(self, posicion_inicial: Tuple[int, int]):
        self.posicion = list(posicion_inicial)
        self.velocidad = [0.0, 0.0]
        self.imagen = self.cargar_imagen("bola.png")
        self.rect = self.imagen.get_rect(center=posicion_inicial)

    def cargar_imagen(self, ruta: str) -> pygame.Surface:
        return pygame.image.load(ruta).convert_alpha()

    def actualizar(self, dt: float):
        self.velocidad[0] *= 0.99  # Resistencia del aire
        self.velocidad[1] += 0.5  # Gravedad
        self.posicion[0] += self.velocidad[0] * dt
        self.posicion[1] += self.velocidad[1] * dt
        self.rect.center = self.posicion

    def dibujar(self, superficie: pygame.Surface):
        superficie.blit(self.imagen, self.rect)

class JuegoRuleta:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Simulación de Ruleta Profesional Papiweb")
        self.reloj = pygame.time.Clock()
        
        self.fuente_principal = pygame.font.Font(None, 36)
        self.fuente_pequeña = pygame.font.Font(None, 24)
        
        self.ruleta = Ruleta((ANCHO//2, ALTO//2 - 50))
        self.bola = Bola((ANCHO//2 + 250, ALTO//2))
        self.capa_transparente = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        
        self.tiempo_sin_actividad = 0.0
        self.alpha_overlay = 255
        self.mostrar_instrucciones = False
        self.ejecutando = True
        
        self.instrucciones = [
            "Instrucciones:",
            "ESPACIO - Girar ruleta",
            "CLICK IZQ - Lanzar bola",
            "I - Mostrar/Ocultar instrucciones",
            "ESC - Salir"
        ]

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == QUIT:
                self.ejecutando = False
            if evento.type == KEYDOWN:
                if evento.key == K_ESCAPE:
                    self.ejecutando = False
                if evento.key == K_i:
                    self.mostrar_instrucciones = not self.mostrar_activo
            if evento.type == MOUSEBUTTONDOWN:
                if evento.button == 1:
                    self.lanzar_bola()

    def lanzar_bola(self):
        self.bola.velocidad = [-15.0, -20.0]
        self.tiempo_sin_actividad = 0.0

    def actualizar_estado(self, dt: float):
        self.ruleta.actualizar(dt)
        self.bola.actualizar(dt)
        
        if self.ruleta.velocidad_rotacion < 0.1:
            self.tiempo_sin_actividad += dt
        else:
            self.tiempo_sin_actividad = 0.0

        if self.alpha_overlay > 0:
            self.alpha_overlay = max(0, self.alpha_overlay - 5)

    def renderizar(self):
        self.pantalla.fill(NEGRO)
        self.capa_transparente.fill((0, 0, 0, 0))
        
        # Dibujar elementos principales
        self.ruleta.dibujar(self.capa_transparente)
        self.bola.dibujar(self.capa_transparente)
        
        # Dibujar interfaz de usuario
        self.dibujar_instrucciones()
        self.dibujar_fps()
        
        self.pantalla.blit(self.capa_transparente, (0, 0))
        self.aplicar_overlay()
        
        pygame.display.flip()

    def dibujar_instrucciones(self):
        if self.mostrar_instrucciones:
            overlay = pygame.Surface((ANCHO, 150), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.capa_transparente.blit(overlay, (0, ALTO - 150))
            
            for i, texto in enumerate(self.instrucciones):
                renderizado = self.fuente_pequeña.render(texto, True, BLANCO)
                self.capa_transparente.blit(renderizado, (20, ALTO - 140 + i * 30))

    def dibujar_fps(self):
        fps = self.reloj.get_fps()
        texto = self.fuente_pequeña.render(f"FPS: {fps:.1f}", True, BLANCO)
        self.capa_transparente.blit(texto, (10, 10))

    def aplicar_overlay(self):
        if self.alpha_overlay > 0:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.alpha_overlay))
            self.pantalla.blit(overlay, (0, 0))

    def ejecutar(self):
        while self.ejecutando:
            dt = self.reloj.tick(FPS)
            self.manejar_eventos()
            self.actualizar_estado(dt)
            self.renderizar()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    juego = JuegoRuleta()
    juego.ejecutar()