async function fetchCardVectors(decklist) {
    const response = await fetch(`/myapp/get_card_vectors/${encodeURIComponent(decklist)}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch vectors for decklist: ${decklist}`);
    }
    return await response.json();
}

async function fetchDecklist(url) {
    const response = await fetch(`/myapp/get_decklist/${encodeURIComponent(url)}`);
    const body = await response.text();

    if (!response.ok) {
        let errorText = body;
        try {errorText = JSON.stringify(JSON.parse(body));} catch (_) {}
        throw new Error(`Failed to fetch card names for decklist: ${url}. Server replied: ${errorText}`);
    }

    // If OK, then try to parse JSON from the body we already read
    try {
        return JSON.parse(body);
    } 
    catch (e) {
        throw new Error(`Invalid JSON returned from server: ${body}`);
    }
}

async function fetchClusters() {
    const response = await fetch(`/myapp/cluster_decklist/`);
    if (!response.ok) {
        throw new Error(`Failed to fetch clusters for decklist.`);
    }
    return await response.json();
}

async function fetchClusterLabels(decklist) {
    const response = await fetch(`/myapp/get_cluster_labels/`);
    if (!response.ok) {
        throw new Error(`Failed to fetch cluster labels for decklist.`);
    }
    return await response.json();
}

const url = document.getElementById("decklist_link");
const start_button = document.getElementById("start");

let card_vectors = null;

function loading_animation(element, untilCondition = () => false) {
    const animation = ["Loading", "Loading.", "Loading..", "Loading..."];
    let index = 0;
    const intervalId = setInterval(() => {
        if (untilCondition()) {
            clearInterval(intervalId);
            return;
        }
        element.innerHTML = animation[index];
        index = (index + 1) % animation.length;
    }, 500);
    return () => clearInterval(intervalId); // Return a function to stop the animation
}

async function loadData() {
  try {
    const response = await fetch('static/json/oracle_cards.json');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to load JSON:', error);
  }
}

(async () => {
  cardData = await loadData();
  console.log(cardData); // now is the array
})();

// console.log(cardData);

async function getImageLink(card_name) {
    try {
    const card = cardData.find(item => item.name === card_name);
    return card.image_uris.normal;
    } catch (error) {
        console.error('Failed to get image:', error);
    }
}

start_button.addEventListener("click", async () => {
    try {
        // Add loading animation in the card_info div
        const cardInfoDiv = document.getElementById("card_map");
        const status = document.getElementById("status");
        status.innerHTML = "Status: Fetching Decklist...";

        // Get and display decklist
        card_names = await fetchDecklist(url.value);
        card_names = card_names["card_names"]

        status.innerHTML = "Status: Clustering Data...";

        // Get and display clusters
        card_vectors = await fetchClusters()
        hoverLabel = document.getElementById("hover_label");
        hoverImage = document.getElementById("hover_img")
        const graph = new VectorGraph("#card_map", card_vectors, {
            defaultRadius: 20,
            repulsion: 3000,
            autoEdgeThresh: 0.1,
            padding: 120,
            drawLabel: false,
                onHover: async (cardName) => {
                    if (cardName) {
                        hoverLabel.innerHTML = `${cardName}`; // Show card name on hover
                        hoverImage.src = await getImageLink(cardName);
                    } else {
                        hoverLabel.innerHTML = ""; // Clear label when not hovering
                        hoverImage.src = "";
                    }
                }
        });

        graph.start();
        console.log("Graph started");

        const cluster_labels = await fetchClusterLabels();
        const legend = document.getElementById("legend");

        legend.innerHTML = "";

        for (const [color, label] of cluster_labels) {
            const p = document.createElement("div");
            p.style.color = color;
            p.textContent = label;
            legend.appendChild(p);
        }

        status.innerHTML = "";

    } catch (error) {
        console.error("Error fetching card names:", error);
        const status = document.getElementById("status");
        status.innerHTML = "<p>Status: Failed</p>";
    }
});