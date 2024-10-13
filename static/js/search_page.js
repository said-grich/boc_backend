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
let filesToUpload = [];

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
                                <small class="file-divider">${formattedFileSize}</small>
                            </div>
                        </div>
                        <button class="cancel-button" onclick="removeFile(${uniqueIdentifier})">
                            <i class="fa fa-times"></i> 
                        </button>
                    </div>
                   
                </div>
            </li>`
}




const removeFile = (uniqueIdentifier) => {
    const fileItem = document.getElementById(`file-item-${uniqueIdentifier}`);
    if (fileItem) {

        fileItem.remove();
        // Find the index of the file to remove
        const fileIndex = filesToUpload.findIndex(file => file.uniqueIdentifier === uniqueIdentifier);
        console.log(fileIndex)

        if (fileIndex > -1) {
            filesToUpload.splice(fileIndex, 1);  // Remove the file from the array
        }

        const fileInput = document.querySelector('.file-browse-input');
        const files = fileInput.files;

        // Create a new DataTransfer object to hold the new FileList
        const dataTransfer = new DataTransfer();

        // Loop through the FileList and add files except the one to remove
        Array.from(files).forEach((file, index) => {
            // You need to match the uniqueIdentifier with the index or some other file property
            if (index !== fileIndex) {
                dataTransfer.items.add(file); // Keep this file
            }
        });

        // Assign the new FileList to the input
        fileInput.files = dataTransfer.files;

        // Update total files and UI
        totalFiles = fileInput.files.length;
        fileCompletedStatus.innerText = `${totalFiles} files`;
    }
};

const handleSelectedFiles = ([...files]) => {

    console.log(files)

    if (files.length === 0) return;

    totalFiles += files.length;

    files.forEach((file, index) => {
        const uniqueIdentifier = Date.now() + index;
        filesToUpload.push({ file, uniqueIdentifier });
        const fileItemHTML = createFileItemHTML(file, uniqueIdentifier);
        if (fileItemHTML) {
            fileList.insertAdjacentHTML("afterbegin", fileItemHTML);

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


const removeAllFiles = () => {
    // Remove all file items from the file list in the UI
    const fileItems = document.querySelectorAll('.file-item');
    fileItems.forEach(fileItem => {
        fileItem.remove();
    });

    // Clear the filesToUpload array
    filesToUpload.length = 0;  // Reset the array

    // Get the file input element and reset its FileList
    const fileInput = document.querySelector('.file-browse-input');
    const dataTransfer = new DataTransfer();
    fileInput.files = dataTransfer.files;  // Clear the file input

    // Update total files and UI
    totalFiles = 0;
    fileCompletedStatus.innerText = `${totalFiles} files`;  // Update the UI to show 0 files
};
