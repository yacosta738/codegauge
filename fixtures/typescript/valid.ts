function outer(value: number) {
    if (value > 0) {
        return value;
    }
    function inner() {
        return 0;
    }
    return inner();
}

const add = (value: number) => value + 1;
