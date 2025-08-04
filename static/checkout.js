// Sistema de Metro de la Ciudad de México
const METRO_LINES = {
    "linea1": {
        name: "🚇 Línea 1 (Rosa) - Pantitlán ↔ Observatorio",
        color: "#f472b6",
        stations: [
            "Pantitlán", "Zaragoza", "Gómez Farías", "Boulevard Puerto Aéreo", "Balbuena", 
            "Moctezuma", "San Lázaro", "Candelaria", "Merced", "Pino Suárez", 
            "Isabel la Católica", "Salto del Agua", "Balderas", "Cuauhtémoc", "Insurgentes", 
            "Sevilla", "Chapultepec", "Juanacatlán", "Tacubaya", "Observatorio"
        ]
    },
    "linea2": {
        name: "🚇 Línea 2 (Azul) - Cuatro Caminos ↔ Tasqueña",
        color: "#3b82f6",
        stations: [
            "Cuatro Caminos", "Panteones", "Tacuba", "Cuitláhuac", "Popotla", 
            "Colegio Militar", "Normal", "San Cosme", "Revolución", "Hidalgo", 
            "Bellas Artes", "Allende", "Zócalo/Tenochtitlan", "Pino Suárez", "San Antonio Abad", 
            "Chabacano", "Viaducto", "Xola", "Villa de Cortés", "Nativitas", 
            "Portero", "Ermita", "General Anaya", "Tasqueña"
        ]
    },
    "linea3": {
        name: "🚇 Línea 3 (Verde Olivo) - Indios Verdes ↔ Universidad",
        color: "#84cc16",
        stations: [
            "Indios Verdes", "Deportivo 18 de Marzo", "Potrero", "La Raza", "Tlatelolco", 
            "Guerrero", "Hidalgo", "Juárez", "Balderas", "Niños Héroes", 
            "Hospital General", "Centro Médico", "Etiopía/Plaza de la Transparencia", "Eugenia", "División del Norte", 
            "Zapata", "Coyoacán", "Viveros/Derechos Humanos", "Miguel Ángel de Quevedo", "Copilco", "Universidad"
        ]
    },
    "linea4": {
        name: "🚇 Línea 4 (Aqua / Cian) - Martín Carrera ↔ Santa Anita",
        color: "#06b6d4",
        stations: [
            "Martín Carrera", "Talismán", "Bondojito", "Consulado", "Canal del Norte", 
            "Morelos", "Candelaria", "Fray Servando", "Jamaica", "Santa Anita"
        ]
    },
    "linea5": {
        name: "🚇 Línea 5 (Amarilla) - Pantitlán ↔ Politécnico",
        color: "#eab308",
        stations: [
            "Pantitlán", "Hangares", "Terminal Aérea", "Oceanía", "Aragón", 
            "Eduardo Molina", "Consulado", "Valle Gómez", "Misterios", "La Raza", 
            "Autobuses del Norte", "Instituto del Petróleo", "Politécnico"
        ]
    },
    "linea6": {
        name: "🚇 Línea 6 (Rojo Oscuro) - El Rosario ↔ Martín Carrera",
        color: "#dc2626",
        stations: [
            "El Rosario", "Tezozómoc", "UAM-Azcapotzalco", "Ferrería/Arena Ciudad de México", "Norte 45", 
            "Vallejo", "Instituto del Petróleo", "Lindavista", "Deportivo 18 de Marzo", "La Villa-Basílica", "Martín Carrera"
        ]
    },
    "linea7": {
        name: "🚇 Línea 7 (Naranja) - El Rosario ↔ Barranca del Muerto",
        color: "#ea580c",
        stations: [
            "El Rosario", "Aquiles Serdán", "Camarones", "Refinería", "Tacuba", 
            "San Joaquín", "Polanco", "Auditorio", "Constituyentes", "Tacubaya", 
            "San Pedro de los Pinos", "San Antonio", "Mixcoac", "Barranca del Muerto"
        ]
    },
    "linea8": {
        name: "🚇 Línea 8 (Verde Bandera) - Garibaldi/Lagunilla ↔ Constitución de 1917",
        color: "#16a34a",
        stations: [
            "Garibaldi/Lagunilla", "Bellas Artes", "San Juan de Letrán", "Salto del Agua", "Doctores", 
            "Obrera", "Chabacano", "La Viga", "Santa Anita", "Coyuya", 
            "Iztacalco", "Apatlaco", "Aculco", "Escuadrón 201", "Atlalilco", 
            "Iztapalapa", "Cerro de la Estrella", "UAM-I", "Constitución de 1917"
        ]
    },
    "linea9": {
        name: "🚇 Línea 9 (Café) - Pantitlán ↔ Tacubaya",
        color: "#a16207",
        stations: [
            "Pantitlán", "Puebla", "Ciudad Deportiva", "Velódromo", "Mixiuhca", 
            "Jamaica", "Chabacano", "Lázaro Cárdenas", "Centro Médico", "Chilpancingo", "Patriotismo", "Tacubaya"
        ]
    },
    "lineaA": {
        name: "🚇 Línea A (Morado) - Pantitlán ↔ La Paz",
        color: "#9333ea",
        stations: [
            "Pantitlán", "Agrícola Oriental", "Canal de San Juan", "Tepalcates", "Guelatao", 
            "Peñón Viejo", "Acatitla", "Santa Marta", "Los Reyes", "La Paz"
        ]
    },
    "lineaB": {
        name: "🚇 Línea B (Verde-Gris) - Buenavista ↔ Ciudad Azteca",
        color: "#059669",
        stations: [
            "Buenavista", "Guerrero", "Garibaldi", "Lagunilla", "Tepito", 
            "Morelos", "San Lázaro", "Ricardo Flores Magón", "Romero Rubio", "Oceanía", 
            "Deportivo Oceanía", "Bosque de Aragón", "Villa de Aragón", "Nezahualcóyotl", "Impulsora", 
            "Río de los Remedios", "Múzquiz", "Ciudad Azteca"
        ]
    },
    "linea12": {
        name: "🚇 Línea 12 (Dorada) - Mixcoac ↔ Tláhuac",
        color: "#d97706",
        stations: [
            "Mixcoac", "Insurgentes Sur", "Hospital 20 de Noviembre", "Zapata", "Parque de los Venados", 
            "Eje Central", "Ermita", "Mexicaltzingo", "Atlalilco", "Culhuacán", 
            "San Andrés Tomatlán", "Lomas Estrella", "Calle 11", "Periférico Oriente", "Tezonco", 
            "Olivos", "Nopalera", "Zapotitlán", "Tlaltenco", "Tláhuac"
        ]
    }
};

let selectedLine = null;
let selectedStation = null;

// Cargar líneas del metro al inicializar
document.addEventListener('DOMContentLoaded', function() {
    loadMetroLines();
    loadTimeSlots();
    setupFormValidation();
    
    // Agregar event listener para zona personalizada
    document.getElementById('custom_zone').addEventListener('input', validateCustomZone);
});

function loadMetroLines() {
    const linesContainer = document.getElementById('metro-lines');
    linesContainer.innerHTML = '';
    
    Object.keys(METRO_LINES).forEach(lineId => {
        const line = METRO_LINES[lineId];
        const lineElement = document.createElement('div');
        lineElement.className = 'metro-line';
        lineElement.style.borderLeft = `4px solid ${line.color}`;
        lineElement.innerHTML = line.name;
        lineElement.onclick = () => selectLine(lineId);
        linesContainer.appendChild(lineElement);
    });
}

function selectLine(lineId) {
    // Remover selección anterior
    document.querySelectorAll('.metro-line').forEach(el => el.classList.remove('selected'));
    
    // Seleccionar nueva línea
    selectedLine = lineId;
    event.target.classList.add('selected');
    
    // Cargar estaciones de la línea seleccionada
    loadStations(lineId);
}

function loadStations(lineId) {
    const stationsContainer = document.getElementById('metro-stations');
    stationsContainer.innerHTML = '';
    
    const line = METRO_LINES[lineId];
    line.stations.forEach(station => {
        const stationElement = document.createElement('div');
        stationElement.className = 'station-option';
        stationElement.innerHTML = station;
        stationElement.onclick = () => selectStation(station, line.name);
        stationsContainer.appendChild(stationElement);
    });
}

function selectStation(station, lineName) {
    // Remover selección anterior
    document.querySelectorAll('.station-option').forEach(el => el.classList.remove('selected'));
    
    // Seleccionar nueva estación
    selectedStation = station;
    event.target.classList.add('selected');
    
    // Mostrar estación seleccionada
    const stationText = `${station} (${lineName})`;
    document.getElementById('final-location').value = stationText;
    document.getElementById('station-name').textContent = stationText;
    document.getElementById('selected-station-display').style.display = 'block';
    
    // Validar formulario
    validateForm();
}

// Nueva función para cambiar entre tipos de ubicación
function toggleLocationMethod() {
    const locationType = document.querySelector('input[name="location_type"]:checked').value;
    const metroSection = document.getElementById('metro-selection');
    const customSection = document.getElementById('custom-location');
    const finalLocation = document.getElementById('final-location');
    
    if (locationType === 'metro') {
        metroSection.style.display = 'block';
        customSection.style.display = 'none';
        // Limpiar zona personalizada
        document.getElementById('custom_zone').value = '';
        // Validar si hay estación seleccionada
        if (selectedStation) {
            validateForm();
        } else {
            finalLocation.value = '';
            validateForm();
        }
    } else {
        metroSection.style.display = 'none';
        customSection.style.display = 'block';
        // Limpiar selección de metro
        selectedStation = null;
        finalLocation.value = '';
        document.getElementById('selected-station-display').style.display = 'none';
        validateForm();
    }
}

// Nueva función para validar zona personalizada
function validateCustomZone() {
    const customZone = document.getElementById('custom_zone').value.trim();
    const finalLocation = document.getElementById('final-location');
    
    if (customZone) {
        finalLocation.value = customZone;
    } else {
        finalLocation.value = '';
    }
    
    validateForm();
}

function loadTimeSlots() {
    const timeSelect = document.getElementById('delivery_time');
    timeSelect.innerHTML = '<option value="">Selecciona una hora...</option>';
    
    // Horarios típicos de entrega (se pueden personalizar basado en la configuración del admin)
    const timeSlots = [
        '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
        '15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
        '18:00', '18:30', '19:00', '19:30', '20:00'
    ];
    
    timeSlots.forEach(time => {
        const option = document.createElement('option');
        option.value = time;
        option.textContent = time;
        timeSelect.appendChild(option);
    });
}

function setupFormValidation() {
    const form = document.getElementById('checkout-form');
    const submitBtn = document.getElementById('submit-btn');
    const requiredFields = ['delivery_day', 'delivery_time', 'delivery_station'];
    
    // Validar cuando cambien los campos
    requiredFields.forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.addEventListener('change', validateForm);
        }
    });
    
    function validateForm() {
        let isValid = true;
        
        requiredFields.forEach(fieldName => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (!field || !field.value.trim()) {
                isValid = false;
            }
        });
        
        submitBtn.disabled = !isValid;
        
        if (isValid) {
            submitBtn.textContent = '🚀 CONFIRMAR PEDIDO';
        } else {
            submitBtn.textContent = '⚠️ Completa todos los campos';
        }
    }
}

// Validación en tiempo real
document.getElementById('delivery_day').addEventListener('change', function() {
    validateForm();
});

document.getElementById('delivery_time').addEventListener('change', function() {
    validateForm();
});

function validateForm() {
    const day = document.getElementById('delivery_day').value;
    const time = document.getElementById('delivery_time').value;
    const location = document.getElementById('final-location').value;
    const submitBtn = document.getElementById('submit-btn');
    
    if (day && time && location) {
        submitBtn.disabled = false;
        submitBtn.textContent = '🚀 CONFIRMAR PEDIDO';
        submitBtn.style.background = '#003300';
        submitBtn.style.color = '#00ff00';
    } else {
        submitBtn.disabled = true;
        submitBtn.textContent = '⚠️ Completa todos los campos';
        submitBtn.style.background = '#444';
        submitBtn.style.color = '#666';
    }
}
