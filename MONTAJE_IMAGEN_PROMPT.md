Imagen: MONTAJE_ORIENTATIVO.png
Herramienta: image_gen integrada; generacion y correccion de etiquetas.
Uso: distribucion conceptual, NO cableado validado por orificios. Consultar ESQUEMA_FINAL.md.

Prompt inicial:

Create a high resolution Spanish electronics assembly illustration, a single landscape image with TWO large panels: left "PROTOBOARD — PRUEBAS", right "PLACA PERFORADA — VISTA SUPERIOR". Clean realistic top-down Fritzing-like technical illustration with recognizable components, large legible labels, white background. Show proposed physical component placement for a Raspberry Pi Pico automotive actuator controller. THIS IS A LAYOUT GUIDE NOT A VERIFIED HOLE-BY-HOLE WIRING PLAN. Prominent subtitle "Distribución orientativa. Cablear por nombre de pin según ESQUEMA_FINAL.md." Do not invent pin locations or breadboard hole coordinates.
Both panels contain a green Raspberry Pi Pico with USB accessible and socket headers, two PC817 DIP4 optocouplers in separate labeled input and monitor zones, red and green LEDs each with 1k resistor, signal connectors for external Hall SS49E and C1442, voltage divider small section, a TB6612FNG module, and TWO blue LM2596 modules clearly labeled "12 V MOTOR" and "5 V LÓGICA". No LM393, no shunt, no current sensor, no relay. SS49E is EXTERNAL in original actuator case, show cable exiting to a small sensor illustration labeled "SS49E en carcasa".
LEFT: one large white solderless breadboard carries Pico, low-current signal circuits and LEDs only. BOTH regulators and TB6612 motor module are OUTSIDE the solderless board on separate supported mounting areas with screw terminals. Heavy motor power connections run outside breadboard, do not pass through breadboard contacts. DC motor icon exterior with 100nF across its terminals. Black common ground star terminal outside breadboard. Label "Potencia fuera de la protoboard". Clearly distinguish 3.3V, 5V and 12V, NEVER 12V to breadboard logic rail. Show logical harness bundles terminated at labeled modules rather than misleading dense invented hole-level wiring.
RIGHT: tan perfboard with isolated copper pads, no continuous stripboard tracks, TOP component side, Pico on female header sockets, PC817 sockets, resistor groups, LED indicators, Hall and PCM connectors. Two buck modules mounted with standoffs away from signal region. TB6612 near motor screw terminal with adjacent 470uF/25V and 100nF. Power wiring thick insulated soldered wire; signal wiring thin. A callout "Puentes soldados por debajo; pads aislados" indicates underside bridges without inventing a mirrored underside map. Keep motor power return separate to common star ground. Show +5V through SS14 diode with band toward Pico VSYS, label "+5 V → SS14 → VSYS".
Bottom neat connection reference table across page, accurate text:
"GP2 → AIN1 + BIN1 | GP3 → AIN2 + BIN2"
"GP4 → PWMA + PWMB | GP5 → STBY; 10k a GND"
"AO1 + BO1 → M1 | AO2 + BO2 → M2"
"3V3 → VCC TB6612 y SS49E | GP26 ← Hall | GP28 ← divisor VM"
"GP15 ← PC817 entrada | GP18 → Monitor | GP16 verde | GP17 rojo"
"C1442: 1 VPWR · 2 GND · 3 CMCV · 4 CMCVM"
Small zone callouts:
"Entrada: 10k + PC817 + diodo antiparalelo"
"Monitor: PC817 + 2N5551; verificar E/B/C"
"Divisor VM: 100k / 22k → 1k → GP28; 10nF a GND"
"Hall: OUT → 1k → GP26; 100k y 10nF a GND"
show remaining signal parts as grouped components no fake pin precise connections. Draw upstream power source as "Alimentación de banco / entrada protegida" with fuse icon, NOT bare automotive battery direct. Footer "Sin corte por sobrecorriente. Confirmar pinout real de los módulos antes de conectar." Layout practical, organized, visibly separate power and signal, color legend red12V orange5V purple3V3 blackGND blue signals. Accurate readable Spanish, no claims of verified assembly, no decorative unrelated objects.

Correccion final solicitada: USB a 5 V; fusible con valor por definir; no pasar corriente del motor por protoboard; indicar que las posiciones de pines y orificios son ilustrativas. Conservar ambas distribuciones y las tablas.
