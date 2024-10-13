$('#submit-button').click(function (event) {
  event.preventDefault();  // Prevent the default form submission

  // Collect all tag input values
  const tags = [];
  $('#search-tags li').each(function () {
    tags.push($(this).text().trim());  // Get the text content of each li element
  });

  const files = $('.file-browse-input')[0].files;  // Capture files

  const formData = new FormData();

  console.log(filesToUpload)


  filesToUpload.forEach((fileObject) => {
    formData.append('files', fileObject.file);  // Append the file itself
  });

  for (let i = 0; i < tags.length; i++) {
    formData.append('tag_names', tags[i]);
  }

  for (var pair of formData.entries()) {
    if (pair[1] instanceof File) {
        console.log(pair[0] + ':');
        console.log(' - File name: ' + pair[1].name);
        console.log(' - File size: ' + pair[1].size + ' bytes');
        console.log(' - File type: ' + pair[1].type);
    } else {
        console.log(pair[0] + ': ' + pair[1]);
    }
}

  $('#loading-spinner').show();

  $.ajax({
    url: searchUrl,  // The URL for the AJAX request
    type: "POST",
    data: formData,
    processData: false,
    contentType: false,
    beforeSend: function(xhr) {
      setAuthHeaders(xhr); // Inject JWT token into the request headers
    },
    headers: {
      'X-CSRFToken': csrfToken  // The CSRF token
    },
    xhr: function () {
      const xhr = new window.XMLHttpRequest();
      xhr.responseType = 'blob';  // Expect a blob response (for file download)
      return xhr;
    },

    success: function (data) {
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
    error: function (error) {
      console.error('Error:', error);
      $('#loading-spinner').hide();  // Hide the spinner
      $('#results').html("An error occurred.");
    }
  });


});
