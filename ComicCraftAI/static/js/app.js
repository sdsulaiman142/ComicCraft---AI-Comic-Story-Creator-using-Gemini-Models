document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.getElementById(
                "comic-form"
            );

        const generateButton =
            document.getElementById(
                "generate-button"
            );


        if (
            form &&
            generateButton
        ) {

            form.addEventListener(
                "submit",
                () => {

                    generateButton.disabled =
                        true;

                    generateButton.textContent =
                        "Generating your comic…";
                }
            );
        }


        const downloadButton =
            document.getElementById(
                "download-button"
            );


        if (downloadButton) {

            downloadButton.addEventListener(
                "click",
                async () => {

                    const status =
                        document.getElementById(
                            "download-status"
                        );

                    const url =
                        downloadButton.dataset.pdfUrl;


                    downloadButton.disabled =
                        true;

                    status.textContent =
                        "Preparing your download…";


                    try {

                        const response =
                            await fetch(url);


                        if (!response.ok) {

                            throw new Error(
                                "The PDF could not be downloaded."
                            );
                        }


                        const blob =
                            await response.blob();


                        const filename =
                            url.split("/").pop()
                            || "comic.pdf";


                        const objectUrl =
                            URL.createObjectURL(
                                blob
                            );


                        const anchor =
                            document.createElement(
                                "a"
                            );


                        anchor.href =
                            objectUrl;

                        anchor.download =
                            filename;


                        document.body.appendChild(
                            anchor
                        );


                        anchor.click();

                        anchor.remove();


                        URL.revokeObjectURL(
                            objectUrl
                        );


                        window.location.href =
                            `/export-success?filename=${encodeURIComponent(
                                filename
                            )}`;

                    } catch (error) {

                        status.textContent =
                            error.message;

                        downloadButton.disabled =
                            false;
                    }
                }
            );
        }

    }
);