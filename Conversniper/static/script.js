function findInterests() {
    const content = document.getElementById('contentInput').value;
    fetch('/find_interests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `content=${encodeURIComponent(content)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        document.getElementById('contentText').textContent = data.content;
        document.getElementById('responseText').textContent = data.response;
        document.getElementById('responseDisplay').style.display = 'block';
    })
    .catch(error => console.error('Error:', error));
}

function showInsights() {
    fetch('/show_insights')
    .then(response => response.text())
    .then(html => {
        document.getElementById('insightsDisplay').innerHTML = html;
        document.getElementById('insightsDisplay').style.display = 'block';
    })
    .catch(error => console.error('Error:', error));
}