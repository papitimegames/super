# Ensure ruleta and dt are defined
dt = 0.016  # Example delta time (16 ms for ~60 FPS)
ruleta = Ruleta()  # Replace with the actual initialization of the ruleta object
ruleta.actualizar(dt)
bola = Bola()  # Replace with the actual initialization of the bola object
bola.actualizar(dt)

# Actualizar tiempo sin actividad
tiempo_sin_actividad += dt / 1000

# Fade in inicial
if fade_in:
    alpha_overlay -= 5
    if alpha_overlay <= 0:
        alpha_overlay = 0
        fade_in = False

# Dibujar la escena
# Fondo (imagen o color)
if fondo:
    pantalla.blit(fondo, (0, 0))
else:
    pantalla.fill(NEGRO)

# Limpiar capa transparente
capa_transparente.fill((0, 0, 0, 0))

# Dibujar objetos en la capa transparente
mesa.dibujar(capa_transparente)
ruleta.dibujar(capa_transparente)
bola.dibujar(capa_transparente)

# Mostrar instrucciones con desvanecimiento
if mostrar_instrucciones:
    # Superficie para instrucciones con transparencia
    overlay_instrucciones = pygame.Surface((ancho, 120), pygame.SRCALPHA)
    overlay_instrucciones.fill((0, 0, 0, 150))
    capa_transparente.blit(overlay_instrucciones, (0, alto - 120))
    
    for i, texto in enumerate(instrucciones):
        instruccion = fuente.render(texto, True, BLANCO)
        capa_transparente.blit(instruccion, (20, alto - 110 + i * 30))
elif tiempo_sin_actividad > 10 and tiempo_sin_actividad < 15:
    # Recordatorio sutil después de 10 segundos sin actividad
    alpha = int(min(255, (tiempo_sin_actividad - 10) * 255))
    texto_ayuda = fuente_pequeña.render("Presiona I para mostrar instrucciones", True, BLANCO)
    texto_superficie = pygame.Surface(texto_ayuda.get_size(), pygame.SRCALPHA)
    texto_superficie.fill((0, 0, 0, min(150, alpha)))
    texto_superficie.blit(texto_ayuda, (0, 0))
    capa_transparente.blit(texto_superficie, (ancho - texto_ayuda.get_width() - 20, alto - 40))

# Añadir la capa transparente a la pantalla
pantalla.blit(capa_transparente, (0, 0))

# Efecto fade-in inicial
if alpha_overlay > 0:
    overlay = pygame.Surface((ancho, alto))
    overlay.fill(NEGRO)
    overlay.set_alpha(alpha_overlay)
    pantalla.blit(overlay, (0, 0))

# Mostrar información de FPS en modo desarrollo
fps = reloj.get_fps()
texto_fps = fuente_pequeña.render(f"FPS: {fps:.1f}", True, BLANCO)
pantalla.blit(texto_fps, (10, 10))

# Actualizar pantalla
pygame.display.flip()

# Tiempo de procesamiento para mantener constante los FPS
tiempo_procesamiento = pygame.time.get_ticks() - tiempo_inicio
tiempo_espera = max(0, int(16.67 - tiempo_procesamiento))  # Aproximadamente 60 FPS
if tiempo_espera > 0:
    pygame.time.wait(tiempo_espera)

# Limpieza al salir

# Ensure the Ruleta class or object is defined
class Ruleta:
    def __init__(self):
        pass  # Initialize any attributes here

    def actualizar(self, dt):
        pass  # Add logic to update the state of the ruleta

# Ensure the Bola class or object is defined
class Bola:
    def actualizar(self, dt):
        pass  # Replace with actual update logic

if __name__ == "__main__":
    main()
    main()

if __name__ == "__main__":
    main()
