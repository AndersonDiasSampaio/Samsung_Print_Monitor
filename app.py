from flask import Flask, render_template, request, jsonify
from pysnmp.hlapi import *
import re
import json
import os

app = Flask(__name__)

# Arquivo para armazenar as impressoras
PRINTERS_FILE = 'printers.json'

# OIDs para Samsung
OIDS = {
    "Nome": "1.3.6.1.2.1.1.5.0",  # Nome do sistema
    "Modelo": "1.3.6.1.2.1.25.3.2.1.3.1",  # Modelo da impressora
    "Páginas Impressas": "1.3.6.1.4.1.236.11.5.11.53.61.5.2.1.14.1.1",  # Contador de páginas
    "Nível de Toner": "1.3.6.1.4.1.236.11.5.1.1.3.22.0",  # Nível do toner
    "Descrição": "1.3.6.1.2.1.1.1.0",  # Descrição do sistema
    "Localização": "1.3.6.1.2.1.1.6.0",  # Localização
    "Número de Série": "1.3.6.1.2.1.43.9.2.1.8.1.1",  # Número de série
    "Firmware": "1.3.6.1.2.1.43.9.2.1.9.1.1",  # Versão do firmware
    "Status": "1.3.6.1.2.1.43.10.2.1.4.1.1",  # Status da impressora
    "Estado de Erro": "1.3.6.1.2.1.43.10.2.1.4.1.2"  # Estado de erro
}

def load_printers():
    if os.path.exists(PRINTERS_FILE):
        with open(PRINTERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_printers(printers):
    with open(PRINTERS_FILE, 'w') as f:
        json.dump(printers, f, indent=4)

def get_printer_info(ip, community):
    try:
        result = {}
        print("\n=== INÍCIO DA CONSULTA SNMP ===")
        print(f"IP: {ip}")
        print(f"Community: {community}")
        print("==============================\n")
        
        for key, oid in OIDS.items():
            print(f"\nTentando OID: {oid}")
            print(f"Descrição: {key}")
            
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                      CommunityData(community),
                      UdpTransportTarget((ip, 161)),
                      ContextData(),
                      ObjectType(ObjectIdentity(oid)))
            )

            if errorIndication:
                print(f"❌ Erro ao obter {key}: {errorIndication}")
                continue
            elif errorStatus:
                print(f"❌ Erro SNMP ao obter {key}: {errorStatus.prettyPrint()}")
                continue
            else:
                for varBind in varBinds:
                    result[key] = str(varBind[1])
                    print(f"✅ Valor obtido: {varBind[1]}")
                    print(f"📝 OID que originou: {oid}")
                    print(f"🔍 Descrição do OID: {key}")

        # Tenta usar os valores Samsung se os padrões não funcionarem
        if not result.get("Modelo") and result.get("Modelo Samsung"):
            result["Modelo"] = result["Modelo Samsung"]
        if not result.get("Número de Série") and result.get("Número de Série Samsung"):
            result["Número de Série"] = result["Número de Série Samsung"]
        if not result.get("Status") and result.get("Status Samsung"):
            result["Status"] = result["Status Samsung"]
        if not result.get("Páginas Impressas") and result.get("Páginas Impressas Samsung"):
            result["Páginas Impressas"] = result["Páginas Impressas Samsung"]
        if not result.get("Nível de Toner") and result.get("Nível de Toner Samsung"):
            result["Nível de Toner"] = result["Nível de Toner Samsung"]
        if not result.get("Firmware") and result.get("Firmware Samsung"):
            result["Firmware"] = result["Firmware Samsung"]

        print("\n=== RESUMO DOS VALORES OBTIDOS ===")
        for key, value in result.items():
            print(f"{key}: {value}")
        print("================================\n")

        return result

    except Exception as e:
        print(f"\n❌ Erro geral: {str(e)}")
        return {'Erro': str(e)}

@app.route('/')
def index():
    printers = load_printers()
    return render_template('index.html', printers=printers)

@app.route('/add_printer', methods=['POST'])
def add_printer():
    ip = request.form.get('ip')
    community = request.form.get('community', 'public')
    name = request.form.get('name', f'Impressora {ip}')

    # Validação básica do IP
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        return jsonify({'Erro': 'Endereço IP inválido'})

    printers = load_printers()
    
    # Verifica se o IP já existe
    if any(p['ip'] == ip for p in printers):
        return jsonify({'Erro': 'Impressora já cadastrada'})

    # Adiciona nova impressora
    printers.append({
        'ip': ip,
        'community': community,
        'name': name
    })
    
    save_printers(printers)
    return jsonify({'ip': ip, 'community': community, 'name': name})

@app.route('/remove_printer', methods=['POST'])
def remove_printer():
    ip = request.form.get('ip')
    printers = load_printers()
    
    # Remove a impressora pelo IP
    printers = [p for p in printers if p['ip'] != ip]
    save_printers(printers)
    
    return jsonify({'Sucesso': 'Impressora removida com sucesso'})

@app.route('/get_printer_status', methods=['POST'])
def get_printer_status():
    ip = request.form.get('ip')
    community = request.form.get('community', 'public')

    # Validação básica do IP
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        return jsonify({'Erro': 'Endereço IP inválido'})

    info = get_printer_info(ip, community)
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True) 