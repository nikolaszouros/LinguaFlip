/**
 * flashcard.js — Study mode logic for LinguaFlip
 *
 * Expects a global `CARDS` array injected by the study template:
 *   const CARDS = [{id, front, back}, ...];
 */

(function () {
    // Only initialise if we are on the study page (CARDS must be defined)
    if (typeof CARDS === 'undefined' || !Array.isArray(CARDS) || CARDS.length === 0) {
        return;
    }

    var currentIndex = 0;

    /**
     * Render the card at the given index.
     * Always starts un-flipped (showing the front).
     */
    function showCard(index) {
        var card = CARDS[index];
        var frontEl = document.getElementById('card-front');
        var backEl = document.getElementById('card-back');
        var counterEl = document.getElementById('card-counter');
        var flashcardEl = document.getElementById('flashcard');

        if (!card || !frontEl || !backEl || !counterEl || !flashcardEl) {
            return;
        }

        // Remove flipped state so the front face is shown
        flashcardEl.classList.remove('flipped');

        frontEl.textContent = card.front;
        backEl.textContent = card.back;
        counterEl.textContent = (index + 1) + ' / ' + CARDS.length;

        // Update prev / next button states
        var prevBtn = document.getElementById('prev-btn');
        var nextBtn = document.getElementById('next-btn');
        if (prevBtn) { prevBtn.disabled = index === 0; }
        if (nextBtn) { nextBtn.disabled = index === CARDS.length - 1; }
    }

    /** Toggle the flip state of the current card. */
    function flipCard() {
        var flashcardEl = document.getElementById('flashcard');
        if (flashcardEl) {
            flashcardEl.classList.toggle('flipped');
        }
    }

    /** Advance to the next card (if available). */
    function nextCard() {
        if (currentIndex < CARDS.length - 1) {
            currentIndex += 1;
            showCard(currentIndex);
        }
    }

    /** Go back to the previous card (if available). */
    function prevCard() {
        if (currentIndex > 0) {
            currentIndex -= 1;
            showCard(currentIndex);
        }
    }

    // Expose functions on window so inline onclick attributes in the template work
    window.flipCard = flipCard;
    window.nextCard = nextCard;
    window.prevCard = prevCard;

    // Click the card scene to flip
    var scene = document.getElementById('flashcard-scene');
    if (scene) {
        scene.addEventListener('click', flipCard);
    }

    // Keyboard navigation — only on the study page (flashcard-scene must exist).
    // This prevents the space key from being swallowed on the test page.
    if (document.getElementById('flashcard-scene')) {
        document.addEventListener('keydown', function (e) {
            switch (e.key) {
                case 'ArrowRight':
                case 'l':
                    nextCard();
                    break;
                case 'ArrowLeft':
                case 'h':
                    prevCard();
                    break;
                case ' ':
                case 'f':
                    e.preventDefault();
                    flipCard();
                    break;
            }
        });
    }

    // Initialise with the first card
    showCard(0);
}());
