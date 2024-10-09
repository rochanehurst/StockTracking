document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('fetch-stock').addEventListener('click', () => {
        const stockSymbol = document.getElementById('stock-symbol').value.toUpperCase();

        if (!stockSymbol){
            alert('Please enter a stock symbol');
            return;
        }

        const spinner = document.getElementById('loading-spinner');
        spinner.classList.remove('d-none');


        fetch(`http://127.0.0.1:5000/stock/${stockSymbol}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();  // Parse the response as JSON
            })
            .then(data => {
                console.log('Data received:', data);  // Log data for debugging

                // Hide the loading spinner after data is fetched
                if (spinner) spinner.classList.add('d-none');

                if (data.error) {

                    alert(data.error);  // Handle any errors

                }else{
                const stockInfo = document.getElementById('stock-info');
                stockInfo.classList.remove('d-none');
                document.getElementById('stock-symbol-display').textContent = data.symbol;
                document.getElementById('last-refreshed').textContent = data.latest_time_pacific;
                document.getElementById('open').textContent = data.open;
                document.getElementById('high').textContent = data.high;
                document.getElementById('low').textContent = data.low;
                document.getElementById('close').textContent = data.close;
                document.getElementById('volume').textContent = data.volume;

                }

            })

            .catch(error => {
                console.error('Error fetching stock data', error);

                spinner.classList.add('d-none');
            });
        });
});