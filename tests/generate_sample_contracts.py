# -*- coding: utf-8 -*-
"""
Generador de PDFs de contratos de ejemplo.
Crea 9 contratos con contenido realista y extenso.
"""

from fpdf import FPDF
from pathlib import Path
from datetime import datetime, timedelta
import random

OUTPUT_DIR = Path(__file__).parent / "data" / "contracts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Fecha base para cálculos (20 de enero de 2026)
TODAY = datetime(2026, 1, 20)


class ContractPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header_section(self, title, expediente):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, "=" * 70, ln=True, align="C")
        self.cell(0, 10, title, ln=True, align="C")
        self.cell(0, 8, "=" * 70, ln=True, align="C")
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"EXPEDIENTE: {expediente}", ln=True)
        self.ln(5)
        
    def section_title(self, title):
        self.ln(5)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"--- {title} ---", ln=True)
        self.ln(2)
        self.set_font("Helvetica", "", 10)
        
    def add_field(self, label, value):
        self.set_font("Helvetica", "B", 10)
        self.multi_cell(0, 6, f"{label}: ", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, str(value))
        self.ln(1)
        
    def add_paragraph(self, text):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(2)


def format_date(dt):
    return dt.strftime("%d/%m/%Y")


def format_money(amount):
    return f"{amount:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", ".")


# Definición de los 9 contratos con escenarios específicos
CONTRACTS = [
    {
        "id": "CON_2024_001",
        "tipo": "Suministro",
        "titulo": "CONTRATO DE SUMINISTRO DE VEHICULOS BLINDADOS",
        "descripcion": "Suministro Vehiculos Blindados",
        "contratante": "Ministerio de Defensa - Direccion General de Armamento y Material",
        "contratista": "DefenseTech Solutions S.L.",
        "cif": "B-12345678",
        "objeto": "Suministro de 15 vehiculos blindados tipo VAMTAC ST5 4x4 con especificaciones tecnicas segun STANAG 4569 Nivel 3, incluyendo sistemas de comunicaciones integrados, blindaje adicional ceramico y kits de supervivencia para tripulacion.",
        "fecha_firma": TODAY - timedelta(days=300),
        "fecha_inicio": TODAY - timedelta(days=290),
        "fecha_fin": TODAY + timedelta(days=9),  # ALERTA CRITICA: vence en 9 dias
        "importe": 2450000.00,
        "aval_importe": 50000.00,
        "aval_entidad": "Banco Santander",
        "aval_numero": "AV-2024-5678",
        "aval_vencimiento": TODAY + timedelta(days=30),
        "permite_revision": False,
        "confidencialidad": True,
        "nivel_seguridad": "DIFUSION LIMITADA",
        "hitos": [
            ("Entrega Lote 1 (5 vehiculos)", TODAY - timedelta(days=100), True),
            ("Entrega Lote 2 (5 vehiculos)", TODAY - timedelta(days=30), True),
            ("Entrega Lote 3 (5 vehiculos)", TODAY + timedelta(days=5), False),
        ],
        "nsn": ["NSN-1234567890123", "NSN-9876543210987", "NSN-5555444433333"],
        "normas": ["STANAG 4569", "ISO 9001:2015", "ISO 14001:2015", "AQAP-2110"],
        "penalizacion": "0,5% del importe por semana de retraso",
        "variacion": "Permitida variacion +/- 10%",
        "subcontratacion": "Requiere autorizacion previa del organo de contratacion",
    },
    {
        "id": "CON_2024_002",
        "tipo": "Servicios",
        "titulo": "CONTRATO DE MANTENIMIENTO DE SISTEMAS DE ARMAMENTO",
        "descripcion": "Mantenimiento Armamento",
        "contratante": "Ejercito de Tierra - Mando de Apoyo Logistico",
        "contratista": "Sistemas Integrados de Defensa S.A.",
        "cif": "A-87654321",
        "objeto": "Servicio integral de mantenimiento preventivo y correctivo de sistemas de armamento ligero y pesado, incluyendo calibracion, reparacion y suministro de repuestos originales para una flota de 500 unidades distribuidas en 12 acuartelamientos.",
        "fecha_firma": TODAY - timedelta(days=400),
        "fecha_inicio": TODAY - timedelta(days=380),
        "fecha_fin": TODAY + timedelta(days=200),
        "importe": 1875000.00,
        "aval_importe": 37500.00,
        "aval_entidad": "CaixaBank",
        "aval_numero": "AV-2024-1234",
        "aval_vencimiento": TODAY + timedelta(days=8),  # ALERTA CRITICA: aval vence en 8 dias
        "permite_revision": True,
        "confidencialidad": True,
        "nivel_seguridad": "CONFIDENCIAL",
        "hitos": [
            ("Revision trimestral Q1", TODAY - timedelta(days=280), True),
            ("Revision trimestral Q2", TODAY - timedelta(days=190), True),
            ("Revision trimestral Q3", TODAY - timedelta(days=100), True),
            ("Revision trimestral Q4", TODAY - timedelta(days=10), True),
        ],
        "nsn": ["NSN-2222333344445", "NSN-6666777788889"],
        "normas": ["STANAG 4107", "ISO 9001:2015", "PECAL 2110"],
        "penalizacion": "1% del importe mensual por cada dia de indisponibilidad superior al SLA",
        "variacion": "No permitida",
        "subcontratacion": "Prohibida para actividades nucleares del contrato",
    },
    {
        "id": "LIC_2024_003",
        "tipo": "Suministro",
        "titulo": "CONTRATO DE SUMINISTRO DE UNIFORMIDAD Y EQUIPAMIENTO",
        "descripcion": "Uniformidad Ejercito",
        "contratante": "Ministerio de Defensa - Subdireccion General de Adquisiciones de Armamento",
        "contratista": "Textiles Militares Espanoles S.A.",
        "cif": "A-11223344",
        "objeto": "Suministro de uniformes de campana tipo pixelado boscoso, equipos de proteccion individual incluyendo chalecos antibala nivel IIIA, cascos balísticos y mochilas tacticas de combate para 5.000 efectivos.",
        "fecha_firma": TODAY - timedelta(days=180),
        "fecha_inicio": TODAY - timedelta(days=170),
        "fecha_fin": TODAY + timedelta(days=26),  # ALERTA MEDIA: vence en 26 dias
        "importe": 3200000.00,
        "aval_importe": 64000.00,
        "aval_entidad": "BBVA",
        "aval_numero": "AV-2024-9876",
        "aval_vencimiento": TODAY + timedelta(days=60),
        "permite_revision": True,
        "confidencialidad": False,
        "nivel_seguridad": "SIN CLASIFICAR",
        "hitos": [
            ("Entrega uniformes Fase 1", TODAY - timedelta(days=90), True),
            ("Entrega chalecos", TODAY - timedelta(days=45), True),
            ("Entrega cascos y mochilas", TODAY + timedelta(days=20), False),
        ],
        "nsn": ["NSN-8888999900001", "NSN-8888999900002", "NSN-8888999900003"],
        "normas": ["UNE-EN 1063", "NIJ Standard 0101.06", "ISO 9001:2015"],
        "penalizacion": "0,3% del importe por cada dia de retraso en entregas parciales",
        "variacion": "Permitida variacion +/- 15%",
        "subcontratacion": "Permitida hasta un 30% del importe",
    },
    {
        "id": "CON_2024_004",
        "tipo": "Servicios",
        "titulo": "CONTRATO DE SERVICIOS DE CIBERSEGURIDAD",
        "descripcion": "Ciberseguridad Infraestructuras",
        "contratante": "Centro de Sistemas y Tecnologias de la Informacion y las Comunicaciones (CESTIC)",
        "contratista": "CyberDefense Iberia S.L.",
        "cif": "B-55667788",
        "objeto": "Prestacion de servicios de ciberseguridad incluyendo monitorizacion 24x7 de redes clasificadas, respuesta a incidentes, analisis forense digital, pentesting trimestral y formacion continua del personal.",
        "fecha_firma": TODAY - timedelta(days=500),
        "fecha_inicio": TODAY - timedelta(days=480),
        "fecha_fin": TODAY + timedelta(days=400),
        "importe": 4500000.00,
        "aval_importe": 90000.00,
        "aval_entidad": "Bankinter",
        "aval_numero": "AV-2023-4567",
        "aval_vencimiento": TODAY + timedelta(days=450),
        "permite_revision": False,  # ALERTA BAJA: sin revision de precios
        "confidencialidad": True,
        "nivel_seguridad": "SECRETO",
        "hitos": [
            ("Despliegue SOC", TODAY - timedelta(days=400), True),
            ("Certificacion ISO 27001", TODAY - timedelta(days=300), True),
            ("Auditoria anual", TODAY + timedelta(days=100), False),
        ],
        "nsn": [],
        "normas": ["ISO 27001:2022", "ENS Alto", "NIST CSF", "CCN-STIC"],
        "penalizacion": "5.000 EUR por cada hora de indisponibilidad del SOC",
        "variacion": "No permitida",
        "subcontratacion": "Prohibida absolutamente por razones de seguridad",
    },
    {
        "id": "CON_2024_005",
        "tipo": "Suministro",
        "titulo": "CONTRATO DE SUMINISTRO DE MUNICION DE INSTRUCCION",
        "descripcion": "Municion Instruccion",
        "contratante": "Ejercito de Tierra - Academia General Militar",
        "contratista": "Explosivos Reunidos S.A.",
        "cif": "A-99887766",
        "objeto": "Suministro de municion de instruccion calibres 5.56x45mm, 7.62x51mm y 9x19mm para ejercicios de tiro de formacion y adiestramiento en campos de tiro militares. Incluye transporte especializado y certificacion de lotes.",
        "fecha_firma": TODAY - timedelta(days=200),
        "fecha_inicio": TODAY - timedelta(days=190),
        "fecha_fin": TODAY + timedelta(days=150),
        "importe": 890000.00,
        "aval_importe": 17800.00,
        "aval_entidad": "Banco Sabadell",
        "aval_numero": "AV-2024-7777",
        "aval_vencimiento": TODAY + timedelta(days=180),
        "permite_revision": True,
        "confidencialidad": True,  # ALERTA MEDIA: requiere confidencialidad
        "nivel_seguridad": "RESERVADO",
        "hitos": [
            ("Entrega primer lote 5.56mm", TODAY - timedelta(days=120), True),
            ("Entrega lote 7.62mm", TODAY - timedelta(days=60), True),
            ("Entrega lote 9mm", TODAY + timedelta(days=10), False),  # ALERTA CRITICA: hito en 10 dias
        ],
        "nsn": ["NSN-1305012345678", "NSN-1305087654321", "NSN-1305011112222"],
        "normas": ["STANAG 4172", "STANAG 4090", "RD 130/2017"],
        "penalizacion": "Rechazo del lote completo si no cumple especificaciones balisticas",
        "variacion": "Permitida variacion +/- 5%",
        "subcontratacion": "No permitida",
    },
    {
        "id": "SUM_2024_006",
        "tipo": "Suministro",
        "titulo": "CONTRATO DE SUMINISTRO DE RACIONES DE COMBATE",
        "descripcion": "Raciones Combate Individual",
        "contratante": "Ministerio de Defensa - Intendencia General",
        "contratista": "Alimentacion Tactica S.L.",
        "cif": "B-44556677",
        "objeto": "Suministro de 50.000 raciones individuales de combate (RIC) con menu variado de 24 horas, incluyendo calentadores sin llama, accesorios desechables y embalaje apto para lanzamiento aereo.",
        "fecha_firma": TODAY - timedelta(days=150),
        "fecha_inicio": TODAY - timedelta(days=140),
        "fecha_fin": TODAY + timedelta(days=300),
        "importe": 1250000.00,
        "aval_importe": 25000.00,
        "aval_entidad": "Ibercaja",
        "aval_numero": "AV-2024-3333",
        "aval_vencimiento": TODAY + timedelta(days=330),
        "permite_revision": True,
        "confidencialidad": False,
        "nivel_seguridad": "SIN CLASIFICAR",
        "hitos": [
            ("Entrega 10.000 raciones", TODAY - timedelta(days=80), True),
            ("Entrega 20.000 raciones", TODAY - timedelta(days=20), True),
            ("Entrega 20.000 raciones final", TODAY + timedelta(days=60), False),
        ],
        "nsn": ["NSN-8970015566778"],
        "normas": ["STANAG 2937", "Reglamento CE 852/2004", "ISO 22000"],
        "penalizacion": "Retirada inmediata de lotes con defectos de calidad alimentaria",
        "variacion": "Permitida variacion +/- 20%",
        "subcontratacion": "Permitida para componentes especificos aprobados",
    },
    {
        "id": "CON_2024_007",
        "tipo": "Obras",
        "titulo": "CONTRATO DE OBRAS DE ACONDICIONAMIENTO DE ACUARTELAMIENTO",
        "descripcion": "Obras Acuartelamiento Zaragoza",
        "contratante": "Infraestructura y Servicios del Ministerio de Defensa (INVIED)",
        "contratista": "Construcciones Militares Reunidas S.A.",
        "cif": "A-33221100",
        "objeto": "Ejecucion de obras de acondicionamiento integral del Acuartelamiento General Queipo de Llano incluyendo reforma de alojamientos, mejora de eficiencia energetica, instalacion de energia solar fotovoltaica y adecuacion de instalaciones deportivas.",
        "fecha_firma": TODAY - timedelta(days=400),
        "fecha_inicio": TODAY - timedelta(days=380),
        "fecha_fin": TODAY + timedelta(days=500),
        "importe": 8750000.00,
        "aval_importe": 175000.00,
        "aval_entidad": "Caja Rural",
        "aval_numero": "AV-2023-8888",
        "aval_vencimiento": TODAY + timedelta(days=530),
        "permite_revision": True,
        "confidencialidad": False,
        "nivel_seguridad": "SIN CLASIFICAR",
        "hitos": [
            ("Fase 1: Demoliciones", TODAY - timedelta(days=300), True),
            ("Fase 2: Estructura", TODAY - timedelta(days=200), True),
            ("Fase 3: Instalaciones", TODAY - timedelta(days=50), True),
            ("Fase 4: Acabados", TODAY + timedelta(days=200), False),
            ("Recepcion provisional", TODAY + timedelta(days=480), False),
        ],
        "nsn": [],
        "normas": ["CTE 2019", "RITE", "REBT", "Normas INVIED"],
        "penalizacion": "0,1% del importe por cada dia natural de retraso",
        "variacion": "Permitida variacion +/- 10% segun art. 205 LCSP",
        "subcontratacion": "Permitida hasta un 60% del importe",
    },
    {
        "id": "SER_2024_008",
        "tipo": "Servicios",
        "titulo": "CONTRATO DE SERVICIOS DE TRANSPORTE ESTRATEGICO",
        "descripcion": "Transporte Estrategico",
        "contratante": "Estado Mayor de la Defensa - J4 Logistica",
        "contratista": "Logistica Militar Internacional S.A.",
        "cif": "A-77889900",
        "objeto": "Prestacion de servicios de transporte estrategico terrestre, maritimo y aereo de material militar y equipos sensibles, incluyendo vehiculos especiales, contenedores de seguridad y escolta armada cuando proceda.",
        "fecha_firma": TODAY - timedelta(days=600),
        "fecha_inicio": TODAY - timedelta(days=580),
        "fecha_fin": TODAY + timedelta(days=180),
        "importe": 5600000.00,
        "aval_importe": 112000.00,
        "aval_entidad": "Banco Santander",
        "aval_numero": "AV-2023-5555",
        "aval_vencimiento": TODAY + timedelta(days=210),
        "permite_revision": True,
        "confidencialidad": True,
        "nivel_seguridad": "DIFUSION LIMITADA",
        "hitos": [
            ("Renovacion flota transporte", TODAY - timedelta(days=400), True),
            ("Certificacion ADR", TODAY - timedelta(days=200), True),
            ("Auditoria de seguridad", TODAY + timedelta(days=90), False),
        ],
        "nsn": [],
        "normas": ["ADR 2023", "IMDG", "IATA DGR", "Normas OTAN AMovP-2"],
        "penalizacion": "10.000 EUR por cada incidencia de seguridad en transporte",
        "variacion": "Permitida variacion +/- 25% en funcion de operaciones",
        "subcontratacion": "Requiere autorizacion caso por caso",
    },
    {
        "id": "CON_2024_009",
        "tipo": "Suministro",
        "titulo": "CONTRATO DE SUMINISTRO DE SISTEMAS DE COMUNICACIONES TACTICAS",
        "descripcion": "Comunicaciones Tacticas",
        "contratante": "Ejercito del Aire y del Espacio - Mando de Combate",
        "contratista": "Electronica Aeroespacial de Defensa S.A.",
        "cif": "A-66554433",
        "objeto": "Suministro de 200 estaciones de radio tactica digital multibanda PR4G V3, incluyendo terminales portatiles, estaciones vehiculares, antenas direccionales y sistemas de cifrado con certificacion OTAN.",
        "fecha_firma": TODAY - timedelta(days=250),
        "fecha_inicio": TODAY - timedelta(days=240),
        "fecha_fin": TODAY + timedelta(days=400),
        "importe": 12500000.00,
        "aval_importe": 250000.00,
        "aval_entidad": "La Caixa",
        "aval_numero": "AV-2024-9999",
        "aval_vencimiento": TODAY + timedelta(days=430),
        "permite_revision": True,
        "confidencialidad": True,
        "nivel_seguridad": "SECRETO",
        "hitos": [
            ("Prototipo homologado", TODAY - timedelta(days=150), True),
            ("Produccion serie 1", TODAY - timedelta(days=50), True),
            ("Produccion serie 2", TODAY + timedelta(days=100), False),
            ("Integracion final", TODAY + timedelta(days=350), False),
        ],
        "nsn": ["NSN-5820123456789", "NSN-5820987654321"],
        "normas": ["STANAG 4591", "STANAG 4538", "MIL-STD-810G", "TEMPEST SDIP-27"],
        "penalizacion": "Rechazo de equipos que no superen pruebas de interoperabilidad",
        "variacion": "No permitida sin modificacion contractual",
        "subcontratacion": "Prohibida para componentes de cifrado",
    },
    # ==================== NUEVOS CONTRATOS (10-20) ====================
    {
        "id": "CON_2024_010",
        "tipo": "Servicios",
        "titulo": "CONTRATO DE SERVICIOS DE VIGILANCIA Y SEGURIDAD PRIVADA",
        "descripcion": "Vigilancia Instalaciones Militares",
        "contratante": "Ministerio de Defensa - Subdireccion General de Servicios Economicos",
        "contratista": "Securitas Defensa S.A.",
        "cif": "A-28011231",
        "objeto": "Prestacion de servicios de vigilancia armada y seguridad privada en instalaciones militares del Mando de Canarias, incluyendo control de accesos, rondas perimetrales, videovigilancia y respuesta ante incidentes.",
        "fecha_firma": TODAY - timedelta(days=120),
        "fecha_inicio": TODAY - timedelta(days=110),
        "fecha_fin": TODAY + timedelta(days=255),
        "importe": 2100000.00,
        "aval_importe": 42000.00,
        "aval_entidad": "Kutxabank",
        "aval_numero": "AV-2024-1010",
        "aval_vencimiento": TODAY + timedelta(days=285),
        "permite_revision": True,
        "confidencialidad": True,
        "nivel_seguridad": "CONFIDENCIAL",
        "hitos": [
            ("Inicio servicio Fase 1", TODAY - timedelta(days=100), True),
            ("Ampliacion a instalaciones adicionales", TODAY + timedelta(days=60), False),
        ],
        "nsn": [],
        "normas": ["UNE-EN ISO 18788", "Ley 5/2014 Seguridad Privada", "CCN-STIC"],
        "penalizacion": "2.000 EUR por cada incidencia grave de seguridad",
        "variacion": "Permitida hasta +20% por ampliacion de instalaciones",
        "subcontratacion": "No permitida",
    },
    {
        "id": "SUM_2024_011",
        "tipo": "Suministro",
        "titulo": "CONTRATO DE SUMINISTRO DE COMBUSTIBLES MILITARES",
        "descripcion": "Combustible Aviacion y Terrestre",
        "contratante": "Mando de Apoyo Logistico del Ejercito del Aire",
        "contratista": "CEPSA Aviacion S.L.",
        "cif": "B-78945612",
        "objeto": "Suministro de combustible JP-8 para aeronaves militares y gasoleo A para vehiculos terrestres en las bases aereas de Torrejon, Zaragoza y Moron, incluyendo servicio de repostaje en pista.",
        "fecha_firma": TODAY - timedelta(days=90),
        "fecha_inicio": TODAY - timedelta(days=85),
        "fecha_fin": TODAY + timedelta(days=280),
        "importe": 6800000.00,
        "aval_importe": 136000.00,
        "aval_entidad": "Unicaja",
        "aval_numero": "AV-2024-1111",
        "aval_vencimiento": TODAY + timedelta(days=310),
        "permite_revision": True,
        "confidencialidad": False,
        "nivel_seguridad": "SIN CLASIFICAR",
        "hitos": [
            ("Inicio suministro Torrejon", TODAY - timedelta(days=80), True),
            ("Inicio suministro Zaragoza", TODAY - timedelta(days=60), True),
            ("Inicio suministro Moron", TODAY + timedelta(days=30), False),
        ],
        "nsn": ["NSN-9130001234567"],
        "normas": ["DEF STAN 91-91", "MIL-DTL-83133", "ASTM D1655"],
        "penalizacion": "Penalizacion por contaminacion: coste total de limpieza mas 50.000 EUR",
        "variacion": "Permitida +/- 30% segun consumo operativo",
        "subcontratacion": "Permitida para transporte",
    },
    {
        "id": "CON_2024_012",
        "tipo": "Obras",
        "titulo": "CONTRATO DE CONSTRUCCION DE CENTRO DE MANDO CONJUNTO",
        "descripcion": "Centro Mando Retamares",
        "contratante": "Estado Mayor de la Defensa - Infraestructuras",
        "contratista": "FCC Construccion S.A.",
        "cif": "A-28037224",
        "objeto": "Construccion de nuevo Centro de Mando y Control Conjunto en la Base de Retamares, incluyendo bunker subterraneo, sala de operaciones, sistemas redundantes de energia y comunicaciones satelitales.",
        "fecha_firma": TODAY - timedelta(days=300),
        "fecha_inicio": TODAY - timedelta(days=280),
        "fecha_fin": TODAY + timedelta(days=600),
        "importe": 28500000.00,
        "aval_importe": 570000.00,
        "aval_entidad": "Liberbank",
        "aval_numero": "AV-2023-1212",
        "aval_vencimiento": TODAY + timedelta(days=630),
        "permite_revision": True,
        "confidencialidad": True,
        "nivel_seguridad": "SECRETO",
        "hitos": [
            ("Excavacion bunker", TODAY - timedelta(days=200), True),
            ("Estructura principal", TODAY - timedelta(days=100), True),
            ("Instalaciones especiales", TODAY + timedelta(days=200), False),
            ("Equipamiento electronico", TODAY + timedelta(days=450), False),
        ],
        "nsn": [],
        "normas": ["CTE DB-SE", "Normas OTAN AC/135", "TEMPEST Level A"],
        "penalizacion": "0,05% del importe por dia natural de retraso",
        "variacion": "Modificaciones por Art. 242 LCSP hasta 20%",
        "subcontratacion": "Limitada a 40% - Requiere HPS para subcontratistas",
    },
    {
        "id": "SER_2024_013",
        "tipo": "Servicios",
        "titulo": "CONTRATO DE FORMACION TECNICA ESPECIALIZADA",
        "descripcion": "Formacion Sistemas Armas",
        "contratante": "Armada Espanola - Jefatura de Personal",
        "contratista": "Indra Sistemas de Defensa S.A.",
        "cif": "A-28599033",
        "objeto": "Imparticion de cursos de formacion tecnica en sistemas de combate AEGIS y radares SPY-1D para personal de la fragata F-110, incluyendo simuladores y practicas en mar.",
        "fecha_firma": TODAY - timedelta(days=60),
        "fecha_inicio": TODAY - timedelta(days=50),
        "fecha_fin": TODAY + timedelta(days=315),
        "importe": 1850000.00,
        "aval_importe": 37000.00,
        "aval_entidad": "Abanca",
        "aval_numero": "AV-2024-1313",
        "aval_vencimiento": TODAY + timedelta(days=345),
        "permite_revision": False,
        "confidencialidad": True,
        "nivel_seguridad": "DIFUSION LIMITADA",
        "hitos": [
            ("Curso basico Fase 1", TODAY - timedelta(days=20), True),
            ("Practicas simulador", TODAY + timedelta(days=90), False),
            ("Practicas embarcadas", TODAY + timedelta(days=250), False),
        ],
        "nsn": [],
        "normas": ["STANAG 6001", "Instrucciones DIVPRO"],
        "penalizacion": "Repeticion gratuita del curso si ratio aprobados < 80%",
        "variacion": "No permitida",
        "subcontratacion": "Prohibida",
    },
    {
        "id": "SUM_2024_014",
        "tipo": "Suministro",
        "titulo": "CONTRATO DE SUMINISTRO DE MATERIAL SANITARIO DE CAMPANA",
        "descripcion": "Material Sanitario Militar",
        "contratante": "Inspeccion General de Sanidad de la Defensa",
        "contratista": "Medline Industries Spain S.L.",
        "cif": "B-86543210",
        "objeto": "Suministro de equipamiento sanitario de campana incluyendo 50 botiquines tacticos IFAK, 10 camillas plegables, 5 unidades de soporte vital y material fungible para hospitales de campana ROL-2.",
        "fecha_firma": TODAY - timedelta(days=45),
        "fecha_inicio": TODAY - timedelta(days=40),
        "fecha_fin": TODAY + timedelta(days=120),
        "importe": 425000.00,
        "aval_importe": 8500.00,
        "aval_entidad": "Bankia",
        "aval_numero": "AV-2024-1414",
        "aval_vencimiento": TODAY + timedelta(days=150),
        "permite_revision": False,
        "confidencialidad": False,
        "nivel_seguridad": "SIN CLASIFICAR",
        "hitos": [
            ("Entrega botiquines IFAK", TODAY + timedelta(days=30), False),
            ("Entrega camillas y SVA", TODAY + timedelta(days=90), False),
        ],
        "nsn": ["NSN-6515123456789", "NSN-6530987654321"],
        "normas": ["MIL-STD-1472", "Directiva 93/42/CEE", "UNE-EN ISO 13485"],
        "penalizacion": "Rechazo de lotes no conformes con trazabilidad sanitaria",
        "variacion": "Permitida +/- 15%",
        "subcontratacion": "Permitida para logistica",
    },
    {
        "id": "SER_2024_015",
        "tipo": "Servicios",
        "titulo": "CONTRATO DE MANTENIMIENTO DE AERONAVES C-295",
        "descripcion": "Mantenimiento Flota C295",
        "contratante": "Ejercito del Aire - Mando Aereo de Combate",
        "contratista": "Airbus Defence and Space S.A.",
        "cif": "A-83854606",
        "objeto": "Servicio integral de mantenimiento programado y correctivo de la flota de 16 aeronaves C-295M, incluyendo inspecciones mayores, reparacion de estructuras y sistemas avionicos.",
        "fecha_firma": TODAY - timedelta(days=450),
        "fecha_inicio": TODAY - timedelta(days=430),
        "fecha_fin": TODAY + timedelta(days=480),
        "importe": 18200000.00,
        "aval_importe": 364000.00,
        "aval_entidad": "ING Bank",
        "aval_numero": "AV-2023-1515",
        "aval_vencimiento": TODAY + timedelta(days=510),
        "permite_revision": True,
        "confidencialidad": True,
        "nivel_seguridad": "RESERVADO",
        "hitos": [
            ("Inspeccion mayor AC001", TODAY - timedelta(days=300), True),
            ("Inspeccion mayor AC002", TODAY - timedelta(days=150), True),
            ("Inspeccion mayor AC003", TODAY + timedelta(days=100), False),
        ],
        "nsn": [],
        "normas": ["EASA Part 145", "MIL-HDBK-217", "ATA Spec 100"],
        "penalizacion": "50.000 EUR por cada dia de indisponibilidad de aeronave sobre SLA",
        "variacion": "No permitida salvo incremento de flota",
        "subcontratacion": "Limitada a talleres homologados EASA",
    },
    {
        "id": "CON_2024_016",
        "tipo": "Suministro",
        "titulo": "CONTRATO DE SUMINISTRO DE EQUIPOS DE VISION NOCTURNA",
        "descripcion": "Vision Nocturna Gen3",
        "contratante": "Mando de Operaciones Especiales (MOE)",
        "contratista": "Thales Espana GRP S.A.U.",
        "cif": "A-28130406",
        "objeto": "Suministro de 500 gafas de vision nocturna Gen3+ con montaje casco, 50 miras termicas para fusiles de precision y 20 camaras termicas portatiles para operaciones especiales.",
        "fecha_firma": TODAY - timedelta(days=180),
        "fecha_inicio": TODAY - timedelta(days=170),
        "fecha_fin": TODAY + timedelta(days=200),
        "importe": 4200000.00,
        "aval_importe": 84000.00,
        "aval_entidad": "Banco Santander",
        "aval_numero": "AV-2024-1616",
        "aval_vencimiento": TODAY + timedelta(days=540),
        "permite_revision": False,
        "confidencialidad": True,
        "nivel_seguridad": "SECRETO",
        "hitos": [
            ("Entrega gafas NVG Fase 1", TODAY - timedelta(days=80), True),
            ("Entrega miras termicas", TODAY + timedelta(days=30), False),
            ("Entrega camaras portatiles", TODAY + timedelta(days=150), False),
        ],
        "nsn": ["NSN-5855012345678", "NSN-5855098765432"],
        "normas": ["MIL-STD-810H", "MIL-I-49428", "STANAG 4694"],
        "penalizacion": "Devolucion del 100% si no supera pruebas operativas",
        "variacion": "No permitida",
        "subcontratacion": "Absolutamente prohibida - ITAR",
    },
    {
        "id": "LIC_2024_017",
        "tipo": "Suministro",
        "titulo": "CONTRATO DE SUMINISTRO DE VEHICULOS LOGISTICOS",
        "descripcion": "Camiones Logisticos IVECO",
        "contratante": "Mando de Apoyo Logistico del Ejercito de Tierra",
        "contratista": "IVECO Defence Vehicles S.p.A.",
        "cif": "IT-12345678901",
        "objeto": "Suministro de 80 camiones logisticos IVECO Trakker 6x6 con capacidad 15 toneladas, configuracion militar incluyendo blindaje cabina, sistemas GPS y predisposicion para grua.",
        "fecha_firma": TODAY - timedelta(days=220),
        "fecha_inicio": TODAY - timedelta(days=210),
        "fecha_fin": TODAY + timedelta(days=160),
        "importe": 9600000.00,
        "aval_importe": 192000.00,
        "aval_entidad": "CaixaBank",
        "aval_numero": "AV-2024-1717",
        "aval_vencimiento": TODAY + timedelta(days=580),
        "permite_revision": True,
        "confidencialidad": False,
        "nivel_seguridad": "SIN CLASIFICAR",
        "hitos": [
            ("Entrega lote 1 (30 uds)", TODAY - timedelta(days=100), True),
            ("Entrega lote 2 (30 uds)", TODAY - timedelta(days=30), True),
            ("Entrega lote 3 (20 uds)", TODAY + timedelta(days=120), False),
        ],
        "nsn": ["NSN-2320234567890"],
        "normas": ["STANAG 2021", "Directiva EuroIV", "VCA Type Approval"],
        "penalizacion": "1.500 EUR por vehiculo y dia de retraso",
        "variacion": "Permitida +/- 10%",
        "subcontratacion": "Permitida para adaptaciones finales",
    },
    {
        "id": "CON_2024_018",
        "tipo": "Obras",
        "titulo": "CONTRATO DE CONSTRUCCION DE HANGARES BASE AEREA",
        "descripcion": "Hangares Moron de la Frontera",
        "contratante": "Ejercito del Aire - Servicio de Infraestructura",
        "contratista": "Dragados S.A.",
        "cif": "A-28013390",
        "objeto": "Construccion de dos hangares de mantenimiento para aeronaves estrategicas en la Base Aerea de Moron, con capacidad para A400M, sistemas contraincendios y gruas puente de 20 toneladas.",
        "fecha_firma": TODAY - timedelta(days=350),
        "fecha_inicio": TODAY - timedelta(days=340),
        "fecha_fin": TODAY + timedelta(days=400),
        "importe": 15800000.00,
        "aval_importe": 316000.00,
        "aval_entidad": "BBVA",
        "aval_numero": "AV-2023-1818",
        "aval_vencimiento": TODAY + timedelta(days=430),
        "permite_revision": True,
        "confidencialidad": True,
        "nivel_seguridad": "CONFIDENCIAL",
        "hitos": [
            ("Cimentacion hangar 1", TODAY - timedelta(days=250), True),
            ("Estructura metalica hangar 1", TODAY - timedelta(days=150), True),
            ("Cimentacion hangar 2", TODAY - timedelta(days=100), True),
            ("Finalizacion hangares", TODAY + timedelta(days=350), False),
        ],
        "nsn": [],
        "normas": ["UFC 4-211-01", "CTE DB-SI", "NFPA 409"],
        "penalizacion": "0,08% del importe por dia de retraso",
        "variacion": "Permitida hasta 15%",
        "subcontratacion": "Permitida hasta 50%",
    },
    {
        "id": "SER_2024_019",
        "tipo": "Servicios",
        "titulo": "CONTRATO DE SERVICIOS DE COMUNICACIONES POR SATELITE",
        "descripcion": "SATCOM Operaciones",
        "contratante": "Estado Mayor de la Defensa - CIS",
        "contratista": "Hispasat S.A.",
        "cif": "A-78931648",
        "objeto": "Prestacion de servicios de comunicaciones satelitales militares mediante capacidad dedicada en satelites geoestacionarios, incluyendo terminales VSAT portatiles y apoyo 24x7 para operaciones.",
        "fecha_firma": TODAY - timedelta(days=400),
        "fecha_inicio": TODAY - timedelta(days=390),
        "fecha_fin": TODAY + timedelta(days=520),
        "importe": 7400000.00,
        "aval_importe": 148000.00,
        "aval_entidad": "Bankinter",
        "aval_numero": "AV-2023-1919",
        "aval_vencimiento": TODAY + timedelta(days=550),
        "permite_revision": False,
        "confidencialidad": True,
        "nivel_seguridad": "SECRETO",
        "hitos": [
            ("Despliegue inicial", TODAY - timedelta(days=350), True),
            ("Ampliacion capacidad", TODAY - timedelta(days=100), True),
            ("Renovacion equipos terminales", TODAY + timedelta(days=200), False),
        ],
        "nsn": [],
        "normas": ["MIL-STD-188-165", "STANAG 4206", "ITU Radio Regulations"],
        "penalizacion": "10.000 EUR por hora de indisponibilidad del servicio",
        "variacion": "Solo permitida por nuevas operaciones",
        "subcontratacion": "Requiere autorizacion de la ONS",
    },
    {
        "id": "CON_2024_020",
        "tipo": "Suministro",
        "titulo": "CONTRATO DE SUMINISTRO DE ARMAMENTO LIGERO",
        "descripcion": "Fusiles Asalto HK416",
        "contratante": "Direccion General de Armamento y Material (DGAM)",
        "contratista": "Heckler & Koch GmbH",
        "cif": "DE-812489300",
        "objeto": "Suministro de 5.000 fusiles de asalto HK416 A5 calibre 5.56x45mm OTAN con accesorios tacticos, incluyendo miras holograficas, linternas tacticas y silenciadores homologados.",
        "fecha_firma": TODAY - timedelta(days=280),
        "fecha_inicio": TODAY - timedelta(days=270),
        "fecha_fin": TODAY + timedelta(days=365),
        "importe": 11200000.00,
        "aval_importe": 224000.00,
        "aval_entidad": "Banco Sabadell",
        "aval_numero": "AV-2024-2020",
        "aval_vencimiento": TODAY + timedelta(days=700),
        "permite_revision": False,
        "confidencialidad": True,
        "nivel_seguridad": "RESERVADO",
        "hitos": [
            ("Homologacion prototipo", TODAY - timedelta(days=200), True),
            ("Entrega lote 1 (2000 uds)", TODAY - timedelta(days=80), True),
            ("Entrega lote 2 (2000 uds)", TODAY + timedelta(days=100), False),
            ("Entrega lote 3 (1000 uds)", TODAY + timedelta(days=300), False),
        ],
        "nsn": ["NSN-1005012345678"],
        "normas": ["STANAG 4694", "MIL-STD-1913", "NATO AEP-97"],
        "penalizacion": "Rechazo lote completo con penalizacion del 15% si no supera pruebas",
        "variacion": "No permitida",
        "subcontratacion": "Prohibida absolutamente",
    },
]


def generate_contract_pdf(contract):
    """Genera un PDF para un contrato."""
    pdf = ContractPDF()
    c = contract
    
    # Encabezado
    pdf.header_section(c["titulo"], c["id"])
    pdf.add_field("TIPO DE CONTRATO", c["tipo"])
    
    # Partes contratantes
    pdf.section_title("PARTES CONTRATANTES")
    pdf.add_field("Organo de Contratacion", c["contratante"])
    pdf.add_field("Contratista", c["contratista"])
    pdf.add_field("CIF/NIF Contratista", c["cif"])
    pdf.add_paragraph(f"El contratista declara cumplir con todos los requisitos de capacidad y solvencia exigidos "
                      f"en el pliego de clausulas administrativas particulares, no estando incurso en ninguna de "
                      f"las prohibiciones de contratar establecidas en el articulo 71 de la Ley 9/2017 de Contratos "
                      f"del Sector Publico.")
    
    # Objeto del contrato
    pdf.section_title("OBJETO DEL CONTRATO")
    pdf.add_paragraph(c["objeto"])
    pdf.add_paragraph("El presente contrato tiene caracter administrativo especial y se regira por las clausulas "
                      "contenidas en el mismo, por el Pliego de Clausulas Administrativas Particulares y el Pliego "
                      "de Prescripciones Tecnicas, y supletoriamente por la Ley 9/2017 de Contratos del Sector Publico "
                      "y demas normativa de aplicacion.")
    
    # Fechas relevantes
    pdf.section_title("FECHAS RELEVANTES")
    pdf.add_field("Fecha de firma", format_date(c["fecha_firma"]))
    pdf.add_field("Fecha de inicio de ejecucion", format_date(c["fecha_inicio"]))
    pdf.add_field("Fecha de finalizacion", format_date(c["fecha_fin"]))
    plazo = (c["fecha_fin"] - c["fecha_inicio"]).days
    pdf.add_field("Plazo de ejecucion", f"{plazo} dias naturales")
    
    for hito_nombre, hito_fecha, cumplido in c["hitos"]:
        estado = "(CUMPLIDO)" if cumplido else "(PENDIENTE)"
        pdf.add_field(hito_nombre, f"{format_date(hito_fecha)} {estado}")
    
    # Importe y condiciones economicas
    pdf.section_title("IMPORTE Y CONDICIONES ECONOMICAS")
    pdf.add_field("Importe total (IVA incluido)", format_money(c["importe"]))
    pdf.add_field("Base imponible", format_money(c["importe"] / 1.21))
    pdf.add_field("IVA (21%)", format_money(c["importe"] - c["importe"] / 1.21))
    pdf.add_field("Forma de pago", "Certificaciones mensuales contra factura conformada")
    revision = "SI - Segun formula polinomica del PCAP" if c["permite_revision"] else "NO PERMITIDA"
    pdf.add_field("Revision de precios", revision)
    pdf.add_paragraph("Los pagos se realizaran mediante transferencia bancaria en un plazo maximo de 30 dias "
                      "desde la conformidad de la factura por el organo de contratacion. El contratista debera "
                      "presentar factura electronica a traves del punto general de entrada de facturas electronicas "
                      "de la Administracion General del Estado (FACe).")
    
    # Garantias y avales
    pdf.section_title("GARANTIAS Y AVALES")
    pdf.add_field("Garantia definitiva", format_money(c["aval_importe"]))
    pdf.add_field("Porcentaje sobre importe", f"{(c['aval_importe'] / c['importe']) * 100:.1f}%")
    pdf.add_field("Tipo de garantia", "Aval bancario")
    pdf.add_field("Entidad avalista", c["aval_entidad"])
    pdf.add_field("Numero de aval", c["aval_numero"])
    pdf.add_field("Fecha de vencimiento del aval", format_date(c["aval_vencimiento"]))
    pdf.add_paragraph("La garantia debera mantenerse vigente hasta que se haya producido el vencimiento del plazo "
                      "de garantia y cumplido satisfactoriamente el contrato, o hasta que se declare la resolucion "
                      "de este sin culpa del contratista. En caso de proximo vencimiento del aval, el contratista "
                      "debera presentar renovacion con al menos 15 dias de antelacion.")
    
    # Codigos NSN
    if c["nsn"]:
        pdf.section_title("CODIGOS NATO STOCK NUMBER (NSN)")
        for nsn in c["nsn"]:
            pdf.add_paragraph(f"  * {nsn}")
        pdf.add_paragraph("Los articulos suministrados deberan identificarse con los codigos NSN asignados "
                          "segun el Sistema OTAN de Catalogacion. El contratista es responsable de solicitar "
                          "la asignacion de NSN para articulos nuevos a traves del SICAB.")
    
    # Normas aplicables
    pdf.section_title("NORMAS APLICABLES Y CERTIFICACIONES")
    for norma in c["normas"]:
        pdf.add_paragraph(f"  * {norma}")
    pdf.add_paragraph("El contratista debera acreditar el cumplimiento de las normas indicadas mediante "
                      "certificados vigentes emitidos por organismos de certificacion acreditados. La no "
                      "vigencia de cualquier certificacion requerida podra ser causa de resolucion del contrato.")
    
    # Clausulas especiales
    pdf.section_title("CLAUSULAS ESPECIALES")
    
    if c["confidencialidad"]:
        pdf.add_field("Clasificacion de seguridad", c["nivel_seguridad"])
        pdf.add_paragraph(f"CLAUSULA DE CONFIDENCIALIDAD: Todo el personal del contratista que participe en la "
                          f"ejecucion del contrato debera disponer de Habilitacion Personal de Seguridad (HPS) "
                          f"de grado {c['nivel_seguridad']} como minimo. El contratista debera disponer de "
                          f"Habilitacion de Seguridad de Empresa (HSEM) vigente expedida por la Oficina Nacional "
                          f"de Seguridad (ONS). La informacion clasificada se tratara conforme a la Ley 9/1968 de "
                          f"Secretos Oficiales y la normativa de proteccion de informacion clasificada de la OTAN.")
    else:
        pdf.add_field("Clasificacion de seguridad", "SIN CLASIFICAR")
    
    pdf.add_field("Penalizacion por incumplimiento", c["penalizacion"])
    pdf.add_field("Modificacion de cantidades", c["variacion"])
    pdf.add_field("Subcontratacion", c["subcontratacion"])
    
    # Obligaciones del contratista
    pdf.section_title("OBLIGACIONES DEL CONTRATISTA")
    pdf.add_paragraph("1. Ejecutar el contrato conforme a las condiciones establecidas en los pliegos.")
    pdf.add_paragraph("2. Comunicar cualquier incidencia que pueda afectar al cumplimiento del contrato.")
    pdf.add_paragraph("3. Mantener durante toda la ejecucion las condiciones de solvencia exigidas.")
    pdf.add_paragraph("4. Guardar sigilo sobre la informacion a la que tenga acceso.")
    pdf.add_paragraph("5. Abonar las indemnizaciones por danos a terceros que se produzcan.")
    pdf.add_paragraph("6. Facilitar las inspecciones y auditorias del organo de contratacion.")
    
    # Facultades de la Administracion
    pdf.section_title("FACULTADES DE LA ADMINISTRACION")
    pdf.add_paragraph("La Administracion ostenta las siguientes prerrogativas en relacion con el contrato:")
    pdf.add_paragraph("a) Interpretacion del contrato.")
    pdf.add_paragraph("b) Resolucion de las dudas que ofrezca su cumplimiento.")
    pdf.add_paragraph("c) Modificacion del contrato por razones de interes publico.")
    pdf.add_paragraph("d) Acordar la resolucion del contrato y determinar sus efectos.")
    pdf.add_paragraph("e) Establecer penalidades por incumplimiento.")
    
    # Resolucion del contrato
    pdf.section_title("CAUSAS DE RESOLUCION")
    pdf.add_paragraph("Seran causas de resolucion del contrato, ademas de las previstas en la LCSP:")
    pdf.add_paragraph("1. El incumplimiento de las obligaciones esenciales del contrato.")
    pdf.add_paragraph("2. La demora superior a 30 dias en el inicio de la ejecucion.")
    pdf.add_paragraph("3. El incumplimiento reiterado de los plazos parciales.")
    pdf.add_paragraph("4. La perdida de la habilitacion de seguridad del contratista.")
    pdf.add_paragraph("5. La cesion o subcontratacion no autorizada.")
    pdf.add_paragraph("6. La declaracion de concurso o insolvencia del contratista.")
    
    # Jurisdiccion
    pdf.section_title("JURISDICCION COMPETENTE")
    pdf.add_paragraph("El orden jurisdiccional contencioso-administrativo sera el competente para resolver "
                      "las controversias que surjan entre las partes en relacion con la preparacion, "
                      "adjudicacion, efectos, cumplimiento y extincion del presente contrato.")
    pdf.add_paragraph("Con sometimiento expreso a los Juzgados y Tribunales de Madrid capital.")
    
    # Firma
    pdf.section_title("FIRMAS")
    pdf.ln(10)
    pdf.add_paragraph(f"En Madrid, a {format_date(c['fecha_firma'])}")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 7, "Por el Organo de Contratacion", align="C")
    pdf.cell(95, 7, "Por el Contratista", align="C")
    pdf.ln(25)
    pdf.cell(95, 7, "_" * 35, align="C")
    pdf.cell(95, 7, "_" * 35, align="C")
    
    # Guardar PDF
    filename = f"{c['id']}_{c['descripcion'].replace(' ', '_')}.pdf"
    filepath = OUTPUT_DIR / filename
    pdf.output(str(filepath))
    print(f"  Generado: {filename}")
    return filepath


def main():
    print("\n" + "=" * 60)
    print("GENERADOR DE PDFs DE CONTRATOS DE EJEMPLO")
    print("=" * 60 + "\n")
    
    print(f"Directorio de salida: {OUTPUT_DIR}\n")
    print("Generando 20 contratos...\n")
    
    for contract in CONTRACTS:
        generate_contract_pdf(contract)
    
    print("\n" + "-" * 60)
    print(f"Generados {len(CONTRACTS)} PDFs correctamente.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
