document.addEventListener('DOMContentLoaded', function() {
    // Sayfa yükleme animasyonu için gerekli elemanlar
    const pageLoader = document.getElementById('page-loader');
    
    // Form işleme için gerekli elemanlar
    const uploadForm = document.getElementById('upload-form');
    const loadingContainer = document.getElementById('loading-container');
    const resultContainer = document.getElementById('result-container');
    const progressBar = document.getElementById('progress-bar');
    const progressStatus = document.getElementById('progress-status');
    const downloadLink = document.getElementById('download-link');
    
    // Dosya yükleme için gerekli elemanlar
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('fileInput');
    const selectFileBtn = document.getElementById('selectFileBtn');
    const fileDetails = document.getElementById('fileDetails');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const fileIcon = document.getElementById('fileIcon');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const formatSelection = document.getElementById('formatSelection');
    const formatCsv = document.getElementById('formatCsv');
    const formatExcel = document.getElementById('formatExcel');
    const submitBtn = document.getElementById('submitBtn');
    
    // Sayfa yüklendiğinde loading animasyonunu gizle
    window.addEventListener('load', function() {
        setTimeout(function() {
            if (pageLoader) {
                pageLoader.style.opacity = '0';
                pageLoader.style.visibility = 'hidden';
            }
        }, 1000);
    });
    
    // Dosya seç butonuna tıklandığında
    if (selectFileBtn) {
        selectFileBtn.addEventListener('click', function() {
            fileInput.click();
        });
    }
    
    // Dosya sürükleme olayları
    if (dropArea) {
        // Sürükleme olayları
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Sürükleme stil değişimleri
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropArea.classList.add('drag-over');
        }
        
        function unhighlight() {
            dropArea.classList.remove('drag-over');
        }
        
        // Dosya bırakma olayı
        dropArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length) {
                fileInput.files = files;
                handleFiles(files);
            }
        }
    }
    
    // Dosya inputu değiştiğinde
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files.length) {
                handleFiles(this.files);
            }
        });
    }
    
    // Dosya kaldırma butonu
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', function() {
            resetFileInput();
        });
    }
    
    // Format seçim olaylarını ekle
    if (formatCsv && formatExcel) {
        formatCsv.addEventListener('change', function() {
            if (this.checked) {
                updateFormatSelection('csv');
            }
        });
        
        formatExcel.addEventListener('change', function() {
            if (this.checked) {
                updateFormatSelection('excel');
            }
        });
    }
    
    // Dosya adından tarih bilgisini çıkaran geliştirilmiş fonksiyon
    function parseDateFromFilename(filename) {
        try {
            // Eğer dosya adı yoksa veya boşsa hemen varsayılan döndür
            if (!filename || typeof filename !== 'string') {
                return "Tarih bilgisi yok";
            }
            
            // Dosya adından tarih bilgisini çıkar
            // Dosya adı formatı: Mehmet-DOĞAN-data_test-mehmetdogan.dev-20250504_223625.xlsx
            
            // Dosya adının son kısmını al (timestamp içeren kısım)
            const parts = filename.split('-');
            if (parts.length < 4) return "Tarih bilgisi yok";
            
            // Son parçayı al (örn: mehmetdogan.dev-20250504_223625.xlsx)
            const lastPart = parts[parts.length - 1];
            
            // Eğer lastPart içinde tarih formatı varsa (8 haneli sayı ve 6 haneli sayı)
            const dateMatch = lastPart.match(/(\d{8})_(\d{6})/);
            
            if (dateMatch) {
                const dateStr = dateMatch[1]; // 20250504
                const timeStr = dateMatch[2]; // 223625
                
                // Tarihi formatla
                const year = dateStr.substring(0, 4);    // 2025
                const month = dateStr.substring(4, 6);   // 05
                const day = dateStr.substring(6, 8);     // 04
                
                // Saati formatla
                const hours = timeStr.substring(0, 2);   // 22
                const minutes = timeStr.substring(2, 4); // 36
                
                // Formatlanmış tarih: 04.05.2025 22:36
                return `${day}.${month}.${year} ${hours}:${minutes}`;
            }
            
            // Alternatif: Eğer dosya adı içinde doğrudan tarih varsa
            // Son parçadan nokta ve dosya uzantısını çıkar
            const filenameWithoutExt = lastPart.split('.')[0];
            
            // Eğer son parça içinde alt çizgi varsa ve tarihi içeriyorsa
            if (filenameWithoutExt.includes('_')) {
                const dateParts = filenameWithoutExt.split('_');
                if (dateParts.length >= 2) {
                    const dateStr = dateParts[0]; // 20250504
                    const timeStr = dateParts[1]; // 223625
                    
                    if (dateStr.length >= 8 && timeStr.length >= 6) {
                        // Tarihi formatla
                        const year = dateStr.substring(0, 4);    // 2025
                        const month = dateStr.substring(4, 6);   // 05
                        const day = dateStr.substring(6, 8);     // 04
                        
                        // Saati formatla
                        const hours = timeStr.substring(0, 2);   // 22
                        const minutes = timeStr.substring(2, 4); // 36
                        
                        // Formatlanmış tarih: 04.05.2025 22:36
                        return `${day}.${month}.${year} ${hours}:${minutes}`;
                    }
                }
            }
            
            // Eğer buraya kadar geldiyse, tarih bilgisi bulunamadı
            // Tarih bilgisini şu anki zamandan oluştur
            const now = new Date();
            const formattedNow = `${String(now.getDate()).padStart(2, '0')}.${String(now.getMonth() + 1).padStart(2, '0')}.${now.getFullYear()} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
            return formattedNow;
            
        } catch (error) {
            console.error("Tarih çözümleme hatası:", error);
            // Hata durumunda şu anki zamanı kullan
            const now = new Date();
            const formattedNow = `${String(now.getDate()).padStart(2, '0')}.${String(now.getMonth() + 1).padStart(2, '0')}.${now.getFullYear()} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
            return formattedNow;
        }
    }
    
    // Format seçimini güncelleme fonksiyonu
    function updateFormatSelection(format) {
        // Seçilen format bilgisini göster
        const formatInfoText = document.createElement('div');
        formatInfoText.className = 'format-info-text';
        
        if (format === 'csv') {
            formatInfoText.innerHTML = '<i class="fas fa-info-circle"></i> CSV formatı işlenecek ve sonuç CSV olarak kaydedilecek.';
        } else {
            formatInfoText.innerHTML = '<i class="fas fa-info-circle"></i> Excel formatı işlenecek ve sonuç Excel olarak kaydedilecek.';
        }
        
        // Eğer önceden bir bilgi mesajı varsa kaldır
        const existingInfo = document.querySelector('.format-info-text');
        if (existingInfo) {
            existingInfo.remove();
        }
        
        // Yeni bilgi mesajını ekle
        if (formatSelection) {
            formatSelection.appendChild(formatInfoText);
        }
        
        // Seçilen formatı vurgula
        const selectedOption = format === 'csv' 
            ? document.querySelector('label[for="formatCsv"]') 
            : document.querySelector('label[for="formatExcel"]');
        
        if (selectedOption) {
            // Tüm seçenekleri resetle
            document.querySelectorAll('.format-option label').forEach(label => {
                label.classList.remove('selected');
            });
            
            // Seçili olanı işaretle
            selectedOption.classList.add('selected');
            
            // Animasyon ekle
            selectedOption.classList.add('pulse-animation');
            setTimeout(() => {
                selectedOption.classList.remove('pulse-animation');
            }, 1000);
        }
    }
    
    // Dosya işleme fonksiyonu
    function handleFiles(files) {
        const file = files[0];
        
        // Dosya türü kontrolü
        const fileType = file.name.split('.').pop().toLowerCase();
        if (!['csv', 'xls', 'xlsx'].includes(fileType)) {
            alert('Lütfen sadece CSV veya Excel dosyası yükleyin!');
            resetFileInput();
            return;
        }
        
        // Dosya bilgilerini göster
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        // Dosya ikonunu ayarla ve uygun format seçeneğini işaretle
        if (fileType === 'csv') {
            fileIcon.className = 'far fa-file-csv';
            formatCsv.checked = true;
            updateFormatSelection('csv');
        } else if (['xls', 'xlsx'].includes(fileType)) {
            fileIcon.className = 'far fa-file-excel';
            formatExcel.checked = true;
            updateFormatSelection('excel');
        }
        
        // Dosya detaylarını ve format seçimini göster
        fileDetails.style.display = 'flex';
        formatSelection.style.display = 'block';
        
        // Submit butonunu aktifleştir
        submitBtn.disabled = false;
        
        // Dosya yükleme alanını pulsla
        dropArea.classList.remove('pulse-animation');
        void dropArea.offsetWidth; // Reflow
        dropArea.classList.add('pulse-animation');
    }
    
    // Dosya boyutu formatını düzenleyen fonksiyon
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Dosya inputunu sıfırlama fonksiyonu
    function resetFileInput() {
        fileInput.value = '';
        fileDetails.style.display = 'none';
        formatSelection.style.display = 'none';
        submitBtn.disabled = true;
        dropArea.classList.remove('pulse-animation');
        
        // Format bilgi mesajını da kaldır
        const existingInfo = document.querySelector('.format-info-text');
        if (existingInfo) {
            existingInfo.remove();
        }
        
        // Seçili format etiketlerini temizle
        document.querySelectorAll('.format-option label').forEach(label => {
            label.classList.remove('selected');
        });
    }
    
    // Form işleme
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Form doğrulama
            const file = fileInput.files[0];
            const firstName = document.getElementById('firstName').value;
            const lastName = document.getElementById('lastName').value;
            const fileFormat = document.querySelector('input[name="fileFormat"]:checked').value;
            
            if (!file || !firstName || !lastName) {
                alert('Lütfen tüm alanları doldurun!');
                return;
            }
            
            // Form verisini oluştur
            const formData = new FormData();
            formData.append('file', file);
            formData.append('firstName', firstName);
            formData.append('lastName', lastName);
            formData.append('fileFormat', fileFormat);
            
            // Progress bar'ı sıfırla ve göster
            if (progressBar) {
                progressBar.style.width = '0%';
            }
            if (progressStatus) {
                progressStatus.textContent = '0%';
            }
            
            // Yükleme arayüzünü göster
            if (uploadForm) uploadForm.style.display = 'none';
            if (loadingContainer) loadingContainer.style.display = 'block';
            if (resultContainer) resultContainer.style.display = 'none';
            
            // AJAX isteği
            fetch('/normalize', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Debug için konsola JSON veriyi yazdır
                    console.log("Sunucudan dönen veri:", data);
                    
                    // İşlem başarılı başlatıldı, şimdi ilerlemeyi takip edelim
                    const processId = data.process_id;
                    if (processId) {
                        trackProgress(processId, data.download_url, data.uploaded_file, data.normalized_file);
                    } else {
                        // Process ID bulunamadı, normal sonuç gösterme
                        completeProcess(data.download_url, data.uploaded_file, data.normalized_file);
                    }
                } else {
                    // Hata oluştu
                    alert('Hata: ' + data.message);
                    resetForm();
                }
            })
            .catch(error => {
                console.error('Hata:', error);
                alert('Bir hata oluştu, lütfen tekrar deneyin.');
                resetForm();
            });
        });
    }
    
    // İlerlemeyi takip etme fonksiyonu
    function trackProgress(processId, downloadUrl, uploadedFile, normalizedFile) {
        let checkInterval = setInterval(() => {
            fetch(`/progress/${processId}`)
            .then(response => response.json())
            .then(data => {
                // İlerleme durumunu güncelle
                let progress = data.progress;
                let status = data.status;
                
                if (progressBar) {
                    progressBar.style.width = `${progress}%`;
                }
                if (progressStatus) {
                    progressStatus.textContent = `${progress}% - ${status}`;
                }
                
                // İşlem tamamlandı veya hata oluştu mu kontrol et
                if (progress >= 100 || progress < 0) {
                    clearInterval(checkInterval);
                    if (progress >= 100) {
                        // İşlem başarıyla tamamlandı
                        completeProcess(downloadUrl, uploadedFile, normalizedFile);
                    } else {
                        // Hata oluştu
                        alert('Hata: ' + status);
                        resetForm();
                    }
                }
            })
            .catch(error => {
                console.error('İlerleme kontrolü hatası:', error);
                clearInterval(checkInterval);
                resetForm();
            });
        }, 500); // Her 500ms'de bir kontrol et
    }
    
    // İşlemi tamamla ve sonucu göster
    function completeProcess(downloadUrl, uploadedFile, normalizedFile) {
        if (downloadLink) {
            downloadLink.href = downloadUrl;
        }
        
        // Debug için konsola veriyi yazdır
        console.log("Tamamlama aşamasında dosya bilgileri:", uploadedFile, normalizedFile);
        
        // Güncel tarih bilgisini oluştur
        const now = new Date();
        const formattedNow = `${String(now.getDate()).padStart(2, '0')}.${String(now.getMonth() + 1).padStart(2, '0')}.${now.getFullYear()} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
        
        // uploadedFile dosya nesnesinde tarih ve dosya adı bilgilerini kontrol et ve güncelle
        if (uploadedFile) {
            // Dosya adını kontrol et ve düzenle
            if (uploadedFile.original_filename && !uploadedFile.display_filename) {
                uploadedFile.display_filename = uploadedFile.original_filename;
            }
            
            // Eğer dosya adı yoksa veya kısaltılmışsa tam dosya adını bul
            if (!uploadedFile.display_filename && uploadedFile.file_name) {
                // Dosya adından kullanıcı bilgilerini ve timestamp'i çıkar
                const parts = uploadedFile.file_name.split('-');
                if (parts.length >= 3) {
                    uploadedFile.display_filename = parts[2]; // İndeks 2'deki kısım genellikle orijinal dosya adıdır
                } else {
                    uploadedFile.display_filename = uploadedFile.file_name;
                }
            }
            
            // Tarih bilgisini kontrol et ve güncelle
            if (uploadedFile.file_name) {
                const parsedDate = parseDateFromFilename(uploadedFile.file_name);
                if (parsedDate && parsedDate !== "Tarih bilgisi yok" && parsedDate !== "Geçersiz tarih") {
                    uploadedFile.date = parsedDate;
                } else {
                    uploadedFile.date = formattedNow;
                }
            } else {
                uploadedFile.date = formattedNow;
            }
        }
        
        // normalizedFile dosya nesnesinde tarih ve dosya adı bilgilerini kontrol et ve güncelle
        if (normalizedFile) {
            // Dosya adını kontrol et ve düzenle  
            if (normalizedFile.original_filename && !normalizedFile.display_filename) {
                normalizedFile.display_filename = normalizedFile.original_filename + "-normalized";
            }
            
            // Eğer dosya adı yoksa veya kısaltılmışsa tam dosya adını bul
            if (!normalizedFile.display_filename && normalizedFile.file_name) {
                // Dosya adından kullanıcı bilgilerini ve timestamp'i çıkar
                const parts = normalizedFile.file_name.split('-');
                if (parts.length >= 4) {
                    normalizedFile.display_filename = parts[2] + "-normalized"; // İndeks 2'deki kısım genellikle orijinal dosya adıdır
                } else {
                    normalizedFile.display_filename = normalizedFile.file_name;
                }
            }
            
            // Tarih bilgisini kontrol et ve güncelle
            if (normalizedFile.file_name) {
                const parsedDate = parseDateFromFilename(normalizedFile.file_name);
                if (parsedDate && parsedDate !== "Tarih bilgisi yok" && parsedDate !== "Geçersiz tarih") {
                    normalizedFile.date = parsedDate;
                } else {
                    normalizedFile.date = formattedNow;
                }
            } else {
                normalizedFile.date = formattedNow;
            }
        }
        
        setTimeout(() => {
            if (loadingContainer) loadingContainer.style.display = 'none';
            if (resultContainer) resultContainer.style.display = 'block';
            
            // Tabloları güncelle - artık her durumda doğru tarih ve dosya adı bilgisiyle
            updateFilesTable(uploadedFile, normalizedFile);
        }, 1000);
    }
    
    function resetForm() {
        if (uploadForm) {
            uploadForm.reset();
            resetFileInput();
            uploadForm.style.display = 'block';
            if (loadingContainer) loadingContainer.style.display = 'none';
            if (resultContainer) resultContainer.style.display = 'none';
        }
    }
    
    function updateFilesTable(uploadedFile, normalizedFile) {
        // Yüklenen dosyalar tablosunu güncelle
        const uploadedFilesList = document.getElementById('uploaded-files-list');
        if (uploadedFilesList && uploadedFile) {
            const fileFormat = getFileFormatHtml(uploadedFile.file_name || "");
            const uploadedRow = document.createElement('tr');
            
            // Doğru dosya adını göster (kısaltılmış olarak)
            let displayFileName = uploadedFile.display_filename || uploadedFile.original_filename || uploadedFile.file_name || "Dosya adı yok";
            const truncatedName = truncateFileName(displayFileName);
            
            // Eğer tarih yoksa veya geçersizse şimdiki zamanı kullan
            let dateToShow = uploadedFile.date || "";
            if (!dateToShow || dateToShow === "Tarih bilgisi yok" || dateToShow === "Geçersiz tarih") {
                const now = new Date();
                dateToShow = `${String(now.getDate()).padStart(2, '0')}.${String(now.getMonth() + 1).padStart(2, '0')}.${now.getFullYear()} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
            }
            
            uploadedRow.innerHTML = `
                <td>${uploadedFile.user_name || ""}</td>
                <td title="${displayFileName}" class="truncated-filename">
                    ${truncatedName}
                </td>
                <td>${fileFormat}</td>
                <td>${dateToShow}</td>
                <td><a href="${uploadedFile.download_url || "#"}" class="btn-download"><i class="fas fa-download"></i></a></td>
            `;
            uploadedFilesList.prepend(uploadedRow);
        }
        
        // Normalize edilmiş dosyalar tablosunu güncelle
        const normalizedFilesList = document.getElementById('normalized-files-list');
        if (normalizedFilesList && normalizedFile) {
            const fileFormat = getFileFormatHtml(normalizedFile.file_name || "");
            const normalizedRow = document.createElement('tr');
            
            // Doğru dosya adını göster (kısaltılmış olarak)
            let displayFileName = normalizedFile.display_filename || normalizedFile.original_filename || normalizedFile.file_name || "Dosya adı yok";
            const truncatedName = truncateFileName(displayFileName);
            
            // Eğer tarih yoksa veya geçersizse şimdiki zamanı kullan
            let dateToShow = normalizedFile.date || "";
            if (!dateToShow || dateToShow === "Tarih bilgisi yok" || dateToShow === "Geçersiz tarih") {
                const now = new Date();
                dateToShow = `${String(now.getDate()).padStart(2, '0')}.${String(now.getMonth() + 1).padStart(2, '0')}.${now.getFullYear()} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
            }
            
            normalizedRow.innerHTML = `
                <td>${normalizedFile.user_name || ""}</td>
                <td title="${displayFileName}" class="truncated-filename">
                    ${truncatedName}
                </td>
                <td>${fileFormat}</td>
                <td>${dateToShow}</td>
                <td><a href="${normalizedFile.download_url || "#"}" class="btn-download"><i class="fas fa-download"></i></a></td>
            `;
            normalizedFilesList.prepend(normalizedRow);
        }
    }
    // Dosya adını kısaltan fonksiyon
    function truncateFileName(fileName, maxLength = 11) {
        if (!fileName) return "Dosya adı yok";
        
        if (fileName.length <= maxLength) {
            return fileName;
        }
        return fileName.substring(0, maxLength) + "...";
    }
    
    // Dosya formatına göre HTML oluştur
    function getFileFormatHtml(fileName) {
        if (!fileName) return '<span class="file-format"><i class="fas fa-file"></i> Bilinmeyen</span>';
        
        const fileExtension = fileName.split('.').pop().toLowerCase();
        
        if (fileExtension === 'csv') {
            return '<span class="file-format csv"><i class="fas fa-file-csv"></i> CSV</span>';
        } else if (['xlsx', 'xls'].includes(fileExtension)) {
            return '<span class="file-format excel"><i class="fas fa-file-excel"></i> Excel</span>';
        } else {
            return '<span class="file-format"><i class="fas fa-file"></i> Bilinmeyen</span>';
        }
    }
    
    // Tablo içindeki mevcut tarih verilerini güncelle
    function updateExistingDates() {
        // Yüklenen dosyalar tablosundaki tarih hücrelerini güncelle
        const uploadedRows = document.querySelectorAll("#uploaded-files-list tr");
        
        uploadedRows.forEach(row => {
            const fileNameCell = row.querySelector("td.truncated-filename");
            const dateCell = row.querySelector("td:nth-child(4)"); // 4. hücre tarih hücresi
            
            if (fileNameCell && dateCell) {
                const fileName = fileNameCell.getAttribute("title");
                if (fileName) {
                    const formattedDate = parseDateFromFilename(fileName);
                    if (formattedDate !== "Tarih çözümlenemedi" && formattedDate !== "Geçersiz tarih") {
                        dateCell.textContent = formattedDate;
                    }
                }
            }
        });
        
        // Normalize edilmiş dosyalar tablosundaki tarih hücrelerini güncelle
        const normalizedRows = document.querySelectorAll("#normalized-files-list tr");
        
        normalizedRows.forEach(row => {
            const fileNameCell = row.querySelector("td.truncated-filename");
            const dateCell = row.querySelector("td:nth-child(4)"); // 4. hücre tarih hücresi
            
            if (fileNameCell && dateCell) {
                const fileName = fileNameCell.getAttribute("title");
                if (fileName) {
                    const formattedDate = parseDateFromFilename(fileName);
                    if (formattedDate !== "Tarih çözümlenemedi" && formattedDate !== "Geçersiz tarih") {
                        dateCell.textContent = formattedDate;
                    }
                }
            }
        });
    }
    
    // Sayfa yüklendiğinde mevcut tarih verilerini güncelle
    updateExistingDates();

    // Flash mesajları için
    const closeButtons = document.querySelectorAll('.close-flash');
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const flashMessage = this.parentElement;
            flashMessage.style.opacity = '0';
            setTimeout(() => {
                flashMessage.style.display = 'none';
            }, 300);
        });
    });
    
    // Flash mesajlarını otomatik olarak 5 saniye sonra kaybolacak şekilde ayarla
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    });
});