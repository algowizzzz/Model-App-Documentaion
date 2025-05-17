/**
 * A test JavaScript file to verify parseable non-Python file handling
 */

class TestClass {
    constructor(value) {
        this.value = value;
    }

    /**
     * A method with JSDoc comments
     * @param {number} x - The input number
     * @returns {number} The doubled value
     */
    doubleValue(x) {
        return x * 2;
    }
}

function testFunction(param1, param2 = "default") {
    return `${param1} - ${param2}`;
}

// Export the components
module.exports = {
    TestClass,
    testFunction
}; 