// editItem function toggles form at main page between "add new item" and "update item details"
function editItem(url, content = null, degree = null) {
    if (content && degree) {
        document.getElementById('main-form').action = url;
        document.getElementById('main-title').textContent = 'Update Item';
        document.getElementById('main-content').value = content;

        if (degree === 'Important') document.getElementById('main-important').checked = true;
        else document.getElementById('main-unimportant').checked = true;

        document.getElementById('main-submit').innerText = 'Save'

        let button = document.getElementById('main-clear');
        button.innerText = 'Cancel';
        button.type = 'button';
        button.onclick = function () {
            editItem('/');
        };
    } else {
        document.getElementById('main-form').action = url;
        document.getElementById('main-title').textContent = 'New Item';
        document.getElementById('main-important').checked = false;
        document.getElementById('main-unimportant').checked = false;
        document.getElementById('main-submit').innerText = 'Add'

        let button = document.getElementById('main-clear');
        button.innerText = 'Clear';
        button.type = 'reset';
        button.removeAttribute('onclick');
    }
}

// toggleForm function toggles form at profile page between "view details" and "edit details"
function toggleForm(email, name, password) {
    let inputs = document.getElementsByClassName('input');
    Array.from(inputs).forEach(input => {
        input.toggleAttribute('disabled');
        input.toggleAttribute('required');

        if (input.name === 'email') input.value = email
        else if (input.name === 'name') input.value = name
        else if (input.disabled) input.value = password
        else input.value = null
    })

    let buttons = document.getElementsByClassName('button');
    Array.from(buttons).forEach(button => {
        let template = document.createElement('template');
        if (button.id === 'button-update')
            template.innerHTML = '<input form="form-update" id="button-save" class="button is-block is-info is-large is-fullwidth" type="submit" value="Save">';
        else if (button.id === 'button-delete')
            template.innerHTML = `<button id="button-cancel" class="button is-block is-info is-outlined is-large is-fullwidth" type="button" onclick="toggleForm('${email}', '${name}', '${password}')">Cancel</button>`;
        else if (button.id === 'button-save')
            template.innerHTML = `<button id="button-update" class="button is-block is-info is-large is-fullwidth" type="button" onclick="toggleForm('${email}', '${name}', '${password}')">Update</button>`;
        else if (button.id === 'button-cancel')
            template.innerHTML = '<input form="form-delete" id="button-delete" class="button is-block is-danger is-large is-fullwidth" type="submit" onclick="return confirm(`Are you sure you want to delete your account?`)" value="Delete">';
        button.replaceWith(template.content);
    })
}
