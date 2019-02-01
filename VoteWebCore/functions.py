# Useful functions
def form_errors(form):
    errors_str = form.errors.as_text()
    _errors = errors_str.split('*')
    errors = []
    for i in range(len(_errors)):
        err = _errors[i].strip()
        if len(err) and err[0].isupper():
            errors.append(err)
    return errors
