document.addEventListener('DOMContentLoaded', function () {
    const map = L.map('map').setView([20.5937, 78.9629], 5); // Centered on India
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const redIcon = new L.Icon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png', shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png', iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41] });

    const reportMarkers = L.layerGroup().addTo(map);

    function addMarkerToMap(report) {
        const marker = L.marker([report.lat, report.lon], { icon: redIcon }).addTo(reportMarkers);

        let popupContent = `<b>Status:</b> ${report.status}<br><b>Reported as:</b> ${report.animal}`;
        if (report.ai_suggestion) {
            popupContent += `<br><b>AI Suggestion:</b> ${report.ai_suggestion}`;
        }
        popupContent += `<br><b>Time:</b> ${report.time}`;
        if (report.desc) {
            popupContent += `<br><b>Description:</b> ${report.desc}`;
        }
        if (report.image_url) {
            popupContent += `<br><img src="${report.image_url}" alt="Incident Image" style="width:150px;height:auto;margin-top:5px;">`;
        }

        marker.bindPopup(popupContent);
    }

    // Initial Load of existing reports
    fetch('/api/reports')
        .then(response => response.json())
        .then(reports => {
            reports.forEach(addMarkerToMap);
        });

    // Real-Time Updates with WebSockets
    const socket = io();
    socket.on('new_report', function(report) {
        addMarkerToMap(report);
        map.panTo([report.lat, report.lon]);
    });

    // Form Handling for New Reports
    const locationStatus = document.getElementById('locationStatus');
    const latInput = document.getElementById('latitude');
    const lonInput = document.getElementById('longitude');
    const submitBtn = document.getElementById('submitBtn');
    let manualMarker = null;

    function updateLocation(lat, lon, message) {
        latInput.value = lat;
        lonInput.value = lon;
        locationStatus.textContent = message;
        locationStatus.style.color = 'green';
        submitBtn.disabled = false;

        if (manualMarker) {
            map.removeLayer(manualMarker);
        }

        manualMarker = L.marker([lat, lon]).addTo(map).bindPopup('New Incident Location').openPopup();
        map.setView([lat, lon], 15);
    }

    document.getElementById('useLocationBtn').addEventListener('click', () => {
        locationStatus.textContent = 'Getting location...';
        navigator.geolocation.getCurrentPosition(position => {
            updateLocation(position.coords.latitude, position.coords.longitude, `Current location captured.`);
        }, () => {
            locationStatus.textContent = 'Could not get your location. Please click on the map.';
            locationStatus.style.color = 'red';
        });
    });

    map.on('click', e => {
        updateLocation(e.latlng.lat, e.latlng.lng, `Manual location selected.`);
    });
});

// Camera functionality
let stream = null;

function openCamera() {
    const video = document.getElementById('camera');
    const captureBtn = document.getElementById('captureBtn');
    
    video.style.display = 'block';
    captureBtn.style.display = 'block';
    
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(function(s) {
            stream = s;
            video.srcObject = stream;
        })
        .catch(function(err) {
            alert('Camera access denied or not available');
            video.style.display = 'none';
            captureBtn.style.display = 'none';
        });
}

function captureImage() {
    const video = document.getElementById('camera');
    const canvas = document.getElementById('canvas');
    const preview = document.getElementById('preview');
    const captureBtn = document.getElementById('captureBtn');
    const retakeBtn = document.getElementById('retakeBtn');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    canvas.toBlob(function(blob) {
        const file = new File([blob], "captured_image.jpg", { type: "image/jpeg" });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        document.getElementById('image').files = dataTransfer.files;
        
        preview.src = URL.createObjectURL(blob);
        preview.style.display = 'block';
    }, 'image/jpeg');
    
    // Stop camera
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    video.style.display = 'none';
    captureBtn.style.display = 'none';
    retakeBtn.style.display = 'block';
}

function retakePhoto() {
    const preview = document.getElementById('preview');
    const retakeBtn = document.getElementById('retakeBtn');
    
    preview.style.display = 'none';
    retakeBtn.style.display = 'none';
    document.getElementById('image').value = '';
    
    openCamera();
}