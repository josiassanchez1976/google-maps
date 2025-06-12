let map;
let markers = [];
let resultsData = [];

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 28.54, lng: -81.38 },
        zoom: 6
    });
}

function clearMarkers() {
    for (const m of markers) {
        m.setMap(null);
    }
    markers = [];
}

function addMarkers(data) {
    clearMarkers();
    for (const item of data) {
        const position = { lat: item.lat, lng: item.lng };
        const marker = new google.maps.Marker({
            position,
            map,
            title: item.name
        });
        const infowindow = new google.maps.InfoWindow({
            content: `<b>${item.name}</b><br>${item.address}<br>${item.category}`
        });
        marker.addListener('click', () => infowindow.open({anchor: marker, map}));
        markers.push(marker);
    }
    if (data.length > 0) {
        map.setCenter({ lat: data[0].lat, lng: data[0].lng });
    }
}

function populateTable(data) {
    const tbody = document.querySelector('#resultsTable tbody');
    tbody.innerHTML = '';
    for (const item of data) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.name}</td>
            <td>${item.phone || ''}</td>
            <td>${item.address}</td>
            <td>${item.place_id}</td>
            <td>
                <a class="btn btn-sm btn-primary me-1" href="https://www.google.com/maps/search/?api=1&query=place_id=${item.place_id}" target="_blank">Ver en Google Maps</a>
                <button class="btn btn-sm btn-danger me-1 delete-btn">Eliminar</button>
                <button class="btn btn-sm btn-secondary copy-btn">Copiar</button>
            </td>`;
        row.querySelector('.delete-btn').addEventListener('click', () => row.remove());
        row.querySelector('.copy-btn').addEventListener('click', () => {
            navigator.clipboard.writeText(`${item.name}\n${item.address}\n${item.phone || ''}`);
        });
        tbody.appendChild(row);
    }
}

$(function() {
    initMap();
    $('#searchForm').on('submit', function(e) {
        e.preventDefault();
        $.post('/search', $(this).serialize(), function(data) {
            resultsData = data;
            addMarkers(data);
            populateTable(data);
        });
    });

    $('#exportBtn').on('click', function() {
        const blob = new Blob([JSON.stringify(resultsData, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'results.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });

});
