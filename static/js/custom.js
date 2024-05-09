function showAlert(title, icon, onload) {
    const Toast = Swal.mixin({
        toast: true,
        position: "top-end",
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.onmouseenter = Swal.stopTimer;
            toast.onmouseleave = Swal.resumeTimer;
        }
    });
    if (onload) {
        window.onload = Toast.fire({
            icon: icon,
            title: title
        })
    } else {
        Toast.fire({
            icon: icon,
            title: title
        });
    }
    
}
