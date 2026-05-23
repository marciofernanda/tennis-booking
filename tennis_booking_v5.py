#!/usr/bin/env python3
"""
⚡ BOT DE RESERVA v5 - SELENIUM COM ESPERA OTIMIZADA
LetzPlay.me - Sem tentativa de API
Reserva: Quadra 2 | Fazenda Vila Real de Itu
Horários: 9-10 e 10-11 | Dia: PRÓXIMO SÁBADO
"""

import os
import sys
import logging
import time
from datetime import datetime, timedelta
import pytz

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

LETZPLAY_URL = "https://letzplay.me"
CONDOMINIO = "Fazenda Vila Real de Itu"
QUADRA = "2"
HORARIOS = [
    {"inicio": "09:00", "fim": "10:00"},
    {"inicio": "10:00", "fim": "11:00"}
]

EMAIL = os.getenv("LETZPLAY_EMAIL", "").strip()
SENHA = os.getenv("LETZPLAY_PASSWORD", "").strip()

TZ_SP = pytz.timezone('America/Sao_Paulo')

# ============================================================================
# CÁLCULO DE DATA
# ============================================================================

def calcular_proximo_sabado():
    """Calcula o próximo sábado onde a abertura ainda não passou"""
    agora = datetime.now(TZ_SP)
    
    # Encontra próximo sábado
    dias_para_sabado = (5 - agora.weekday())
