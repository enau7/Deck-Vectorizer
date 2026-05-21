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
        // console.error("Error during loading:", error);
        // popup.innerHTML = "Error during loading: " + error;
        // const button = document.createElement("button");
        // popup.appendChild(button);
        // button.innerText="Return";
        // button.addEventListener("click", async () => {
        //     popup.remove();
        //     overlay.remove();
        // });
        // overlay.addEventListener("click", async () => {
        //     popup.remove();
        //     overlay.remove();
        // });
    } finally {
        url.value="";
    }
});

async function create_recent_cards(div){
    recent_deck = document.createElement('div');
    div.createChild(recent_deck)

    recent_deck = document.createElement('div')
};

const recents = document.getElementById("recently_visited")
create_recent_cards(recents);