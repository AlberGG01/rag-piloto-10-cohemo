# 🛡️ Informe de Evaluación: Golden Dataset (Hard Mode)

**Fecha:** 27/01/2026 02:08
**Dataset:** C:\Users\alber\Piloto Empresa\defense_contracts_system\tests\golden_dataset_hard.json
**Modelo Evaluador:** gpt-4o-mini

## 📊 Resumen Ejecutivo

| Métrica | Resultado | Objetivo |
|---------|-----------|----------|
| **Accuracy (Score >= 4)** | **86.7%** | > 85% |
| **Score Promedio (1-5)** | **4.23** | > 4.5 |
| **Recall@K Promedio** | **0.92** | > 0.90 |
| **Latencia Promedio** | **58.70s** | < 15s |

---

## 🛑 Análisis de Fallos (Score <= 2)

### ❌ [EM_08] ¿En qué fecha exacta finaliza el plazo de ejecución del contrato firmado con 'Medline Industries Spain S.L.'?
- **Esperado:** 20/05/2026
- **Generado:** Error procesando la consulta: name 'chunks_context' is not defined
- **Docs Recuperados:** ['SER_2024_008_Transporte_Estrategico.pdf', 'CON_2024_005_Municion_Instruccion.pdf', 'LIC_2024_017_Camiones_Logisticos_IVECO.pdf', 'SUM_2024_006_Raciones_Combate_Individual.pdf', 'CON_2024_009_Comunicaciones_Tacticas.pdf', 'CON_2024_020_Fusiles_Asalto_HK416.pdf', 'SER_2024_019_SATCOM_Operaciones.pdf', 'CON_2024_007_Obras_Acuartelamiento_Zaragoza.pdf', 'CON_2024_004_Ciberseguridad_Infraestructuras.pdf', 'SUM_2024_014_Material_Sanitario_Militar.pdf']
- **Docs Esperados:** ['SUM_2024_014_Material_Sanitario_Militar.pdf']
- **Razón Juez:** La respuesta del alumno no proporciona información relevante sobre la fecha de finalización del contrato y muestra un error de procesamiento, lo que indica falta de conocimiento sobre el tema.

### ❌ [DC_04] ¿Cuál es el 'Plazo de ejecución' exacto en días naturales para el contrato de mantenimiento de flota C295?
- **Esperado:** 910 días
- **Generado:** **Informe de situación: Plazo de ejecución del contrato de mantenimiento de flota C295**

Se ha identificado el plazo de ejecución exacto para el contrato de mantenimiento de la flota **C295**. A continuación, se presenta la información relevante:

- **Plazo de ejecución**: **760 días naturales**
- **Fuente Verificada**: SER_2024_008_Transporte_Estrategico.pdf

Esta información ha sido confirmada con un nivel de confianza alto según la evidencia recolectada.
- **Docs Recuperados:** ['SER_2024_008_Transporte_Estrategico.pdf', 'SER_2024_019_SATCOM_Operaciones.pdf', 'CON_2024_009_Comunicaciones_Tacticas.pdf', 'SUM_2024_006_Raciones_Combate_Individual.pdf', 'LIC_2024_017_Camiones_Logisticos_IVECO.pdf', 'SER_2024_013_Formacion_Sistemas_Armas.pdf', 'CON_2024_012_Centro_Mando_Retamares.pdf', 'CON_2024_020_Fusiles_Asalto_HK416.pdf', 'CON_2024_005_Municion_Instruccion.pdf', 'CON_2024_007_Obras_Acuartelamiento_Zaragoza.pdf']
- **Docs Esperados:** ['SER_2024_015_Mantenimiento_Flota_C295.pdf']
- **Razón Juez:** La respuesta del alumno proporciona un plazo de ejecución incorrecto (760 días) en lugar del correcto (910 días), lo que constituye un fallo en la información presentada.

### ❌ [DC_07] ¿Qué contrato prohíbe la subcontratación 'por razones de seguridad' de forma absoluta?
- **Esperado:** CON_2024_004
- **Generado:** **Informe de Situación: Prohibición de Subcontratación por Razones de Seguridad**

Se ha identificado que los siguientes contratos prohíben absolutamente la subcontratación por razones de seguridad:

1. **Contrato de Ciberseguridad en Infraestructuras**
   - **Fuente Verificada**: CON_2024_004_Ciberseguridad_Infraestructuras.pdf

2. **Contrato de Visión Nocturna Gen3**
   - **Fuente Verificada**: CON_2024_016_Vision_Nocturna_Gen3.pdf

3. **Contrato de Fusiles de Asalto HK416**
   - **Fuente Verificada**: CON_2024_020_Fusiles_Asalto_HK416.pdf

Estos contratos han sido identificados con un nivel de confianza alto en la evidencia recolectada.
- **Docs Recuperados:** ['CON_2024_004_Ciberseguridad_Infraestructuras.pdf', 'CON_2024_016_Vision_Nocturna_Gen3.pdf', 'CON_2024_020_Fusiles_Asalto_HK416.pdf', 'CON_2024_002_Mantenimiento_Armamento.pdf', 'CON_2024_009_Comunicaciones_Tacticas.pdf', 'SER_2024_013_Formacion_Sistemas_Armas.pdf', 'CON_2024_010_Vigilancia_Instalaciones_Militares.pdf', 'CON_2024_005_Municion_Instruccion.pdf', 'SUM_2024_006_Raciones_Combate_Individual.pdf', 'SER_2024_019_SATCOM_Operaciones.pdf']
- **Docs Esperados:** ['CON_2024_004_Ciberseguridad_Infraestructuras.pdf']
- **Razón Juez:** La respuesta menciona varios contratos, pero solo uno es correcto. Además, la información es ambigua y no se centra en la pregunta específica sobre la prohibición absoluta de subcontratación por razones de seguridad.

### ❌ [SYN_06] ¿Cuál es la diferencia en días de ejecución entre el contrato de Mantenimiento C295 y el de Ciberseguridad?
- **Esperado:** 30 días (910 vs 880)
- **Generado:** Informe de situación:

Se ha identificado que el **Contrato de Ciberseguridad (CON_2024_004)** tiene un plazo de ejecución de **880 días naturales**. Sin embargo, no se ha encontrado información específica sobre el contrato de **Mantenimiento C295** en los documentos proporcionados, lo que impide determinar la diferencia en días de ejecución entre ambos contratos.

Adicionalmente, se ha encontrado que el **Contrato CON_2024_012** también tiene un plazo de ejecución de **880 días naturales**, igual al del contrato de Ciberseguridad.

Dado que no se dispone de información sobre el contrato de Mantenimiento C295, no es posible realizar una comparación directa. A continuación, se presenta la información disponible:

| Contrato                      | Plazo de Ejecución | Fuente Verificada                          |
|-------------------------------|--------------------|--------------------------------------------|
| Ciberseguridad (CON_2024_004) | 880 días naturales | CON_2024_004_Ciberseguridad_Infraestructuras.pdf |
| Centro Mando Retamares (CON_2024_012) | 880 días naturales | CON_2024_012_Centro_Mando_Retamares.pdf |

Conclusión: Ambos contratos mencionados tienen el mismo plazo de ejecución de **880 días naturales**. No se puede determinar la diferencia con el contrato de Mantenimiento C295 debido a la falta de información específica sobre este último.
- **Docs Recuperados:** ['CON_2024_012_Centro_Mando_Retamares.pdf', 'CON_2024_009_Comunicaciones_Tacticas.pdf', 'LIC_2024_017_Camiones_Logisticos_IVECO.pdf', 'CON_2024_005_Municion_Instruccion.pdf', 'CON_2024_020_Fusiles_Asalto_HK416.pdf', 'SUM_2024_006_Raciones_Combate_Individual.pdf', 'CON_2024_004_Ciberseguridad_Infraestructuras.pdf', 'SER_2024_019_SATCOM_Operaciones.pdf', 'SER_2024_008_Transporte_Estrategico.pdf', 'SER_2024_013_Formacion_Sistemas_Armas.pdf']
- **Docs Esperados:** ['SER_2024_015_Mantenimiento_Flota_C295.pdf', 'CON_2024_004_Ciberseguridad_Infraestructuras.pdf']
- **Razón Juez:** La respuesta del alumno no proporciona la información necesaria sobre el contrato de Mantenimiento C295, lo que impide calcular la diferencia en días de ejecución. Aunque menciona correctamente el plazo del contrato de Ciberseguridad, la falta de datos sobre el otro contrato y la conclusión ambigua hacen que la respuesta sea insuficiente.


## 📝 Detalle Completo

| ID | Query | Score | Recall | Latency |
|----|-------|-------|--------|---------|
| EM_01 | ¿Qué contrato específico tiene asignado el código NSN-5855098765432? | ✅ 4 | 1.00 | 49.31s |
| EM_02 | Facilita el CIF exacto de la empresa adjudicataria del contrato de Ciberseguridad (CON_2024_004). | ✅ 5 | 1.00 | 39.60s |
| EM_03 | ¿Cuál es el importe de la base imponible EXACTA (con céntimos) del contrato SER_2024_015? | ✅ 5 | 1.00 | 38.32s |
| EM_04 | Busca el número de aval AV-2023-1515 e indica qué entidad lo emitió. | ✅ 5 | 1.00 | 57.10s |
| EM_05 | ¿Qué normativa específica 'EASA Part 145' se menciona y en qué contrato? | ✅ 5 | 1.00 | 90.56s |
| EM_06 | Localiza el contrato que cita la norma 'MIL-HDBK-217'. | ✅ 4 | 1.00 | 56.79s |
| EM_07 | ¿Qué contrato incluye el código NSN-6530987654321 para material sanitario? | ✅ 4 | 1.00 | 23.20s |
| EM_08 | ¿En qué fecha exacta finaliza el plazo de ejecución del contrato firmado con 'Medline Industries Spain S.L.'? | ❌ 1 | 1.00 | 49.19s |
| EM_09 | ¿Cuál es la fecha exacta de vencimiento del aval del contrato de Ciberseguridad? | ✅ 5 | 1.00 | 49.93s |
| EM_10 | ¿Qué porcentaje exacto de IVA se aplica al contrato CON_2024_016? (Dato numérico implícito en cálculo) | ✅ 5 | 1.00 | 43.39s |
| DC_01 | ¿Cuál es la penalización por hora de indisponibilidad del SOC en el contrato de ciberseguridad? | ✅ 5 | 1.00 | 54.15s |
| DC_02 | ¿Qué hito de entrega del contrato CON_2024_016 está programado para el 19/06/2026? | ✅ 5 | 1.00 | 45.54s |
| DC_03 | ¿Qué certificación ISO específica se requiere para el material sanitario militar en SUM_2024_014? | ✅ 5 | 1.00 | 35.81s |
| DC_04 | ¿Cuál es el 'Plazo de ejecución' exacto en días naturales para el contrato de mantenimiento de flota C295? | ❌ 1 | 0.00 | 45.99s |
| DC_05 | ¿Qué acciones incluye el objeto del contrato SER_2024_015 además del mantenimiento programado? | ✅ 5 | 1.00 | 49.77s |
| DC_06 | ¿Qué día se cumplió el hito de 'Despliegue SOC' según el contrato CON_2024_004? | ✅ 5 | 1.00 | 42.33s |
| DC_07 | ¿Qué contrato prohíbe la subcontratación 'por razones de seguridad' de forma absoluta? | ❌ 2 | 1.00 | 55.66s |
| DC_08 | ¿Cuál es la penalización diaria por indisponibilidad de aeronave en el contrato de Airbus? | ✅ 5 | 1.00 | 59.47s |
| DC_09 | ¿Qué directiva europea sanitara aplica al contrato SUM_2024_014? | ✅ 5 | 1.00 | 33.61s |
| DC_10 | ¿Qué habilitación de seguridad personal mínima se exige para el contrato CON_2024_016? | ✅ 5 | 1.00 | 38.96s |
| SYN_01 | Compara la penalización económica entre el contrato de Ciberseguridad y el de Mantenimiento de Flota C295. | ✅ 4 | 1.00 | 64.95s |
| SYN_02 | ¿Qué contratos requieren habilitación de seguridad de grado 'SECRETO' y cuáles 'RESERVADO'? Clasifícalos. | ✅ 4 | 1.00 | 92.11s |
| SYN_03 | Suma los importes totales (IVA incluido) de los contratos adjudicados a 'CyberDefense Iberia' y 'Thales Espana'. | ✅ 5 | 1.00 | 74.65s |
| SYN_04 | ¿Qué contratos tienen avales que vencen en el año 2027? Lista sus códigos y fechas. | ✅ 4 | 1.00 | 69.16s |
| SYN_05 | Identifica los contratos que prohíben o limitan estrictamente la subcontratación y explica la razón citada. | ✅ 4 | 1.00 | 60.10s |
| SYN_06 | ¿Cuál es la diferencia en días de ejecución entre el contrato de Mantenimiento C295 y el de Ciberseguridad? | ❌ 2 | 0.50 | 93.88s |
| SYN_07 | Lista todas las normas militares (MIL-*) mencionadas en los contratos de Visión Nocturna y Material Sanitario. | ✅ 5 | 1.00 | 82.13s |
| SYN_08 | ¿Qué banco avala el contrato de mayor importe entre SER_2024_015 y CON_2024_004? | ✅ 4 | 0.50 | 104.45s |
| SYN_09 | ¿Qué contratos finalizarán su ejecución en el año 2026? | ✅ 4 | 0.50 | 76.62s |
| SYN_10 | Calcula el importe total de las garantías definitivas acumuladas de los contratos CON_2024_004, CON_2024_016 y SER_2024_015. | ✅ 5 | 1.00 | 84.34s |
