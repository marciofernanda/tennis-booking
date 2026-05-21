#!/usr/bin/env python3
"""
⚡ BOT ULTRA-RÁPIDO DE RESERVA - LetzPlay.me
Ataca exatamente à meia-noite (abertura de reservas)
Reserva: Quadra 2 | Fazenda Vila Real de Itu
Horários: 9-10 e 10-11 | Dia: PRÓXIMO SÁBADO
"""

import os
import sys
import json
import logging
import requests
import time
from datetime import datetime, timedelta
from threading import Thread
import pytz

# Importações Selenium (fallback)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
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

# Timezone São Paulo
TZ_SP = pytz.timezone('America/Sao_Paulo')

# Configurações de ataque
MAX_RETRIES = 10
RETRY_DELAY = 0.5  # segundos entre tentativas
REQUEST_TIMEOUT = 10  # timeout para requisições HTTP

# ============================================================================
# CÁLCULO DE DATA - SEMPRE 1 SÁBADO À FRENTE (abertura 7 dias antes)
# ============================================================================

def calcular_proximo_sabado():
    """
    Calcula o sábado que será reservado.
    
    Lógica:
    - Encontra o próximo sábado
    - Se ele está no passado (já abriu), pega o próximo sábado
    - SEMPRE retorna um sábado onde a abertura ainda não passou
    """
    agora = datetime.now(TZ_SP)
    
    # Encontra próximo sábado
    dias_para_sabado = (5 - agora.weekday()) % 7
    if dias_para_sabado == 0:
        dias_para_sabado = 7
    proximo_sabado = agora + timedelta(days=dias_para_sabado)
    
    # Verifica se a abertura desse sábado já passou
    # Abertura = 7 dias antes (sexta-feira anterior)
    data_abertura = proximo_sabado.date() - timedelta(days=1)
    hora_abertura = TZ_SP.localize(datetime.combine(data_abertura, datetime.min.time()))
    
    # Se abertura já passou, pega o próximo sábado
    if agora > hora_abertura:
        # Avança para o sábado seguinte
        proximo_sabado = proximo_sabado + timedelta(days=7)
    
    return proximo_sabado.date()

def calcular_tempo_abertura():
    """
    Calcula quando a reserva abre (7 dias antes do sábado).
    
    Abre na sexta-feira à 00:00.
    """
    sabado_alvo = calcular_proximo_sabado()
    # Abertura = 7 dias antes = sexta-feira anterior
    data_abertura = sabado_alvo - timedelta(days=1)
    abertura = TZ_SP.localize(datetime.combine(data_abertura, datetime.min.time()))
    return abertura

def tempo_ate_abertura():
    """Retorna segundos até a abertura da reserva"""
    agora = datetime.now(TZ_SP)
    abertura = calcular_tempo_abertura()
    delta = abertura - agora
    return delta.total_seconds()

# ============================================================================
# ABORDAGEM 1: API DIRETA (MAIS RÁPIDO)
# ============================================================================

class LetzPlayAPI:
    """Comunica com API do LetzPlay.me diretamente"""
    
    def __init__(self, email, senha):
        self.email = email
        self.senha = senha
        self.session = requests.Session()
        self.token = None
        self.facility_id = None
        self.court_id = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def login(self):
        """Faz login via API"""
        try:
            logger.info("🔐 Iniciando login via API...")
            
            # Tentar obter token
            response = self.session.post(
                f"{LETZPLAY_URL}/api/auth/login",
                json={"email": self.email, "password": self.senha},
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token') or data.get('access_token')
                self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                logger.info("✅ Login API bem-sucedido!")
                return True
            else:
                logger.warning(f"❌ Login API falhou: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️  Erro ao fazer login via API: {e}")
            return False
    
    def encontrar_facility(self):
        """Encontra o ID da facility (condomínio)"""
        try:
            logger.info(f"🏢 Procurando facility: {CONDOMINIO}")
            
            response = self.session.get(
                f"{LETZPLAY_URL}/api/facilities",
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                facilities = response.json()
                for facility in facilities:
                    if CONDOMINIO.lower() in facility.get('name', '').lower():
                        self.facility_id = facility.get('id')
                        logger.info(f"✅ Facility encontrado: {self.facility_id}")
                        return True
            
            logger.warning("❌ Facility não encontrado")
            return False
            
        except Exception as e:
            logger.warning(f"⚠️  Erro ao buscar facilities: {e}")
            return False
    
    def encontrar_quadra(self):
        """Encontra o ID da quadra 2"""
        try:
            logger.info(f"🎾 Procurando quadra {QUADRA}...")
            
            response = self.session.get(
                f"{LETZPLAY_URL}/api/facilities/{self.facility_id}/courts",
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                courts = response.json()
                for court in courts:
                    if QUADRA in str(court.get('number', '')):
                        self.court_id = court.get('id')
                        logger.info(f"✅ Quadra encontrada: {self.court_id}")
                        return True
            
            logger.warning("❌ Quadra não encontrada")
            return False
            
        except Exception as e:
            logger.warning(f"⚠️  Erro ao buscar quadras: {e}")
            return False
    
    def reservar_horario(self, data, hora_inicio, hora_fim, tentativa=1):
        """Reserva um horário específico"""
        try:
            logger.info(f"⏱️  [{tentativa}] Tentando: {data} {hora_inicio}-{hora_fim}")
            
            payload = {
                "facility_id": self.facility_id,
                "court_id": self.court_id,
                "date": data.isoformat(),
                "start_time": hora_inicio,
                "end_time": hora_fim,
                "duration_minutes": 60
            }
            
            response = self.session.post(
                f"{LETZPLAY_URL}/api/bookings",
                json=payload,
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Reserva realizada: {hora_inicio}-{hora_fim}")
                return True
            else:
                logger.warning(f"❌ Falha na reserva: {response.status_code} - {response.text[:100]}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️  Erro ao reservar: {e}")
            return False
    
    def reservar_com_retry(self, data, hora_inicio, hora_fim):
        """Tenta reservar com múltiplas tentativas"""
        for tentativa in range(1, MAX_RETRIES + 1):
            if self.reservar_horario(data, hora_inicio, hora_fim, tentativa):
                return True
            
            if tentativa < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
        
        return False

# ============================================================================
# ABORDAGEM 2: SELENIUM (FALLBACK)
# ============================================================================

def configurar_chrome():
    """Configura Chrome para máxima velocidade"""
    options = Options()
    
    if os.getenv("CI") or os.getenv("RAILWAY"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    else:
        options.add_argument("--start-maximized")
    
    # Desabilitar features que desaceleram
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    return options

def reservar_via_selenium(data_sabado):
    """Fallback: usa Selenium se API não funcionar"""
    logger.info("=" * 70)
    logger.info("🔄 Ativando FALLBACK: Selenium")
    logger.info("=" * 70)
    
    driver = None
    try:
        options = configurar_chrome()
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(15)
        
        logger.info("🌐 Acessando LetzPlay.me...")
        driver.get(LETZPLAY_URL)
        
        wait = WebDriverWait(driver, 10)
        
        # Login
        logger.info("🔐 Fazendo login...")
        time.sleep(0.5)
        
        try:
            login_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Entrar')] | //a[contains(text(), 'Login')]"))
            )
            login_btn.click()
        except:
            pass
        
        email_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='email'] | //input[@placeholder*='email' or @placeholder*='Email']"))
        )
        email_input.send_keys(EMAIL)
        
        senha_input = driver.find_element(By.XPATH, "//input[@type='password']")
        senha_input.send_keys(SENHA)
        
        entrar_btn = driver.find_element(By.XPATH, "//button[@type='submit'] | //button[contains(text(), 'Entrar')]")
        entrar_btn.click()
        
        wait.until(EC.url_changes(driver.current_url))
        logger.info("✅ Login Selenium bem-sucedido!")
        
        # Selecionar condomínio
        logger.info(f"🏢 Selecionando: {CONDOMINIO}")
        time.sleep(1)
        
        condominio_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Condomínio')] | //*[contains(text(), 'Facility')] | //*[contains(text(), 'Local')]"))
        )
        condominio_btn.click()
        
        condominio_opt = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{CONDOMINIO}')]"))
        )
        condominio_opt.click()
        
        logger.info("✅ Condomínio selecionado!")
        
        # Reservar horários
        data_formatada = data_sabado.strftime("%d/%m/%Y")
        reservas_ok = 0
        
        for horario in HORARIOS:
            try:
                logger.info(f"🎾 Reservando: {horario['inicio']}-{horario['fim']}")
                time.sleep(0.5)
                
                quadra_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), 'Quadra {QUADRA}')] | //*[contains(text(), 'Court {QUADRA}')]"))
                )
                quadra_btn.click()
                
                time.sleep(0.3)
                input_data = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='date'] | //input[@placeholder*='Data']"))
                )
                input_data.clear()
                input_data.send_keys(data_formatada)
                
                input_hora = driver.find_elements(By.XPATH, "//input[@type='time']")
                if len(input_hora) >= 1:
                    input_hora[0].clear()
                    input_hora[0].send_keys(horario['inicio'])
                
                if len(input_hora) >= 2:
                    input_hora[1].clear()
                    input_hora[1].send_keys(horario['fim'])
                
                time.sleep(0.2)
                reservar_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Reservar')] | //button[contains(text(), 'Book')]")
                reservar_btn.click()
                
                time.sleep(1)
                logger.info(f"✅ {horario['inicio']}-{horario['fim']} reservado!")
                reservas_ok += 1
                
            except Exception as e:
                logger.error(f"❌ Erro em {horario['inicio']}-{horario['fim']}: {e}")
                continue
        
        return reservas_ok > 0
        
    except Exception as e:
        logger.error(f"❌ Erro fatal no Selenium: {e}")
        return False
    finally:
        if driver:
            driver.quit()

# ============================================================================
# ORQUESTRAÇÃO PRINCIPAL
# ============================================================================

def aguardar_abertura():
    """Aguarda a abertura das reservas com precisão"""
    logger.info("=" * 70)
    logger.info("⏰ MODO: Espera pela Abertura")
    logger.info("=" * 70)
    
    while True:
        agora = datetime.now(TZ_SP)
        segundos_faltando = tempo_ate_abertura()
        
        if segundos_faltando <= 0:
            logger.info("🚀 ABERTURA AGORA! Atacando...")
            return True
        
        # Log a cada segundo no último minuto
        if segundos_faltando <= 60:
            minutos = int(segundos_faltando) // 60
            segundos = int(segundos_faltando) % 60
            logger.info(f"⏳ Faltam: {minutos}m {segundos}s")
            time.sleep(0.5)
        else:
            # A cada 5 minutos se estiver longe
            logger.info(f"⏳ Faltam: {int(segundos_faltando / 60)} minutos")
            time.sleep(300)

def executar_ataque():
    """Executa o ataque de reserva"""
    logger.info("=" * 70)
    logger.info("🚀 INICIANDO ATAQUE DE RESERVA")
    logger.info("=" * 70)
    
    # Validações
    if not EMAIL or not SENHA:
        logger.error("❌ ERRO: Credenciais não configuradas!")
        logger.error("   Configure: LETZPLAY_EMAIL e LETZPLAY_PASSWORD")
        return False
    
    data_sabado = calcular_proximo_sabado()
    logger.info(f"📅 Alvo: {data_sabado.strftime('%A, %d de %B de %Y')}")
    logger.info(f"🎾 Quadra: {QUADRA}")
    logger.info(f"🏢 Condomínio: {CONDOMINIO}")
    
    # ABORDAGEM 1: Tentar via API (mais rápido)
    logger.info("\n" + "=" * 70)
    logger.info("💪 FASE 1: API Direta")
    logger.info("=" * 70)
    
    api = LetzPlayAPI(EMAIL, SENHA)
    
    if api.login() and api.encontrar_facility() and api.encontrar_quadra():
        logger.info("📍 Pré-requisitos OK. Aguardando abertura...")
        aguardar_abertura()
        
        # Ataque coordenado nos dois horários
        logger.info("\n🎯 ATAQUE PRINCIPAL!")
        resultados = []
        
        for horario in HORARIOS:
            resultado = api.reservar_com_retry(
                data_sabado,
                horario['inicio'],
                horario['fim']
            )
            resultados.append(resultado)
        
        if any(resultados):
            logger.info("\n" + "=" * 70)
            logger.info("✅✅✅ SUCESSO! RESERVAS CONFIRMADAS!")
            logger.info("=" * 70)
            return True
    
    # ABORDAGEM 2: Fallback para Selenium
    logger.warning("\n⚠️  API falhou. Ativando Selenium...")
    aguardar_abertura()
    
    if reservar_via_selenium(data_sabado):
        logger.info("\n" + "=" * 70)
        logger.info("✅ SUCESSO COM SELENIUM!")
        logger.info("=" * 70)
        return True
    
    logger.error("\n" + "=" * 70)
    logger.error("❌ FALHA COMPLETA: Nenhuma reserva realizada")
    logger.error("=" * 70)
    return False

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        sucesso = executar_ataque()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        logger.info("\n\n⏸️  Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Erro fatal: {e}", exc_info=True)
        sys.exit(1)
