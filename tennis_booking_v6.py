#!/usr/bin/env python3
"""
⚡ BOT DE RESERVA v6 - DIAGNÓSTICO APRIMORADO
LetzPlay.me - Sem tentativa de API
Reserva: Quadra 2 | Fazenda Vila Real de Itu
Horários: 9-10 e 10-11 | Dia: PRÓXIMO SÁBADO
"""

import os
import sys
import logging
import time
from datetime import datetime, timedelta

# IMPRIMIR IMEDIATAMENTE para garantir que apareça
print("=" * 80)
print("🚀 INICIANDO BOT DE RESERVA v6 (DIAGNÓSTICO APRIMORADO)")
print("=" * 80)
print()

# Validar credenciais PRIMEIRO
EMAIL = os.getenv("LETZPLAY_EMAIL", "").strip()
SENHA = os.getenv("LETZPLAY_PASSWORD", "").strip()

print(f"📧 EMAIL configurado: {'✅ SIM' if EMAIL else '❌ NÃO'}")
print(f"🔑 SENHA configurada: {'✅ SIM' if SENHA else '❌ NÃO'}")
print()

if not EMAIL or not SENHA:
    print("❌ ERRO: Credenciais não configuradas!")
    print("Defina: LETZPLAY_EMAIL e LETZPLAY_PASSWORD")
    sys.exit(1)

# Agora importar as bibliotecas
print("📚 Importando bibliotecas...")
try:
    import pytz
    print("  ✅ pytz")
except ImportError as e:
    print(f"  ❌ pytz: {e}")
    sys.exit(1)

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    print("  ✅ selenium")
except ImportError as e:
    print(f"  ❌ selenium: {e}")
    sys.exit(1)

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    print("  ✅ webdriver-manager")
except ImportError as e:
    print(f"  ❌ webdriver-manager: {e}")
    sys.exit(1)

print("✅ Todas as bibliotecas importadas com sucesso!")
print()

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

TZ_SP = pytz.timezone('America/Sao_Paulo')

# ============================================================================
# CÁLCULO DE DATA
# ============================================================================

def calcular_proximo_sabado():
    """Calcula o próximo sábado onde a abertura ainda não passou"""
    agora = datetime.now(TZ_SP)
    
    # Encontra próximo sábado
    dias_para_sabado = (5 - agora.weekday()) % 7
    if dias_para_sabado == 0:
        dias_para_sabado = 7
    proximo_sabado = agora + timedelta(days=dias_para_sabado)
    
    # Verifica se a abertura desse sábado já passou
    # Abertura = 7 dias antes (sexta-feira anterior) à 00:00
    data_abertura = proximo_sabado.date() - timedelta(days=1)
    hora_abertura = TZ_SP.localize(datetime.combine(data_abertura, datetime.min.time()))
    
    # Se abertura já passou, pega o próximo sábado
    if agora > hora_abertura:
        proximo_sabado = proximo_sabado + timedelta(days=7)
    
    return proximo_sabado.date()

# ============================================================================
# SELENIUM - RESERVA VIA NAVEGADOR
# ============================================================================

def configurar_chrome():
    """Configura Chrome para máxima performance"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    
    return options

def fazer_reserva():
    """Reserva as quadras via Selenium"""
    logger.info("=" * 80)
    logger.info("🚀 FASE: INICIALIZAR SELENIUM")
    logger.info("=" * 80)
    
    data_reserva = calcular_proximo_sabado()
    
    logger.info(f"📅 Data alvo: {data_reserva.strftime('%A, %d de %B de %Y')}")
    logger.info(f"🎾 Quadra: {QUADRA}")
    logger.info(f"🏢 Condomínio: {CONDOMINIO}")
    logger.info(f"⏰ Horários: 09:00-10:00 e 10:00-11:00")
    
    driver = None
    try:
        options = configurar_chrome()
        
        # Usar webdriver-manager para gerenciar ChromeDriver automaticamente
        logger.info("🔧 Configurando ChromeDriver automático...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        logger.info("✅ ChromeDriver carregado com sucesso!")
        
        logger.info("\n" + "=" * 80)
        logger.info("FASE 1: ACESSAR LETZPLAY E FAZER LOGIN")
        logger.info("=" * 80)
        
        logger.info("🌐 Acessando LetzPlay.me...")
        driver.get(LETZPLAY_URL)
        
        # Aguardar carregamento completo da página
        logger.info("⏳ Aguardando carregamento da página (5s)...")
        time.sleep(5)
        logger.info("✅ Página carregada!")
        
        wait = WebDriverWait(driver, 20)
        
        # ===== FAZER LOGIN =====
        logger.info("🔐 Fazendo login...")
        
        try:
            # Procurar e clicar em botão de login
            logger.info("🔍 Procurando botão de login...")
            login_btn = driver.find_elements(By.XPATH, "//button[contains(text(), 'Entrar')] | //button[contains(text(), 'LOGIN')] | //a[contains(text(), 'Login')]")
            if login_btn:
                logger.info("✅ Botão de login encontrado, clicando...")
                login_btn[0].click()
                time.sleep(2)
            else:
                logger.warning("⚠️  Botão de login não encontrado, continuando...")
        except Exception as e:
            logger.warning(f"⚠️  Erro ao clicar em login: {e}")
        
        # Preencher email - aguardar campo estar disponível
        logger.info(f"📧 Preenchendo email: {EMAIL}")
        try:
            email_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='email'] | //input[@placeholder*='email' or @placeholder*='Email' or @name*='email' or @name*='login']"))
            )
            logger.info("✅ Campo de email encontrado")
            time.sleep(1)
            email_input.clear()
            email_input.send_keys(EMAIL)
            logger.info("✅ Email preenchido")
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"❌ Erro ao preencher email: {e}")
            return False
        
        # Preencher senha
        logger.info("🔑 Preenchendo senha...")
        try:
            senha_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password'] | //input[@name*='password' or @name*='senha']"))
            )
            logger.info("✅ Campo de senha encontrado")
            time.sleep(1)
            senha_input.clear()
            senha_input.send_keys(SENHA)
            logger.info("✅ Senha preenchida")
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"❌ Erro ao preencher senha: {e}")
            return False
        
        # Clicar em entrar
        logger.info("🔓 Clicando em Entrar...")
        try:
            entrar_btn = driver.find_element(By.XPATH, "//button[@type='submit'] | //button[contains(text(), 'Entrar')] | //button[contains(text(), 'LOGIN')]")
            entrar_btn.click()
        except Exception as e:
            logger.error(f"❌ Erro ao clicar em entrar: {e}")
            return False
        
        logger.info("⏳ Aguardando autenticação...")
        time.sleep(6)
        logger.info("✅ Login realizado!")
        
        # ===== SELECIONAR CONDOMÍNIO =====
        logger.info("\n" + "=" * 80)
        logger.info("FASE 2: SELECIONAR CONDOMÍNIO")
        logger.info("=" * 80)
        
        logger.info(f"🏢 Procurando condomínio: {CONDOMINIO}")
        time.sleep(2)
        
        try:
            # Clicar em seletor de condomínio
            cond_selector = driver.find_elements(By.XPATH, "//*[contains(text(), 'Condomínio')] | //*[contains(text(), 'Facility')] | //*[contains(text(), 'Local')]")
            if cond_selector:
                cond_selector[0].click()
                time.sleep(1)
        except:
            logger.warning("⚠️  Seletor de condomínio não encontrado")
        
        # Procurar e clicar no condomínio específico
        try:
            cond_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{CONDOMINIO.lower()}')]"))
            )
            logger.info(f"✅ Condomínio encontrado, selecionando...")
            cond_option.click()
            time.sleep(2)
            logger.info("✅ Condomínio selecionado!")
        except Exception as e:
            logger.error(f"❌ Erro ao selecionar condomínio: {e}")
            return False
        
        # ===== FAZER RESERVAS =====
        logger.info("\n" + "=" * 80)
        logger.info("FASE 3: RESERVAR HORÁRIOS")
        logger.info("=" * 80)
        
        reservas_ok = 0
        
        for idx, horario in enumerate(HORARIOS, 1):
            try:
                logger.info(f"\n🎾 Reserva {idx}/{len(HORARIOS)}: {horario['inicio']}-{horario['fim']}")
                time.sleep(1)
                
                # Selecionar quadra
                logger.info(f"  Selecionando quadra {QUADRA}...")
                quadra_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), 'Quadra {QUADRA}')] | //*[contains(text(), 'Court {QUADRA}')]"))
                )
                quadra_btn.click()
                time.sleep(0.5)
                
                # Selecionar data (formato DD/MM/YYYY)
                data_str = data_reserva.strftime("%d/%m/%Y")
                logger.info(f"  Selecionando data: {data_str}...")
                
                date_inputs = driver.find_elements(By.XPATH, "//input[@type='date'] | //input[@placeholder*='data' or @placeholder*='Data']")
                if date_inputs:
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(data_str)
                    time.sleep(0.3)
                
                # Selecionar horários
                logger.info(f"  Selecionando horário: {horario['inicio']}-{horario['fim']}...")
                time_inputs = driver.find_elements(By.XPATH, "//input[@type='time']")
                
                if len(time_inputs) >= 1:
                    time_inputs[0].clear()
                    time_inputs[0].send_keys(horario['inicio'])
                    time.sleep(0.2)
                
                if len(time_inputs) >= 2:
                    time_inputs[1].clear()
                    time_inputs[1].send_keys(horario['fim'])
                    time.sleep(0.2)
                
                # Clicar em reservar
                logger.info(f"  Clicando em Reservar...")
                time.sleep(0.5)
                reservar_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Reservar')] | //button[contains(text(), 'Book')] | //button[contains(text(), 'RESERVAR')]")
                reservar_btn.click()
                
                time.sleep(2)
                logger.info(f"  ✅ Reserva {idx} confirmada!")
                reservas_ok += 1
                
            except Exception as e:
                logger.error(f"  ❌ Erro ao reservar {horario['inicio']}-{horario['fim']}: {e}")
                continue
        
        # ===== RESULTADO FINAL =====
        if reservas_ok > 0:
            logger.info("\n" + "=" * 80)
            logger.info(f"✅✅✅ SUCESSO! {reservas_ok}/{len(HORARIOS)} RESERVAS CONFIRMADAS!")
            logger.info("=" * 80)
            return True
        else:
            logger.error("\n" + "=" * 80)
            logger.error("❌ FALHA: Nenhuma reserva foi realizada")
            logger.error("=" * 80)
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        return False
    finally:
        if driver:
            driver.quit()
            logger.info("\n🔌 Navegador fechado.")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    logger.info("\n")
    
    sucesso = fazer_reserva()
    
    if sucesso:
        logger.info("\n✅ BOT CONCLUÍDO COM SUCESSO!")
        sys.exit(0)
    else:
        logger.error("\n❌ BOT FALHOU!")
        sys.exit(1)
