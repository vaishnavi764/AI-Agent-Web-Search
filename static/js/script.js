document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (file && file.name.endsWith('.csv')) {
        console.log("File selected:", file.name);

        // Use PapaParse to parse the CSV file
        Papa.parse(file, {
            complete: function(results) {
                console.log("Parsing complete:", results);

                const columns = results.data[0];  // Get the header row (first row)
                console.log("Columns:", columns);

                // Populate the select dropdown with column names
                const columnSelect = document.getElementById('columnSelect');
                columnSelect.innerHTML = '';  // Clear previous options

                columns.forEach(function(column) {
                    const option = document.createElement('option');
                    option.value = column;
                    option.textContent = column;
                    columnSelect.appendChild(option);
                });

                // Show the column selection dropdown and query input
                document.getElementById('columnSection').style.display = 'block';
                document.getElementById('querySection').style.display = 'block';
            },
            error: function(error) {
                console.error("Error parsing CSV:", error.message);
            }
        });
    } else {
        alert("Please select a valid CSV file.");
    }
});

// Handle the search button click
document.getElementById('searchButton').addEventListener('click', function() {
    const columnSelect = document.getElementById('columnSelect');
    const selectedColumn = columnSelect.value;
    const queryInput = document.getElementById('queryInput').value;

    if (!selectedColumn || !queryInput) {
        alert("Please select a column and enter a query.");
        return;
    }

    // Example of how you would send the query and get results (mock-up)
    console.log(`Searching for: ${queryInput.replace('{company}', selectedColumn)}`);

    // Example mock results from a web search (replace with actual API call)
    const mockResults = [
        { entity: "Example Company", extractedInfo: "contact@example.com" },
        { entity: "Another Company", extractedInfo: "another@example.com" }
    ];

    // Display the results
    const resultTableBody = document.querySelector('#resultTable tbody');
    resultTableBody.innerHTML = ''; // Clear previous results

    mockResults.forEach(function(result) {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${result.entity}</td><td>${result.extractedInfo}</td>`;
        resultTableBody.appendChild(row);
    });

    document.getElementById('resultSection').style.display = 'block';
});

// Handle Google Sheets connection
document.getElementById('connectSheets').addEventListener('click', function() {
    const sheetUrl = document.getElementById('sheetsInput').value;
    
    if (!sheetUrl) {
        alert("Please enter a valid Google Sheets URL.");
        return;
    }
    
    // Example API request to fetch data from Google Sheets (you'll need the Google Sheets API to connect)
    console.log("Connecting to Google Sheets with URL:", sheetUrl);
    // Replace this with actual API logic to fetch the sheet data and parse it.
});
