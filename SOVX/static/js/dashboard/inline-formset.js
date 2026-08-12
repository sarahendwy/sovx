// Generic add/remove UI for Django inline formsets rendered by
// partials/components/form.html. A formset section is any element with a
// `data-formset` attribute containing:
//   - `[data-formset-forms]`      the container holding one `data-formset-form` per row
//   - `template[data-formset-empty-form]`  markup for a new blank row (uses `__prefix__`)
//   - `[data-formset-add]`        button that appends a new row
//   - the management form's TOTAL_FORMS hidden input
//
// Rows are never removed from the DOM: "Remove" just checks the row's DELETE
// checkbox and hides it, so Django still sees the submitted data and, for
// existing rows, deletes the related object on save.
(function () {
  function bindRow(row) {
    const deleteInput = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
    const removeButton = row.querySelector('[data-formset-remove]');

    if (deleteInput && deleteInput.checked) {
      row.hidden = true;
    }

    if (removeButton) {
      removeButton.addEventListener('click', function () {
        if (deleteInput) {
          deleteInput.checked = true;
        }
        row.hidden = true;
      });
    }
  }

  function initFormset(root) {
    const formsContainer = root.querySelector('[data-formset-forms]');
    const emptyTemplate = root.querySelector('template[data-formset-empty-form]');
    const addButton = root.querySelector('[data-formset-add]');
    const totalFormsInput = root.querySelector('input[name$="-TOTAL_FORMS"]');

    if (!formsContainer) return;

    formsContainer.querySelectorAll('[data-formset-form]').forEach(bindRow);

    if (addButton && emptyTemplate && totalFormsInput) {
      addButton.addEventListener('click', function () {
        const index = parseInt(totalFormsInput.value, 10);
        const html = emptyTemplate.innerHTML.replace(/__prefix__/g, index);

        const wrapper = document.createElement('div');
        wrapper.innerHTML = html.trim();
        const newRow = wrapper.firstElementChild;

        formsContainer.appendChild(newRow);
        bindRow(newRow);
        totalFormsInput.value = String(index + 1);
      });
    }
  }

  document.querySelectorAll('[data-formset]').forEach(initFormset);
})();
