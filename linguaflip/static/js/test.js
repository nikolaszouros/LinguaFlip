/**
 * test.js — Test mode logic for LinguaFlip
 *
 * Expects globals injected by the test template:
 *   const CARDS = [{id, front, back}, ...];
 *   const DECK_ID = <int>;
 *   const SUBMIT_URL = "<url>";
 */

(function () {
    // Only initialise on the test page
    if (typeof CARDS === 'undefined' || typeof SUBMIT_URL === 'undefined') {
        return;
    }

    var currentIndex = 0;
    var answers = [];

    /** Display the question at the given index and update progress UI. */
    function showQuestion(index) {
        var card = CARDS[index];
        var questionEl = document.getElementById('question-text');
        var counterEl = document.getElementById('test-counter');
        var progressEl = document.getElementById('progress-fill');
        var inputEl = document.getElementById('answer-input');
        var submitBtn = document.getElementById('submit-btn');

        if (!questionEl || !card) { return; }

        questionEl.textContent = card.front;

        if (counterEl) {
            counterEl.textContent = (index + 1) + ' / ' + CARDS.length;
        }

        if (progressEl) {
            progressEl.style.width = (((index) / CARDS.length) * 100) + '%';
        }

        if (inputEl) {
            inputEl.value = '';
            inputEl.focus();
        }

        // Update submit button label on last card
        if (submitBtn) {
            submitBtn.textContent = (index === CARDS.length - 1) ? 'Finish' : 'Submit';
        }
    }

    /** Record the current answer and either advance or submit the test. */
    function handleSubmit() {
        var inputEl = document.getElementById('answer-input');
        var answer = inputEl ? inputEl.value.trim() : '';

        answers.push({
            card_id: CARDS[currentIndex].id,
            answer: answer
        });

        if (currentIndex < CARDS.length - 1) {
            currentIndex += 1;
            showQuestion(currentIndex);
        } else {
            // All questions answered — submit to server
            submitTest();
        }
    }

    /** POST all answers to the server and render the results inline. */
    function submitTest() {
        var submitBtn = document.getElementById('submit-btn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting…';
        }

        fetch(SUBMIT_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ answers: answers })
        })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            renderResults(data);
        })
        .catch(function () {
            alert('An error occurred while submitting. Please try again.');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Finish';
            }
        });
    }

    /** Hide the question section and display the inline results. */
    function renderResults(data) {
        var questionSection = document.getElementById('question-section');
        var resultsSection = document.getElementById('results-section');
        var progressEl = document.getElementById('progress-fill');
        var counterEl = document.getElementById('test-counter');

        if (progressEl) { progressEl.style.width = '100%'; }
        if (counterEl) { counterEl.textContent = CARDS.length + ' / ' + CARDS.length; }
        if (questionSection) { questionSection.style.display = 'none'; }
        if (!resultsSection) { return; }

        resultsSection.style.display = 'flex';

        var scoreTitle = document.getElementById('score-title');
        if (scoreTitle) {
            var pct = data.total > 0 ? Math.round(data.score / data.total * 100) : 0;
            scoreTitle.textContent = data.score + ' / ' + data.total + '  (' + pct + '%)';
        }

        var tbody = document.getElementById('results-body');
        if (tbody && data.results) {
            // Build a lookup from card_id to front text
            var cardMap = {};
            CARDS.forEach(function (c) { cardMap[c.id] = c.front; });

            tbody.innerHTML = '';
            data.results.forEach(function (r) {
                var tr = document.createElement('tr');
                tr.className = r.correct ? 'result-row--correct' : 'result-row--wrong';

                var question = cardMap[r.card_id] || '—';
                var badge = r.correct
                    ? '<span class="badge badge--success">Correct</span>'
                    : '<span class="badge badge--error">Wrong</span>';

                tr.innerHTML =
                    '<td>' + escapeHtml(question) + '</td>' +
                    '<td>' + escapeHtml(r.given) + '</td>' +
                    '<td>' + escapeHtml(r.expected) + '</td>' +
                    '<td>' + badge + '</td>';

                tbody.appendChild(tr);
            });
        }
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(String(text)));
        return div.innerHTML;
    }

    // Wire up the submit button
    var submitBtn = document.getElementById('submit-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', handleSubmit);
    }

    // Allow Enter key to submit the answer
    var inputEl = document.getElementById('answer-input');
    if (inputEl) {
        inputEl.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleSubmit();
            }
        });
    }

    // Kick off
    showQuestion(0);
}());
