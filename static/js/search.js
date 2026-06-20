document.addEventListener("DOMContentLoaded", () => {

    const searchInput =
        document.querySelector("input[name='keyword']");

    if(searchInput){

        searchInput.addEventListener("keyup", function(){

            const value =
                this.value.toLowerCase();

            const cards =
                document.querySelectorAll(".material-card");

            cards.forEach(card => {

                const text =
                    card.innerText.toLowerCase();

                if(text.includes(value)){
                    card.style.display = "block";
                }
                else{
                    card.style.display = "none";
                }

            });

        });

    }

});