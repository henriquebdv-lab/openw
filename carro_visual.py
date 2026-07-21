"""
Gera uma imagem SVG de carro (vista de cima) com cor customizável.
Determinístico por seed para variações visuais.
"""

import random


def _limitar(valor, minimo, maximo):
    return max(minimo, min(valor, maximo))


def gerar_svg_carro(cor_hex="#FF0000", largura=120, altura=160):
    """
    Gera SVG de carro com a cor especificada.
    
    Args:
        cor_hex: cor em formato hexadecimal (ex: "#FF0000" para vermelho)
        largura: largura do SVG
        altura: altura do SVG
    
    Returns:
        String SVG do carro
    """
    
    cx = largura / 2
    cy = altura / 2
    
    # Componentes do carro
    # Corpo principal (chassis)
    chassis_width = 35
    chassis_height = 75
    
    # Rodas
    roda_raio = 6
    roda_front_y = cy - 25
    roda_rear_y = cy + 28
    roda_left_x = cx - 18
    roda_right_x = cx + 18
    
    # Cockpit
    cockpit_width = 25
    cockpit_height = 20
    cockpit_y = cy - 15
    
    # Asa traseira (DRS)
    wing_width = 50
    wing_height = 8
    wing_y = cy + 32
    
    return f'''<svg viewBox="0 0 {largura} {altura}" xmlns="http://www.w3.org/2000/svg">
    <!-- Fundo -->
    <rect width="{largura}" height="{altura}" fill="#f5f5f5"/>
    
    <!-- Chassi/Corpo principal -->
    <ellipse cx="{cx}" cy="{cy - 5}" rx="{chassis_width}" ry="{chassis_height * 0.4}" fill="{cor_hex}" stroke="#333" stroke-width="1"/>
    <rect x="{cx - chassis_width}" y="{cy - 20}" width="{chassis_width * 2}" height="{chassis_height * 0.6}" fill="{cor_hex}" stroke="#333" stroke-width="1" rx="3"/>
    
    <!-- Cockpit/Cabine -->
    <ellipse cx="{cx}" cy="{cockpit_y}" rx="{cockpit_width * 0.5}" ry="{cockpit_height * 0.5}" fill="#222" stroke="#111" stroke-width="0.5"/>
    <rect x="{cx - cockpit_width * 0.4}" y="{cockpit_y - 6}" width="{cockpit_width * 0.8}" height="12" fill="#333" stroke="#111" stroke-width="0.5" rx="2"/>
    
    <!-- Asa dianteira (pequena) -->
    <rect x="{cx - wing_width * 0.4}" y="{cy - 32}" width="{wing_width * 0.8}" height="{wing_height * 0.6}" fill="#666" stroke="#333" stroke-width="0.5" rx="1"/>
    
    <!-- Asa traseira (DRS) -->
    <rect x="{cx - wing_width * 0.5}" y="{wing_y}" width="{wing_width}" height="{wing_height}" fill="#888" stroke="#333" stroke-width="0.5" rx="1"/>
    <line x1="{cx - wing_width * 0.3}" y1="{wing_y}" x2="{cx - wing_width * 0.3}" y2="{wing_y + wing_height}" stroke="#333" stroke-width="0.5"/>
    <line x1="{cx + wing_width * 0.3}" y1="{wing_y}" x2="{cx + wing_width * 0.3}" y2="{wing_y + wing_height}" stroke="#333" stroke-width="0.5"/>
    
    <!-- Rodas dianteiras -->
    <circle cx="{roda_left_x}" cy="{roda_front_y}" r="{roda_raio}" fill="#222" stroke="#111" stroke-width="0.5"/>
    <circle cx="{roda_left_x}" cy="{roda_front_y}" r="{roda_raio * 0.6}" fill="#555"/>
    
    <circle cx="{roda_right_x}" cy="{roda_front_y}" r="{roda_raio}" fill="#222" stroke="#111" stroke-width="0.5"/>
    <circle cx="{roda_right_x}" cy="{roda_front_y}" r="{roda_raio * 0.6}" fill="#555"/>
    
    <!-- Rodas traseiras (um pouco maiores) -->
    <circle cx="{roda_left_x}" cy="{roda_rear_y}" r="{roda_raio * 1.2}" fill="#222" stroke="#111" stroke-width="0.5"/>
    <circle cx="{roda_left_x}" cy="{roda_rear_y}" r="{roda_raio * 0.7}" fill="#555"/>
    
    <circle cx="{roda_right_x}" cy="{roda_rear_y}" r="{roda_raio * 1.2}" fill="#222" stroke="#111" stroke-width="0.5"/>
    <circle cx="{roda_right_x}" cy="{roda_rear_y}" r="{roda_raio * 0.7}" fill="#555"/>
    
    <!-- Detalhes: Farol dianteiro -->
    <circle cx="{cx - 8}" cy="{cy - 35}" r="2" fill="#ffff00" stroke="#ffa500" stroke-width="0.5"/>
    <circle cx="{cx + 8}" cy="{cy - 35}" r="2" fill="#ffff00" stroke="#ffa500" stroke-width="0.5"/>
    
    <!-- Número da equipe (espaço vazio para número) -->
    <rect x="{cx - 8}" y="{cy + 5}" width="16" height="16" fill="#fff" stroke="#333" stroke-width="0.5" rx="1"/>
    <text x="{cx}" y="{cy + 15}" font-size="10" font-weight="bold" font-family="Arial" fill="#333" text-anchor="middle">1</text>
</svg>'''


def cores_sugeridas():
    """Retorna cores padrão que podem ser usadas."""
    return [
        {"nome": "Vermelho Ferrari", "hex": "#DC0000"},
        {"nome": "Amarelo Renault", "hex": "#FFD700"},
        {"nome": "Azul McLaren", "hex": "#0066FF"},
        {"nome": "Verde Jaguar", "hex": "#004225"},
        {"nome": "Branco Mercedes", "hex": "#FFFFFF"},
        {"nome": "Preto AlphaTauri", "hex": "#2D826D"},
        {"nome": "Laranja Alpine", "hex": "#FF6600"},
        {"nome": "Vermelho Claro", "hex": "#FF4444"},
        {"nome": "Roxo Custom", "hex": "#9933FF"},
        {"nome": "Ciano Neon", "hex": "#00FFFF"},
        {"nome": "Magenta Neon", "hex": "#FF00FF"},
        {"nome": "Ouro Clássico", "hex": "#FFD700"},
    ]
