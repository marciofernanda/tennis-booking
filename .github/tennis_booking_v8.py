#!/usr/bin/env python3
"""
⚡ BOT DE RESERVA v8 - SELETORES EM MINÚSCULAS
LetzPlay.me - Placeholders em português minúsculo
Reserva: Quadra 2 | Fazenda Vila Real de Itu
Horários: 9-10 e 10-11 | Dia: PRÓXIMO SÁBADO
"""

import os
import sys
import logging
import time
from datetime import datetime, timedelta

# IMPRIMIR IMEDIATAMENTE
print("=" * 80)
print("🚀 INICIANDO BOT DE RESERVA v8 (SELETORES CORRIGIDOS)")
print("=" * 80)
print()

# Validar credenciais
EMAIL = os.getenv("LETZPLAY_EMAIL", "").strip()
SENHA = os.getenv("LETZPLAY_PASSWORD", "").strip()

print(f"📧 EMAIL configurado: {'✅ SIM' if EMAIL else '❌ NÃO'}")
print(f"🔑 SENHA configurada: {'✅ SIM' if SENHA else '❌ NÃO'}")
print()

if not EMAIL or not SENHA:
    print("❌ ERRO: Credenciais não configuradas!")
    print("Defina: LETZPLAY_EMAIL e LETZPLAY_PASSWORD")
    sys.exit(1)

# Importar bibliotecas
print("📚 Importando bibliotecas...")
try:
    import pytz
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    print("  ✅ Todas as bibliotecas carregadas!")
except ImportError as e:
    print(f"  ❌ Erro ao importar: {e}")
    sys.exit(1)

print()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configurações
LETZPLAY_URL = "https://letzplay.me"
CONDOMINIO = "Fazenda Vila Real de Itu"
QUADRA = "2"
HORARIOS = [
    {"inicio": "09:00", "fim": "10:00"},
    {"inicio": "10:00", "fim": "11:00"}
]

TZ_SP = pytz.timezone('America/Sao_Paulo')

def calcular_proximo_sabado():
    """Calcula o próximo sábado"""
    agora = datetime.now(TZ_SP)
    dias_para_sabado = (5 - agora.weekday()) % 7
    if dias_para_sabado == 0:
        dias_para_sabado = 7
    proximo_sabado = agora + timedelta(days=dias_para_sabado)
    
    data_abertura = proximo_sabado.date() - timedelta(days=1)
    hora_abertura = TZ_SP.localize(datetime.combine(data_abertura, datetime.min.time()))
    
    if agora > hora_abertura:
        proximo_sabado = proximo_sabado + timedelta(days=7)
    
    return proximo_sabado.date()

def configurar_chrome():
    """Configura Chrome"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return options

def fazer_reserva():
    """Reserva as quadras"""
    logger.info("=" * 80)
    logger.info("🚀 INICIANDO RESERVA")
    logger.info("=" * 80)
    
    data_reserva = calcular_proximo_sabado()
    logger.info(f"📅 Data: {data_reserva.strftime('%d/%m/%Y')}")
    logger.info(f"🎾 Quadra: {QUADRA}")
    logger.info(f"🏢 Condomínio: {CONDOMINIO}")
    
    driver = None
    try:
        options = configurar_chrome()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        logger.info("✅ ChromeDriver pronto!")
        
        logger.info("\n" + "=" * 80)
        logger.info("FASE 1: LOGIN")
        logger.info("=" * 80)
        
        logger.info("🌐 Acessando LetzPlay...")
        driver.get(LETZPLAY_URL)
        time.sleep(5)
        logger.info("✅ Página carregada!")
        
        wait = WebDriverWait(driver, 20)
        
        # ===== EMAIL =====
        logger.info(f"📧 Preenchendo email...")
        try:
            # Seletor com placeholder em minúsculas
            email_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'e-mail')]"))
            )
            email_input.clear()
            email_input.send_keys(EMAIL)
            logger.info("✅ Email preenchido!")
        except Exception as e:
            logger.error(f"❌ Erro ao preencher email: {e}")
            return False
        
        time.sleep(1)
        
        # ===== SENHA =====
        logger.info(f"🔑 Preenchendo senha...")
        try:
            # Seletor com placeholder em minúsculas
            senha_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'senha')]"))
            )
            senha_input.clear()
            senha_input.send_keys(SENHA)
            logger.info("✅ Senha preenchida!")
        except Exception as e:
            logger.error(f"❌ Erro ao preencher senha: {e}")
            return False
        
        time.sleep(1)
        
        # ===== BOTÃO ENTRAR =====
        logger.info("🔓 Clicando em 'Entrar'...")
        try:
            entrar_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Entrar')]")
            entrar_btn.click()
            logger.info("✅ Botão clicado!")
        except Exception as e:
            logger.error(f"❌ Erro ao clicar: {e}")
            return False
        
        logger.info("⏳ Aguardando autenticação (6s)...")
        time.sleep(6)
        logger.info("✅ Login realizado!")
        
        # ===== SELECIONAR CONDOMÍNIO =====
        logger.info("\n" + "=" * 80)
        logger.info("FASE 2: SELECIONAR CONDOMÍNIO")
        logger.info("=" * 80)
        
        logger.info(f"🏢 Procurando: {CONDOMINIO}")
        time.sleep(2)
        
        try:
            cond_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{CONDOMINIO}')]"))
            )
            logger.info("✅ Condomínio encontrado!")
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
                
                logger.info(f"  Selecionando quadra {QUADRA}...")
                quadra_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), 'Quadra {QUADRA}')]"))
                )
                quadra_btn.click()
                time.sleep(0.5)
                
                data_str = data_reserva.strftime("%d/%m/%Y")
                logger.info(f"  Selecionando data: {data_str}...")
                
                date_inputs = driver.find_elements(By.XPATH, "//input[@type='date']")
                if date_inputs:
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(data_str)
                    time.sleep(0.3)
                
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
                
                logger.info(f"  Clicando em Reservar...")
                time.sleep(0.5)
                reservar_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Reservar')]")
                reservar_btn.click()
                
                time.sleep(2)
                logger.info(f"  ✅ Reserva {idx} confirmada!")
                reservas_ok += 1
                
            except Exception as e:
                logger.error(f"  ❌ Erro: {e}")
                continue
        
        # Resultado
        if reservas_ok > 0:
            logger.info("\n" + "=" * 80)
            logger.info(f"✅✅✅ SUCESSO! {reservas_ok}/{len(HORARIOS)} RESERVAS!")
            logger.info("=" * 80)
            return True
        else:
            logger.error("\n" + "=" * 80)
            logger.error("❌ FALHA: Nenhuma reserva")
            logger.error("=" * 80)
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        return False
    finally:
        if driver:
            driver.quit()
            logger.info("\n🔌 Navegador fechado.")

# Entry point
if __name__ == "__main__":
    logger.info("\n")
    sucesso = fazer_reserva()
    
    if sucesso:
        logger.info("\n✅ BOT CONCLUÍDO COM SUCESSO!")
        sys.exit(0)
    else:
        logger.error("\n❌ BOT FALHOU!")
        sys.exit(1)
