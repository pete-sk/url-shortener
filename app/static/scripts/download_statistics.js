
const link = document.querySelector('#link').innerHTML;
const totalNumOfClicks = document.querySelector('#num-of-clicks').innerHTML;

var page = 1;
var countOfLoadedClicks = 0;

function downloadStatistics () {
    if (countOfLoadedClicks < totalNumOfClicks) {
        document.querySelector('#load-more-button').disabled = true;
        document.querySelector('#load-more-button').innerHTML = 'Loading...';

        const url = window.location.origin + '/statistics/' + link + '?page=' + page;

        const Http = new XMLHttpRequest();
        Http.open('GET', url);
        Http.send();
        
        Http.onreadystatechange = (e) => {
            if (Http.readyState == 4 && Http.status == 200) {
                let clicks = JSON.parse(Http.responseText);
                for (let i = 0; i < clicks.length; i++) {

                    let ordinal = totalNumOfClicks - countOfLoadedClicks;

                    let dateClicked = clicks[i]['date_clicked'];
                    let location = clicks[i]['location'];
                    let platform = clicks[i]['os'];
                    let browser = clicks[i]['browser'];
                    let ipAddress = clicks[i]['ip_address'];
                    let referrer = clicks[i]['referrer'];

                    let referrerHtml;
                    if (referrer==='None') {
                        referrerHtml = 'Direct/Unknown'
                    } else {
                        referrerHtml = `<a class="analytics-traffic-link" href="${referrer}">${referrer}</a>`
                    }

                    document.querySelector('#statistics').innerHTML += `
                    <div class="card">
                        <div class="card-body-compact">
                            <span><b>#${ordinal}</b> - ${dateClicked}, ${location}, ${platform}, ${browser}, ${ipAddress}, ${referrerHtml}</span>
                        </div>
                    </div> `;

                    countOfLoadedClicks++;
                }

                if (countOfLoadedClicks == totalNumOfClicks) {
                    document.querySelector('#load-more-button').remove();
                } else {
                    document.querySelector('#load-more-button').innerHTML = 'Load more';
                    document.querySelector('#load-more-button').disabled = false;
                }

                page++;
            }
        }
    }
}

window.onload = downloadStatistics();
document.querySelector('#load-more-button').addEventListener('click', downloadStatistics);
