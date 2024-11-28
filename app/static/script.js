        const fileInput = document.getElementById('fileInput');
        const selectedFiles = document.getElementById('selectedFiles');
        const uploadForm = document.getElementById('uploadForm');
        const messageElement = document.getElementById('message');
        const calculateButton = document.getElementById('calculateButton');
        const resultMessageElement = document.getElementById('resultMessage');
        const calculateLoader = document.getElementById('calculateLoader');
        const downloadButton = document.getElementById('downloadButton');
        const downloadLoader = document.getElementById('downloadLoader');
        const uploadButton = document.getElementById('uploadButton');
        const backToStartButton = document.getElementById('backToStartButton');
        const container = document.getElementById('container');

        for (let i = 0; i < 48; i++) {
        const span = document.createElement('span');
        span.textContent = 'ММТС';
        container.appendChild(span);
    }

        fileInput.addEventListener('change', function() {
            const fileList = Array.from(this.files);
            selectedFiles.innerHTML = fileList.map(file => `<div>${file.name}</div>`).join('');
        });

        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);

            if (formData.getAll('files').length !== 12) {
                messageElement.textContent = 'Пожалуйста, выберите ровно 12 файлов.';
                messageElement.className = 'error';
                messageElement.style.opacity = '1';
                return;
            }

            uploadButton.style.display = 'none';

            fetch('/load/upload_files', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageElement.textContent = 'Файлы успешно загружены!';
                    messageElement.className = 'success';
                    calculateButton.style.display = 'flex';
                } else {
                    messageElement.textContent = 'Ошибка при загрузке файлов. Пожалуйста, попробуйте снова.';
                    messageElement.className = 'error';
                    calculateButton.style.display = 'none';
                    uploadButton.style.display = 'flex';
                }
                messageElement.style.opacity = '1';
            })
            .catch(error => {
                console.error('Error:', error);
                messageElement.textContent = 'Произошла ошибка при отправке запроса.';
                messageElement.className = 'error';
                messageElement.style.opacity = '1';
                calculateButton.style.display = 'none';
                uploadButton.style.display = 'flex';
            });
        });

        calculateButton.addEventListener('click', function() {
            calculateLoader.style.display = 'inline-block';
            calculateButton.disabled = true;
            resultMessageElement.style.opacity = '0';
            downloadButton.style.display = 'none';

            fetch('/load/result', {
                method: 'GET'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    resultMessageElement.textContent = 'Расчет успешно выполнен!';
                    resultMessageElement.className = 'success';
                    downloadButton.style.display = 'flex';

                    if (data.not_counted && Object.keys(data.not_counted).length > 0) {
                        let notCountedMessage = 'Не удалось посчитать следующие элементы:\n';
                        for (const [key, value] of Object.entries(data.not_counted)) {
                            notCountedMessage += `${key}: ${value}\n`;
                        }
                        resultMessageElement.className = 'error';
                        resultMessageElement.textContent += '\n\n' + notCountedMessage;
                    }
                } else if (data.detail) {
                    resultMessageElement.textContent = (data.detail);
                    resultMessageElement.className = 'error';
                } else {
                    resultMessageElement.textContent = 'Ошибка при выполнении расчета. Пожалуйста, попробуйте снова.';
                    resultMessageElement.className = 'error';
                }
                resultMessageElement.style.opacity = '1';
            })
            .catch(error => {
                console.error('Error:', error);
                resultMessageElement.textContent = 'Произошла ошибка при отправке запроса на расчет.';
                resultMessageElement.className = 'error';
                resultMessageElement.style.opacity = '1';
            })
            .finally(() => {
                calculateLoader.style.display = 'none';
                calculateButton.disabled = false;
            });
        });

        downloadButton.addEventListener('click', function() {
            downloadLoader.style.display = 'inline-block';
            downloadButton.disabled = true;
            downloadButton.style.display = 'none';

            fetch('/load/download_files', {
                method: 'GET'
            })
            .then(response => {
                if (response.ok) {
                    const filename = response.headers.get('Content-Disposition').split('filename=')[1];
                    return response.blob().then(blob => ({ blob, filename }));
                }
                throw new Error('Ошибка при скачивании файлов');
            })
            .then(({ blob, filename }) => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename || 'excel_files.zip';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                resultMessageElement.textContent = 'Файлы успешно скачаны!';
                resultMessageElement.className = 'success';
                resultMessageElement.style.opacity = '1';
            })
            .catch(error => {
                console.error('Error:', error);
                resultMessageElement.textContent = 'Произошла ошибка при скачивании файлов.';
                resultMessageElement.className = 'error';
                resultMessageElement.style.opacity = '1';
                downloadButton.style.display = 'flex';
            })
            .finally(() => {
                downloadLoader.style.display = 'none';
                downloadButton.disabled = false;
            });
        });

        backToStartButton.addEventListener('click', function() {
            window.location.href = '/load';
        });



