#!/usr/bin/env python3
"""
🧪 Script de teste local - valida setup antes do ataque real
"""

import os
import sys
import requests
import json
from datetime import datetime
import pytz

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{RESET}\n")

def print_ok(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warn(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def teste_credenciais():
    """Valida se credenciais estão configuradas"""
    print_header("1️⃣  TESTE: Credenciais")
    
    email = os.getenv("LETZPLAY_EMAIL", "").strip()
    senha = os.getenv("LETZPLAY_PASSWORD", "").strip()
    
    if not email:
        print_error("LETZPLAY_EMAIL não configurado")
        return False
    
    if not senha:
        print_error("LETZPLAY_PASSWORD não configurado")
        return False
    
    print_ok(f"Email: {email}")
    print_ok(f"Senha: {'*' * len(senha)}")
    return True

def teste_dependencias():
    """Valida se dependências estão instaladas"""
    print_header("2️⃣  TESTE: Dependências Python")
    
    deps = {
        'selenium': 'Selenium',
        'requests': 'Requests',
        'pytz': 'PyTZ'
    }
    
    todas_ok = True
    for module, name in deps.items():
        try:
            __import__(module)
            print_ok(f"{name} instalado")
        except ImportError:
            print_error(f"{name} NÃO instalado")
            print_info(f"  Instale: pip install {module}")
            todas_ok = False
    
    return todas_ok

def teste_conexao_api():
    """Testa conectividade com LetzPlay.me"""
    print_header("3️⃣  TESTE: Conexão API")
    
    try:
        response = requests.get(
            "https://letzplay.me",
            timeout=5
        )
        
        if response.status_code == 200:
            print_ok("LetzPlay.me está online")
            return True
        else:
            print_warn(f"Status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Timeout ao acessar LetzPlay.me")
        return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

def teste_timezone():
    """Valida timezone e calcula próxima abertura"""
    print_header("4️⃣  TESTE: Timezone e Datas")
    
    TZ_SP = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(TZ_SP)
    
    print_info(f"Hora atual (São Paulo): {agora.strftime('%A %d/%m/%Y %H:%M:%S')}")
    
    # Calcular próximo sábado
    dias_para_sabado = (5 - agora.weekday()) % 7
    if dias_para_sabado == 0:
        dias_para_sabado = 7
    
    from datetime import timedelta
    proximo_sabado = agora + timedelta(days=dias_para_sabado)
    
    print_ok(f"Próximo sábado: {proximo_sabado.strftime('%A %d/%m/%Y')}")
    
    # Abertura
    data_abertura = proximo_sabado.date() - timedelta(days=1)
    hora_abertura = TZ_SP.localize(datetime.combine(data_abertura, datetime.min.time()))
    
    print_ok(f"Abertura: {hora_abertura.strftime('%A %d/%m/%Y às %H:%M:%S')}")
    
    # Quanto falta
    delta = hora_abertura - agora
    if delta.total_seconds() > 0:
        horas = int(delta.total_seconds()) // 3600
        minutos = (int(delta.total_seconds()) % 3600) // 60
        print_info(f"Faltam: {horas}h {minutos}m")
    else:
        print_warn("Abertura já passou!")
    
    return True

def teste_login_api():
    """Tenta fazer login na API"""
    print_header("5️⃣  TESTE: Login na API")
    
    email = os.getenv("LETZPLAY_EMAIL", "").strip()
    senha = os.getenv("LETZPLAY_PASSWORD", "").strip()
    
    if not email or not senha:
        print_error("Credenciais não disponíveis")
        return False
    
    try:
        session = requests.Session()
        response = session.post(
            "https://letzplay.me/api/auth/login",
            json={"email": email, "password": senha},
            timeout=5
        )
        
        if response.status_code == 200:
            print_ok("Login bem-sucedido na API!")
            data = response.json()
            if data.get('token') or data.get('access_token'):
                print_ok("Token obtido com sucesso")
                return True
        else:
            print_error(f"Login falhou: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Erro de conexão")
        return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

def main():
    print(f"\n{BLUE}{'='*70}")
    print(f"🧪 TESTE DE CONFIGURAÇÃO - ATAQUE DE RESERVA")
    print(f"{'='*70}{RESET}\n")
    
    testes = [
        ("Credenciais", teste_credenciais),
        ("Dependências", teste_dependencias),
        ("Conexão API", teste_conexao_api),
        ("Timezone/Datas", teste_timezone),
        ("Login API", teste_login_api),
    ]
    
    resultados = []
    
    for nome, teste_func in testes:
        try:
            resultado = teste_func()
            resultados.append((nome, resultado))
        except Exception as e:
            print_error(f"Erro ao executar teste: {e}")
            resultados.append((nome, False))
    
    # Resumo
    print_header("📊 RESUMO")
    
    total = len(resultados)
    passes = sum(1 for _, r in resultados if r)
    
    for nome, resultado in resultados:
        status = f"{GREEN}✅ PASSOU{RESET}" if resultado else f"{RED}❌ FALHOU{RESET}"
        print(f"  {nome:.<50} {status}")
    
    print(f"\n  {BLUE}Total: {passes}/{total}{RESET}")
    
    if passes == total:
        print(f"\n{GREEN}{'='*70}")
        print("✅ TUDO OK! Sistema pronto para o ataque")
        print(f"{'='*70}{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{'='*70}")
        print("❌ Alguns testes falharam. Veja acima e corrija.")
        print(f"{'='*70}{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
