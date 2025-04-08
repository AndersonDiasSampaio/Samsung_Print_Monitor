from pysnmp.hlapi import *
import time

# Configurações da impressora
PRINTER_IP = "10.36.150.97"  # IP da impressora
COMMUNITY = "public"  # Community string padrão

# OIDs específicos para Samsung M4020
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

def get_printer_info():
    try:
        print(f"Tentando conectar à impressora Samsung M4020 {PRINTER_IP}")

        # Obtém informações específicas
        print("\nObtendo informações da impressora...")
        for name, oid in OIDS.items():
            try:
                errorIndication, errorStatus, errorIndex, varBinds = next(
                    getCmd(SnmpEngine(),
                          CommunityData(COMMUNITY),
                          UdpTransportTarget((PRINTER_IP, 161)),
                          ContextData(),
                          ObjectType(ObjectIdentity(oid)))
                )

                if errorIndication:
                    print(f"Erro ao obter {name}: {errorIndication}")
                elif errorStatus:
                    print(f"Erro ao obter {name}: {errorStatus}")
                else:
                    for varBind in varBinds:
                        print(f"{name}: {varBind[1]}")
            except Exception as e:
                print(f"Erro ao obter {name}: {str(e)}")
            time.sleep(0.5)

        print("\nConsulta finalizada")

    except Exception as e:
        print(f"Erro geral ao acessar a impressora: {str(e)}")

if __name__ == "__main__":
    get_printer_info()