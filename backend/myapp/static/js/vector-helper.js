const url = document.getElementById("decklist_url");
const start_button = document.getElementById("submit");

start_button.addEventListener("click", async (event) => {
    const [overlay, popup] = await create_loading_popup();
    try {

        if (!((url.value.includes("moxfield") && developing_locally) ||
               url.value.includes("archidekt"))) {
            throw(new Error("Only Archidekt links are supported."));
        }

        popup.innerHTML = "Fetching decklist...";
        decklist = await fetchDecklist(url.value);

        popup.innerHTML = "Clustering cards...";
        await fetchClusters();

        popup.innerHTML = "Fetching cluster labels...";
        await fetchClusterLabels();

        // Save recent deck
        await saveRecentDeck();

        // Redirect to dashboard after loading
        window.location.href = "/dashboard/";

        popup.remove();
        overlay.remove();
    } catch (error) {
        popup.remove()
        overlay.remove()
        Toastify({
            text: error,
            duration: 3000,
            gravity: "top", // `top` or `bottom`
            position: "center", // `left`, `center` or `right`
            stopOnFocus: true, // Prevents dismissing of toast on hover
            style: {
                background: "white",
                color: "red",
            },
            onClick: function(){} // Callback after click
            }).showToast();
    } finally {
        url.value="";
    }
});

const developing_locally = (async () => {
    const response = await fetch(`/myapp/developing_locally/`);
    if (!response.ok) {
        throw new Error(`Failed to check local development status.`);
    }
    const localDevelopment = await response.json();
    return localDevelopment === "true";
})();

async function create_loading_popup() {
    // Create gray overlay
    const body = document.getElementsByTagName('body')[0];
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    body.appendChild(overlay);
    
    // Create loading popup
    const popup = document.createElement('div');
    popup.className = 'loading-popup';
    overlay.appendChild(popup);

    return [overlay, popup];
};

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

async function fetchCardVectors(decklist) {
    const response = await fetch(`/myapp/get_card_vectors/${encodeURIComponent(decklist)}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch vectors for decklist: ${decklist}`);
    }
    return await response.json();
}

async function fetchClusters() {
    const response = await fetch(`/myapp/cluster_decklist/`);
    if (!response.ok) {
        throw new Error(`Failed to fetch clusters for decklist.`);
    }
    return await response.json();
}

async function fetchClusterLabels() {
    const response = await fetch(`/myapp/get_cluster_labels/`);
    if (!response.ok) {
        throw new Error(`Failed to fetch cluster labels for decklist.`);
    }
    return await response.json();
}

async function fetchRecentDecks() {
    const response = await fetch(`/myapp/get_recents/`)
    if (!response.ok) {
        throw new Error(`Failed to fetch recent decklists.`);
    }
    return await response.json();
}

async function loadRecentDeck(loc) {
    const response = await fetch(`/myapp/load_from_recents/${loc}`);
    window.location.href = "/dashboard/";
}

async function saveRecentDeck() {
    const response = await fetch(`/myapp/save_to_recents/`);
}