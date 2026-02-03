# 🧪 THE PREMIUM ACCURACY TEST (V4)
**Fecha de Generación:** 29/01/2026  
**Auditor:** AntiGravity Agent  
**Estándar:** Zero Error Policy

---

## 🏗️ 1. EXTRACCIÓN PURA (Datos Nucleares)
Datos que el sistema debe recuperar con exactitud de OCR, sin margen de error.

| ID | Pregunta | Respuesta Correcta Verification | Referencia |
|:---|:---|:---|:---|
| NUM_01 | ¿Cuál es el importe total exacto de CON_2024_012? | **28.500.000,00 EUR** | PDF CON_2024_012 (Pág 1/Cláusula 3) |
| NUM_02 | ¿Qué entidad emitió el aval para SER_2024_015? | **ING Bank** | PDF SER_2024_015 (Anexo Garantías) |
| NUM_03 | Importe exacto de la garantía de CON_2024_016. | **84.000,00 EUR** | PDF CON_2024_016 |
| NUM_04 | Normativa MIL de combustible en SUM_2024_011. | **MIL-DTL-83133** | PDF SUM_2024_011 (Pliego Téc) |
| NUM_05 | Códigos STANAG en Munición Instrucción (CON_2024_005). | **STANAG 4172, STANAG 4090** | PDF CON_2024_005 |
| NUM_06 | Norma ISO exigida en Vigilancia (CON_2024_010). | **ISO 18788** | PDF CON_2024_010 |
| NUM_07 | Importe total adjudicación LIC_2024_017. | **9.600.000,00 EUR** | PDF LIC_2024_017 |
| NUM_08 | CIF de adjudicataria Ciberseguridad (CON_2024_004). | **B-55667788** | PDF CON_2024_004 (Cabecera) |
| NUM_09 | Importe garantía Transporte Estratégico (SER_2024_008). | **112.000,00 EUR** | PDF SER_2024_008 |
| NUM_10 | Normas ISO/MIL en Material Sanitario (SUM_2024_014). | **ISO 13485, MIL-STD-1472** | PDF SUM_2024_014 |

---

## 🧠 2. INFERENCIA DIRECTA
Relaciones causa-efecto y cálculos que requieren procesar el texto.

| ID | Pregunta | Respuesta Correcta | Lógica / Cálculo |
|:---|:---|:---|:---|
| INF_01 | ¿Contratos con penalización diaria de 50.000 EUR? | **SER_2024_015, SUM_2024_011** | Extracción comparada de cláusulas penales. |
| INF_02 | Comparar importe Ciberseguridad vs Visión Nocturna. | **Ciberseguridad > Visión (+300k)** | 4.5M - 4.2M test numérico. |
| INF_03 | ¿Contrato que requiere raíles Picatinny? | **CON_2024_020** | Inferencia: STANAG 4694 = Rails. |
| INF_04 | Fecha fin de ejecución Retamares. | **12/10/2027** | Selección de fecha máxima en hitos. |
| INF_05 | Normativa seguridad alimentaria en raciones. | **ISO 22000** | Inferencia de dominio (Food Safety). |
| INF_06 | ¿Garantía SER_2024_008 es el 2% exacto? | **SÍ** | 5.600.000 * 0.02 = 112.000 check. |
| INF_07 | Contrato de comunicaciones con STANAG HF (4538). | **CON_2024_009** | Asociación técnica específica. |
| INF_08 | Diferencia importe C295 vs Hangares Morón. | **2.400.000,00 EUR** | 18.2M - 15.8M resta simple. |
| INF_09 | Contrato sanitario con ergonomía (MIL-STD-1472). | **SUM_2024_014** | Asociación de estándar HFE. |
| INF_10 | Suma Combustible + Mantenimiento C295. | **25.000.000,00 EUR** | 6.8M + 18.2M suma agregada. |

---

## ⚠️ 3. CASOS LÍMITE (Stress Test)
Excepciones, datos faltantes y trampas para evitar alucinaciones.

| ID | Pregunta | Respuesta Correcta | Tipo de Trampa |
|:---|:---|:---|:---|
| EDGE_01 | Contratos con ISO 9001 genérica (sin año). | **LIC_2024_003, CON_2024_001...** | Precisión de versión normativa. |
| EDGE_02 | Responsable técnico de Drones Predator. | **No consta / Inexistente** | Alucinación negativa (Dato no existe). |
| EDGE_03 | Aval emitido explícitamente por ING Bank. | **SER_2024_015** | Búsqueda de entidad específica rara. |
| EDGE_04 | Contrato con mayor densidad de hitos (~10). | **CON_2024_007** | Conteo de items en listas. |
| EDGE_05 | Penalización exacta de 10.000 EUR. | **SER_2024_008, SER_2024_019** | Precisión numérica exacta. |
| EDGE_06 | Prohibición explícita de subcontratación total. | **CON_2024_004** | Cláusula legal restrictiva única. |
| EDGE_07 | Contratos con hito compartido el 16/12/2024. | **CON_2024_004, 007, SER_008...** | Cruce de datos multi-documento. |
| EDGE_08 | Contrato con normas mixtas ISO + STANAG. | **SUM_2024_006** | Fusión de dominios civil/militar. |
| EDGE_09 | Contrato de menor cuantía global. | **SUM_2024_014 (425k)** | Ranking mínimo global. |
| EDGE_10 | Coste desglosado limpieza en Combustible. | **No consta / 0,00** | Dato cualitativo vs cuantitativo. |
