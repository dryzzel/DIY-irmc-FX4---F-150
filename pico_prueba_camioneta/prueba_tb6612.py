"""Prueba manual de banco. Ejecutar desde el editor, NO como main.py.

Motor libre/desacoplado: el giro no usa Hall ni limita corriente.
La opcion h aprende lecturas Hall con el motor deshabilitado.
La opcion t identifica direccion desde el centro, con corte por Hall.
La opcion r visita ambos extremos y registra el Hall despues del corte.
1 y 2 son sentidos electricos, no abierto/cerrado ni extremos A/B.
"""
from machine import Pin, PWM, ADC
from time import ticks_ms, ticks_diff, sleep_ms

PULSO_MS = 150
RAMPA_MS = 75
PWM_INICIAL = 0.25
PWM_FINAL = 0.60  # Ensayo de mayor fuerza durante el recorrido.
PAUSA_MS = 500
PREPARACION_S = 10
MEDICION_MS = 10000
GIRO_MS = 2000
RAMPA_GIRO_MS = 200
TOPE_A = 40000  # Alto: cerrado. Umbral provisional de las capturas del usuario.
TOPE_B = 26000  # Bajo: abierto.
DIRECCION_A = 1  # Cables del motor invertidos al soldar: sentido 1 cierra A; 2 abre B.
CENTRO_MIN = 30000
CENTRO_MAX = 34000
TOPE_TIMEOUT_MS = 1000  # Recorrido previo incompleto a 500 ms; no limita corriente.
RECORRIDO_TIMEOUT_MS = 2500  # Maximo provisional por tramo completo, no validado.
RETENCION_A = 35000  # Juego medido: A minimo 35936; provisional de banco.
RETENCION_B = 31300  # Juego medido: B maximo 31009; margen estrecho al centro.
FRENO_MS = 50  # Pulso inicial experimental; no retencion permanente.
HALL_LOOP_MS = 1  # Espera; intervalo real incluye ADC, Python y otras latencias.

standby = Pin(5, Pin.OUT, value=0)
monitor = Pin(18, Pin.OUT, value=0)
in1 = Pin(2, Pin.OUT, value=0)
in2 = Pin(3, Pin.OUT, value=0)
pwm = PWM(Pin(4))
pwm.duty_u16(0)
opto = Pin(15, Pin.IN, Pin.PULL_UP)


def parar():
    standby.off()
    pwm.duty_u16(0)
    in1.off()
    in2.off()


def iniciar_freno():
    # Preparar ambos canales deshabilitados para evitar estados distintos.
    standby.off()
    pwm.duty_u16(0)
    in1.on()
    in2.on()
    inicio = ticks_ms()
    standby.on()  # IN1=IN2=1, PWM=0: short brake en ambos canales.
    return inicio


def frenar_breve(sensor):
    try:
        inicio = iniciar_freno()
        while ticks_diff(ticks_ms(), inicio) < FRENO_MS:
            leer_hall_tope(sensor)  # Una lectura invalida aborta y deshabilita.
            sleep_ms(HALL_LOOP_MS)
    finally:
        parar()


def pulso(sentido, duracion_ms=PULSO_MS, rampa_ms=RAMPA_MS):
    parar()
    if sentido not in (1, 2):
        raise ValueError('Sentido debe ser 1 o 2')
    try:
        sleep_ms(PAUSA_MS)
        in1.value(sentido == 1)
        in2.value(sentido == 2)
        inicio = ticks_ms()
        while True:
            transcurrido = ticks_diff(ticks_ms(), inicio)
            if transcurrido >= duracion_ms:
                break
            fraccion = min(1.0, transcurrido / rampa_ms)
            duty = PWM_INICIAL + (PWM_FINAL - PWM_INICIAL) * fraccion
            pwm.duty_u16(int(duty * 65535))
            standby.on()
            sleep_ms(5)
    finally:
        parar()


def probar_giro():
    parar()
    print('GIRO DE BANCO: motor conectado pero mecanicamente libre, sin engranajes.')
    print('Salidas en paralelo por etiquetas verificadas; nunca sujetar el eje.')
    print('Duracion:', GIRO_MS // 1000, 's | PWM 25% -> 60% | Ctrl+C para cancelar.')
    sentido = input('Sentido 1 o 2 (otro cancela): ').strip()
    if sentido not in ('1', '2'):
        return
    try:
        for segundos in range(3, 0, -1):
            print('Arranca en', segundos, 's')
            sleep_ms(1000)
        print('GIRANDO durante', GIRO_MS // 1000, 's...')
        pulso(int(sentido), GIRO_MS, RAMPA_GIRO_MS)
        print('Apagado. Espera a que el eje se detenga antes de otro ensayo.')
        print('Pausa entre ensayos: 10 s. Revisar ruido, olor o calentamiento anormal.')
        sleep_ms(10000)
    finally:
        parar()


def leer_entrada():
    nivel = opto.value()
    print('GP15 =', nivel, '| PC817', 'ENCENDIDO' if nivel == 0 else 'APAGADO')
    print('Lectura instantanea. No dispara movimiento ni confirma posicion.')


def probar_automatico():
    parar()
    monitor.off()
    try:
        import config as base
        from controller import Controller

        class Banco:
            pass

        cfg = Banco()
        for nombre in dir(base):
            if nombre.isupper():
                setattr(cfg, nombre, getattr(base, nombre))
        cfg.DRIVE_ENABLED = True
        cfg.MONITOR_ENABLED = False
        cfg.OPEN_END = 'B'
        cfg.A_DIRECTION = DIRECCION_A
        cfg.MOTION_TIMEOUT_MS = 2000
        cfg.HALL_A_ENTER, cfg.HALL_A_EXIT = TOPE_A, RETENCION_A
        cfg.HALL_B_ENTER, cfg.HALL_B_EXIT = TOPE_B, RETENCION_B
        cfg.PWM_START, cfg.PWM_RUN = PWM_INICIAL, PWM_FINAL
        # Banco sin divisor GP28 confirmado: no inventar una medida de VM.
        cfg.VM_MONITOR_ENABLED = False
        control = Controller(cfg)
        sensor = ADC(26)
        print('AUTOMATICO DE BANCO. PC817 encendido / GP15=0 -> CERRAR A.')
        print('PC817 apagado / GP15=1 -> ABRIR B. Monitor DESHABILITADO.')
        print('Sin supervision de VM ni corriente. Usar fuente de banco verificada.')
        print('Puede moverse al iniciar segun la entrada actual. Ctrl+C detiene y vuelve al menu.')
        for segundos in (3, 2, 1):
            print('Inicio en', segundos, 's')
            sleep_ms(1000)
        anterior = ticks_ms()
        ahora = 0
        direccion_activa = 0
        ultimo_estado = None
        ultimo_reporte = -1000
        ultima_lectura = None
        max_intervalo = 0
        freno_inicio = None
        freno_comando = None
        while True:
            tick = ticks_ms()
            ahora += ticks_diff(tick, anterior)
            anterior = tick
            hall = leer_hall_tope(sensor)
            lectura_tick = ticks_ms()
            if direccion_activa and ultima_lectura is not None:
                max_intervalo = max(max_intervalo, ticks_diff(lectura_tick, ultima_lectura))
            ultima_lectura = lectura_tick
            comando = opto.value()
            salida = control.step(ahora, comando, hall, None)
            direccion = salida['direction']
            if freno_inicio is not None:
                if (salida['fault'] or comando != freno_comando
                        or ticks_diff(ticks_ms(), freno_inicio) >= FRENO_MS):
                    parar()
                    freno_inicio = None
                direccion = 0  # Nunca arrancar durante el pulso de frenado.
            elif not direccion:
                if (direccion_activa and not salida['fault']
                        and salida['signal'] is not None
                        and extremo_hall(hall) == control.target):
                    freno_inicio = iniciar_freno()
                    freno_comando = comando
                else:
                    parar()
            else:
                if direccion != direccion_activa:
                    parar()
                    max_intervalo = 0
                    in1.value(direccion == 1)
                    in2.value(direccion == -1)
                pwm.duty_u16(int(salida['duty'] * 65535))
                standby.on()
            if direccion_activa and not direccion and freno_inicio is None:
                print('Corte Hall:', hall, '| intervalo max entre lecturas:', max_intervalo,
                      'ms | estado:', salida['state'])
            direccion_activa = direccion
            estado = (salida['state'], salida['signal'], control.target, salida['fault'])
            if not direccion and freno_inicio is None and (estado != ultimo_estado or ahora - ultimo_reporte >= 1000):
                print('Estado:', salida['state'], '| GP15:', salida['signal'],
                      '| destino:', control.target, '| Hall:', hall,
                      '| posicion:', salida['position'], '| fallo:', salida['fault'])
                ultimo_estado, ultimo_reporte = estado, ahora
            if salida['fault']:
                print('Fallo bloqueado: no hay reintento por cambio de entrada.')
                print('Revisar antes de volver a seleccionar a.')
                return
            sleep_ms(HALL_LOOP_MS)
    except KeyboardInterrupt:
        parar()
        print('Automatico cancelado; motor apagado.')
    except (ValueError, OSError) as error:
        parar()
        print('Automatico detenido:', error)
    finally:
        parar()
        monitor.off()


def leer_hall_tope(sensor, registro=None):
    muestras = [sensor.read_u16() for _ in range(8)]
    bajo, alto = min(muestras), max(muestras)
    valor = sum(muestras) // 8
    if registro is not None:
        registro['min'] = min(registro['min'], valor)
        registro['max'] = max(registro['max'], valor)
        registro['crudo_min'] = min(registro['crudo_min'], bajo)
        registro['crudo_max'] = max(registro['crudo_max'], alto)
        registro['lecturas'] += 1
        ahora = ticks_ms()
        if registro['ultimo_ms'] is not None:
            registro['intervalo_max_ms'] = max(registro['intervalo_max_ms'],
                                             ticks_diff(ahora, registro['ultimo_ms']))
        registro['ultimo_ms'] = ahora
    if bajo <= 2000 or alto >= 63500:
        raise ValueError('Hall fuera de rango: crudo_min={} crudo_max={} media={}'.format(bajo, alto, valor))
    return valor


def extremo_hall(valor):
    if valor >= TOPE_A:
        return 'A'
    if valor <= TOPE_B:
        return 'B'
    return None


def probar_topes():
    parar()
    monitor.off()
    sensor = ADC(26)
    print('DIRECCION CON HALL: A >=40000 CERRADO; B <=26000 ABIERTO.')
    print('Antes: verificar a mano que esos umbrales aparecen ANTES de los topes duros.')
    print('Con potencia quitada, colocar mecanica en centro sin forzar engranajes.')
    print('Reponer potencia, retirar manos. No usar 1/2/g con esta mecanica acoplada.')
    print('Corte al primer umbral o a', TOPE_TIMEOUT_MS, 'ms; sin reintento automatico.')
    sentido = input('Sentido electrico 1 o 2 (otro cancela): ').strip()
    if sentido not in ('1', '2'):
        return
    registro = {'min': 65535, 'max': 0, 'crudo_min': 65535, 'crudo_max': 0,
                'lecturas': 0, 'ultimo_ms': None, 'intervalo_max_ms': 0}
    try:
        print('Diagnostico: corta en CUALQUIER extremo, no solo el esperado.')
        print('PWM maximo de este archivo:', int(PWM_FINAL * 100), '%')
        for segundo in (3, 2, 1):
            print('Inicio en', segundo, 's; retirar manos. Ctrl+C cancela.')
            sleep_ms(1000)
        # Validar durante la espera y justo antes del arranque.
        for _ in range(50):
            valor = leer_hall_tope(sensor)
            if not CENTRO_MIN <= valor <= CENTRO_MAX:
                print('NO ARRANCA: Hall', valor, 'no esta en centro 30000..34000.')
                return
            sleep_ms(10)
        inicial = leer_hall_tope(sensor)
        if not CENTRO_MIN <= inicial <= CENTRO_MAX:
            print('NO ARRANCA: posicion cambio durante la espera.')
            return
        print('Inicio Hall:', inicial, '| sentido:', sentido)
        in1.value(sentido == '1')
        in2.value(sentido == '2')
        inicio = ticks_ms()
        extremo = None
        while True:
            valor = leer_hall_tope(sensor, registro)
            extremo = extremo_hall(valor)
            tiempo = ticks_diff(ticks_ms(), inicio)
            if extremo is not None or tiempo >= TOPE_TIMEOUT_MS:
                parar()  # Cortar ANTES de imprimir o confirmar estabilidad.
                break
            duty = PWM_INICIAL + (PWM_FINAL - PWM_INICIAL) * min(1.0, tiempo / RAMPA_GIRO_MS)
            pwm.duty_u16(int(duty * 65535))
            standby.on()
            sleep_ms(HALL_LOOP_MS)
        if extremo is not None:
            frenar_breve(sensor)
        print('Corte: Hall', valor, '| tiempo', tiempo, 'ms | freno:', FRENO_MS if extremo else 0, 'ms')
        if extremo is None:
            print('TIMEOUT: no llego a un umbral; direccion NO confirmada.')
            print('No aumentar tiempo automaticamente. Revisar recorrido y estas lecturas.')
            return
        # Confirmar SOLO con potencia cortada; nunca insistir si era ruido.
        for _ in range(10):
            sleep_ms(10)
            if extremo_hall(leer_hall_tope(sensor)) != extremo:
                print('Lectura no sostenida tras corte; direccion NO confirmada.')
                return
        direccion_a = 1 if (sentido == '1') == (extremo == 'A') else -1
        print('Sentido', sentido, '->', extremo, 'CERRADO' if extremo == 'A' else 'ABIERTO')
        print('Candidato A_DIRECTION =', direccion_a, '| OPEN_END = B')
        print('Confirmar movimiento observado; no se modifico config.py.')
    except ValueError as error:
        parar()
        print('PRUEBA DETENIDA:', error)
    finally:
        parar()
        monitor.off()
        if registro['lecturas']:
            print('HALL DURANTE EL ENSAYO (antes del freno):')
            print('Promedios min/max:', registro['min'], registro['max'])
            print('Crudos min/max:', registro['crudo_min'], registro['crudo_max'])
            print('Lecturas:', registro['lecturas'], '| intervalo max:', registro['intervalo_max_ms'], 'ms')


def posicion_retenida(valor):
    if valor >= RETENCION_A:
        return 'A'
    if valor <= RETENCION_B:
        return 'B'
    if CENTRO_MIN <= valor <= CENTRO_MAX:
        return 'CENTRO'
    return 'INDEFINIDA'


def observar_parada(sensor, destino, corte, instante_corte, frenando=False):
    # No imprimir mientras se toman las muestras: evita retrasarlas por USB.
    puntos = []
    minimo, maximo = corte, corte
    objetivos = (0, 100, 300, 700)
    retenido = True
    while len(puntos) < len(objetivos):
        valor = leer_hall_tope(sensor)
        tiempo = ticks_diff(ticks_ms(), instante_corte)
        if frenando and tiempo >= FRENO_MS:
            parar()
            frenando = False
        minimo, maximo = min(minimo, valor), max(maximo, valor)
        if tiempo >= 100 and posicion_retenida(valor) != destino:
            retenido = False
        if tiempo >= objetivos[len(puntos)]:
            puntos.append({'objetivo_ms': objetivos[len(puntos)],
                           'real_ms': tiempo, 'hall': valor})
        if len(puntos) < len(objetivos):
            sleep_ms(5)
    return {'muestras': puntos, 'min': minimo, 'max': maximo,
            'retenido': retenido, 'hall_final': puntos[-1]['hall']}


def tramo_hall(sensor, destino):
    parar()
    sleep_ms(PAUSA_MS)
    inicial = leer_hall_tope(sensor)
    if extremo_hall(inicial) == destino:
        raise ValueError('Ya esta en destino; no se inicia ese tramo')
    direccion = DIRECCION_A if destino == 'A' else -DIRECCION_A
    in1.value(direccion == 1)
    in2.value(direccion == -1)
    inicio = ticks_ms()
    ultima_lectura = None
    max_intervalo = 0
    try:
        while True:
            valor = leer_hall_tope(sensor)
            lectura_tick = ticks_ms()
            if ultima_lectura is not None:
                max_intervalo = max(max_intervalo, ticks_diff(lectura_tick, ultima_lectura))
            ultima_lectura = lectura_tick
            tiempo = ticks_diff(ticks_ms(), inicio)
            llegado = extremo_hall(valor) == destino
            if llegado or tiempo >= RECORRIDO_TIMEOUT_MS:
                parar()
                instante_corte = ticks_ms()
                break
            duty = PWM_INICIAL + (PWM_FINAL - PWM_INICIAL) * min(1.0, tiempo / RAMPA_GIRO_MS)
            pwm.duty_u16(int(duty * 65535))
            standby.on()
            sleep_ms(HALL_LOOP_MS)
    finally:
        parar()
    try:
        if llegado:
            instante_corte = iniciar_freno()
        parada = observar_parada(sensor, destino, valor, instante_corte, frenando=llegado)
    finally:
        parar()
    return {'destino': destino, 'hall_inicial': inicial, 'hall_corte': valor,
            'marcha_ms': tiempo, 'motivo': 'HALL' if llegado else 'TIMEOUT',
            'freno_ms': FRENO_MS if llegado else 0,
            'intervalo_hall_max_ms': max_intervalo,
            'parada': parada}


def probar_recorrido():
    parar()
    monitor.off()
    sensor = ADC(26)
    informe = {'version': 1, 'completo': False, 'tramos': []}
    print('RECORRIDO DOS IMANES: sentido 1 cierra A; sentido 2 abre B.')
    print('Motor acoplado, Hall instalado. Retirar manos. Ctrl+C cancela.')
    print('PWM 25% -> 60%; maximo provisional', RECORRIDO_TIMEOUT_MS, 'ms por tramo.')
    print('Freno electrico', FRENO_MS, 'ms, luego rueda libre; mediciones desde inicio del freno.')
    try:
        for segundo in (3, 2, 1):
            print('Inicio en', segundo, 's')
            sleep_ms(1000)
        posicion = posicion_retenida(leer_hall_tope(sensor))
        if posicion == 'INDEFINIDA':
            raise ValueError('Posicion inicial ambigua: colocar en centro con potencia quitada')
        # Verificar posicion inicial estable, sin mover.
        for _ in range(20):
            sleep_ms(10)
            if posicion_retenida(leer_hall_tope(sensor)) != posicion:
                raise ValueError('Hall inicial inestable; no arrancar')
        ruta = ('B', 'A') if posicion == 'A' else ('A', 'B')
        print('Ruta:', ruta, '| inicio:', posicion)
        for destino in ruta:
            resultado = tramo_hall(sensor, destino)
            informe['tramos'].append(resultado)
            print('\nDestino:', destino, 'CERRADO' if destino == 'A' else 'ABIERTO')
            print('Inicio Hall:', resultado['hall_inicial'], '| corte:', resultado['hall_corte'],
                  '| marcha:', resultado['marcha_ms'], 'ms |', resultado['motivo'])
            for muestra in resultado['parada']['muestras']:
                print('Tras corte:', muestra['real_ms'], 'ms | Hall:', muestra['hall'])
            print('Hall min/max tras corte:', resultado['parada']['min'], resultado['parada']['max'])
            if resultado['motivo'] != 'HALL':
                raise ValueError('TIMEOUT: se cancela el resto de la ruta, sin reintento')
            if not resultado['parada']['retenido']:
                raise ValueError('Hall salio de la zona del extremo tras corte; no continuar')
        informe['completo'] = True
        print('Dos destinos medidos. No se repite el ciclo automaticamente.')
    except (ValueError, OSError) as error:
        parar()
        informe['error'] = str(error)
        print('RECORRIDO DETENIDO:', error)
    except KeyboardInterrupt:
        parar()
        informe['error'] = 'Cancelado por usuario'
        print('Recorrido cancelado; salidas apagadas.')
    finally:
        parar()
        monitor.off()
    # Guardar solo con motor deshabilitado. No cambia config.py.
    import json
    try:
        with open('hall_recorrido.json', 'w') as archivo:
            json.dump(informe, archivo)
        print('Registro guardado en hall_recorrido.json (reemplaza el anterior).')
    except OSError as error:
        print('No se pudo guardar; conservar la salida de consola:', error)


def capturar_hall(sensor):
    """Dos segundos; rangos crudos y de promedios de ocho muestras."""
    total = 0
    minimo, maximo = 65535, 0
    crudo_min, crudo_max = 65535, 0
    for _ in range(100):
        muestras = [sensor.read_u16() for _ in range(8)]
        valor = sum(muestras) // 8
        total += valor
        minimo, maximo = min(minimo, valor), max(maximo, valor)
        crudo_min = min(crudo_min, min(muestras))
        crudo_max = max(crudo_max, max(muestras))
        sleep_ms(20)
    media = total // 100
    return {'media': media, 'min': minimo, 'max': maximo,
            'ruido_pp': maximo - minimo, 'crudo_min': crudo_min,
            'crudo_max': crudo_max, 'voltios_aprox': media * 3.3 / 65535}


def aprender_hall():
    parar()
    monitor.off()
    print('APRENDIZAJE HALL: desconectar potencia VM del motor; Pico por USB.')
    print('Mantener Hall alimentado a 3.3 V. Mover SOLO a mano, sin forzar engranajes.')
    print('Mantener sensor e imanes en su posicion/distancia de montaje.')
    print('Se registran lecturas; no se mueve el motor ni se cambia config.py.')
    sensor = ADC(26)
    resultados = {}
    pasos = (
        ('centro', 'Coloca el mecanismo entre extremos, sin iman enfrentado al sensor.'),
        ('extremo_1', 'Coloca el primer iman frente al Hall, en su extremo mecanico.'),
        ('extremo_2', 'Coloca el segundo iman frente al Hall, en el otro extremo.'),
    )
    try:
        for nombre, instruccion in pasos:
            print('\n', nombre, ':', instruccion)
            if input('Enter para capturar; q para cancelar: ').strip().lower() == 'q':
                print('Cancelado. No se guardo un aprendizaje nuevo.')
                return
            print('Mantener inmovil durante 2 segundos...')
            datos = capturar_hall(sensor)
            resultados[nombre] = datos
            print('Media:', datos['media'], '| min:', datos['min'], '| max:', datos['max'])
            print('Variacion pico a pico:', datos['ruido_pp'],
                  '| voltaje aproximado: {:.3f} V'.format(datos['voltios_aprox']))

        centro = resultados['centro']
        orden = sorted(('extremo_1', 'extremo_2'), key=lambda n: resultados[n]['media'])
        bajo, alto = resultados[orden[0]], resultados[orden[1]]
        separadas = bajo['max'] < centro['min'] and centro['max'] < alto['min']
        saturadas = any(d['crudo_min'] <= 100 or d['crudo_max'] >= 65435
                        for d in resultados.values())
        informe = {'version': 1, 'gpio': 26, 'referencia_v_aprox': 3.3,
                   'capturas': resultados, 'rangos_separados': separadas,
                   'cerca_de_rieles_adc': saturadas, 'validado_para_control': False}
        if separadas and not saturadas:
            informe['candidato_A_alto'] = orden[1]
            informe['candidato_B_bajo'] = orden[0]
            print('Rangos separados: candidato A (alto) =', orden[1],
                  '| candidato B (bajo) =', orden[0])
        else:
            print('REVISAR: rangos no separables alrededor del centro o ADC cerca de sus limites.')
            print('Verificar cableado, orientacion, distancia e inmovilidad; no usar para control.')
        import json
        with open('hall_aprendizaje.json', 'w') as archivo:
            json.dump(informe, archivo)
        print('Capturas guardadas en hall_aprendizaje.json (reemplaza captura anterior).')
        print('No determina Norte/Sur ni abierto/cerrado. No aplica umbrales automaticamente.')
        print('Copia las tres lecturas para revisarlas antes de mover con Hall.')
    finally:
        parar()
        monitor.off()


def medir_driver():
    parar()
    print('SOLO SIN MOTOR: quitar alimentacion, desconectar AMBOS cables del motor,')
    print('Separar AO1 de BO1 y AO2 de BO2: cuatro salidas independientes.')
    print('Mantener GND comun. Si calienta en reposo, cortar potencia y NO continuar.')
    print('Se aplicara salida continua al 100% durante', MEDICION_MS // 1000, 'segundos, SIN CARGA.')
    if input('Escribe SEPARADOS para confirmar motor fuera y salidas separadas: ').strip() != 'SEPARADOS':
        print('Medicion cancelada; salidas apagadas.')
        return
    try:
        print('Coloca las puntas: salida deshabilitada durante la cuenta regresiva.')
        print('STBY, AIN1, BIN1, PWMA, PWMB: ~3.3 V; AIN2, BIN2: ~0 V.')
        print('AO1, BO1: ~VM; AO2, BO2: ~0 V. Ctrl+C cancela.')
        for segundos in range(PREPARACION_S, 0, -1):
            print('Preparacion:', segundos, 's | STBY=0')
            sleep_ms(1000)
        print('MIDE AHORA respecto a GND del driver.')
        in1.on()
        in2.off()
        pwm.duty_u16(65535)
        inicio = ticks_ms()
        standby.on()
        ultimo_segundo = None
        while True:
            restante = MEDICION_MS - ticks_diff(ticks_ms(), inicio)
            if restante <= 0:
                break
            segundos = (restante + 999) // 1000
            if segundos != ultimo_segundo:
                print('Salida ACTIVA:', segundos, 's restantes')
                ultimo_segundo = segundos
            sleep_ms(20)
    finally:
        parar()
    print('Medicion terminada; STBY=0. Quitar potencia antes de reconectar motor.')


def main():
    parar()
    try:
        pwm.freq(20000)
        print('PRUEBA MANUAL TB6612: motor libre, sin llegar a topes.')
        print('Pulsos de', PULSO_MS, 'ms. PWM 25% -> 60%. Sin control de corriente.')
        while True:
            print('\na: automatico PC817 + Hall | 1/2: pulsos SIN HALL | g: giro SIN HALL | t: direccion con topes Hall | r: dos imanes + mediciones | h: aprender Hall | s: PC817 | c: medir SIN MOTOR | 0: salir')
            opcion = input('Opcion: ').strip().lower()
            if opcion in ('1', '2'):
                pulso(int(opcion))
                print('Pulso terminado; STBY=0, motor en rueda libre.')
            elif opcion == 's':
                leer_entrada()
            elif opcion == 'g':
                probar_giro()
            elif opcion == 'h':
                aprender_hall()
            elif opcion == 't':
                probar_topes()
            elif opcion == 'r':
                probar_recorrido()
            elif opcion == 'a':
                probar_automatico()
            elif opcion == 'c':
                medir_driver()
            elif opcion == 'm':
                parar()
                print('Prueba larga deshabilitada. Usar c SIN MOTOR y con salidas separadas.')
            elif opcion == '0':
                break
            else:
                print('Opcion no valida; motor apagado.')
    finally:
        parar()
        monitor.off()
        pwm.deinit()


if __name__ == '__main__':
    main()
