/**
 * Class to update a preview image when file selected.
 * Based on https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file#examples
 */
class ImagePreviewer {

    /**
     * Constructor
     * @param inputSelector - input selector for file input
     * @param previewSelector - image selector for preview image
     * @param fileTypes - valid file types
     */
    constructor(inputSelector, previewSelector, fileTypes) {
        this.inputSelector = inputSelector;
        this.previewSelector = previewSelector;
        this.fileTypes = fileTypes;

        this.input = undefined;      // file input
        this.preview = undefined;    // preview image
    }

    /**
     * Initialise the preview
     */
    initialise() {
        this.input = document.querySelector(this.inputSelector);
        this.preview = document.querySelector(this.previewSelector);

        this.input.addEventListener('change', (event) => {
            this.updateImageDisplay();
        });
    }

    /**
     * Update image preview
     */
    updateImageDisplay() {
        const curFiles = this.input.files;
        if (curFiles.length === 0) {
            alert("No files currently selected for upload");
        } else {
            for (const file of curFiles) {
                if (this.validFileType(file)) {
                    this.preview.setAttribute("src", URL.createObjectURL(file));
                } else {
                    alert(`${file.name} is not a valid file type. Please update your selection.`);
                }
            }
        }
    }

    /**
     * Check if valid file type
     * @param file - file
     * @returns {boolean}
     */
    validFileType(file) {
        return this.fileTypes.includes(file.type);
    }

    /**
     * Get friendly file size text
     * @param number - file size
     * @returns {string}
     */
    returnFileSize(number) {
        if (number < 1024) {
            return `${number} bytes`;
        } else if (number >= 1024 && number < 1048576) {
            return `${(number / 1024).toFixed(1)} KB`;
        } else if (number >= 1048576) {
            return `${(number / 1048576).toFixed(1)} MB`;
        }
    }
}
