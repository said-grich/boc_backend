
$(document).ready(function() {

    function downloadFile(searchId) {
        $.ajax({
            url: `/api/export-search-results/${searchId}/`,
            method: 'GET',
            xhrFields: {
                responseType: 'blob'  // Important to get a binary (blob) response
            },
            beforeSend: function(xhr) {
                setAuthHeaders(xhr); // Assuming setAuthHeaders is defined elsewhere
            },
            success: function(response, status, xhr) {
                // Get the filename from the Content-Disposition header if available
                var filename = "";
                var disposition = xhr.getResponseHeader('Content-Disposition');
                if (disposition && disposition.indexOf('attachment') !== -1) {
                    var matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
                    if (matches != null && matches[1]) {
                        filename = matches[1].replace(/['"]/g, '');
                    }
                }
                
                if (!filename) {
                    filename = `search_result_${searchId}.docx`;  // Default filename if none provided
                }
    
                // Create a link element, trigger a download, and remove the link element
                var blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
                var link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = filename;  // Set the download filename
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);  // Remove link after triggering the download
            },
            error: function(xhr, status, error) {
                alert('Failed to download file');
            }
        });
    }
    // Function to create table rows dynamically
    function populateTable(data) {
        var tableBody = $('#table-body');  // Reference to the table body
        tableBody.empty();  // Clear any existing rows
    
        // Loop through each record in the data
        data.forEach(function(entry) {
            var tags = entry.tags.join(', ');  // Join the tags array into a comma-separated string
    
            // Combine document names with their respective dates
            var documentsWithDates = entry.source_file_names.map(function(docName, index) {
                return `${docName}`;  // Format as "DocumentName (Date)"
            }).join('<br>');  // Join the documents into a single string with line breaks
    
            // Create a single row for the search_id
            var row = `
                <li class="table-row">
                    <div class="col col-2" data-label="Document Name">${documentsWithDates}</div>
                    <div class="col col-3" data-label="Tags">${tags}</div>
                    <div class="col col-3" data-label="Date">${entry.dates.join(', ')}</div>
                    <div class="col col-4" data-label="Options">
                        <button class="download-btn" data-doc-id="${entry.search_id}" style="background-color: #007BFF; color: white; padding: 5px 10px; border: none; border-radius: 5px;">
                            <i class="fa-solid fa-download"></i></button>
                        <button class="delete-btn" data-doc-id="${entry.search_id}" style="background-color: #FF4B4B; color: white; padding: 5px 10px; border: none; border-radius: 5px;">
                            <i class="fa-solid fa-trash-can"></i></button>
                    </div>
                </li>
            `;
            // Append the new row to the table body
            tableBody.append(row);
        });
    }
    

    // Fetch data from the backend (ListExtractedDataView)
    function fetchHistory() {
        $.ajax({
            url: '/api/history/',  // Adjust the URL based on your backend route
            method: 'GET',
            beforeSend: function(xhr) {
                setAuthHeaders(xhr); // Assuming setAuthHeaders is defined elsewhere
            },
            success: function(response) {
                populateTable(response);  // Populate table with the response data
            },
            error: function(xhr, status, error) {
                console.error('Failed to fetch data:', error);
            }
        });
    }

    // Call the function to fetch and populate the history table when the page loads
    fetchHistory();

    // Event listener for delete button
    $(document).on('click', '.delete-btn', function() {
        var docId = $(this).data('doc-id');
        var docName = $(this).data('doc-name');
        var confirmation = confirm('Are you sure you want to delete ' + docName + '?');
        if (confirmation) {
            // AJAX request to delete the document by search_id
            $.ajax({
                url: '/api/history/delete/' + docId + '/',  // Adjust based on the correct route
                type: 'DELETE',
                beforeSend: function(xhr) {
                    setAuthHeaders(xhr); // Assuming setAuthHeaders is defined elsewhere
                },
                success: function(response) {
                    alert('Document deleted successfully');
                    fetchHistory();  // Refresh the table after deletion
                },
                error: function(xhr, status, error) {
                    alert('Failed to delete document');
                }
            });
        }
    });



    
    // Event listener for download button
    $(document).on('click', '.download-btn', function() {
        var docId = $(this).data('doc-id');
        downloadFile(docId);
    });






});
