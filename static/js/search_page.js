const ul = document.querySelector("ul"),
input = document.querySelector("input"),
tagNumb = document.querySelector(".details span");

let maxTags = 100,
tags = ["document", "gap"];

countTags();
createTag();

function countTags(){
    input.focus();
    tagNumb.innerText = maxTags - tags.length;
}

function createTag(){
    ul.querySelectorAll("li").forEach(li => li.remove());
    tags.slice().reverse().forEach(tag =>{
        let liTag = `<li>${tag} <i class="uit uit-multiply" class="tag-input" onclick="remove(this, '${tag}')"></i></li>`;
        ul.insertAdjacentHTML("afterbegin", liTag);
    });
    countTags();
}

function remove(element, tag){
    let index  = tags.indexOf(tag);
    tags = [...tags.slice(0, index), ...tags.slice(index + 1)];
    element.parentElement.remove();
    countTags();
}

function addTag(e){
    if(e.key == "Enter"){
        let tag = e.target.value.replace(/\s+/g, ' ');
        if(tag.length > 1 && !tags.includes(tag)){
            if(tags.length < 10){
                tag.split(',').forEach(tag => {
                    tags.push(tag);
                    createTag();
                });
            }
        }
        e.target.value = "";
    }
}

input.addEventListener("keyup", addTag);

const removeBtn = document.querySelector(".details button");
removeBtn.addEventListener("click", () =>{
    tags.length = 0;
    ul.querySelectorAll("li").forEach(li => li.remove());
    countTags();
});


//file 

const fileList = document.querySelector(".file-list");
const fileBrowseButton = document.querySelector(".file-browse-button");
const fileBrowseInput = document.querySelector(".file-browse-input");
const fileUploadBox = document.querySelector(".file-upload-box");
const fileCompletedStatus = document.querySelector(".file-completed-status");

let totalFiles = 0;
let completedFiles = 0;


const createFileItemHTML = (file, uniqueIdentifier) => {
    const { name, size, type } = file;
    const extension = name.split(".").pop();
    const formattedFileSize = size >= 1024 * 1024 ? `${(size / (1024 * 1024)).toFixed(2)} MB` : `${(size / 1024).toFixed(2)} KB`;



    return `<li class="file-item" id="file-item-${uniqueIdentifier}">
                <div class="file-extension">${extension.toUpperCase()}</div>
                <div class="file-content-wrapper">
                    <div class="file-content">
                        <div class="file-details">
                            <h5 class="file-name">${name}</h5>
                            <div class="file-info">
                                <small class="file-size">0 MB / ${formattedFileSize}</small>
                                <small class="file-divider">•</small>
                            </div>
                        </div>
                        <button class="cancel-button" onclick="removeFile(${uniqueIdentifier})">
                            <i class="fa fa-times"></i> 
                        </button>
                    </div>
                    <div class="file-progress-bar">
                        <div class="file-progress"></div>
                    </div>
                </div>
            </li>`;
}

const removeFile = (uniqueIdentifier) => {
    const fileItem = document.getElementById(`file-item-${uniqueIdentifier}`);
    if (fileItem) {
        fileItem.remove();
        
        // Find the index of the file to remove
        const fileIndex = filesToUpload.findIndex(file => file.uniqueIdentifier === uniqueIdentifier);
        if (fileIndex > -1) {
            filesToUpload.splice(fileIndex, 1);  // Remove the file from the array
        }

        totalFiles--;
        fileCompletedStatus.innerText = `${totalFiles} files`;
    }
};

const handleFileUploading = (file, uniqueIdentifier) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("files", file);

    // Adding progress event listener to the ajax request
    xhr.upload.addEventListener("progress", (e) => {
        const fileProgress = document.querySelector(`#file-item-${uniqueIdentifier} .file-progress`);
        const fileSize = document.querySelector(`#file-item-${uniqueIdentifier} .file-size`);
        const statusElement = document.getElementById(`file-status-${uniqueIdentifier}`);

        const formattedFileSize = file.size >= 1024 * 1024 ? `${(e.loaded / (1024 * 1024)).toFixed(2)} MB / ${(e.total / (1024 * 1024)).toFixed(2)} MB` : `${(e.loaded / 1024).toFixed(2)} KB / ${(e.total / 1024).toFixed(2)} KB`;

        const progress = Math.round((e.loaded / e.total) * 100);
        fileProgress.style.width = `${progress}%`;
        fileSize.innerText = formattedFileSize;
        statusElement.innerText = "Uploading...";
    });

    xhr.open("POST", "/api/search/", true);
    xhr.setRequestHeader("X-CSRFToken", csrfToken);

    // Update the status to uploading
    xhr.addEventListener("loadstart", () => {
        const statusElement = document.getElementById(`file-status-${uniqueIdentifier}`);
        statusElement.innerText = "Uploading...";
    });

    // Update the status on success
    xhr.addEventListener("load", () => {
        if (xhr.status === 200) {
            const statusElement = document.getElementById(`file-status-${uniqueIdentifier}`);
            statusElement.innerText = "Completed";
            statusElement.style.color = "#00B125";
            document.querySelector(`#file-item-${uniqueIdentifier} .cancel-button`).remove();
        } else {
            const statusElement = document.getElementById(`file-status-${uniqueIdentifier}`);
            statusElement.innerText = "Error";
            statusElement.style.color = "#E3413F";
        }
    });

    // Handle error
    xhr.addEventListener("error", () => {
        const statusElement = document.getElementById(`file-status-${uniqueIdentifier}`);
        statusElement.innerText = "Error";
        statusElement.style.color = "#E3413F";
        alert("An error occurred during the file upload!");
    });

    xhr.send(formData);
}


const handleSelectedFiles = ([...files]) => {
    if (files.length === 0) return;
    totalFiles += files.length;

    files.forEach((file, index) => {
        const uniqueIdentifier = Date.now() + index;
        const fileItemHTML = createFileItemHTML(file, uniqueIdentifier);
        if (fileItemHTML) {
            fileList.insertAdjacentHTML("afterbegin", fileItemHTML);
            handleFileUploading(file, uniqueIdentifier);
        }
    });

    fileCompletedStatus.innerText = `${totalFiles} files`;
}

fileUploadBox.addEventListener("drop", (e) => {
    e.preventDefault();
    handleSelectedFiles(e.dataTransfer.files);
    fileUploadBox.classList.remove("active");
    fileUploadBox.querySelector(".file-instruction").innerText = "Drag files here or";
});

fileUploadBox.addEventListener("dragover", (e) => {
    e.preventDefault();
    fileUploadBox.classList.add("active");
    fileUploadBox.querySelector(".file-instruction").innerText = "Release to upload or";
});

fileUploadBox.addEventListener("dragleave", (e) => {
    e.preventDefault();
    fileUploadBox.classList.remove("active");
    fileUploadBox.querySelector(".file-instruction").innerText = "Drag files here or";
});

fileBrowseInput.addEventListener("change", (e) => handleSelectedFiles(e.target.files));
fileBrowseButton.addEventListener("click", () => fileBrowseInput.click());

