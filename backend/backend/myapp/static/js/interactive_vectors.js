async function fetchCardVectors(decklist) {
    const response = await fetch(`/myapp/get_card_vectors/${encodeURIComponent(decklist)}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch vectors for decklist: ${decklist}`);
    }
    return await response.json();
}

const url = document.getElementById("decklist_link");
const start_button = document.getElementById("start");

let card_vectors = null;

start_button.addEventListener("click", async () => {
    try {
        // Add loading animation in the card_info div
        const cardInfoDiv = document.getElementById("card_info");
        cardInfoDiv.innerHTML = "<p>Loading...</p>";

        // Display the Vector Graph
        card_vectors = await fetchCardVectors(url.value);
        console.log("Card vectors:", card_vectors);
        hoverLabel = document.getElementById("hover_label");
        const graph = new VectorGraph("#card_info", card_vectors, {
            defaultRadius: 10,
            repulsion: 1000,
            autoEdgeThresh: 0.1
        });
        graph.start();
        console.log("Graph started");

    } catch (error) {
        console.error("Error fetching card names:", error);
    }
});