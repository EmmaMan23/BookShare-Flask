document.addEventListener('DOMContentLoaded', () => {
    const genreForm = document.getElementById('genreForm');
    const editUrl = genreForm.dataset.editUrl;
    const createUrl = genreForm.dataset.createUrl;
    const cancelBtn = document.getElementById('cancelEditBtn');

    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', () => {
            const genreId = button.dataset.id;
            const genreName = button.dataset.name;
            const genreImage = button.dataset.image;

            // Update form fields
            document.getElementById('genre_id').value = genreId;
            document.getElementById('name').value = genreName;

            // Update radio selection
            const radios = document.querySelectorAll('input[name="image"]');
            radios.forEach(radio => {
                radio.checked = (radio.value === genreImage);
            });

            // Change form action and labels
            genreForm.action = editUrl;

            document.getElementById('genreFormHeading').innerText = "Edit Genre";
            document.getElementById('genreFormSubmit').innerText = "Update Genre";

            document.getElementById('createGenreForm').classList.add('editing');

            // Scroll to form
            document.getElementById('createGenreForm').scrollIntoView({ behavior: 'smooth' });

            cancelBtn.style.display = 'inline-block';
        });
    });

    // Cancel button logic
    cancelBtn.addEventListener('click', () => {
        // Reset form fields
        genreForm.reset();

        // Clear hidden genre_id input
        document.getElementById('genre_id').value = '';

        // Reset form action and UI texts
        genreForm.action = createUrl;
        document.getElementById('genreFormHeading').innerText = "Create a New Genre";
        document.getElementById('genreFormSubmit').innerText = "Add Genre";

        // Hide cancel button and remove editing class
        cancelBtn.style.display = 'none';
        document.getElementById('createGenreForm').classList.remove('editing');
    });
});
