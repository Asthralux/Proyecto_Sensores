<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoreo de Datos Eléctricos</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@^1.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
</head>

<body>

<canvas id="voltajeChart" width="800" height="400"></canvas>
<canvas id="corrienteChart" width="800" height="400"></canvas>
<canvas id="potenciaActivaChart" width="800" height="400"></canvas>
<canvas id="potenciaReactivaChart" width="800" height="400"></canvas>
<canvas id="factorDePotenciaChart" width="800" height="400"></canvas>
<canvas id="frecuenciaChart" width="800" height="400"></canvas>

<?php
$host = 'localhost';
$user = 'daniel';
$pass = '123';
$db = 'Sensor';

$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    die("Falla en la Conexión: " . $conn->connect_error);
}

if (isset($_GET['voltaje']) && isset($_GET['corriente']) && isset($_GET['potencia_activa']) && isset($_GET['potencia_reactiva']) && isset($_GET['factor_de_potencia']) && isset($_GET['frecuencia'])) {
    $voltaje = $_GET['voltaje'];
    $corriente = $_GET['corriente'];
    $potencia_activa = $_GET['potencia_activa'];
    $potencia_reactiva = $_GET['potencia_reactiva'];
    $factor_de_potencia = $_GET['factor_de_potencia'];
    $frecuencia = $_GET['frecuencia'];

    $sql = "INSERT INTO Datos (voltaje, corriente, potencia_activa, potencia_reactiva, factor_de_potencia, frecuencia) VALUES ('$voltaje', '$corriente', '$potencia_activa', '$potencia_reactiva', '$factor_de_potencia', '$frecuencia')";

    if ($conn->query($sql) === TRUE) {
        echo "Datos insertados con exitosamente<br>";
    } else {
        echo "Error: " . $sql . "<br>" . $conn->error . "<br>";
    }
}

$query = "SELECT * FROM Datos";
$result = $conn->query($query);

$fechaHora = [];
$voltajes = [];
$corrientes = [];
$potencias_activas = [];
$potencias_reactivas = [];
$factores_de_potencia = [];
$frecuencias = [];

while ($row = $result->fetch_assoc()) {
    $fechaHora[] = $row["fecha_hora"];
    $voltajes[] = $row["voltaje"];
    $corrientes[] = $row["corriente"];
    $potencias_activas[] = $row["potencia_activa"];
    $potencias_reactivas[] = $row["potencia_reactiva"];
    $factores_de_potencia[] = $row["factor_de_potencia"];
    $frecuencias[] = $row["frecuencia"];
}

$fechaHora_json = json_encode($fechaHora);
$voltajes_json = json_encode($voltajes);
$corrientes_json = json_encode($corrientes);
$potencias_activas_json = json_encode($potencias_activas);
$potencias_reactivas_json = json_encode($potencias_reactivas);
$factores_de_potencia_json = json_encode($factores_de_potencia);
$frecuencias_json = json_encode($frecuencias);

$conn->close();
?>

<script>
    let fechaHora = <?php echo $fechaHora_json; ?>;
    let voltajes = <?php echo $voltajes_json; ?>;
    let corrientes = <?php echo $corrientes_json; ?>;
    let potencias_activas = <?php echo $potencias_activas_json; ?>;
    let potencias_reactivas = <?php echo $potencias_reactivas_json; ?>;
    let factores_de_potencia = <?php echo $factores_de_potencia_json; ?>;
    let frecuencias = <?php echo $frecuencias_json; ?>;


const options = {
    scales: {
        x: {
            type: 'time',
            time: {
                unit: 'minute'
            }
        }
    }
};

new Chart(document.getElementById('voltajeChart'), {
    type: 'line',
    data: {
        labels: fechaHora,
        datasets: [{
            label: 'Voltaje',
            data: voltajes,
            borderColor: '#00c1d5',
            fill: false
        }]
    },
    options: options
});

new Chart(document.getElementById('corrienteChart'), {
    type: 'line',
    data: {
        labels: fechaHora,
        datasets: [{
            label: 'Corriente',
            data: corrientes,
            borderColor: '#f37121',
            fill: false
        }]
    },
    options: options
});

new Chart(document.getElementById('potenciaActivaChart'), {
    type: 'line',
    data: {
        labels: fechaHora,
        datasets: [{
            label: 'Potencia Activa',
            data: potencias_activas,
            borderColor: '#0a74da',
            fill: false
        }]
    },
    options: options
});

new Chart(document.getElementById('potenciaReactivaChart'), {
    type: 'line',
    data: {
        labels: fechaHora,
        datasets: [{
            label: 'Potencia Reactiva',
            data: potencias_reactivas,
            borderColor: '#33cc33',
            fill: false
        }]
    },
    options: options
});

new Chart(document.getElementById('factorDePotenciaChart'), {
    type: 'line',
    data: {
        labels: fechaHora,
        datasets: [{
            label: 'Factor de Potencia',
            data: factores_de_potencia,
            borderColor: '#9900cc',
            fill: false
        }]
    },
    options: options
});

new Chart(document.getElementById('frecuenciaChart'), {
    type: 'line',
    data: {
        labels: fechaHora,
        datasets: [{
            label: 'Frecuencia',
            data: frecuencias,
            borderColor: '#f0db4f',
            fill: false
        }]
    },
    options: options
});
</script>

</body>
</html>