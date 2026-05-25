async function create_recent_cards(){
    const response = await fetchRecentDecks();
    const recents = document.getElementById("recently_visited")
    const recent_container = document.getElementById("recent_container")

    if (response["status"] == "found") {

        if (response["recents"].length > 0) { 
            title = document.createElement("h4")
            title.innerText = "Recently Visited"
            recent_container.prepend(title);
        };
        for (let i = 0; i < response["recents"].length; i++) {
            let deck = response["recents"][i]
            let el = document.createElement("div");
            el.className = "recent_deck";
            el.innerText = deck["name"]
            el.style.backgroundImage = `linear-gradient(to bottom, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, .5) 100%), url(${deck["img"]})`
            recents.appendChild(el)
            el.addEventListener("click", async (params) => {
                let deckindex = i;
                loadRecentDeck(deckindex);
            })
        }
    } else {
        console.log("No recent decks found.")
    }

};

create_recent_cards();