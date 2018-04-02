function rating_to_color(n) {
    if (n >= 3.5 && n <= 5)
        return 'good';
    else if (n >= 2.5 && n < 3.5)
        return 'neutral';
    else if (n >=0 && n < 2.5)
        return 'bad';
    else
        return 'bg-secondary';
}

function gpa_to_color(n) {
    if (n >= 3.67 && n <= 4.33)
        return 'good';
    else if (n >= 2.33 && n < 3.67)
        return 'neutral';
    else if (n >=0 && n < 2.33)
        return 'bad';
    else
        return 'bg-secondary';
}

function workload_to_color(n) {
    if (n >= 3.5 && n <= 5)
        return 'bad';
    else if (n >= 2.5 && n < 3.5)
        return 'neutral';
    else if (n >=0 && n < 2.5)
        return 'good';
    else
        return 'bg-secondary';
}