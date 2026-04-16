// NAVIGATION
function showSection(id) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    document.getElementById(id + '-sec').classList.add('active');
    event.currentTarget.classList.add('active');
}

// MODALS — fixed: was '.modal-overlay' (hyphen), must match CSS class '.modal_overlay' (underscore)
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

function closeModals() {
    document.querySelectorAll('.modal_overlay').forEach(m => m.style.display = 'none'); // ✅ underscore
}

// REMOVE ROW FUNCTION
function deleteRow(btn) {
    if (confirm('Are you sure you want to delete this record?')) {
        const row = btn.parentNode.parentNode;
        row.parentNode.removeChild(row);
    }
}

// GENERIC FORM HANDLER
function setupForm(formId, tableId, rowGenerator) {
    const form = document.getElementById(formId);
    form.onsubmit = (e) => {
        e.preventDefault();
        const table = document.getElementById(tableId);
        const newRow = document.createElement('tr');

        newRow.innerHTML = rowGenerator() + `<td><button class="btn-remove" onclick="deleteRow(this)"><i class="fas fa-trash"></i></button></td>`;

        table.appendChild(newRow);
        closeModals();
        form.reset();
    };
}

// INIT ALL FORMS
setupForm('invForm', 'inventoryTable', () => {
    const price = parseFloat(document.getElementById('inv_price').value) || 0;
    return `<td>${document.getElementById('inv_id').value}</td><td>${document.getElementById('inv_name').value}</td><td>${document.getElementById('inv_qty').value}</td><td>${document.getElementById('inv_cat').value}</td><td>$${price.toFixed(2)}</td><td>${document.getElementById('inv_date').value}</td>`;
});

setupForm('catForm', 'catTable', () =>
    `<td>${document.getElementById('c_id').value}</td><td>${document.getElementById('c_name').value}</td>`
);

setupForm('empForm', 'empTable', () => {
    const sal = parseFloat(document.getElementById('e_sal').value) || 0;
    return `<td>${document.getElementById('e_id').value}</td><td>${document.getElementById('e_name').value}</td><td>${document.getElementById('e_pos').value}</td><td>${document.getElementById('e_con').value}</td><td>${document.getElementById('e_sex').value}</td><td>${document.getElementById('e_dob').value}</td><td>${document.getElementById('e_hired').value}</td><td>$${sal.toFixed(2)}</td>`;
});

setupForm('salesForm', 'salesTable', () => {
    const qty   = parseFloat(document.getElementById('s_qty').value)   || 0;
    const price = parseFloat(document.getElementById('s_price').value) || 0;
    const disc  = parseFloat(document.getElementById('s_disc').value)  || 0;
    const total = (qty * price) - disc;
    return `<td>${document.getElementById('s_rid').value}</td><td>${document.getElementById('s_mid').value}</td><td>${document.getElementById('s_pid').value}</td><td>${document.getElementById('s_eid').value}</td><td>${qty.toFixed(2)}</td><td>$${price.toFixed(2)}</td><td>$${disc.toFixed(2)}</td><td><b>$${total.toFixed(2)}</b></td>`;
});

setupForm('purForm', 'purTable', () => {
    const qty   = parseFloat(document.getElementById('p_qty').value)   || 0;
    const price = parseFloat(document.getElementById('p_price').value) || 0;
    const total = qty * price;
    return `<td>${document.getElementById('p_id').value}</td><td>${document.getElementById('p_pid').value}</td><td>${document.getElementById('p_name').value}</td><td>${qty.toFixed(2)}</td><td>$${price.toFixed(2)}</td><td>$${total.toFixed(2)}</td>`;
});

setupForm('resForm', 'resTable', () => {
    const qty   = parseFloat(document.getElementById('r_qty').value)   || 0;
    const price = parseFloat(document.getElementById('r_price').value) || 0;
    const total = qty * price;
    return `<td>${document.getElementById('r_id').value}</td><td>${document.getElementById('r_pid').value}</td><td>${document.getElementById('r_name').value}</td><td>${qty.toFixed(2)}</td><td>$${price.toFixed(2)}</td><td>$${total.toFixed(2)}</td>`;
});

setupForm('memForm', 'memTable', () => {
    const pts = parseFloat(document.getElementById('m_pts').value) || 0;
    return `<td>${document.getElementById('m_id').value}</td><td>${document.getElementById('m_rank').value}</td><td>${document.getElementById('m_name').value}</td><td>${pts.toFixed(2)}</td><td>${document.getElementById('m_date').value}</td>`;
});