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

async function getImageLink(card_vectors, card_name) {
    try {
    const card = card_vectors[card_name];
    return card["img_src"];
    } catch (error) {
        console.error('Failed to get image:', error);
    }
}

function from_cluster_labels(cluster_labels) {
    const legend = document.getElementById("legend");
    legend.innerHTML = "";

    for (const [color, label] of cluster_labels) {
        const p = document.createElement("div");
        p.style.color = color;
        p.textContent = label;
        legend.appendChild(p);
    }
}

function from_card_vectors(card_vectors) {
    const cardInfoDiv = document.getElementById("card_map");
    hoverLabel = document.getElementById("hover_label");
    hoverImage = document.getElementById("hover_img")
    const graph = new VectorGraph("#card_map", card_vectors, {
        defaultRadius: 20,
        repulsion: 400,
        autoEdgeThresh: 0.40,
        drawImage: false,
        padding: 50,
        drawLabel: false,
            onHover: async (cardName) => {
                if (cardName) {
                    hoverLabel.innerHTML = `${cardName}`; // Show card name on hover
                    hoverImage.src = await getImageLink(card_vectors, cardName);
                } else {
                    hoverLabel.innerHTML = ""; // Clear label when not hovering
                    hoverImage.src = "";
                }
            }
    });

    graph.start();
    console.log("Graph started");

    window.addEventListener("resize", async() => {
        graph.resize(cardInfoDiv.clientWidth, cardInfoDiv.clientHeight)
    })

    return graph;
}

(async () => {
    try {
        const response = await fetch(`/myapp/load_session/`);
        const data = await response.json();
        if (data["status"] === "found") {
            console.log("Session found, loading graph...");
            const card_vectors = data["cluster"];
            from_card_vectors(card_vectors);

            const cluster_labels = data["cluster_labels"];
            from_cluster_labels(cluster_labels);
        } else {
            console.log("No session found, waiting for user input...");
        }
    } catch (error) {
        console.error("Error loading session:", error);
    }
})();