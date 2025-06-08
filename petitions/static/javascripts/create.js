// Update
document.addEventListener('DOMContentLoaded', function () {
    const input = document.querySelector('input[type="file"][name="image"]');
    const preview = document.getElementById('image-preview');

    if (input) {
      input.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
          };
          reader.readAsDataURL(file);
        }
      });
    }
  });



// Form
    document.addEventListener('DOMContentLoaded', function () {
        const input = document.querySelector('input[type="file"][name="image"]');
        const preview = document.getElementById('image-preview');
        const fileLabel = document.querySelector('.file-upload-label');

        input.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    fileLabel.innerHTML = `<i class="fas fa-check"></i> ${file.name}`;
                };
                reader.readAsDataURL(file);
            }
        });
    });



