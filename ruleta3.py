import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
import numpy as np
from scipy.integrate import odeint

class LuxuryTable:
    def __init__(self):
        # Inicialización de OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Carga de texturas
        self.table_texture = self.load_texture("red_velvet.jpg")
        self.footer_texture = self.create_footer_texture()
        
        # Configuración de shaders
        self.diamond_shader = self.compile_shader_program(
            vertex_shader_source="""
            #version 330 core
            layout(location = 0) in vec3 position;
            layout(location = 1) in vec2 texCoord;
            out vec2 vTexCoord;
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
            void main() {
                gl_Position = projection * view * model * vec4(position, 1.0);
                vTexCoord = texCoord;
            }
            """,
            
            fragment_shader_source="""
            #version 330 core
            in vec2 vTexCoord;
            out vec4 fragColor;
            uniform sampler2D texture_diffuse;
            uniform float time;
            void main() {
                vec4 texColor = texture(texture_diffuse, vTexCoord);
                vec3 sparkle = vec3(sin(time * 5.0 + vTexCoord.x * 50.0) * 0.5 + 0.5);
                fragColor = texColor * vec4(sparkle, 1.0);
            }
            """
        )
        
        # Modelado 3D de fichas
        self.chip_model = self.create_chip_mesh()
        
        # Configuración inicial de la cámara
        self.projection = self.get_projection_matrix()
        self.view = self.get_view_matrix()

    def load_texture(self, path):
        """Carga una textura desde archivo con gestión de errores"""
        try:
            texture_surface = pygame.image.load(path)
            texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
            
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                        texture_surface.get_width(), texture_surface.get_height(),
                        0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
            glGenerateMipmap(GL_TEXTURE_2D)
            
            return texture_id
        except Exception as e:
            print(f"Error loading texture {path}: {str(e)}")
            return None

    def create_chip_mesh(self):
        """Crea un modelo 3D de ficha de casino con geometría detallada"""
        vertices = []
        indices = []
        segments = 32
        
        # Generar geometría cilíndrica
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = math.cos(angle) * 0.1
            z = math.sin(angle) * 0.1
            
            # Vértices superiores e inferiores
            vertices.extend([x, 0.02, z, 0.5, 0.5])  # Coordenadas UV
            vertices.extend([x, -0.02, z, 0.5, 0.5])
            
            # Indices para formar triángulos
            if i < segments - 1:
                indices.extend([i*2, i*2+1, (i+1)*2])
                indices.extend([(i+1)*2, i*2+1, (i+1)*2+1])
        
        # Crear y configurar VAO/VBO
        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        ebo = glGenBuffers(1)
        
        glBindVertexArray(vao)
        
        # Configurar VBO
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, 
                    (GLfloat * len(vertices))(*vertices),
                    GL_STATIC_DRAW)
        
        # Configurar EBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     (GLuint * len(indices))(*indices),
                     GL_STATIC_DRAW)
        
        # Atributos de vértice
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), None)
        glEnableVertexAttribArray(0)
        
        # Atributos de textura
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), 
                             ctypes.c_void_p(3 * sizeof(GLfloat)))
        glEnableVertexAttribArray(1)
        
        return {
            'vao': vao,
            'vbo': vbo,
            'ebo': ebo,
            'indices': len(indices)
        }

    def create_footer_texture(self):
        """Crea una textura con el texto del footer"""
        footer_surface = pygame.Surface((800, 100), pygame.SRCALPHA)
        font = pygame.font.Font(None, 36)
        text = font.render("Papiweb desarrollos informaticos", True, (255, 255, 255, 200))
        
        # Dibujar fondo semitransparente
        pygame.draw.rect(footer_surface, (0, 0, 0, 150), (0, 0, 800, 100))
        footer_surface.blit(text, (400 - text.get_width()//2, 50 - text.get_height()//2))
        
        return self.texture_from_surface(footer_surface)

    def compile_shader_program(self, vertex_shader_source, fragment_shader_source):
        """Compila y enlaza un programa de shaders con manejo de errores"""
        program = glCreateProgram()
        vertex_shader = self.compile_shader(GL_VERTEX_SHADER, vertex_shader_source)
        fragment_shader = self.compile_shader(GL_FRAGMENT_SHADER, fragment_shader_source)
        
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        glLinkProgram(program)
        
        # Verificar enlace
        if not glGetProgramiv(program, GL_LINK_STATUS):
            print(f"Shader link error: {glGetProgramInfoLog(program).decode()}")
            return None
        
        return program

    def texture_from_surface(self, surface):
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                    surface.get_width(), surface.get_height(),
                    0, GL_RGBA, GL_UNSIGNED_BYTE,
                    pygame.image.tostring(surface, "RGBA", True))
        return tex

    def render_footer(self):
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 800, 0, 600)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glBindTexture(GL_TEXTURE_2D, self.footer_texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(200, 10)
        glTexCoord2f(1, 0); glVertex2f(600, 10)
        glTexCoord2f(1, 1); glVertex2f(600, 50)
        glTexCoord2f(0, 1); glVertex2f(200, 50)
        glEnd()
        
        glDisable(GL_BLEND)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)

class Roulette3D(LuxuryTable):
    def __init__(self):
        # Non-OpenGL initialization
        super().__init__()
        self.wheel_radius = 2.3
        self.ball_radius = 0.04
        self.deceleration = -0.02
        self.wobble_factor = 0.15
        self.ball_position = [0, 0.03, 0]
        self.angular_velocity = 0
        self.angle = 0
        self.time = 0.0

    def initialize_opengl_resources(self):
        # Call parent class OpenGL initialization
        super().initialize_opengl_resources()
        self.wheel_texture = self.load_texture("ruleta.jpg")
        self.spin_sound = pygame.mixer.Sound("spin.wav")
        self.bounce_sound = pygame.mixer.Sound("bounce.wav")

    def physics_update(self, dt):
        # Sistema de ecuaciones diferenciales actualizado
        def dynamics(y, t):
            theta, omega = y
            dydt = [omega, self.deceleration * (1 - omega/35)**3]
            return dydt
        
        sol = odeint(dynamics, [self.angle, self.angular_velocity], [0, dt])
        self.angle, self.angular_velocity = sol[-1]
        self.ball_position[1] = max(0, 0.03 + (self.angular_velocity/40) - (self.angular_velocity/120)**2)
        
        if self.ball_position[1] <= 0 and self.angular_velocity > 0.5:
            self.angular_velocity *= -0.6
            self.bounce_sound.play()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        # Activar shader de diamantes
        glUseProgram(self.diamond_shader)
        glUniform1f(glGetUniformLocation(self.diamond_shader, "time"), self.time)
        
        # Dibujar mesa de apuestas
        self.render_betting_table()
        
        # Dibujar ruleta
        glBindTexture(GL_TEXTURE_2D, self.wheel_texture)
        self.draw_wheel()
        
        # Dibujar bola
        self.draw_ball()
        
        # Footer
        self.render_footer()
        
        pygame.display.flip()
        self.time += 0.01

    def render_betting_table(self):
        # Dibujar mesa de apuestas con efecto de diamantes
        glBindVertexArray(self.chip_model['vao'])
        glBindTexture(GL_TEXTURE_2D, self.table_texture)
        glDrawElements(GL_TRIANGLES, self.chip_model['indices'], GL_UNSIGNED_INT, None)

    def run(self):
        pygame.init()
        display = (800, 600)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, -1.0, -10)

        # Initialize OpenGL-dependent resources after context creation
        self.initialize_opengl_resources()

        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            self.physics_update(dt)
            self.render()

if __name__ == "__main__":
    game = Roulette3D()
    game.run()