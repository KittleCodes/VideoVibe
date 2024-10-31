async function getRecommendations(videoId, amount = 10, cursor = null) {
    const url = 'http://127.0.0.1:8000/recommendation/get_recommendations';

    const payload = {
        video_id: videoId,
        amount: amount,
        cursor: cursor
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error:', errorData.message);
            return;
        }

        const data = await response.json();
        const recommendations = data.recommendations;

        console.log('Recommendations:', recommendations);

        displayRecommendations(recommendations);

        const nextCursor = data.next_cursor;
        if (nextCursor) {
            console.log('Next cursor for pagination:', nextCursor);
        }
        
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('relatedVideos');

    recommendations.forEach(function (recommendation) {
        const cardTemplate = document.getElementById('relatedVideoTemplate');
        const card = cardTemplate.cloneNode(true);

        card.style.display = 'block';
        console.log(recommendation);
        card.id = recommendation.token;
        card.querySelector('img').parentElement.href = `/video/${recommendation.token}`;
        card.querySelector('img').src = `http://127.0.0.1:8000/video/dash/${recommendation.token}/${recommendation.token}.jpg`;
        card.querySelector('.card-title').parentElement.href = `/video/${recommendation.token}`;
        card.querySelector('.card-title').textContent = recommendation.title || "Video Title";
        card.querySelector('.card-subtitle').parentElement.href = `/channel/${recommendation.author_id}`;
        card.querySelector('.card-subtitle').textContent = `${recommendation.name} (@${recommendation.username})` || "Channel Name";

        container.appendChild(card);
    });
}
