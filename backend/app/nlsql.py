import json
import time

import httpx

from .integraciones import obtener
from .sqlguard import guard
from .supabase_db import esquema_texto, run_sql

_TIPOS = "number | bar | line | area | pie | table"


def _system_planner(esquema: str, perfil: str) -> str:
    foco = {
        "financiero": "Prioriza costos, ingresos, rentabilidad y consumo por destino/tarifa.",
        "supervisor": "Prioriza desempeño de campañas y agentes: contactabilidad, ventas, TMO.",
        "coordinador": "Prioriza visión comparativa entre campañas y equipos.",
        "admin": "Acceso total a cualquier métrica de la operación.",
    }.get(perfil, "")
    return f"""Eres un analista de datos experto en call centers. Trabajas sobre este esquema
PostgreSQL de SOLO LECTURA:

{esquema}

Si hay turnos anteriores de esta conversación arriba, úsalos para resolver referencias de la
pregunta actual ("esas llamadas", "¿y ayer?", "compáralo con la anterior") tomando el período,
filtros o entidad del turno previo correspondiente. Si la pregunta actual ya es autosuficiente,
ignora el historial.

PASO 0 — ¿La pregunta pide MODIFICAR datos (actualizar, insertar, borrar, eliminar, cambiar un
valor existente, "para que sea X en vez de Y", etc.)? Este sistema SOLO puede consultar, nunca
escribir. NO inventes un SELECT que intente simular o rodear el pedido: responde de inmediato
{{"rechazado": true, "motivo": "explicación breve y clara de que solo puedes consultar datos, no
modificarlos"}} y detente ahí (no generes preguntas de aclaración ni SQL).

PASO 1 — ¿La pregunta necesita ACLARACIÓN? Marca necesita_aclaracion=true si la pregunta es
ambigua, puede interpretarse de varias formas, o NO especifica un período de tiempo claro. Una
FECHA EXPLÍCITA ("el 22 de julio de 2026", "del 1 al 15 de junio") SÍ es un período claro — no la
trates como ambigua solo porque no coincide con las 5 opciones típicas (Hoy/Ayer/Últimos 7
días/Este mes/Todo el histórico); esas son sugerencias para cuando el usuario NO dio fecha, no una
lista cerrada de períodos válidos.
También marca necesita_aclaracion=true cuando la MÉTRICA es vaga aunque el período sea claro:
"¿qué tan efectivos fuimos hoy?", "¿cómo nos fue esta semana?", "¿cómo vamos?". Palabras como
efectividad, rendimiento, desempeño o "cómo vamos" pueden significar contactabilidad, conversión
a venta, volumen o costo — pregunta CUÁL en vez de elegir una por tu cuenta.
Si el usuario ya incluyó "Aclaraciones del usuario", NO vuelvas a preguntar (necesita_aclaracion=false).
Cuando necesita_aclaracion=true, devuelve HASTA 3 preguntas para aclarar (máx 3) e incluye SIEMPRE:
  1. PERÍODO, con opciones adecuadas (p.ej. "Hoy","Ayer","Últimos 7 días","Este mes","Todo el histórico").
  2. TIPO DE GRÁFICO, con 2 a 4 opciones que MEJOR representen la consulta
     ("Barras","Torta","Línea (tendencia)","Tabla","Número").
  3. (opcional) una tercera si hay ambigüedad real ("¿Por agente o por campaña?", "¿Qué métrica?"...).
Cada pregunta = {{"pregunta": "...", "clave": "snake_case", "opciones": ["...","..."]}}.
En ese caso NO generes SQL.

VOCABULARIO DEL CALL CENTER — usa SIEMPRE estas equivalencias, no inventes etiquetas. Los valores
válidos de cada enum están en el esquema de arriba; NUNCA uses uno que no aparezca ahí.
MAPEO OBLIGATORIO de sinónimos -> estado_llamada. Es la fuente de verdad: aplícalo LITERALMENTE.
Varias de estas frases suenan parecidas entre sí, pero cada bloque va a UN valor y solo uno; dos
preguntas del mismo bloque DEBEN producir exactamente el mismo número.
  'no_contesta' <- "perdida(s)", "no contestada(s)", "no atendida(s)", "no contestamos",
                   "se cayó"/"se cayeron", "se colgó"/"se colgaron", "timbró y nadie contestó",
                   "nadie respondió"
  'abandonada'  <- SOLO si dicen literalmente "abandonada(s)", "abandono", "tasa de abandono",
                   "se cansó de esperar", "colgó en la cola"/"colgó esperando"
  'fallida'     <- SOLO si dicen "fallida(s)", "error técnico", "falló la línea"
  'contestada'  <- "atendida(s)", "contestada(s)", "conectada(s)", "efectiva(s)"
OJO: en este negocio "se cayó la llamada" y "se colgaron" significan que NO se contestó
('no_contesta'); NO significan que el cliente abandonó la cola ('abandonada') ni que hubo un
fallo técnico ('fallida'). No los intercambies.
Si de verdad quieren "todo lo que no se contestó" (agrupando no_contesta + buzon + ocupado +
abandonada + fallida), usa estado_llamada != 'contestada' y dilo explícito en la descripción.
- "recibidas", "entrantes", "entraron", "nos llamaron" -> AÑADE direccion = 'entrante'.
  "salientes", "marcadas", "llamamos" -> direccion = 'saliente'. Si la pregunta implica dirección,
  filtrar por ella es OBLIGATORIO.
- "contactabilidad" = contestadas / total de llamadas (la vista v_kpi_campania_dia ya trae
  pct_contacto ya calculado).
- DURACIONES, no las confundas ni las sumes entre sí: duracion_seg es SOLO conversación real;
  espera_seg es tiempo en cola (solo tiene valor en abandonadas); timbrado_seg es timbrado;
  acw_seg es trabajo posterior. "tiempo hablado"/"conversación real" -> duracion_seg.
- Una llamada con duracion_seg = 0 nunca conectó (buzón, ocupado, abandonada). Para "llamadas
  cortas" filtra duracion_seg > 0 AND duracion_seg < N, y aclara ese criterio en la descripción.

PASO 2 — Si NO necesita aclaración (o ya hay aclaraciones), genera el reporte con estas reglas:
- Solo una consulta SELECT/WITH de SOLO LECTURA, con columnas/tablas que existan. Prefiere las VISTA v_*.
- Respeta el PERÍODO y el TIPO DE GRÁFICO indicados en las "Aclaraciones del usuario" si existen.
- Mapea el período sobre fecha_hora_inicio: Hoy->current_date; Ayer->current_date-1;
  "Últimos 7 días"-> >= current_date-6; "Este mes"-> >= date_trunc('month',current_date);
  "Todo el histórico"-> sin filtro de fecha. Si la pregunta da una FECHA EXPLÍCITA, usa
  fecha_hora_inicio::date = 'YYYY-MM-DD'; si da un rango explícito, usa
  fecha_hora_inicio::date BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'.
  El costo está en COP. Incluye ORDER BY y LIMIT (máx 200).
- SEMANA/MES CALENDARIO vs VENTANA MÓVIL — no los confundas:
  "esta semana" -> fecha_hora_inicio >= date_trunc('week', current_date)  (lunes a hoy)
  "la semana pasada" -> >= date_trunc('week',current_date) - interval '7 days'
                        AND < date_trunc('week', current_date)
  "últimos 7 días" -> >= current_date - 6  (ventana móvil; NO es lo mismo que "esta semana")
  "mes pasado" -> >= date_trunc('month',current_date) - interval '1 month'
                  AND < date_trunc('month', current_date)
- DÍA DE LA SEMANA relativo ("el lunes pasado", "el martes de la semana pasada"): calcula desde
  date_trunc('week', current_date) - interval '7 days' y súmale días con interval
  (lunes=+0, martes=+1, ... domingo=+6). PROHIBIDO usar % (módulo) sobre date o interval:
  en PostgreSQL "date - numeric" e "interval % integer" NO existen y la consulta falla.
- PORCENTAJES Y RATIOS — error clásico, revísalo dos veces antes de responder: si mides "qué
  porcentaje son X", el WHERE NO puede contener la condición X. Si la pones ahí, numerador y
  denominador quedan sobre el MISMO conjunto y el resultado es 100% siempre, pase lo que pase.
  La condición X va ÚNICAMENTE dentro del FILTER. Protege el denominador con nullif(...,0).
  MAL (da 100% siempre):
    select count(*) filter (where estado_llamada='abandonada')*100.0/nullif(count(*),0)
    from llamadas where estado_llamada='abandonada'
  BIEN (sin WHERE de esa condición, el denominador es el total real):
    select count(*) filter (where estado_llamada='abandonada')*100.0/nullif(count(*),0) as pct,
           avg(espera_seg) filter (where estado_llamada='abandonada') as seg_prom
    from llamadas
- `eje_x` SIEMPRE columna categórica/temporal, NUNCA una métrica ni el nombre de la entidad comparada.
- COINCIDENCIA DE NOMBRES: nunca uses igualdad exacta; normaliza con translate() para ignorar tildes y
  compara el nombre completo por PALABRAS con LIKE (términos en minúscula y sin tildes; el orden no importa).
- Para COMPARAR varias entidades: inclúyelas TODAS, en formato ANCHO (una columna numérica por entidad)
  y tipo_grafico "bar". Ej: with n as (select id, translate(lower(nombres||' '||apellidos),'áéíóúü','aeiouu')
  as nom from agentes) select l.estado_llamada, count(*) filter (where nom like '%sofia%' and nom like
  '%herrera%' and nom like '%luna%') as "Sofía Herrera Luna", ... from llamadas l join n on n.id=l.agente_id
  group by l.estado_llamada  -> eje_x="estado_llamada", series=[nombres...], tipo_grafico="bar".
- "pie" SOLO para la distribución de UNA sola serie sobre categorías (nunca para comparar entidades).
- UNIDADES en los alias: conserva siempre el sufijo de unidad para que el lector no la adivine
  (..._seg para segundos, ..._cop para pesos, ..._pct para porcentajes). Ej: avg(espera_seg) as
  espera_promedio_seg, NO "espera_promedio" a secas.
- Incluye un "resumen": frase corta de lo que se consulta (métrica · período · visualización).
- Perfil del usuario: {perfil}. {foco}

Responde SOLO un JSON:
- Si pide modificar datos: {{"rechazado": true, "motivo": "..."}}
- Si necesita aclaración:
  {{"necesita_aclaracion": true, "preguntas": [ {{"pregunta":"...","clave":"...","opciones":["..."]}} ]}}
- Si no:
  {{"necesita_aclaracion": false, "sql": "SELECT ...", "tipo_grafico": "{_TIPOS}",
    "titulo": "título corto", "eje_x": "columna o null", "series": ["columnas numéricas"],
    "resumen": "qué se consulta (métrica · período · gráfico)", "descripcion": "1 frase"}}"""


def _system_analista(perfil: str) -> str:
    return f"""Eres un analista senior de operaciones de call center. A partir de una pregunta y los
resultados de una consulta, redactas un análisis ejecutivo en español, claro, diciente y estratégico
para un perfil {perfil}.

REGLAS ESTRICTAS (obligatorias):
- Usa ÚNICAMENTE los números que aparezcan en los "Datos" entregados. Está PROHIBIDO inventar,
  estimar, redondear a un valor distinto o completar cifras que no estén en los datos.
- Si algo que se preguntó NO está en los datos (por ejemplo, una entidad o métrica que no aparece
  en el resultado), dilo explícitamente ("no hay datos de X en el resultado") en vez de suponer.
- No menciones entidades que no estén presentes en los datos.
- NUNCA inventes ni conviertas UNIDADES. Un valor solo está en segundos si la columna lo dice
  (sufijo _seg); en pesos si dice _cop o es un monto/costo; en porcentaje si dice _pct o pct_.
  Si el nombre de la columna no indica la unidad, di la cifra sin unidad en vez de suponerla.
  Confundir segundos con minutos u horas es un error grave: no lo hagas.
- Si TODOS los valores son 0 (o no hay filas), NO afirmes como un hecho que hubo cero actividad,
  pero TAMPOCO des por sentado que los filtros están mal. Presenta las dos lecturas posibles:
  (a) que en ese período realmente no hubo actividad todavía —muy normal cuando se pregunta por
  "hoy" y la jornada apenas empieza—, o (b) que algún filtro (un nombre, una fecha) no coincide
  con los datos. Deja claro cuál habría que verificar para distinguirlas.

Responde SOLO un JSON:
{{
  "insight": "análisis en markdown (2-4 frases, solo con cifras que estén en los datos)",
  "recomendaciones": ["acción sugerida 1", "acción sugerida 2"]
}}"""


async def _chat(cfg: dict, messages: list[dict], temperature: float = 0.1) -> dict:
    url = (cfg.get("base_url") or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
    payload = {
        "model": cfg.get("model", "gpt-4o"),
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    async with httpx.AsyncClient(timeout=45) as cli:
        r = await cli.post(url, headers={"Authorization": f"Bearer {cfg['api_key']}"}, json=payload)
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI respondió HTTP {r.status_code}: {r.text[:200]}")
    return json.loads(r.json()["choices"][0]["message"]["content"])


async def responder(
    pregunta: str, perfil: str, aclaraciones: dict | None = None, historial: list[dict] | None = None
) -> dict:
    ocfg = await obtener("openai")
    if not ocfg or not ocfg.get("api_key"):
        raise RuntimeError("OpenAI no está configurado. Ve a Configuración.")

    esquema = await esquema_texto()

    # El contenido incluye las aclaraciones del usuario si ya las respondió.
    contenido = pregunta
    if aclaraciones:
        detalle = "; ".join(f"{k}: {v}" for k, v in aclaraciones.items() if v)
        contenido = f"{pregunta}\n\nAclaraciones del usuario -> {detalle}"

    # Turnos previos de la conversación como mensajes reales, para que el modelo pueda
    # resolver referencias como "esas llamadas" o "¿y ayer?" sin que el usuario repita el
    # contexto. Cada turno pasado se resume a lo que realmente se consultó (no los datos
    # completos, para no disparar el costo de tokens).
    mensajes_planner = [{"role": "system", "content": _system_planner(esquema, perfil)}]
    for turno in (historial or [])[-3:]:
        mensajes_planner.append({"role": "user", "content": turno["pregunta"]})
        mensajes_planner.append(
            {
                "role": "assistant",
                "content": json.dumps(
                    {"resumen": turno.get("resumen"), "sql": turno.get("sql")}, ensure_ascii=False
                ),
            }
        )
    mensajes_planner.append({"role": "user", "content": contenido})

    # 1) Planificador: decide si aclara, o genera SQL + especificación de gráfico
    plan = await _chat(ocfg, mensajes_planner)

    # Pedido de escritura (update/insert/delete/"cambia X por Y"): se rechaza explícito en vez
    # de dejar que el modelo invente un SELECT que no tiene nada que ver con lo pedido.
    if plan.get("rechazado"):
        raise RuntimeError(
            plan.get("motivo") or "Este asistente solo puede consultar datos, no modificarlos."
        )

    # Si la pregunta es ambigua y aún no hay aclaraciones, devolvemos las preguntas.
    if plan.get("necesita_aclaracion") and not aclaraciones:
        return {"tipo": "aclaracion", "preguntas": plan.get("preguntas", [])[:3]}

    # El usuario YA respondió las aclaraciones pero el modelo insiste en preguntar y no manda
    # SQL. Sin esto el guard falla con "La consulta está vacía" y el usuario ve un error después
    # de haber contestado el formulario -que es justo lo que no debe pasar-.
    if not plan.get("sql"):
        mensajes_planner.append({"role": "assistant", "content": json.dumps(plan, ensure_ascii=False)})
        mensajes_planner.append(
            {
                "role": "user",
                "content": "Ya tienes la información necesaria: usa las aclaraciones que te di y, si "
                "algo sigue sin estar definido, asume la interpretación más razonable y decláralo en "
                "la descripción. NO vuelvas a pedir aclaración; responde el JSON con la clave sql ya "
                "construida.",
            }
        )
        plan = await _chat(ocfg, mensajes_planner)

    sql = plan.get("sql", "")
    sql_guarded = guard(sql)  # lanza SQLError si no es SELECT válido

    # 2) Ejecución (solo lectura). Si el SQL falla en PostgreSQL, se reintenta 1 vez
    #    pidiéndole al modelo que lo corrija con el mensaje de error real.
    t0 = time.monotonic()
    try:
        columnas, filas = await run_sql(sql_guarded)
    except Exception as err:  # noqa: BLE001 - error al ejecutar el SQL generado por el LLM
        plan = await _chat(
            ocfg,
            [
                {"role": "system", "content": _system_planner(esquema, perfil)},
                {"role": "user", "content": contenido},
                {"role": "assistant", "content": json.dumps(plan, ensure_ascii=False)},
                {
                    "role": "user",
                    "content": f"El SQL anterior falló en PostgreSQL con este error: {err}. "
                    "Corrígelo usando SOLO columnas y tablas que existan en el esquema dado. "
                    "Responde de nuevo el JSON completo con la clave sql ya corregida.",
                },
            ],
        )
        sql = plan.get("sql", "")
        sql_guarded = guard(sql)
        try:
            columnas, filas = await run_sql(sql_guarded)
        except Exception as err2:  # noqa: BLE001
            raise RuntimeError(
                "No pude construir una consulta válida para esa pregunta. Intenta reformularla."
            ) from err2
    ms = int((time.monotonic() - t0) * 1000)

    # 3) Analista: insight estratégico sobre los datos reales
    muestra = filas[:50]
    analisis = await _chat(
        ocfg,
        [
            {"role": "system", "content": _system_analista(perfil)},
            {
                "role": "user",
                "content": f"Pregunta: {pregunta}\nTítulo: {plan.get('titulo')}\n"
                f"Columnas: {columnas}\nDatos (muestra): {json.dumps(muestra, ensure_ascii=False)}",
            },
        ],
        temperature=0.4,
    )

    return {
        "tipo": "resultado",
        "pregunta": pregunta,
        "sql": sql,
        "tipo_grafico": plan.get("tipo_grafico", "table"),
        "titulo": plan.get("titulo", "Resultado"),
        "resumen": plan.get("resumen", ""),
        "eje_x": plan.get("eje_x"),
        "series": plan.get("series", []),
        "descripcion": plan.get("descripcion", ""),
        "columnas": columnas,
        "filas": filas,
        "insight": analisis.get("insight", ""),
        "recomendaciones": analisis.get("recomendaciones", []),
        "ms": ms,
        "n_filas": len(filas),
    }
