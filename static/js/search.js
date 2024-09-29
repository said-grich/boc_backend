$('#submit-button').click(function(event) {
  event.preventDefault();  // Prevent the default form submission

  // Collect all tag input values
  const tags = [];
  $('#search-tags li').each(function() {
    tags.push($(this).text().trim());  // Get the text content of each li element
  });

  const files = $('.file-browse-input')[0].files;  // Capture files
  const formData = new FormData();



  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }
  for (let i = 0; i < tags.length; i++) {
    formData.append('tag_names', tags[i]);
  }
  console.log(formData)

  // Show the loading spinner
  $('#loading-spinner').show();

  $.ajax({
    url: searchUrl,  // The URL for the AJAX request
    type: "POST",
    data: formData,
    processData: false,
    contentType: false,
    headers: {
      'X-CSRFToken': csrfToken  // The CSRF token
    },
    xhr: function() {
      const xhr = new window.XMLHttpRequest();
      xhr.responseType = 'blob';  // Expect a blob response (for file download)
      return xhr;
    },

    success: function(data) {
      $('#loading-spinner').hide();  // Hide the spinner

      // Download the returned file
      const url = window.URL.createObjectURL(data);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'search_result.docx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    },
    error: function(error) {
      console.error('Error:', error);
      $('#loading-spinner').hide();  // Hide the spinner
      $('#results').html("An error occurred.");
    }
  });
});
